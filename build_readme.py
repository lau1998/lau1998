import feedparser
import re
from datetime import datetime

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 8

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"

AUTHOR_NAME = "czhlove"

# 两行“卡片感”模板：标题强、日期弱、观感精致
TEMPLATE = (
    "- **{idx}. [{title}]({link})**  \n"
    "  <sub>📅 {date} · ✍️ {author}</sub>"
)


def md_escape(text: str) -> str:
    """简单转义可能影响 Markdown 链接/标题的字符"""
    if not text:
        return ""
    return (
        text.replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def pick_date(entry) -> str:
    """兼容 RSS 常见日期字段：published / updated"""
    dt = None
    if getattr(entry, "published_parsed", None):
        dt = datetime(*entry.published_parsed[:6])
    elif getattr(entry, "updated_parsed", None):
        dt = datetime(*entry.updated_parsed[:6])
    return dt.strftime("%Y年%m月%d日") if dt else "未知日期"


def format_posts(entries) -> str:
    formatted_list = []
    for i, entry in enumerate(entries[:MAX_POSTS], start=1):
        title = md_escape(getattr(entry, "title", "无标题"))
        link = getattr(entry, "link", "#")
        date = pick_date(entry)

        formatted_list.append(
            TEMPLATE.format(
                idx=i,
                title=title,
                link=link,
                date=date,
                author=AUTHOR_NAME,
            )
        )

    header = f"✨ 最近更新（保留 {MAX_POSTS} 篇）\n\n"
    return header + "\n".join(formatted_list)


def update_readme(new_block: str) -> bool:
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError(
            "README 中未找到标记区块，请确保包含：\n"
            f"{START_MARKER}\n{END_MARKER}"
        )

    # 非贪婪匹配，只替换标记之间内容，避免误伤
    pattern = re.compile(
        re.escape(START_MARKER) + r"[\s\S]*?" + re.escape(END_MARKER)
    )

    replacement = f"{START_MARKER}\n{new_block}\n{END_MARKER}"
    new_readme = pattern.sub(replacement, readme, count=1)

    if new_readme != readme:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_readme)
        return True

    return False


def main():
    feed = feedparser.parse(RSS_URL)
    if not getattr(feed, "entries", None):
        raise RuntimeError(f"RSS 获取失败或没有 entries：{RSS_URL}")

    new_block = format_posts(feed.entries)
    changed = update_readme(new_block)

    if changed:
        print("✅ README.md updated.")
    else:
        print("ℹ️ No changes detected. README.md unchanged.")


if __name__ == "__main__":
    main()
