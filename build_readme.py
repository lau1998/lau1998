import feedparser
import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

def get_stable_seed(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def format_posts(posts):
    # --- 配置直接写在这里，防止被外部错误的全局变量覆盖 ---
    MAX_POSTS = 5
    
    TEMPLATE = """
<td width="50%" valign="top">
    <a href="{link}" target="_blank">
        <img src="https://picsum.photos/seed/{seed}/400/220" width="100%" style="border-radius:8px; border:1px solid #30363d;" alt="{title}">
    </a>
    <p align="left">
        <a href="{link}" target="_blank"><b>{title}</b></a><br/>
        <img src="https://img.shields.io/badge/Release-{date}-blue?style=flat-square" />
    </p>
</td>"""

    target_posts = posts[:MAX_POSTS]
    rows = []
    for i in range(0, len(target_posts), 2):
        pair = target_posts[i:i+2]
        cells = []
        for entry in pair:
            try:
                date_obj = datetime(*entry.published_parsed[:6])
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except:
                formatted_date = "Recently"
            title = entry.title.replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')
            seed = get_stable_seed(entry.link)
            cells.append(TEMPLATE.format(title=title, link=entry.link, date=quote(formatted_date), seed=seed))
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')
        rows.append(f"  <tr>{''.join(cells)}</tr>")

    table = '<table width="100%">\n' + "\n".join(rows) + "\n</table>"
    return table + f'\n<div align="center"><a href="https://czhlove.cn/" target="_blank">查看更多文章</a></div>'

def update_readme(new_content):
    file_path = "README.md"
    # --- 关键：在这里硬编码标记位，确保绝不会是空字符串 ---
    start_marker = ""
    end_marker = ""

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 检查标记位是否存在
    if start_marker not in content or end_marker not in content:
        print(f"Error: Markers '{start_marker}' or '{end_marker}' not found in README.md")
        return False

    # 2. 物理切割：解决“重复内容”和“文件过大”的核心逻辑
    # 逻辑：取 Start 之前的所有内容 + 新内容 + End 之后的所有内容
    try:
        # split 的参数绝对不能是空字符串，这里我们已经硬编码保证了
        header = content.split(start_marker)[0]
        footer = content.rsplit(end_marker, 1)[-1]
        
        # 重新组装
        new_readme = f"{header}{start_marker}\n{new_content}\n{end_marker}{footer}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_readme)
        return True
        
    except Exception as e:
        print(f"An error occurred during update: {str(e)}")
        return False

def main():
    rss_url = "https://czhlove.cn/rss.xml"
    print(f"Fetching RSS: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("Error: No entries found in RSS feed.")
        return

    print(f"Found {len(feed.entries)} posts.")
    html = format_posts(feed.entries)
    
    if update_readme(html):
        print("Success: README.md updated.")
    else:
        print("Failed to update README.md.")

if __name__ == "__main__":
    main()