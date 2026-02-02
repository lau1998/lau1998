import feedparser
import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 10  # 限制 10 条
START_MARKER = ""
END_MARKER = ""

# --- 增强版卡片模板 ---
# 1. 增加图片边框阴影效果
# 2. 使用固定高度保证对齐
TEMPLATE = """
<td width="50%" valign="top" style="padding: 10px;">
    <a href="{link}" target="_blank">
        <img src="https://picsum.photos/seed/{seed}/400/220" width="100%" style="border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border: 1px solid #30363d;" alt="{title}">
    </a>
    <br />
    <p align="left" style="margin-top: 8px;">
        <a href="{link}" target="_blank"><b>{title}</b></a>
        <br />
        <img src="https://img.shields.io/badge/Release-{date}-blue?style=flat-square&logo=clock" />
    </p>
</td>
"""

def get_stable_seed(text):
    """根据内容生成唯一且固定的随机种子"""
    return hashlib.md5(text.encode()).hexdigest()[:8]

def format_posts(posts):
    target_posts = posts[:MAX_POSTS]
    rows = []
    
    for i in range(0, len(target_posts), 2):
        pair = target_posts[i:i+2]
        cells = []
        for entry in pair:
            # 格式化日期：Shields.io 格式要求不能有空格
            try:
                date_obj = datetime(*entry.published_parsed[:6])
                formatted_date = date_obj.strftime("%Y--%m--%d")
            except:
                formatted_date = "Recently"
            
            title = entry.title.replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')
            seed = get_stable_seed(entry.link)
            
            cells.append(TEMPLATE.format(
                title=title, 
                link=entry.link, 
                date=quote(formatted_date), # 关键：进行 URL 编码防止 404
                seed=seed
            ))
        
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')
        rows.append(f"  <tr>{''.join(cells)}</tr>")

    # 底部装饰：居中的“查看更多”按钮
    footer = """
<div align="center">
    <br />
    <a href="https://czhlove.cn/" target="_blank">
        <img src="https://img.shields.io/badge/🚀%20查看我的全部文章-0366d6?style=for-the-badge&logo=rss&logoColor=white" />
    </a>
</div>
"""
    return '<table width="100%" border="0">\n' + "\n".join(rows) + "\n</table>" + footer

def update_readme(new_content):
    if not os.path.exists(README_FILE): return False
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
    replacement = f"{START_MARKER}\n{new_content}\n{END_MARKER}"
    
    if not pattern.search(content): return False
    new_readme = pattern.sub(replacement, content)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)
    return True

if __name__ == "__main__":
    feed = feedparser.parse(RSS_URL)
    if feed.entries:
        update_readme(format_posts(feed.entries))