import feedparser
import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 5 
START_MARKER = ""
END_MARKER = ""

TEMPLATE = """
<td width="50%" valign="top">
    <a href="{link}" target="_blank">
        <img src="https://picsum.photos/seed/{seed}/400/220" width="100%" style="border-radius:8px; border:1px solid #30363d;" alt="{title}">
    </a>
    <p align="left">
        <a href="{link}" target="_blank"><b>{title}</b></a><br/>
        <img src="https://img.shields.io/badge/Release-{date}-blue?style=flat-square" />
    </p>
</td>
"""

def get_stable_seed(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def format_posts(posts):
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
    footer = f'\n<div align="center"><a href="https://czhlove.cn/" target="_blank">查看更多文章</a></div>'
    return table + footer

def update_readme(new_content):
    if not os.path.exists(README_FILE):
        return False
        
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 核心修复逻辑：不再使用 re.sub，改用字符串分割 ---
    if START_MARKER not in content or END_MARKER not in content:
        print("错误：README 中缺少标记位")
        return False

    # 1. 取得标记位之前的内容 (Header)
    # 取第一个 START_MARKER 之前的所有内容
    header = content.split(START_MARKER)[0]
    
    # 2. 取得标记位之后的内容 (Footer)
    # 取最后一个 END_MARKER 之后的所有内容
    footer = content.rsplit(END_MARKER, 1)[-1]

    # 3. 重新组装内容，彻底抛弃中间所有重复的垃圾数据
    new_readme = f"{header}{START_MARKER}\n{new_content}\n{END_MARKER}{footer}"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)
    return True

if __name__ == "__main__":
    print("开始获取 RSS...")
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        if update_readme(format_posts(feed.entries)):
            print("README.md 更新成功！")
    else:
        print("RSS 源为空")