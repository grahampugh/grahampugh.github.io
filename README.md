This is the repository for Graham Pugh's [What The Mac?!](http://grahampugh.github.io) blog.

## Post header and tags

Each blog post should start with YAML front matter. Include a `tags:` list to allow filtering and tag-specific RSS feeds.

Example:

```yaml
---
layout: post
title: "My blog post title"
comments: true
tags:
  - apple
  - mac
  - jamf
  - api
---
```

The `tags:` list is used for:

- displaying tag links on the site
- building tag pages
- generating tag-specific RSS feed URLs

Example URLs:

- Full blog feed: `https://grahamrpugh.com/feed.xml`
- Tag page example: `https://grahamrpugh.com/tags/apple/`
- Tag feed example: `https://grahamrpugh.com/tags/apple/feed.xml`

## Generating tag pages and RSS feeds

The site uses a small Python script to generate static tag pages and feed files from the post front matter. This keeps the setup GitHub Pages-friendly and does not require a custom Jekyll plugin.

From the repo root, run:

```bash
cd /Users/gpugh/sourcecode/grahampugh.github.io
python3 scripts/generate_tag_feeds.py
```

The script:

- scans all files in `_posts/`
- reads each post's `tags:` list
- creates `tags/<tag>/index.html` for each tag
- creates `tags/<tag>/feed.xml` for each tag
- writes the generated output into the `tags/` directory

If you want to regenerate everything after adding or changing tags:

```bash
python3 scripts/generate_tag_feeds.py
git add tags
git commit -m "Update generated tag pages and feeds"
git push
```

This is the recommended workflow for static tag feeds on GitHub Pages.
