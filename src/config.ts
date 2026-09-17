/**
 * Central site configuration — branding (PRODUCTIZATION-PLAN §3), SKU map (§4)
 * and tracked CTA destinations.
 *
 * NOTHING here is a live checkout yet: every Gumroad/Notion URL is a
 * TRACKED PLACEHOLDER that follows the real storefront slug, so the moment
 * R12 (Gumroad store creation) lands, the only edit needed is a find/replace
 * of `promptforge.gumroad.com` and flipping `PLACEHOLDERS_LIVE` to true.
 */

export const SITE = {
  name: 'PromptForge',
  legalName: 'PromptForge',
  tagline: 'Proven prompts, forged to work.',
  masterTitle:
    'The PromptForge Library — 30 Proven Prompt Templates Engineered for Real Results',
  description:
    'Copy-and-paste prompt templates, 16 prompting formulas and a mastered Stable Diffusion 1.5 POV guide — every template ships with the negatives and the checklist it was tested against.',
  /** Absolute canonical root of the deployed site (GitHub Pages project URL). */
  baseUrl: 'https://bhongong.github.io/promptforge-site',
  repoUrl: 'https://github.com/bhongong/promptforge-site',
  email: 'hello@promptforge.dev',
  /** Set true once the Gumroad store is live to hide the placeholder notice. */
  PLACEHOLDERS_LIVE: false,
  /**
   * Lead-magnet (SKU-LM) capture endpoint. Empty string = "not configured":
   * the form then runs in preview mode (validates + confirms, no network call)
   * instead of silently posting nowhere. Set to your form endpoint
   * (Buttondown / Kit / Formspree) to make captures real.
   */
  leadEndpoint: '',
  /** Where the free Starter Kit itself is delivered once Gumroad is live. */
  leadMagnetUrl:
    'https://promptforge.gumroad.com/l/starter-kit?utm_source=site&utm_medium=lead-magnet&utm_campaign=free-starter-kit',
} as const;

export type SkuKey = 'LM' | 'P1' | 'P2' | 'P3' | 'N1' | 'B1';

export interface Sku {
  key: SkuKey;
  name: string;
  format: string;
  price: string;
  blurb: string;
  url: string;
  badge?: string;
}

const gumroad = (slug: string, sku: SkuKey) =>
  `https://promptforge.gumroad.com/l/${slug}?utm_source=site&utm_medium=cta&utm_campaign=${sku.toLowerCase()}`;

export const SKUS: Record<SkuKey, Sku> = {
  LM: {
    key: 'LM',
    name: 'The PromptForge Starter Kit',
    format: 'PDF + copy-paste txt',
    price: 'Free',
    blurb:
      '5 starter prompts (one per beginner-friendly category) + 3 essential formulas (RTF, Chain-of-Thought, Persona) + the one-page "how to test a prompt" sheet.',
    url: SITE.leadMagnetUrl,
    badge: 'Start here',
  },
  P1: {
    key: 'P1',
    name: 'The PromptForge Library — 30 Proven Prompts',
    format: 'PDF + .txt',
    price: '$12',
    blurb:
      'The full library: 32 templates across 14 categories, each with its use case, the negatives/constraints that make it reliable, and how it was tested.',
    url: gumroad('promptforge-library', 'P1'),
  },
  P2: {
    key: 'P2',
    name: 'The PromptForge Masterclass — 16 Formulas That Fix Prompts',
    format: 'PDF + .md',
    price: '$19',
    blurb:
      'CO-STAR, CRISPE, RTF, TAG, ReAct, Tree of Thoughts, Chain-of-Verification and more — each with the skeleton, when to use it, and 8 anti-hallucination rules.',
    url: gumroad('promptforge-masterclass', 'P2'),
  },
  P3: {
    key: 'P3',
    name: 'The AI System Builder — Sub-Agent Prompt Architectures',
    format: 'PDF + .md',
    price: '$24',
    blurb:
      'Sub-agent system prompts, output contracts and evaluation checklists for building deterministic multi-agent systems.',
    url: gumroad('ai-system-builder', 'P3'),
  },
  N1: {
    key: 'N1',
    name: 'PromptForge Notion System (Library database)',
    format: 'Notion template',
    price: '$19',
    blurb:
      'The whole library as a duplicate-ready Notion database: per-category views, a formula cheat-sheet page and the POV guide page.',
    url: gumroad('promptforge-notion-system', 'N1'),
  },
  B1: {
    key: 'B1',
    name: 'PromptForge Image Studio — SD1.5 POV, LoRA & Imagegen Master Pack',
    format: 'PDF + .md + image prompt pack',
    price: '$39',
    blurb:
      'Everything in P1 + P2 + N1 PLUS the structured SD1.5 POV dictionary, the 6-step hierarchy, negative-prompt packs, LoRA weights and 4 imagegen templates.',
    url: gumroad('promptforge-image-studio', 'B1'),
    badge: 'Best value — save $11',
  },
};

/**
 * Adds placement-level UTM tracking to any destination so Gumroad/analytics can
 * attribute conversions to the exact page + slot that produced the click.
 */
export function track(url: string, placement: string): string {
  const sep = url.includes('?') ? '&' : '?';
  return `${url}${sep}utm_content=${encodeURIComponent(placement)}`;
}