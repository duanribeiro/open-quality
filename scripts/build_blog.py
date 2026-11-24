"""Build crawlable static blog pages from Markdown sources."""

from __future__ import annotations

import html
import json
import math
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content" / "blog"
WEB_DIR = ROOT / "web"
BLOG_DIR = WEB_DIR / "blog"
SITE_URL = "https://duanribeiro.github.io/open-quality"
SITE_TITLE = "Open Quality"
BLOG_TITLE = "Open Quality Blog"
BLOG_DESCRIPTION = (
    "Practical articles on quality as code, software quality requirements, "
    "ISO SQuaRE, and the Open Quality CLI."
)
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INLINE_PATTERN = re.compile(
    r"(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*.+?\*\*|(?<!\*)\*[^*]+\*)"
)


@dataclass(frozen=True)
class Post:
    title: str
    description: str
    published: date
    author: str
    slug: str
    category: str
    tags: list[str]
    source: Path
    body: str

    @property
    def url(self) -> str:
        return f"{SITE_URL}/blog/{self.slug}/"

    @property
    def reading_minutes(self) -> int:
        words = re.findall(r"\b[\w'-]+\b", self.body)
        return max(1, math.ceil(len(words) / 200))


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid quoted front matter value: {value}") from error
        if not isinstance(parsed, str):
            raise ValueError(f"front matter values must be strings: {value}")
        return parsed
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def parse_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: article must start with YAML front matter")

    metadata: dict[str, Any] = {}
    active_list: str | None = None
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing is None:
        raise ValueError(f"{path}: YAML front matter is missing its closing ---")

    for line in lines[1:closing]:
        if not line.strip():
            continue
        if line.lstrip().startswith("-") and active_list:
            metadata[active_list].append(parse_scalar(line.lstrip()[1:]))
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid front matter line: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValueError(f"{path}: front matter keys cannot be empty")
        if raw_value:
            metadata[key] = parse_scalar(raw_value)
            active_list = None
        else:
            metadata[key] = []
            active_list = key

    required = ("title", "description", "date", "author", "slug", "category", "tags")
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ValueError(f"{path}: missing front matter fields: {', '.join(missing)}")
    if not isinstance(metadata["tags"], list) or not all(
        isinstance(tag, str) and tag.strip() for tag in metadata["tags"]
    ):
        raise ValueError(f"{path}: tags must be a non-empty YAML list")
    slug = str(metadata["slug"])
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"{path}: slug must use lowercase kebab-case: {slug}")
    category = str(metadata["category"]).strip()
    if not category:
        raise ValueError(f"{path}: category cannot be empty")
    try:
        published = date.fromisoformat(str(metadata["date"]))
    except ValueError as error:
        raise ValueError(f"{path}: date must use YYYY-MM-DD format") from error

    body = "\n".join(lines[closing + 1 :]).strip()
    if not body:
        raise ValueError(f"{path}: article body cannot be empty")
    return Post(
        title=str(metadata["title"]),
        description=str(metadata["description"]),
        published=published,
        author=str(metadata["author"]),
        slug=slug,
        category=category,
        tags=list(metadata["tags"]),
        source=path,
        body=body,
    )


def inline_markdown(text: str) -> str:
    output: list[str] = []
    cursor = 0
    for match in INLINE_PATTERN.finditer(text):
        output.append(html.escape(text[cursor : match.start()]))
        token = match.group(0)
        if token.startswith("`"):
            output.append(f"<code>{html.escape(token[1:-1])}</code>")
        elif token.startswith("["):
            link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token)
            if not link:
                output.append(html.escape(token))
            else:
                label, url = link.groups()
                if not url.startswith(("https://", "http://", "#")):
                    output.append(html.escape(label))
                else:
                    output.append(
                        f'<a href="{html.escape(url, quote=True)}">'
                        f"{html.escape(label)}</a>"
                    )
        elif token.startswith("**"):
            output.append(f"<strong>{html.escape(token[2:-2])}</strong>")
        else:
            output.append(f"<em>{html.escape(token[1:-1])}</em>")
        cursor = match.end()
    output.append(html.escape(text[cursor:]))
    return "".join(output)


def heading_id(text: str) -> str:
    plain = re.sub(r"[`*_]", "", text).lower()
    plain = re.sub(r"[^a-z0-9]+", "-", plain).strip("-")
    return plain or "section"


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    result: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = ""
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            result.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items:
            items = "".join(f"<li>{inline_markdown(item)}</li>" for item in list_items)
            result.append(f"<{list_tag}>{items}</{list_tag}>")
            list_items.clear()
            list_tag = ""

    def flush_code() -> None:
        nonlocal in_code
        if in_code:
            rendered = html.escape("\n".join(code_lines))
            result.append(f"<pre><code>{rendered}</code></pre>")
            code_lines.clear()
            in_code = False

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                flush_code()
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        heading = re.match(r"^(#{2,4})\s+(.+?)\s*#*$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            title = heading.group(2)
            result.append(
                f'<h{level} id="{heading_id(title)}">'
                f"{inline_markdown(title)}</h{level}>"
            )
            continue
        if re.fullmatch(r"(?:---|\*\*\*)", line.strip()):
            flush_paragraph()
            flush_list()
            result.append("<hr>")
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or numbered:
            flush_paragraph()
            wanted_tag = "ul" if bullet else "ol"
            if list_tag and list_tag != wanted_tag:
                flush_list()
            list_tag = wanted_tag
            list_items.append((bullet or numbered).group(1))
            continue
        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            flush_list()
            result.append(f"<blockquote><p>{inline_markdown(quote.group(1))}</p></blockquote>")
            continue
        flush_list()
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    if in_code:
        flush_code()
    return "\n".join(result)


def document_template(
    *,
    title: str,
    description: str,
    canonical: str,
    root_prefix: str,
    blog_prefix: str,
    content: str,
    structured_data: dict[str, Any],
    author: str = "",
    og_type: str = "article",
    extra_scripts: str = "",
) -> str:
    json_ld = json.dumps(structured_data, ensure_ascii=False).replace("</", "<\\/")
    script_markup = f"  {extra_scripts}" if extra_scripts else ""
    author_meta = (
        f'<meta name="author" content="{html.escape(author, quote=True)}">'
        if author
        else ""
    )
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  {author_meta}
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
  <meta property="og:type" content="{html.escape(og_type, quote=True)}">
  <meta property="og:site_name" content="{SITE_TITLE}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:url" content="{html.escape(canonical, quote=True)}">
  <meta name="twitter:card" content="summary">
  <link rel="stylesheet" href="{root_prefix}styles.css">
  <link rel="stylesheet" href="{root_prefix}blog.css">
  <link rel="alternate" type="application/rss+xml" title="{BLOG_TITLE}" href="{blog_prefix}feed.xml">
  <script type="application/ld+json">{json_ld}</script>
{script_markup}
</head>
<body class="blog-body">
  <header class="blog-header">
    <a class="blog-brand" href="{root_prefix}" aria-label="Open Quality home">
      <span class="blog-brand-mark" aria-hidden="true">OQ</span>
      <span>Open Quality</span>
    </a>
    <nav aria-label="Main navigation">
      <a class="blog-nav-active" href="{blog_prefix}">Blog</a>
      <a href="{root_prefix}#/quick-start">Docs</a>
      <a href="https://github.com/duanribeiro/open-quality" rel="noopener noreferrer">GitHub</a>
    </nav>
  </header>
  {content}
  <footer class="blog-footer">
    <a href="{root_prefix}">Open Quality</a>
    <span>Quality as Code for software teams</span>
    <a href="{blog_prefix}feed.xml">RSS feed</a>
  </footer>
</body>
</html>
'''


def post_json_ld(post: Post) -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.description,
        "datePublished": post.published.isoformat(),
        "dateModified": post.published.isoformat(),
        "author": {"@type": "Organization", "name": post.author},
        "publisher": {
            "@type": "Organization",
            "name": SITE_TITLE,
            "url": SITE_URL,
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": post.url},
        "keywords": post.tags,
    }


def category_id(category: str) -> str:
    return heading_id(category)


def render_post_card(post: Post) -> str:
    category = html.escape(category_id(post.category), quote=True)
    return f'''<article class="blog-card" data-category="{category}">
  <p class="blog-card-meta"><span class="blog-category">{html.escape(post.category)}</span><span aria-hidden="true">·</span><time datetime="{post.published.isoformat()}">{post.published.strftime("%B %-d, %Y")}</time><span aria-hidden="true">·</span><span>{post.reading_minutes} min read</span></p>
  <h2><a href="{html.escape(post.slug, quote=True)}/">{html.escape(post.title)}</a></h2>
  <p>{html.escape(post.description)}</p>
  <a class="blog-read-more" href="{html.escape(post.slug, quote=True)}/">Read article <span aria-hidden="true">↗</span></a>
</article>'''


def render_blog_index(posts: list[Post]) -> str:
    canonical = f"{SITE_URL}/blog/"
    cards = "\n".join(render_post_card(post) for post in posts)
    categories = list(dict.fromkeys(post.category for post in posts))
    filters = "".join(
        f'<button type="button" data-filter="{html.escape(category_id(category), quote=True)}" aria-pressed="false">{html.escape(category)}</button>'
        for category in categories
    )
    content = f'''<main class="blog-main">
  <section class="blog-hero">
    <p class="blog-eyebrow"><span aria-hidden="true"></span>Open Quality · Blog</p>
    <h1>Clear thinking for better software quality.</h1>
    <p>Guides and ideas for turning quality expectations into requirements teams can review, measure, and improve.</p>
  </section>
  <nav class="blog-filters" aria-label="Filter articles by topic">
    <button type="button" data-filter="all" aria-pressed="true">All articles</button>{filters}
  </nav>
  <section class="blog-posts" aria-labelledby="latest-articles">
    <div class="blog-section-heading">
      <div><p class="blog-eyebrow">Ideas, guides, and references</p><h2 id="latest-articles">Latest articles</h2></div>
      <a href="feed.xml">Subscribe via RSS</a>
    </div>
    <p class="blog-filter-status" aria-live="polite">Showing {len(posts)} {"article" if len(posts) == 1 else "articles"}</p>
    <div class="blog-grid">{cards}</div>
    <p class="blog-empty-state" hidden>No articles in this topic yet.</p>
  </section>
  <section class="blog-about">
    <div><p class="blog-eyebrow">About Open Quality</p><h2>Make quality expectations part of the repository.</h2></div>
    <p>Open Quality is an open-source contract format and CLI for describing software quality requirements, workflows, measures, and evidence as version-controlled resources.</p>
    <a href="https://github.com/duanribeiro/open-quality" rel="noopener noreferrer">Explore the GitHub repository</a>
  </section>
</main>'''
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": BLOG_TITLE,
        "description": BLOG_DESCRIPTION,
        "url": canonical,
        "publisher": {"@type": "Organization", "name": SITE_TITLE, "url": SITE_URL},
    }
    return document_template(
        title=f"{BLOG_TITLE} | Software Quality as Code",
        description=BLOG_DESCRIPTION,
        canonical=canonical,
        root_prefix="../",
        blog_prefix="./",
        content=content,
        structured_data=structured_data,
        og_type="website",
        extra_scripts='<script src="../blog-filter.js" defer></script>',
    )


def render_post_page(post: Post) -> str:
    canonical = post.url
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in post.tags)
    article_body = markdown_to_html(post.body)
    content = f'''<main class="blog-main blog-article-main">
  <nav class="blog-breadcrumbs" aria-label="Breadcrumb"><a href="../">Blog</a><span>/</span><span>{html.escape(post.title)}</span></nav>
  <article class="blog-article">
    <header class="blog-article-header">
      <p class="blog-article-category">{html.escape(post.category)}</p>
      <div class="blog-card-tags">{tags}</div>
      <h1>{html.escape(post.title)}</h1>
      <p class="blog-article-description">{html.escape(post.description)}</p>
      <p class="blog-article-byline">By {html.escape(post.author)} · <time datetime="{post.published.isoformat()}">{post.published.strftime("%B %-d, %Y")}</time> · {post.reading_minutes} min read</p>
    </header>
    <div class="blog-article-body">{article_body}</div>
    <footer class="blog-article-footer">
      <p>Open Quality is an open-source quality contract format and CLI.</p>
      <a href="https://github.com/duanribeiro/open-quality" rel="noopener noreferrer">Explore the project on GitHub</a>
    </footer>
  </article>
</main>'''
    return document_template(
        title=f"{post.title} | {SITE_TITLE}",
        description=post.description,
        canonical=canonical,
        root_prefix="../../",
        blog_prefix="../",
        content=content,
        structured_data=post_json_ld(post),
        author=post.author,
    )


def render_feed(posts: list[Post]) -> str:
    items = []
    for post in posts:
        pub_date = datetime.combine(post.published, datetime.min.time(), timezone.utc)
        items.append(
            "<item>"
            f"<title>{html.escape(post.title)}</title>"
            f"<link>{html.escape(post.url)}</link>"
            f"<guid isPermaLink=\"true\">{html.escape(post.url)}</guid>"
            f"<description>{html.escape(post.description)}</description>"
            f"<pubDate>{format_datetime(pub_date, usegmt=True)}</pubDate>"
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{BLOG_TITLE}</title>"
        f"<link>{SITE_URL}/blog/</link>"
        f"<description>{html.escape(BLOG_DESCRIPTION)}</description>"
        f"<language>en-us</language>{''.join(items)}"
        "</channel></rss>\n"
    )


def render_sitemap(posts: list[Post]) -> str:
    latest = max(post.published for post in posts).isoformat()
    locations = [
        (f"{SITE_URL}/", None),
        (f"{SITE_URL}/blog/", latest),
        *((post.url, post.published.isoformat()) for post in posts),
    ]
    entries = "".join(
        f"<url><loc>{html.escape(url)}</loc>"
        f"{f'<lastmod>{lastmod}</lastmod>' if lastmod else ''}</url>"
        for url, lastmod in locations
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}</urlset>\n"
    )


def load_posts() -> list[Post]:
    paths = sorted(path for path in POSTS_DIR.glob("*.md") if path.name != "README.md")
    if not paths:
        raise SystemExit(f"No Markdown articles found in {POSTS_DIR}")
    posts = [parse_post(path) for path in paths]
    slugs = [post.slug for post in posts]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("Blog article slugs must be unique")
    return sorted(posts, key=lambda post: (post.published, post.title), reverse=True)


def main() -> None:
    posts = load_posts()
    if BLOG_DIR.exists():
        shutil.rmtree(BLOG_DIR)
    BLOG_DIR.mkdir(parents=True)
    (BLOG_DIR / "index.html").write_text(render_blog_index(posts), encoding="utf-8")
    for post in posts:
        output = BLOG_DIR / post.slug / "index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_post_page(post), encoding="utf-8")
    (BLOG_DIR / "feed.xml").write_text(render_feed(posts), encoding="utf-8")
    (WEB_DIR / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")
    print(f"Generated blog index and {len(posts)} article pages in {BLOG_DIR}")


if __name__ == "__main__":
    main()
