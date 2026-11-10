# Docs and releases

- User documentation is the Jekyll site in `docs/` (just-the-docs, `color_scheme: mocha`), published by GitHub Pages from `main` `/docs` at https://psyb0t.github.io/ibkr-httpapi/.
- A change to an endpoint, parameter, config key, environment variable, Make target, MCP tool or compose service updates the matching docs page in the same change: `api.md`, `configuration.md`, `mcp.md`, `deployment.md`, `development.md`, and the skill under `.agents/skills/ibkr-httpapi/` when the client-facing behaviour moved.
- Links from `docs/` or the README to repository files are full `https://github.com/psyb0t/ibkr-httpapi/blob/main/...` URLs (or `tree/main/...` for a directory).
- Build the site before you hand it off: `make docs` runs GitHub's own Pages build image and writes into the gitignored `DOCS_SITE` directory named in the Makefile. Check every internal link and anchor in the output.
- Wrap any docs code block that contains `{{` or `{%` in `{% raw %}` / `{% endraw %}` kept inside HTML comments, or Jekyll eats it.
- `CHANGELOG.md` has one `## vX.Y.Z, YYYY-MM-DD` section per release. Releases are annotated `v*` tags; CI cuts the GitHub release from the tag message. Bump the version in `.agents/.codex-plugin/plugin.json` with each release.
- The skill under `.agents/skills/ibkr-httpapi/` and the OpenClaw bridge under `.agents/plugins/ibkr-httpapi/` are published to ClawHub by CI on every tag. Keep their tool lists and safety wording in step with `ibkrapi/mcp_server.py`.
