# Open Quality documentation site

This is a dependency-free static site for GitHub Pages. The workflow at
`.github/workflows/pages.yml` publishes the `site/` directory whenever it
changes on `main`.

Before the first deployment, set the repository Pages source to **GitHub
Actions** under **Settings → Pages**.

The source documentation remains in `docs/`. This folder is the presentation
layer used by the hosted site.
