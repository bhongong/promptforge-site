"""Export the PromptForge knowledge base into the site's content layer.

Single source of truth = H:\\03-services-and-infra\\prompt-engineer\\knowledge_base.
Running this script regenerates site/src/data/content.json, which the Astro build
turns into every prompt / category / formula page.

Usage:
    python site/scripts/export_content.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parents[1]
ASSET_ROOT = SITE_DIR.parent
OUT_PATH = SITE_DIR / "src" / "data" / "content.json"

sys.path.insert(0, str(ASSET_ROOT))

from knowledge_base import formulas as kb_formulas  # noqa: E402
from knowledge_base import prompt_library as kb_prompts  # noqa: E402
from knowledge_base import sd15_general as kb_sd15  # noqa: E402
from knowledge_base import sd15_pov as kb_pov  # noqa: E402

# The library uses "code-prompt" for its entries while CATEGORIES lists "code".
CATEGORY_ALIASES = {"code-prompt": "code"}

CATEGORY_COPY: dict[str, dict[str, str]] = {
    "image-sd15": {
        "name": "Stable Diffusion 1.5 Image Prompts",
        "blurb": "Proven SD1.5 prompt templates for photoreal, cinematic POV, anime "
                 "and LoRA styling — with the negative prompts that keep hands and "
                 "faces intact.",
    },
    "system-prompt": {
        "name": "System Prompts",
        "blurb": "Production system prompts built on the identity / constraints / "
                 "process / output-contract architecture.",
    },
    "function-prompt": {
        "name": "Function-Calling Prompts",
        "blurb": "Contract-bound prompts for tool calling, extraction and "
                 "classification that return parseable output every time.",
    },
    "code": {
        "name": "Code Prompts",
        "blurb": "Spec-first coding prompts that state constraints, versions and the "
                 "tests the answer must satisfy.",
    },
    "writing": {
        "name": "Writing Prompts",
        "blurb": "Long-form and rewrite prompts with voice, structure and "
                 "preservation rules.",
    },
    "analysis": {
        "name": "Analysis Prompts",
        "blurb": "Decision-grade analysis prompts: SWOT, weighted comparison and "
                 "evidence-backed recommendations.",
    },
    "reasoning": {
        "name": "Reasoning Prompts",
        "blurb": "Chain-of-thought, self-check and root-cause prompts for problems "
                 "that need a correct answer, not a plausible one.",
    },
    "marketing": {
        "name": "Marketing Prompts",
        "blurb": "AIDA copy, positioning and pain-point discovery prompts for "
                 "campaigns that convert.",
    },
    "translation": {
        "name": "Translation Prompts",
        "blurb": "Meaning-first translation and full localization prompts with "
                 "register and glossary control.",
    },
    "education": {
        "name": "Education Prompts",
        "blurb": "Explainer and assessment prompts that build understanding and "
                 "check it.",
    },
    "data-extraction": {
        "name": "Data Extraction Prompts",
        "blurb": "Table and entity extraction prompts that return verbatim values in "
                 "a fixed schema.",
    },
    "roleplay": {
        "name": "Roleplay Prompts",
        "blurb": "Character and scenario prompts with explicit in-character "
                 "contracts.",
    },
    "agent": {
        "name": "Agent Prompts",
        "blurb": "Research and planning prompts for ReAct loops, decomposition and "
                 "citation-backed answers.",
    },
    "chat": {
        "name": "Chat Prompts",
        "blurb": "Assistant and mentor chat prompts with boundaries against "
                 "fabrication.",
    },
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")


def clamp(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:-") + "…"


def seo_title(title: str, suffix: str, limit: int = 80) -> str:
    """Build a <80 char title, trimming the prompt title if needed."""
    room = limit - len(suffix)
    trimmed = title if len(title) <= room else clamp(title, room)
    return f"{trimmed}{suffix}"


def main() -> None:
    categories: list[dict] = []
    prompts: list[dict] = []

    for category in kb_prompts.CATEGORIES:
        copy = CATEGORY_COPY.get(category, {"name": category, "blurb": ""})
        categories.append(
            {
                "slug": slugify(category),
                "key": category,
                "name": copy["name"],
                "blurb": copy["blurb"],
                "prompt_slugs": [],
            }
        )
    by_key = {c["key"]: c for c in categories}

    description_seen: set[str] = set()

    for entry in kb_prompts.LIBRARY:
        key = CATEGORY_ALIASES.get(entry.category, entry.category)
        if key not in by_key:
            raise SystemExit(f"category {entry.category!r} missing from CATEGORIES")
        cat = by_key[key]
        slug = slugify(entry.id)
        meta = clamp(
            f"{entry.description} Copy-and-paste ready, with the negative prompt and "
            f"the checklist to test it. Part of the PromptForge {cat['name']} set.",
            158,
        )
        if meta in description_seen:
            meta = clamp(meta + f" Prompt id: {slug}.", 158)
        description_seen.add(meta)
        prompt = {
            "id": entry.id,
            "slug": slug,
            "category_key": key,
            "category_slug": cat["slug"],
            "category_name": cat["name"],
            "title": entry.title,
            "description": entry.description,
            "template": entry.template,
            "tags": list(entry.tags),
            "seo_title": seo_title(entry.title, " — Prompt Template | PromptForge"),
            "meta_description": meta,
            "url_path": f"/prompts/{slug}/",
        }
        prompts.append(prompt)
        cat["prompt_slugs"].append(slug)

    # Related prompts: same category first, then shared tags, then fill.
    by_slug = {p["slug"]: p for p in prompts}
    for prompt in prompts:
        related: list[str] = []
        for other in prompts:
            if other["slug"] == prompt["slug"]:
                continue
            if other["category_key"] == prompt["category_key"]:
                related.append(other["slug"])
        if len(related) < 3:
            for other in prompts:
                if other["slug"] in related or other["slug"] == prompt["slug"]:
                    continue
                if set(other["tags"]) & set(prompt["tags"]):
                    related.append(other["slug"])
        prompt["related"] = related[:4]
        prompt["related_urls"] = [by_slug[s]["url_path"] for s in prompt["related"]]

    formula_description_seen: set[str] = set()
    formulas_out: list[dict] = []
    for formula in kb_formulas.FORMULAS:
        slug = slugify(formula.name)
        meta = clamp(
            f"{formula.description} When to use it: {formula.when_to_use} "
            "Includes the copy-paste skeleton. From the PromptForge Masterclass.",
            158,
        )
        if meta in formula_description_seen:
            meta = clamp(meta + f" Formula id: {slug}.", 158)
        formula_description_seen.add(meta)
        formulas_out.append(
            {
                "slug": slug,
                "name": formula.name,
                "description": formula.description,
                "skeleton": formula.skeleton,
                "when_to_use": formula.when_to_use,
                "seo_title": seo_title(formula.name, " — Prompting Formula | PromptForge"),
                "meta_description": meta,
                "url_path": f"/formulas/{slug}/",
            }
        )

    pov = {
        "framework_facts": list(kb_pov.FRAMEWORK_FACTS),
        "pov_keywords": list(kb_pov.POV_KEYWORDS),
        "danbooru_pov_tags": list(kb_pov.DANBOORU_POV_TAGS),
        "pov_side_effects": list(kb_pov.POV_SIDE_EFFECTS),
        "lens_artifact_negatives": list(kb_pov.LENS_ARTIFACT_NEGATIVES),
        "anatomy_positives": list(kb_pov.ANATOMY_POSITIVES),
        "anatomy_negatives": list(kb_pov.ANATOMY_NEGATIVES),
        "depth_focus_positives": list(kb_pov.DEPTH_FOCUS_POSITIVES),
        "depth_focus_negatives": list(kb_pov.DEPTH_FOCUS_NEGATIVES),
        "composition_shots": dict(kb_pov.COMPOSITION_SHOTS),
        "composition_negatives": list(kb_pov.COMPOSITION_NEGATIVES),
        "lighting_terms": {k: list(v) for k, v in kb_pov.LIGHTING_TERMS.items()},
        "lighting_negatives": list(kb_pov.LIGHTING_NEGATIVES),
        "cinematic_modifiers": list(kb_pov.CINEMATIC_MODIFIERS),
        "dictionary": {
            group: {kind: list(terms) for kind, terms in buckets.items()}
            for group, buckets in kb_pov.POV_DICTIONARY.items()
        },
        "baseline_negatives": list(kb_pov.BASELINE_NEGATIVES),
        "hierarchy_steps": list(kb_pov.HIERARCHY_STEPS),
        "guide_source": "knowledge_base/data/sd15_pov_guide.md",
    }

    sd15_general = {
        "clip_token_limit": kb_sd15.CLIP_TOKEN_LIMIT,
        "weight_rules": [list(pair) for pair in kb_sd15.WEIGHT_RULES],
        "weight_guidance": dict(kb_sd15.WEIGHT_GUIDANCE),
        "lora_syntax": kb_sd15.LORA_SYNTAX,
        "lora_examples": list(kb_sd15.LORA_EXAMPLES),
        "embedding_syntax": kb_sd15.EMBEDDING_SYNTAX,
        "hypernet_syntax": kb_sd15.HYPERNET_SYNTAX,
        "lora_guide": [dict(item) for item in kb_sd15.LORA_GUIDE],
        "lora_trigger_words": list(kb_sd15.LORA_TRIGGER_WORDS),
        "danbooru_style": {k: list(v) for k, v in kb_sd15.DANBOORU_STYLE.items()},
        "photoreal_style": {k: list(v) for k, v in kb_sd15.PHOTOREAL_STYLE.items()},
        "parameter_guidance": dict(kb_sd15.PARAMETER_GUIDANCE),
        "negative_packs": {k: list(v) for k, v in kb_sd15.NEGATIVE_PACKS.items()},
        "aspect_ratios": dict(kb_sd15.ASPECT_RATIOS),
    }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(ASSET_ROOT),
        "counts": {
            "prompts": len(prompts),
            "categories": len(categories),
            "formulas": len(formulas_out),
            "robustness_rules": len(kb_formulas.ROBUSTNESS_RULES),
        },
        "brand": {
            "line": "PromptForge",
            "tagline": "Proven prompts, forged to work.",
            "master_title": "The PromptForge Library — 30 Proven Prompt Templates "
                            "Engineered for Real Results",
        },
        "categories": categories,
        "prompts": prompts,
        "formulas": formulas_out,
        "robustness_rules": list(kb_formulas.ROBUSTNESS_RULES),
        "system_prompt_architecture": dict(kb_formulas.SYSTEM_PROMPT_ARCHITECTURE),
        "pov": pov,
        "sd15_general": sd15_general,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    over_title = [p["slug"] for p in prompts if len(p["seo_title"]) >= 80]
    over_meta = [p["slug"] for p in prompts if len(p["meta_description"]) > 160]
    dupes = len(prompts) - len({p["meta_description"] for p in prompts})
    print(f"wrote {OUT_PATH}")
    print(f"counts: {payload['counts']}")
    print(f"titles >=80 chars: {over_title}")
    print(f"meta descriptions >160: {over_meta}")
    print(f"duplicate meta descriptions: {dupes}")


if __name__ == "__main__":
    main()