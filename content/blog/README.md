# Writing blog posts

Add one Markdown file per article in this directory. The Pages workflow builds
each post as a standalone HTML page, so crawlers can read its title, article
body, canonical URL, and structured metadata without running the documentation
app.

Use this front matter at the top of each file:

```yaml
---
title: "A clear, descriptive article title"
description: "A short summary for search and social previews."
date: 2026-11-24
author: "Open Quality"
slug: "lowercase-kebab-case"
category: "Quality as Code"
tags:
  - quality as code
  - software quality
---
```

Write the article below the closing `---`. Supported Markdown includes headings,
paragraphs, bullet and numbered lists, blockquotes, fenced code, links, inline
code, bold, and emphasis. Use one H1-equivalent title in the front matter; the
generator creates the page's H1 from it. Article slugs must be unique. Set
`category` to one clear topic; the blog index uses it to build the topic filters.

After editing or adding a post, regenerate the static pages from the repository
root:

```bash
python3 scripts/build_blog.py
```

The generated HTML, sitemap, and RSS feed are written under `web/`. The Pages
workflow runs the same generator on every deployment.
