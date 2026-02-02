import feedparser
import re
from datetime import datetime

# --- 配置 ---
RSS_URL = "https://czhlove.cn/rss.xml"
README_FILE = "README.md"
MAX_POSTS = 8

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"

TEMPLATE = "* 🚀 [{title}]({link}) - *{date}*"


def format_posts(posts):
    formatted_list = []
    for entry in posts[:MAX_POSTS]:
        # RSS 里有的用 published_parsed，有的用 updated_parsed
        dt = None
        if getattr(entry, "published_parsed", None):
            dt = datetime(*entry.published_parsed[:6])
        elif getattr(entry, "updated_parsed", None):
            dt = datetime(*entry.updated_parsed[:6])

        formatted_date = dt.strftime("%Y年%m月%d日") if dt else "未知日期"

        formatted_list.append(
            TEMPLATE.format(
                title=getattr(entry, "title", "无标题"),
                link=getattr(entry, "link", "#"),
                date=formatted_date,
            )
        )
    return "\n".join(formatted_list)


def update_readme(new_content: str) -> bool:
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError(
            f"README 中未找到标记，请确认包含：\n{START_MARKER}\n{END_MARKER}"
        )

    # 非贪婪匹配，且对 marker 做 escape，避免正则特殊字符问题
    pattern = re.compile(
        re.escape(START_MARKER) + r"[\s\S]*?" + re.escape(END_MARKER)
    )

    replacement = f"{START_MARKER}\n{new_content}\n{END_MARKER}"
    new_readme = pattern.sub(replacement, readme, count=1)

    if new_readme != readme:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_readme)
        return True

    return False


def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        raise RuntimeError("RSS 获取失败或解析不到 entries，请检查 RSS_URL。")

    new_posts = format_posts(feed.entries)
    changed = update_readme(new_posts)

    if changed:
        print("README.md updated.")
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
