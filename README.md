# PromptForge site

Static SEO prompt-library site for the PromptForge product line. Built with **Astro**
(static output), generated from the `prompt-engineer` knowledge base so the free pages and
the paid packs can never drift apart.

- **Live:** https://bhongong.github.io/promptforge-site/
- **Productization brief (source of truth):** `../docs/PRODUCTIZATION-PLAN.md`
- **Launch switches:** [`CONFIG.md`](CONFIG.md)

## What it builds

71 indexable pages, all pre-rendered HTML (no client-side rendering for crawlers):

| Route | Count | Notes |
|---|---|---|
| `/` | 1 | hero, featured prompts, category grid, lead capture |
| `/prompts/` + `/prompts/<slug>/` | 1 + 32 | canonical page per prompt, full template text, placeholder table, related prompts, per-prompt CTA |
| `/categories/` + `/categories/<slug>/` | 1 + 14 | category landing pages with internal links |
| `/formulas/` + `/formulas/<slug>/` | 1 + 16 | prompting formulas with skeletons |
| `/pov-guide/` | 1 | flagship SD1.5 POV long-form page (dictionary, hierarchy, negatives, LoRA, FAQ) |
| `/free-starter-kit/` | 1 | lead magnet page + email capture |
| `/products/` | 1 | SKU map with tracked CTAs |
| `/about/`, `/license/`, `/404.html` | 3 | |
| `/sitemap.xml`, `/robots.txt` | 2 | generated endpoints |

## Architecture

```
scripts/export_content.py   knowledge_base/*.py  ->  src/data/content.json   (content layer)
src/config.ts               branding + SKU map + tracked CTA URLs
src/lib/routes.ts           base-aware URL helper, canonical builder, page inventory
src/lib/schema.ts           JSON-LD builders (WebSite, Organization, Article, ItemList,
                            BreadcrumbList, Product, FAQPage)
src/layouts/Base.astro      <head> SEO block: title, description, canonical, OG, JSON-LD
src/components/             PromptCard, CtaBlock (UTM tracking), LeadForm (email capture)
src/pages/                  one file per page family; [slug].astro = getStaticPaths
```

`src/data/content.json` is **committed on purpose**: CI builds the site without access to the
private knowledge base that lives beside the repo. Regenerate it with `npm run content`
whenever the knowledge base changes, then commit the diff.

## Commands

```bash
npm ci                # install
npm run content       # knowledge base -> src/data/content.json
npm run build:full    # content + build (regenerates + builds)
npm run build         # build only (CI path)
npm run check         # astro type check (0 errors expected)
npm run verify        # 1,800+ SEO invariant checks over dist/
npm run serve         # preview at http://127.0.0.1:4321/promptforge-site/
```

## SEO invariants enforced by `scripts/verify_site.py`

- one `<title>` per page, every title **< 80 characters**, no duplicate titles
- one unique `<meta name="description">` per page, each **<= 160 characters**
- `<link rel="canonical">` on every page, pointing at the deploy origin + exact path
- exactly one `<h1>` per page
- valid JSON-LD structured data on every page (Article / ItemList / Product / FAQPage / BreadcrumbList / WebSite)
- OG + Twitter card tags on every page
- `sitemap.xml` lists every indexable page and nothing that is not built; `robots.txt` declares the sitemap
- every internal link resolves to a built file (no 404s from the crawl surface)
- every product CTA carries `utm_source` + `utm_content` (placement-level attribution)
- the email capture form is present with a real `type="email"` input
- no rendered template artefacts (`undefined`, `NaN`, `[object Object]`)

CI runs the same script on every push, so a regression fails the deploy.

## Lighthouse (local `astro preview`, Chrome headless)

| Page | Performance | Accessibility | Best practices | SEO |
|---|---|---|---|---|
| `/` | 100 | 96 | 96 | **100** |
| `/prompts/sd15-pov-cinematic/` | 100 | 93 | 96 | **100** |
| `/pov-guide/` | 100 | 93 | 96 | **100** |
| `/categories/image-sd15/` | 100 | 95 | 96 | **100** |

Reproduce:

```bash
npm run serve                                             # in one shell
export CHROME_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe"
npx lighthouse http://127.0.0.1:4321/promptforge-site/ \
  --only-categories=seo,performance,accessibility,best-practices \
  --output=json --output-path=/tmp/lh.json \
  --chrome-flags="--headless=new --no-sandbox"
python scripts/lighthouse_report.py /tmp/lh.json
```

## Deploy

```bash
bash scripts/deploy_pages.sh
```

That script: regenerates `content.json` from the knowledge base → builds → runs the SEO
verifier → publishes `dist/` to the **`gh-pages`** branch (force push) → writes
`.nojekyll` so GitHub Pages does not run Jekyll over the `_astro/` asset directory.

GitHub Pages for this repo is configured as **deploy from branch: `gh-pages` / (root)**,
so the site is served at <https://bhongong.github.io/promptforge-site/>.

An equivalent GitHub Actions pipeline is kept at
`deploy/github-pages-workflow.yml.disabled`. Rename it back to
`.github/workflows/deploy.yml` to move to CI-based deploys — this requires the GitHub CLI
token to carry the `workflow` scope, and Pages must be switched to **build_type: workflow**.

## Content rules

- SFW only. Nothing NSFW-flagged from `imagegen.py` may reach this site or any paid pack.
- Model/LoRA names stay **tool-agnostic** (A1111 / ComfyUI / SD.Next) — never mention a local
  checkpoint key.
- No secrets, tokens, API keys or the internal SQLite DB in this repo.
