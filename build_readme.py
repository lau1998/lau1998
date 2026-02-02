import feedparser
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

def get_stable_seed(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def format_posts(posts):
    MAX_POSTS = 5
    # 使用 picsum + seed 确保图片稳定且随机
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
            
            # 清理标题特殊字符
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
    start_marker = ""
    end_marker = ""
    
    if not os.path.exists(file_path):
        print("README.md not found!")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if start_marker not in content or end_marker not in content:
        print("Error: 标记位丢失！请在 README.md 中添加 和 ")
        return False

    # 物理截断法：不管中间有什么垃圾数据，直接丢弃，只拼接头尾和新内容
    try:
        header = content.split(start_marker)[0]
        footer = content.rsplit(end_marker, 1)[-1]
        new_readme = f"{header}{start_marker}\n{new_content}\n{end_marker}{footer}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README 内容已在本地更新...")
        return True
    except Exception as e:
        print(f"Error updating file: {e}")
        return False

if __name__ == "__main__":
    rss_url = "https://czhlove.cn/rss.xml"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        if update_readme(format_posts(feed.entries)):
            print("脚本运行完成，等待 Git Push...")
    else:
        print("RSS 无内容")