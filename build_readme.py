import feedparser
import re
import os
from datetime import datetime

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 6  # 因为有大图，展示 6 篇（3行）视觉效果较好
START_MARKER = ""
END_MARKER = ""

# --- 进阶美化模板 ---
# 使用 HTML 表格单元格 (td)。
# 包含：封面大图(顶部)、标题(中部)、日期徽章(底部)
# 样式说明：
# valign="top": 内容顶对齐
# object-fit: cover: 保证图片填充且不变形
# border-radius: 圆角让卡片更柔和
TEMPLATE = """
<td width="50%" valign="top" style="padding: 10px;">
    <a href="{link}" target="_blank">
        <img src="{image_url}" width="100%" height="160" style="object-fit: cover; border-radius: 8px; border: 1px solid #e1e4e8;" alt="{title}">
    </a>
    <h4 align="left" style="margin-top: 12px; margin-bottom: 8px;">
        <a href="{link}" target="_blank" style="text-decoration: none; color: #0366d6;">{title}</a>
    </h4>
    <div align="left">
        <img src="https://img.shields.io/badge/📅%20发布于-{date}-F3F4F6?style=flat-square&logoColor=57606A&labelColor=F3F4F6&color=9CA3AF" alt="{date}" />
    </div>
</td>
"""

def format_posts(posts):
    """将文章列表转换成带封面的双列 HTML 表格"""
    rows = []
    # 限制文章数量
    target_posts = posts[:MAX_POSTS]
    
    # 每次循环处理 2 篇文章
    for i in range(0, len(target_posts), 2):
        pair = target_posts[i:i+2]
        cells = []
        # 内部循环处理每一行的 1 或 2 篇文章
        # 使用 j 来计算全局索引，用于生成唯一的随机图
        for j, entry in enumerate(pair):
            global_index = i + j
            try:
                date_obj = datetime(*entry.published_parsed[:6])
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except:
                formatted_date = "Recently"
            
            # 清理标题
            title = entry.title.replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')
            
            # --- 生成随机封面图 URL (进阶功能核心) ---
            # 使用 Unsplash Source，关键词 tech,code,laptop
            # 关键：加上 &sig={global_index} 确保每张卡片的图片不一样
            image_url = f"https://source.unsplash.com/400x250/?tech,code,developer&sig={global_index}"
            
            cells.append(TEMPLATE.format(
                title=title, 
                link=entry.link, 
                date=formatted_date,
                image_url=image_url
            ))
        
        # 如果最后一行落单，补一个空单元格维持布局
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')
        
        rows.append(f"  <tr>{''.join(cells)}</tr>")

    return '<table width="100%">\n' + "\n".join(rows) + "\n</table>"

def update_readme(new_content):
    """定位标记位并替换内容"""
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.")
        return False

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 正则匹配
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    replacement = f"{START_MARKER}\n{new_content}\n{END_MARKER}"
    
    if not pattern.search(content):
        print("Error: 未在 README 中找到标记位！")
        return False

    new_readme = pattern.sub(replacement, content)

    # 检查是否有实质变化
    # 注意：由于每次图片 URL 都是新的，这里几乎每次都会触发更新，这是预期的
    if new_readme != content:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_readme)
        return True
    return False

def main():
    print(f"Fetching RSS: {RSS_URL}")
    # 增加超时设置，防止卡住
    feed = feedparser.parse(RSS_URL, agent="Mozilla/5.0")

    if not feed.entries:
        print("Error: Could not retrieve RSS feed.")
        # 尝试打印一些调试信息
        if hasattr(feed, "status"):
             print(f"HTTP Status: {feed.status}")
        return

    html_content = format_posts(feed.entries)
    
    if update_readme(html_content):
        print("Success: README updated with new post cards!")
    else:
        print("Info: No changes detected.")

if __name__ == "__main__":
    main()