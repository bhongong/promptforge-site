# Configuration & launch switches

Everything a human needs to flip the site from "placeholder" to "live". Code lives in
[`src/config.ts`](src/config.ts); this file is the checklist.

## 1. Where things are

| What | Value |
|---|---|
| Deploy origin | `https://bhongong.github.io/promptforge-site` |
| Astro `site` / `base` | `astro.config.mjs` (`site: https://bhongong.github.io`, `base: /promptforge-site`) |
| Canonical root used by every page | `SITE.baseUrl` in `src/config.ts` |
| Content source of truth | `../knowledge_base/*.py` via `scripts/export_content.py` → `src/data/content.json` |

All three must agree. If you move to a custom domain, change **all** of them, then
`npm run build:full`.

## 2. Gumroad / Notion CTA URLs (currently TRACKED PLACEHOLDERS)

Every paid CTA points at `https://promptforge.gumroad.com/l/<slug>` and every link already
carries `utm_source=site`, `utm_medium=cta`, `utm_campaign=<sku>` plus a per-placement
`utm_content` added by `track()`.

| SKU | Placeholder slug | Price | Real URL goes here |
|---|---|---|---|
| SKU-LM | `/l/starter-kit` | Free | `SITE.leadMagnetUrl` |
| P1 | `/l/promptforge-library` | $12 | `SKUS.P1.url` |
| P2 | `/l/promptforge-masterclass` | $19 | `SKUS.P2.url` |
| P3 | `/l/ai-system-builder` | $24 | `SKUS.P3.url` |
| N1 | `/l/promptforge-notion-system` | $19 | `SKUS.N1.url` |
| B1 | `/l/promptforge-image-studio` | $39 (early $29) | `SKUS.B1.url` |

**To go live:** create the Gumroad products with those exact permalinks, then set
`SITE.PLACEHOLDERS_LIVE = true` in `src/config.ts`. That value only controls the "still a
placeholder" notices; the URLs themselves then already resolve. If the real permalinks
differ, edit `gumroad()` call sites in `src/config.ts` — nothing else references them.

## 3. Email capture (SKU-LM delivery)

`SITE.leadEndpoint` is empty, which puts the form in **preview mode**: it validates input,
shows the subscriber what would happen, sends **nothing**, and stores **nothing**. There is
no silent black hole.

To make capture real, set `leadEndpoint` to a form endpoint that accepts a JSON POST
(Buttondown, Kit/ConvertKit, Formspree, or your own endpoint). The form posts this payload:

```json
{ "email": "...", "first_name": "...", "utm_source": "site", "utm_medium": "lead-magnet",
  "utm_campaign": "free-starter-kit", "utm_content": "<page placement>", "sku": "LM" }
```

A hidden honeypot field (`company`) is checked client-side and dropped if filled.

Decide once where SKU-LM is delivered (Gumroad free product vs. the email tool) and set
`SITE.leadMagnetUrl` to match — it is the destination the confirmation copy promises.

## 4. Analytics

No analytics script is bundled (keeps Lighthouse performance at 100 and avoids cookie
consent). To add privacy-friendly analytics, drop the Umami/Plausible snippet into
`src/layouts/Base.astro` just before `</head>`.

## 5. Domain + hosting

Currently GitHub Pages (project site, path-based URL). For `promptforge.com`:

1. Register the domain and point it at GitHub Pages (or move to Cloudflare Pages / Netlify).
2. Set `base: '/'` in `astro.config.mjs`, update `site` and `SITE.baseUrl`.
3. `npm run build:full && npm run verify`, then redeploy.
4. Re-submit `sitemap.xml` in Google Search Console under the new origin.

## 6. Commands

```bash
npm run content     # regenerate src/data/content.json from the knowledge base
npm run build:full  # content + build (use locally)
npm run build       # build only (what CI runs — content.json is committed)
npm run check       # astro type check
npm run verify      # SEO invariants over dist/ (titles, meta, canonical, sitemap, CTAs)
npm run serve       # local preview at http://127.0.0.1:4321/promptforge-site/
```
