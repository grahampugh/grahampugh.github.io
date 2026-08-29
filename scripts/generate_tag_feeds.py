#!/usr/bin/env python3

import re
from pathlib import Path

SITE_URL = "https://grahamrpugh.com"
POSTS_DIR = Path("_posts")
OUT_DIR = Path("tags")


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-")


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def read_front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}

    front = text[4:end]
    values = {}
    current_key = None

    for raw_line in front.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if raw_line.startswith("  - ") and current_key == "tags":
            item = stripped[2:].strip().strip("'\"")
            if item:
                values.setdefault("tags", []).append(item)
            continue

        if ":" in stripped and not raw_line.startswith("  "):
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "tags":
                current_key = "tags"
                items = []
                if value.startswith("[") and value.endswith("]"):
                    value = value[1:-1]
                if value:
                    for part in value.split(","):
                        part = part.strip().strip("'\"")
                        if part:
                            items.append(part)
                    values["tags"] = items
                else:
                    values["tags"] = []
            else:
                current_key = None
                if value:
                    values[key] = value.strip("'\"")
                else:
                    values[key] = ""
        elif current_key == "tags" and raw_line.startswith("  - "):
            item = stripped[2:].strip().strip("'\"")
            if item:
                values.setdefault("tags", []).append(item)

    return values


def get_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")) + sorted(POSTS_DIR.glob("*.markdown")):
        front = read_front_matter(path)
        if "tags" in front and front["tags"]:
            posts.append((path, front))
    return posts


def write_tag_index(tag_map):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for tag in sorted(tag_map):
        slug = slugify(tag)
        lines.append(
            '  <li><a href="' + SITE_URL + '/tags/' + slug + '/">#' + escape_xml(tag) + "</a></li>"
        )

    content = """---
layout: page
title: Tags
permalink: /tags/
nav_exclude: true
sitemap: false
---

<h2>Tags</h2>

<ul>
""" + "\n".join(lines) + """
</ul>
"""

    (OUT_DIR / "index.html").write_text(content, encoding="utf-8")


def write_tag_page(tag, tag_posts):
    slug = slugify(tag)
    tag_dir = OUT_DIR / slug
    tag_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for path, front in tag_posts:
        title = front.get("title", path.stem)
        post_url = SITE_URL + "/" + path.stem
        items.append('  <li><a href="' + escape_xml(post_url) + '">' + escape_xml(title) + "</a></li>")

    content = (
        "---\n"
        "layout: page\n"
        'title: "Tag: ' + escape_xml(tag) + '"\n'
        "permalink: /tags/" + slug + "/\n"
        "nav_exclude: true\n"
        "sitemap: false\n"
        "---\n\n"
        "<h2># " + escape_xml(tag) + "</h2>\n\n"
        "<ul>\n"
        + "\n".join(items)
        + "\n</ul>\n"
    )

    (tag_dir / "index.html").write_text(content, encoding="utf-8")


def write_tag_feed(tag, tag_posts):
    slug = slugify(tag)
    tag_dir = OUT_DIR / slug
    tag_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for path, front in tag_posts:
        title = front.get("title", path.stem)
        summary = front.get("summary")
        description = summary if summary else title
        post_url = SITE_URL + "/" + path.stem
        pub_date = front.get("date", "2020-01-01")
        items.append(
            "    <item>\n"
            + "      <title>" + escape_xml(title) + "</title>\n"
            + "      <link>" + escape_xml(post_url) + "</link>\n"
            + "      <guid>" + escape_xml(post_url) + "</guid>\n"
            + "      <pubDate>" + escape_xml(pub_date) + "</pubDate>\n"
            + "      <description>" + escape_xml(description) + "</description>\n"
            + "    </item>"
        )

    feed = (
        "---\n"
        "layout: null\n"
        "permalink: /tags/" + slug + "/feed.xml\n"
        "---\n"
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<rss version=\"2.0\">\n"
        "  <channel>\n"
        "    <title>" + escape_xml(tag) + " | " + SITE_URL + "</title>\n"
        "    <link>" + SITE_URL + "/tags/" + slug + "/</link>\n"
        "    <description>Posts tagged with " + escape_xml(tag) + "</description>\n"
        + "\n".join(items)
        + "\n  </channel>\n"
        "</rss>\n"
    )

    (tag_dir / "feed.xml").write_text(feed, encoding="utf-8")


def main():
    posts = get_posts()
    tag_map = {}

    for path, front in posts:
        for tag in front["tags"]:
            tag_map.setdefault(tag, []).append((path, front))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_tag_index(tag_map)

    for tag, tag_posts in sorted(tag_map.items()):
        ordered_posts = sorted(tag_posts, key=lambda item: item[1].get("date", ""))
        write_tag_page(tag, ordered_posts)
        write_tag_feed(tag, ordered_posts)


if __name__ == "__main__":
    main()