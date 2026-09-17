import content from '../data/content.json';

export interface Prompt {
  id: string;
  slug: string;
  category_key: string;
  category_slug: string;
  category_name: string;
  title: string;
  description: string;
  template: string;
  tags: string[];
  seo_title: string;
  meta_description: string;
  url_path: string;
  related: string[];
  related_urls: string[];
}

export interface Category {
  slug: string;
  key: string;
  name: string;
  blurb: string;
  prompt_slugs: string[];
}

export interface Formula {
  slug: string;
  name: string;
  description: string;
  skeleton: string;
  when_to_use: string;
  seo_title: string;
  meta_description: string;
  url_path: string;
}

export const brand = content.brand;
export const counts = content.counts;
export const generatedAt = content.generated_at;
export const sourceRoot = content.source;

export const categories = content.categories as Category[];
export const prompts = content.prompts as Prompt[];
export const formulas = content.formulas as Formula[];
export const robustnessRules = content.robustness_rules as string[];
export const systemPromptArchitecture = content.system_prompt_architecture as Record<
  string,
  string
>;
export const pov = content.pov;
export const sd15 = content.sd15_general;

export const promptsBySlug: Record<string, Prompt> = Object.fromEntries(
  prompts.map((p) => [p.slug, p]),
);
export const formulasBySlug: Record<string, Formula> = Object.fromEntries(
  formulas.map((f) => [f.slug, f]),
);
export const categoriesBySlug: Record<string, Category> = Object.fromEntries(
  categories.map((c) => [c.slug, c]),
);

export function promptsInCategory(slug: string): Prompt[] {
  const cat = categoriesBySlug[slug];
  if (!cat) return [];
  return cat.prompt_slugs.map((s) => promptsBySlug[s]).filter(Boolean);
}

export const featuredPromptSlugs = [
  'sd15-pov-cinematic',
  'system-expert-assistant',
  'function-json-extractor',
  'marketing-copy',
  'reasoning-math-cot',
  'agent-researcher',
  'writing-article',
  'code-generate-fix',
];

export const featuredPrompts = featuredPromptSlugs
  .map((s) => promptsBySlug[s])
  .filter(Boolean);