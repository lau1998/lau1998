import feedparser
import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 5  # 严格限制 5 条文章
START_MARKER = ""
END_MARKER = ""

# --- 模板：使用极简 HTML ---
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
    # 2列布局逻辑
    for i in range(0, len(target_posts), 2):
        pair = target_posts[i:i+2]
        cells = []
        for entry in pair:
            try:
                date_obj = datetime(*entry.published_parsed[:6])
                formatted_date = date_obj.strftime("%Y--%m--%d")
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

    # 关键改进：使用 .*? 进行非贪婪匹配，防止吞掉整个文件
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    if not pattern.search(content):
        print("错误：未找到标记位，请检查 README.md 是否包含正确的注释")
        return False

    # 替换内容
    new_readme = pattern.sub(f"{START_MARKER}\n{new_content}\n{END_MARKER}", content)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)
    return True

if __name__ == "__main__":
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        if update_readme(format_posts(feed.entries)):
            print("更新成功")