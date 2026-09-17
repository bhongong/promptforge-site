"""Print Lighthouse category scores and any failing SEO audits from JSON reports.

Usage:
    python site/scripts/lighthouse_report.py report1.json report2.json ...
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CATEGORIES = ("performance", "accessibility", "best-practices", "seo")


def main(paths: list[str]) -> int:
    exit_code = 0
    for path in paths:
        report = json.loads(Path(path).read_text(encoding="utf-8"))
        url = report.get("finalUrl") or report.get("requestedUrl")
        print(f"\n== {url}")
        for category in CATEGORIES:
            data = report["categories"].get(category)
            if not data:
                continue
            score = round((data["score"] or 0) * 100)
            flag = "  <-- FAIL" if category == "seo" and score < 90 else ""
            print(f"   {category:<16} {score}{flag}")
            if category == "seo" and score < 90:
                exit_code = 1
        print("   -- non-perfect audits --")
        for category in CATEGORIES:
            if category == "performance":
                continue
            for ref in report["categories"][category]["auditRefs"]:
                audit = report["audits"][ref["id"]]
                mode = audit.get("scoreDisplayMode")
                if audit.get("score") is not None and audit["score"] < 1 and mode in ("binary", "numeric"):
                    print(f"   [{category}] {ref['id']}: {audit.get('title')}")
                    if category == "seo":
                        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))