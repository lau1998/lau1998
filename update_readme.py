import feedparser
import re
import os
from datetime import datetime

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 8
START_MARKER = ""
END_MARKER = ""
# 定义“酷炫”的美化模板
# 使用 Emoji 和粗体
TEMPLATE = "* 🚀 [{title}]({link}) - *{date}*" 
# --------------------

def format_posts(posts):
    """根据模板格式化博客文章列表"""
    formatted_list = []
    
    # 获取最新的 N 篇文章
    for entry in posts[:MAX_POSTS]:
        # 解析日期并格式化（例如：2025年12月05日）
        try:
            # 尝试解析常用的RSS日期格式
            date_obj = datetime(*entry.published_parsed[:6])
            formatted_date = date_obj.strftime("%Y年%m月%d日")
        except:
            formatted_date = "未知日期"
            
        # 使用配置的模板
        post_line = TEMPLATE.format(
            title=entry.title,
            link=entry.link,
            date=formatted_date
        )
        formatted_list.append(post_line)
        
    return "\n".join(formatted_list)

def update_readme(new_content):
    """读取 README，替换标记内的内容，并写回文件"""
    print(f"Reading {README_FILE}...")
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # 使用正则表达式找到开始和结束标记之间的内容
    pattern = re.compile(f"{START_MARKER}.*{END_MARKER}", re.DOTALL)

    # 替换内容
    new_readme_content = pattern.sub(
        f"{START_MARKER}\n{new_content}\n{END_MARKER}",
        readme_content
    )

    if new_readme_content != readme_content:
        print(f"Content changed. Writing back to {README_FILE}...")
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_readme_content)
        return True
    else:
        print("No change in blog list content. Skipping file write.")
        return False

def main():
    print(f"Fetching RSS from: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("Error: Could not retrieve or parse RSS feed.")
        return

    # 1. 格式化文章列表
    new_posts_content = format_posts(feed.entries)
    print("Generated Post Content:\n" + new_posts_content)

    # 2. 更新 README 文件
    if update_readme(new_posts_content):
        print("Successfully updated README.md!")
    else:
        print("README.md did not need updating.")

if __name__ == "__main__":
    # 需要安装：pip install feedparser
    main()