#!/usr/bin/env python3
"""Index the screenshot set produced by the Playwright run.

Scans ``tests/screenshots/<project>/*.png`` and writes:

  * ``tests/screenshots/manifest.json`` — machine-readable index (project, flow,
    bytes, sha256, captured_at) used by the QA gate to prove the set is complete.
  * ``tests/screenshots/INDEX.md`` — human-readable checklist for the `frontend`
    role to review each flow.

Usage:  python tests/build_screenshot_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "screenshots"

# flow id -> what the reviewer must look at
EXPECTED_FLOWS = {
    "01-home": "Hero, featured prompts, category grid, lead form render correctly.",
    "02-prompts-index": "Prompt catalogue lists every template with category links.",
    "03-prompt-detail": "Template text, placeholder table, related prompts and CTA all present.",
    "04-categories-index": "All 14 categories listed and internally linked.",
    "05-category-detail": "Category landing page cross-links its prompts.",
    "06-formulas-index": "All 16 formulas listed with skeletons.",
    "07-formula-detail": "Formula skeleton + 'when to use' sections readable.",
    "08-pov-guide": "Long-form POV guide: dictionary, hierarchy, negatives, FAQ.",
    "09-free-starter-kit": "Lead-magnet page: form fields + value bullets visible.",
    "10-products": "SKU map with prices, badges and tracked CTAs.",
    "11-about": "Brand story page renders without layout breaks.",
    "12-license": "Licence terms legible, no placeholder lorem.",
    "13-404": "404 page is on-brand and offers a way back.",
    "14-lead-form-states": "Form validation + confirmation status is visible.",
    "15-products-ctas": "Every CTA shows its price and points at a storefront.",
    "16-nav-home-to-prompt": "Home -> prompt navigation lands on a prompt page.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    if not SHOTS.exists():
        print(f"no screenshots at {SHOTS} — run `npm run test:e2e` first", file=sys.stderr)
        return 1

    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entries = []
    for png in sorted(SHOTS.rglob("*.png")):
        project = png.parent.name
        flow = png.stem
        entries.append(
            {
                "project": project,
                "flow": flow,
                "file": png.relative_to(ROOT.parent).as_posix(),
                "bytes": png.stat().st_size,
                "sha256": sha256(png),
            }
        )

    projects = sorted({e["project"] for e in entries})
    found = {(e["project"], e["flow"]) for e in entries}
    missing = sorted(
        f"{p}/{f}" for p in projects for f in EXPECTED_FLOWS if (p, f) not in found
    )

    manifest = {
        "captured_at": captured_at,
        "projects": projects,
        "screenshot_count": len(entries),
        "expected_flows": sorted(EXPECTED_FLOWS),
        "missing": missing,
        "screenshots": entries,
    }
    out = SHOTS / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# PromptForge screenshot review sheet (QA gate)",
        "",
        f"Captured: {captured_at}  ·  projects: {', '.join(projects)}  ·  "
        f"files: {len(entries)}  ·  missing: {len(missing)}",
        "",
        "| Flow | What to check | Files |",
        "| --- | --- | --- |",
    ]
    for flow, note in EXPECTED_FLOWS.items():
        files = [e["file"] for e in entries if e["flow"] == flow]
        lines.append(f"| `{flow}` | {note} | {', '.join(files) if files else '**MISSING**'} |")
    lines += ["", "Verdict is recorded as a kanban review on the ENG test-suite card.", ""]
    (SHOTS / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {out} ({len(entries)} screenshots, {len(missing)} missing)")
    for miss in missing:
        print(f"  MISSING {miss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
