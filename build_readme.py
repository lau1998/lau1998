import feedparser
import re
import os
import datetime
import pathlib
import httpx

# 如果您没有安装 python_graphql_client，请在 requirements.txt 中添加它
try:
    from python_graphql_client import GraphqlClient
except ImportError:
    # 作为一个占位符，如果环境没有安装，可能需要跳过 GitHub API 相关的函数
    class GraphqlClient:
        def __init__(self, endpoint):
            print("Warning: GraphqlClient is not installed. GitHub API functions will not work.")
            pass
    pass
    
# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 8
# --------------------

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")

# 确保在 GitHub Actions 中设置了 GH_TOKEN secret
TOKEN = os.environ.get("GH_TOKEN", "")

# --- 核心辅助函数 ---

def replace_chunk(content, marker, chunk, inline=False):
    """使用标记替换 README.md 中的内容块"""
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def formatGMTime(timestamp):
    """格式化 GMT 时间"""
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    try:
        # 尝试解析常用的 RSS 日期格式，并转换为本地时间 (假设为 UTC+8)
        dateStr = datetime.datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
        return dateStr.date()
    except:
        return "未知日期"

# --- 抓取函数 (保持原脚本结构，但添加您的 CZH 博客) ---

def make_query(after_cursor=None):
    # GitHub GraphQL 查询...
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

# 警告: fetch_releases 依赖于 client (GraphqlClient) 的实现
# 假设它能正确运行并返回 [{repo, release, url, published_at, repo_url, description}, ...]
def fetch_releases(token):
    # 此处省略了完整的 GitHub API 交互代码，以简化文件
    # 假设这是您原有脚本中定义的函数，用于获取 GitHub Releases
    return [] # 替换为您的实际实现

def fetch_code_time():
    # 警告: fetch_code_time 依赖于 httpx 的实现
    return httpx.get(
        "https://gist.githubusercontent.com/pseudoyu/48675a7b5e3cca534e7817595d566003/raw/"
    )

def fetch_blog_entries():
    # 抓取 pseudoyu 的博客 (作为原有脚本的一部分)
    entries = feedparser.parse("https://www.pseudoyu.com/zh/index.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]

# 警告: fetch_douban 依赖于外部数据源和实现
# 假设这是您原有脚本中定义的函数，用于获取豆瓣动态
def fetch_douban():
    return [] # 替换为您的实际实现

def fetch_czh_blog_entries():
    """
    抓取您的博客文章 (https://czhlove.cn/rss.xml) 并格式化
    """
    print(f"Fetching CZH Blog RSS from: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Error: Could not retrieve or parse CZH RSS feed.")
        return []
        
    formatted_entries = []
    for entry in feed.entries:
        published_date = ""
        try:
            # 尝试解析日期并格式化
            date_obj = datetime.datetime(*entry.published_parsed[:6])
            published_date = date_obj.strftime("(%Y-%m-%d)")
        except Exception:
            published_date = "(未知日期)"
            
        formatted_entries.append({
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "date": published_date,
        })
        
    return formatted_entries

# --- 静态内容定义 ---

def get_static_profile_header():
    """定义您要求的新静态头部内容"""
    # 注意：这里的 Markdown 格式是为了直接插入到 README 中
    header = """
<p align="center">
 <h3 align="center">🧑🏻‍💻 Vibe Coding... 🧑🏻‍💻</h3>
</p>

### Hi there ✋

I'm [pseudoyu](https://www.pseudoyu.com), Blockchain Developer, MSc Graduate in ECIC(Electronic Commerce and Internet Computing) @ The University of Hong Kong (HKU). Love to learn and build things. Follow me on [GitHub](https://github.com/pseudoyu). Know me on [Telegram Channel](https://t.me/pseudoyulife).

I want to learn things and become a better person. I enjoy reading, thinking and writing in my leisure time.

#### 🔨 Coding Activities

[![Contributions Badge](https://badges.strrl.dev/contributions/all/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Contributions Badge](https://badges.strrl.dev/contributions/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Commits Badge](https://badges.strrl.dev/commits/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Issues and PRs Badge](https://badges.strrl.dev/issues-and-prs/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)

- 💼 Love open-source
- 💬 Ask me about anything, [email me](mailto:pseudoyu@connect.hku.hk)

#### :octocat: Github Stats

<table align="center" width="100%">
  <tr>
    <td align="center">
      <strong> 🌟 I'm proud to be part of these organizations 🌟 </strong><br>
      <table>
        <tr>
          <td align="center">
            <a href="https://github.com/NaturalSelectionLabs">
              <img src="https://avatars.githubusercontent.com/u/82145280?s=150&v=4" />
            </a>
          </td>
          <td align="center">
            <a href="https://github.com/rss3-network">
              <img src="https://avatars.githubusercontent.com/u/152575164?s=150&v=4" />
            </a>
          </td>
        </tr>
      </table>
    </td>
    <td align="center">
      <img width="120%" src="https://yu-readme.vercel.app/api?username=pseudoyu&count_private=true&theme=gotham&show_icons=true" />
    </td>
  </tr>
  <tr>
          <td align="center">
            <img src="https://yu-readme.vercel.app/api/top-langs/?username=pseudoyu&hide=html,php,css,java,Svelte,smarty&layout=compact&theme=gotham">
          </td>
    <td align="center">
      <img src="https://github-readme-streak-stats.herokuapp.com/?user=pseudoyu&theme=gotham">
    </td>
  </tr>
</table>
"""
    return header

# --- 主执行逻辑 ---

if __name__ == "__main__":
    readme = root / "README.md"
    # 检查 README 文件是否存在，如果不存在则创建
    if not readme.exists():
        print(f"Warning: {README_FILE} not found. Creating a minimal one.")
        with open(readme, "w", encoding="utf-8") as f:
            f.write("<!-- profile_header starts --><!-- profile_header ends -->\n")
            f.write("#### 📰 Recent Posts (Pseudoyu)\n<!-- blog starts --><!-- blog ends -->\n")
            f.write("#### 📝 Latest Blog Posts (CZH Love)\n<!-- czh_blog starts --><!-- czh_blog ends -->\n")

    # 1. 读取 README 内容
    readme_contents = readme.open(encoding="utf-8").read()
    rewritten = readme_contents

    # 2. 插入静态头部信息 (使用新的 profile_header 标记)
    profile_header_md = get_static_profile_header()
    rewritten = replace_chunk(rewritten, "profile_header", profile_header_md)

    # 3. 更新 GitHub Releases
    releases = fetch_releases(TOKEN)
    releases.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    md = "\n".join(
        [
            "* <a href={url} target='_blank'>{repo} {release}</a> - {published_at}".format(**release)
            for release in releases[:10]
        ]
    )
    rewritten = replace_chunk(rewritten, "recent_releases", md)

    # 4. 更新 Code Time
    code_time_text = "\n```text\n"+fetch_code_time().text+"\n```\n"
    rewritten = replace_chunk(rewritten, "code_time", code_time_text)

    # 5. 更新 Douban Digests
    doubans = fetch_douban()[:5]
    doubans_md = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in doubans]
    )
    rewritten = replace_chunk(rewritten, "douban", doubans_md)

    # 6. 更新 Pseudoyu 博客文章 (原有逻辑)
    entries = fetch_blog_entries()[:6]
    entries_md = "\n".join(
        ["* <a href={url} target='_blank'>{title}</a>".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    # 7. 更新您的 CZH Love 博客文章 (新逻辑)
    czh_entries = fetch_czh_blog_entries()[:MAX_POSTS]
    # 使用酷炫模板：🚀 粗体标题 斜体日期
    czh_entries_md = "\n".join(
        [
            "* 🚀 **<a href={url} target='_blank'>{title}</a>** *{date}*".format(**entry) 
            for entry in czh_entries
        ]
    )
    rewritten = replace_chunk(rewritten, "czh_blog", czh_entries_md)


    # 8. 写回 README 文件
    if rewritten != readme_contents:
        print("Content changed. Writing back to README.md...")
        readme.open("w", encoding="utf-8").write(rewritten)
    else:
        print("No changes detected in README.md content.")
    
    # 由于您原脚本中包含 releases.md 逻辑，这里保留但不完整展示
    # project_releases = root / "releases.md" 
    # ...