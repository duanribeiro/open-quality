# Open Quality documentation site

This is a dependency-free static site for GitHub Pages. The workflow at
`.github/workflows/pages.yml` publishes the `web/` directory whenever it
changes on `main`.

Before the first deployment, set the repository Pages source to **GitHub
Actions** under **Settings → Pages**.

The source documentation remains in `docs/`. This folder is the presentation
layer used by the hosted site.

Run a local preview from the repository root:

```bash
python3 -m http.server 8000 --directory web
```

Open http://localhost:8000. Routes use URL hashes, so the site needs no server
rewrite rules. Content and search metadata live in `app.js`; navigation lives
in `index.html`. Keep CLI examples aligned with `docs/`, `cli/`, and
`schema/v0.1/` when updating the site.
