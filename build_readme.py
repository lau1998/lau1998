from python_graphql_client import GraphqlClient
import feedparser
import httpx
import json
import pathlib
import re
import os
import datetime

# 确定仓库的根目录
root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")

# 从环境变量中获取 TOKEN
TOKEN = os.environ.get("GH_TOKEN", "")

def replace_chunk(content, marker, chunk, inline=False):
    """
    替换 Markdown/文本中的特定标记块。
    """
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def formatGMTime(timestamp):
    """
    格式化 GMT 时间戳，并转换为北京时间 (UTC+8)。
    """
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    try:
        dateStr = datetime.datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
        return dateStr.date()
    except ValueError:
        return datetime.date.today()

def make_query(after_cursor=None):
    """
    构建 GraphQL 查询，用于分页获取仓库 Releases 信息。
    """
    return """
query {
  viewer {
    repositories(first: 100, privacy: PUBLIC, after:AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        description
        url
        releases(last:1) {
          totalCount
          nodes {
            name
            publishedAt
            url
          }
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def fetch_releases(oauth_token):
    """
    通过 GraphQL API 获取所有仓库的最新 Release。
    """
    releases = []
    repo_names = set()
    has_next_page = True
    after_cursor = None

    # 如果 TOKEN 不存在，则返回空列表并打印警告
    if not oauth_token:
        print("Warning: GH_TOKEN is missing or empty. Skipping release fetch.")
        return []

    while has_next_page:
        try:
            # 这里的 Authorization 使用了您的 PAT/Secret
            data = client.execute(
                query=make_query(after_cursor),
                headers={"Authorization": "Bearer {}".format(oauth_token)},
            )
        except Exception as e:
            # 捕获 HTTP 或连接错误
            print(f"Error fetching releases from GraphQL: {e}")
            return []

        # 检查是否有 API 级别的错误（例如 401 Unauthorized）
        if "errors" in data:
            print("GraphQL API returned errors:")
            print(json.dumps(data["errors"], indent=4))
            return []

        repositories = data.get("data", {}).get("viewer", {}).get("repositories", {})
        if not repositories:
            break
            
        for repo in repositories.get("nodes", []):
            # 检查是否有 release 且仓库名未重复
            if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
                repo_names.add(repo["name"])
                if repo["releases"]["nodes"]:
                    release_node = repo["releases"]["nodes"][0]
                    releases.append(
                        {
                            "repo": repo["name"],
                            "repo_url": repo["url"],
                            "description": repo["description"],
                            "release": release_node["name"]
                            .replace(repo["name"], "")
                            .strip(),
                            "published_at": release_node["publishedAt"].split("T")[0],
                            "url": release_node["url"],
                        }
                    )
        
        page_info = repositories.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after_cursor = page_info.get("endCursor")
        
    return releases

# --- 外部数据抓取函数 ---
def fetch_code_time():
    """获取 Gist 中的代码时间统计信息"""
    try:
        return httpx.get(
            "https://gist.githubusercontent.com/pseudoyu/48675a7b5e3cca534e7817595d566003/raw/"
        )
    except Exception as e:
        print(f"Error fetching code time: {e}")
        return type('obj', (object,), {'text' : 'Failed to load code time.'})() # 返回一个模拟对象

def fetch_douban():
    """获取豆瓣 RSS 订阅条目"""
    try:
        entries = feedparser.parse("https://www.douban.com/feed/people/pseudo-yu/interests")["entries"]
        return [
            {
                "title": item["title"],
                "url": item["link"].split("#")[0],
                "published": formatGMTime(item["published"])
            }
            for item in entries
        ]
    except Exception as e:
        print(f"Error fetching douban feed: {e}")
        return []

def fetch_blog_entries():
    """获取博客 RSS 订阅条目"""
    try:
        entries = feedparser.parse("https://www.pseudoyu.com/zh/index.xml")["entries"]
        return [
            {
                "title": entry["title"],
                "url": entry["link"].split("#")[0],
                "published": entry["published"].split("T")[0],
            }
            for entry in entries
        ]
    except Exception as e:
        print(f"Error fetching blog feed: {e}")
        return []

# --- 主逻辑 ---
if __name__ == "__main__":
    readme = root / "README.md"
    project_releases = root / "releases.md"
    
    # 📌 修复文件缺失错误: 检查并创建 releases.md
    if not project_releases.exists():
        initial_content = """
# Project Releases

This file is automatically generated by GitHub Actions.

<!-- release_count starts -->0<!-- release_count ends --> releases tracked.

<!-- recent_releases starts -->
No releases found yet.
<!-- recent_releases ends -->
"""
        project_releases.open("w", encoding="utf-8").write(initial_content.strip())
        print("Created initial releases.md file.")

    # 1. 获取并处理 Releases
    releases = fetch_releases(TOKEN)
    releases.sort(key=lambda r: r["published_at"], reverse=True)
    
    # README.md 更新
    md = "\n".join(
        [
            "* <a href={url} target='_blank'>{repo} {release}</a> - {published_at}".format(**release)
            for release in releases[:10]
        ]
    )
    readme_contents = readme.open().read()
    rewritten = replace_chunk(readme_contents, "recent_releases", md)

    # releases.md 更新
    project_releases_md = "\n".join(
        [
            (
                "* **[{repo}]({repo_url})**: [{release}]({url}) - {published_at}\n"
                "<br>{description}"
            ).format(**release)
            for release in releases
        ]
    )
    # 确保文件存在后才读取
    project_releases_content = project_releases.open().read()
    project_releases_content = replace_chunk(
        project_releases_content, "recent_releases", project_releases_md
    )
    project_releases_content = replace_chunk(
        project_releases_content, "release_count", str(len(releases)), inline=True
    )
    project_releases.open("w").write(project_releases_content)

    # 2. 更新 Code Time
    code_time_text = "\n```text\n"+fetch_code_time().text+"\n```\n"
    rewritten = replace_chunk(rewritten, "code_time", code_time_text)

    # 3. 更新 Douban
    doubans = fetch_douban()[:5]
    doubans_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in doubans]
    )
    rewritten = replace_chunk(rewritten, "douban", doubans_md)

    # 4. 更新 Blog Entries
    entries = fetch_blog_entries()[:6]
    entries_md = "\n".join(
        ["* <a href={url} target='_blank'>{title}</a>".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    # 写入最终的 README.md
    readme.open("w").write(rewritten)