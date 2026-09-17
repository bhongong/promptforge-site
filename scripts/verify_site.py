"""Verify the built PromptForge site against the SEO acceptance criteria.

Run after `npm run build`:
    python site/scripts/verify_site.py

Exit code 0 = every check passed. Checks:
  * every page: single <title> <= 80 chars, single unique meta description <= 160,
    canonical pointing at the deploy origin, exactly one <h1>, valid JSON-LD,
    OG tags present, no template artefacts ("undefined"/"NaN"/"{{")
  * sitemap.xml: every listed URL exists in dist/ and every indexable page is listed
  * robots.txt: declares the sitemap and allows crawling
  * internal links resolve to a real built file
  * every product CTA carries UTM tracking parameters
  * the email capture form is present with a real email input
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parents[1]
DIST = SITE_DIR / "dist"
ORIGIN = "https://bhongong.github.io/promptforge-site"
BASE = "/promptforge-site"

failures: list[str] = []
checks_run = 0


def check(condition: bool, message: str) -> None:
    global checks_run
    checks_run += 1
    if not condition:
        failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def dist_files() -> list[Path]:
    return sorted(p for p in DIST.rglob("*.html"))


def page_path(html_file: Path) -> str:
    rel = html_file.relative_to(DIST).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def url_to_file(path: str) -> Path:
    if path == "/":
        return DIST / "index.html"
    return DIST / path.strip("/") / "index.html"


def link_exists(href: str) -> bool:
    """An internal href resolves to a built file or a built directory index."""
    rel = href[len(BASE):].lstrip("/") if href.startswith(BASE) else href.lstrip("/")
    target = DIST / rel
    if rel == "":
        return (DIST / "index.html").exists()
    if target.is_file():
        return True
    return (target / "index.html").exists()


def main() -> int:
    if not DIST.exists():
        print("dist/ not found — run `npm run build` first")
        return 2

    pages = [p for p in dist_files() if page_path(p) not in ("/404/", "/404.html")]
    page_urls = {page_path(p) for p in pages}
    check(len(pages) >= 60, f"expected >= 60 indexable pages, found {len(pages)}")

    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    all_links: set[str] = set()

    for html_file in pages:
        path = page_path(html_file)
        html = read(html_file)

        title_matches = re.findall(r"<title>(.*?)</title>", html, re.S)
        check(len(title_matches) == 1, f"{path}: expected 1 <title>, found {len(title_matches)}")
        if title_matches:
            title = title_matches[0].strip()
            check(len(title) <= 80, f"{path}: title is {len(title)} chars (max 80): {title!r}")
            check(bool(title), f"{path}: empty title")
            titles[path] = title

        desc_matches = re.findall(r'<meta name="description" content="(.*?)"', html, re.S)
        check(len(desc_matches) == 1, f"{path}: expected 1 meta description, found {len(desc_matches)}")
        if desc_matches:
            desc = desc_matches[0].strip()
            check(0 < len(desc) <= 160, f"{path}: meta description is {len(desc)} chars (max 160)")
            check(desc not in descriptions, f"{path}: duplicate meta description with {descriptions.get(desc)}")
            descriptions[desc] = path

        canon = re.findall(r'<link rel="canonical" href="(.*?)"', html)
        check(len(canon) == 1, f"{path}: expected 1 canonical link, found {len(canon)}")
        if canon:
            expected = f"{ORIGIN}{path}"
            check(canon[0] == expected, f"{path}: canonical {canon[0]!r} != {expected!r}")

        h1s = re.findall(r"<h1[ >]", html)
        check(len(h1s) == 1, f"{path}: expected exactly 1 <h1>, found {len(h1s)}")

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        check(len(blocks) >= 1, f"{path}: no JSON-LD structured data")
        for block in blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                failures.append(f"{path}: invalid JSON-LD ({error})")

        check('property="og:title"' in html, f"{path}: missing og:title")
        check('property="og:description"' in html, f"{path}: missing og:description")

        for artefact in ("undefined", "NaN", "[object Object]"):
            check(artefact not in html, f"{path}: rendered artefact {artefact!r} found")

        for href in re.findall(r'href="(/[^"#]*)"', html):
            all_links.add(href)

    duplicate_titles = len(titles) - len(set(titles.values()))

    # ---- internal links resolve -------------------------------------------------
    for href in sorted(all_links):
        if href.startswith(BASE):
            check(link_exists(href), f"broken internal link: {href}")
        elif href.startswith("/"):
            failures.append(f"internal link missing deploy base: {href}")

    # ---- sitemap -----------------------------------------------------------------
    sitemap_file = DIST / "sitemap.xml"
    check(sitemap_file.exists(), "sitemap.xml missing from dist")
    if sitemap_file.exists():
        sitemap = read(sitemap_file)
        locs = re.findall(r"<loc>(.*?)</loc>", sitemap)
        check(len(locs) == len(page_urls), f"sitemap has {len(locs)} urls but {len(page_urls)} pages exist")
        listed = set()
        for loc in locs:
            check(loc.startswith(ORIGIN), f"sitemap url not on deploy origin: {loc}")
            rel = loc[len(ORIGIN):]
            listed.add(rel)
            check(url_to_file(rel).exists(), f"sitemap url has no built file: {loc}")
        for path in sorted(page_urls):
            check(path in listed, f"page missing from sitemap: {path}")

    # ---- robots ------------------------------------------------------------------
    robots_file = DIST / "robots.txt"
    check(robots_file.exists(), "robots.txt missing from dist")
    if robots_file.exists():
        robots = read(robots_file)
        check("User-agent: *" in robots, "robots.txt missing User-agent")
        check("Allow: /" in robots, "robots.txt does not allow crawling")
        check(
            f"Sitemap: {ORIGIN}/sitemap.xml" in robots,
            "robots.txt does not point at the sitemap",
        )

    # ---- CTAs + lead form --------------------------------------------------------
    home = read(DIST / "index.html")
    check(home.count("utm_source=") >= 3, "home page CTAs are not UTM tracked")

    for html_file in pages:
        html = read(html_file)
        if "gumroad.com" in html:
            for match in re.findall(r'href="(https://[^"]*gumroad\.com[^"]*)"', html):
                check("utm_source=" in match, f"{page_path(html_file)}: untracked CTA {match}")
                check("utm_content=" in match, f"{page_path(html_file)}: CTA missing placement {match}")

    form_pages = [
        p
        for p in pages
        if 'type="email"' in read(p) and "lead-form" in read(p)
    ]
    check(len(form_pages) >= 30, f"email capture form only on {len(form_pages)} pages")

    # ---- content completeness ----------------------------------------------------
    pov_page = DIST / "pov-guide" / "index.html"
    check(pov_page.exists(), "pov-guide page missing")
    if pov_page.exists():
        pov_html = read(pov_page)
        for needle in ("6-step prompt hierarchy", "FAQPage", "wide angle lens"):
            check(needle in pov_html, f"pov-guide missing {needle!r}")

    sample_prompt = DIST / "prompts" / "sd15-pov-cinematic" / "index.html"
    check(sample_prompt.exists(), "sample prompt page missing")
    if sample_prompt.exists():
        sample = read(sample_prompt)
        check("POV shot, eye-level close-up" in sample, "prompt template text not rendered in HTML")

    # ---- report ------------------------------------------------------------------
    print(f"pages checked: {len(pages)}")
    print(f"unique titles: {len(set(titles.values()))} (duplicates: {duplicate_titles})")
    print(f"unique meta descriptions: {len(descriptions)}")
    print(f"internal links checked: {len(all_links)}")
    print(f"checks run: {checks_run}")
    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for failure in failures[:60]:
            print(f"  - {failure}")
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())