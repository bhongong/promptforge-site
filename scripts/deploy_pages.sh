#!/usr/bin/env bash
# Build the site, verify it, and publish dist/ to the gh-pages branch of origin.
#
# Why not GitHub Actions? Adding .github/workflows/* requires a token with the
# `workflow` scope. Until that is granted, this script is the deploy path; the
# equivalent workflow is kept at deploy/github-pages-workflow.yml.disabled.
#
# Usage:  bash scripts/deploy_pages.sh
set -euo pipefail

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SITE_DIR"

REMOTE="$(git remote get-url origin)"
echo "== remote: $REMOTE"

echo "== build (regenerating content from the knowledge base)"
npm run build:full

echo "== verify SEO invariants"
python scripts/verify_site.py

echo "== publish dist/ -> gh-pages"
rm -rf dist/.git
cd dist
touch .nojekyll   # keep GitHub Pages from running Jekyll over the _astro/ asset dir
git init -q
git checkout -q -b gh-pages
git add -A
git -c user.email="bhongong@gmail.com" -c user.name="Calixto Ong" commit -q \
  -m "Deploy PromptForge site $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push -f "$REMOTE" gh-pages
cd "$SITE_DIR"
rm -rf dist/.git

echo "== deployed: https://bhongong.github.io/promptforge-site/"
