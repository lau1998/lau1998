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
    # 占位符类，避免程序在缺少依赖时崩溃
    class GraphqlClient:
        def __init__(self, endpoint):
            print("Warning: GraphqlClient is not installed. GitHub API functions will not work.")
            pass
    client = GraphqlClient(endpoint="https://api.github.com/graphql")
    
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

# 此处省略 formatGMTime 和 make_query 函数，假设它们在您实际的环境中已定义并运行

# --- 抓取函数 (MOCK 或简化版本，需要您确保其在您的环境中具有实际的实现) ---

def fetch_releases(token):
    # 模拟 GitHub Releases
    # 请替换为您的实际实现
    return [
        {"repo": "icondog", "release": "v0.0.1", "url": "https://github.com/djyde/icondog/releases/tag/v0.0.1", "published_at": "2024-06-15"},
    ] 

def fetch_code_time():
    """获取 WakaTime 代码时间统计 Gist"""
    # 警告: fetch_code_time 依赖于 httpx 的实现
    return httpx.get(
        "https://gist.githubusercontent.com/pseudoyu/48675a7b5e3cca534e7817595d566003/raw/"
    )

def fetch_douban():
    # 模拟豆瓣动态
    # 请替换为您的实际实现
    return [
        {"title": "在看东周列国·春秋篇", "url": "https://movie.douban.com/subject/2341884/", "published": "2025-11-22"},
        {"title": "想读欢乐英雄", "url": "https://book.douban.com/subject/1264579/", "published": "2025-10-25"},
    ]

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
            # 使用 datetime.datetime(*entry.published_parsed[:6]) 兼容性更好
            date_obj = datetime.datetime(*entry.published_parsed[:6])
            published_date = date_obj.strftime("%Y-%m-%d") # 简洁日期格式
        except Exception:
            published_date = "未知日期"
            
        formatted_entries.append({
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "date": published_date,
        })
        
    return formatted_entries

# --- 静态内容定义 ---

def get_static_profile_header():
    """定义炫酷的个人介绍头部 (profile_header)"""
    header = """
<p align="center">
 <h3 align="center">🧑🏻‍💻 Vibe Coding... 🧑🏻‍💻</h3>
</p>

### Hi there ✋

[![wakatime](https://wakatime.com/badge/user/990b78cd-738d-40b5-b130-3aacf3ce0b82.svg)](https://wakatime.com/@990b78cd-738d-40b5-b130-3aacf3ce0b82)
[![GitHub](https://img.shields.io/github/followers/pseudoyu?logo=github&style=flat-square)](https://github.com/pseudoyu)
[![yu-blog](https://img.shields.io/badge/blog-yu-9cf?style=flat-square)](https://www.pseudoyu.com)
[![Visits Badge](https://badges.strrl.dev/visits/pseudoyu/pseudoyu?style=flat-square)](https://github.com/pseudoyu)

<br />

I'm [pseudoyu](https://www.pseudoyu.com), Blockchain Developer, MSc Graduate in ECIC(Electronic Commerce and Internet Computing) @ The University of Hong Kong (HKU). Love to learn and build things. Follow me on [GitHub](https://github.com/pseudoyu). Know me on [Telegram Channel](https://t.me/pseudoyulife).

I want to learn things and become a better person. I enjoy reading, thinking and writing in my leisure time.

#### 🔨 Coding Activities

[![Contributions Badge](https://badges.strrl.dev/contributions/all/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Contributions Badge](https://badges.strrl.dev/contributions/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Commits Badge](https://badges.strrl.dev/commits/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)
[![Issues and PRs Badge](https://badges.strrl.dev/issues-and-prs/weekly/pseudoyu?style=flat-square)](https://github.com/pseudoyu)

- 💼 Love open-source
- 💬 Ask me about anything, [email me](mailto:pseudoyu@connect.hku.hk)
"""
    return header

def get_github_stats():
    """定义炫酷的 GitHub 统计信息 (github_stats)"""
    stats = """
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
    return stats


# --- 主执行逻辑 ---

def main():
    # 确保文件路径正确
    readme = root / README_FILE
    
    # 检查 README 文件是否存在，如果不存在则创建包含标记的最小模板
    if not readme.exists():
        print(f"Warning: {README_FILE} not found. Creating a minimal one.")
        minimal_content = (
            "<!-- profile_header starts --><!-- profile_header ends -->\n"
            "<!-- github_stats starts --><!-- github_stats ends -->\n"
            "#### 👨🏻‍💻 This Week I Code With\n<!-- code_time starts --><!-- code_time ends -->\n"
            "#### 📰 Recent Posts (Pseudoyu)\n<!-- blog starts --><!-- blog ends -->\n"
            "#### 🚀 CZH Love Blog\n<!-- czh_blog starts --><!-- czh_blog ends -->\n"
            "#### 🎧 Recent Digests\n<!-- douban starts --><!-- douban ends -->\n"
            "#### 💻 Recent Releases\n<!-- recent_releases starts --><!-- recent_releases ends -->\n"
        )
        with open(readme, "w", encoding="utf-8") as f:
            f.write(minimal_content)

    # 1. 读取 README 内容
    readme_contents = readme.open(encoding="utf-8").read()
    rewritten = readme_contents

    # 2. 插入静态头部信息 (个人介绍和徽章)
    profile_header_md = get_static_profile_header()
    rewritten = replace_chunk(rewritten, "profile_header", profile_header_md)

    # 3. 插入 GitHub Stats 统计信息
    github_stats_md = get_github_stats()
    rewritten = replace_chunk(rewritten, "github_stats", github_stats_md)
    
    # 4. 更新 Code Time
    try:
        code_time_text = "\n```text\n"+fetch_code_time().text+"\n```\n"
    except Exception as e:
        print(f"Error fetching Code Time: {e}")
        code_time_text = "\n```text\nCode time data fetch failed.\n```\n"
    rewritten = replace_chunk(rewritten, "code_time", code_time_text)

    # 5. 更新 Pseudoyu 博客文章 (原有逻辑)
    entries = fetch_blog_entries()[:6]
    entries_md = "\n".join(
        ["* <a href={url} target='_blank'>{title}</a>".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    # 6. 更新您的 CZH Love 博客文章 (优化样式)
    czh_entries = fetch_czh_blog_entries()[:MAX_POSTS]
    # 酷炫模板：🚀 **标题** *(日期)*
    czh_entries_md = "\n".join(
        [
            "* 🚀 **<a href={url} target='_blank'>{title}</a>** *({date})*".format(**entry) 
            for entry in czh_entries
        ]
    )
    rewritten = replace_chunk(rewritten, "czh_blog", czh_entries_md)
    
    # 7. 更新 Douban Digests
    doubans = fetch_douban()[:5]
    doubans_md = "\n".join(
        ["* 🎧 <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in doubans]
    )
    rewritten = replace_chunk(rewritten, "douban", doubans_md)
    
    # 8. 更新 GitHub Releases
    releases = fetch_releases(TOKEN)
    releases.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    md = "\n".join(
        [
            # 💻 使用 Emoji 强调代码
            "* 💻 <a href={url} target='_blank'>{repo} {release}</a> - {published_at}".format(**release)
            for release in releases[:10]
        ]
    )
    rewritten = replace_chunk(rewritten, "recent_releases", md)

    # 9. 写回 README 文件
    if rewritten != readme_contents:
        print("Content changed. Writing back to README.md...")
        readme.open("w", encoding="utf-8").write(rewritten)
    else:
        print("No changes detected in README.md content. Skipping file write.")

if __name__ == "__main__":
    main()