import feedparser
import re
import os
import hashlib
from datetime import datetime
from urllib.parse import quote

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 5  # 严格限制 5 条
START_MARKER = ""
END_MARKER = ""

# --- 极简稳定的模板 ---
# 修复了双减号问题，确保徽章显示正常
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
                # 改回单减号，query parameter 形式不需要双减号
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except:
                formatted_date = "Recently"
            
            title = entry.title.replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')
            seed = get_stable_seed(entry.link)
            cells.append(TEMPLATE.format(
                title=title, 
                link=entry.link, 
                date=quote(formatted_date), 
                seed=seed
            ))
        
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')
        rows.append(f"  <tr>{''.join(cells)}</tr>")

    table = '<table width="100%">\n' + "\n".join(rows) + "\n</table>"
    footer = f'\n<div align="center"><a href="https://czhlove.cn/" target="_blank">查看更多文章</a></div>'
    return table + footer

def update_readme(new_content):
    if not os.path.exists(README_FILE):
        print("README.md 不存在")
        return False
        
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 检查标记位是否存在
    if START_MARKER not in content or END_MARKER not in content:
        print("错误：未找到标记位！")
        return False

    # 2. 使用正则表达式进行精准替换
    # flags=re.DOTALL 让 . 匹配换行符
    # count=1 极其重要：防止重复替换导致的文件爆炸
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        flags=re.DOTALL
    )

    replacement = f"{START_MARKER}\n{new_content}\n{END_MARKER}"
    
    # 执行替换
    new_readme, substitute_count = pattern.subn(replacement, content, count=1)

    if substitute_count == 0:
        print("替换失败")
        return False

    # 3. 最终检查：防止意外的标记嵌套
    # 如果发现替换后的内容里包含了两组标记，说明之前的文件已经脏了
    if new_readme.count(START_MARKER) > 1:
        print("检测到重复标记，正在尝试清理...")
        # 这种情况下，我们强制只保留最外层的一组
        parts = new_readme.split(START_MARKER)
        # 重新组合：第一部分 + 标记 + 新内容 + 结束标记 + 最后一部分（跳过中间所有的旧标记）
        final_parts = new_readme.split(END_MARKER)
        new_readme = parts[0] + replacement + final_parts[-1]

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
            print("更新失败，请检查标记位。")
    else:
        print("RSS 源没有内容")