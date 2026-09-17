import { SITE } from '../config';
import { categories, formulas, prompts } from './content';

/** Astro's configured base ('/promptforge-site' here), without a trailing slash. */
export const BASE = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');

/** Internal link with the deploy base prefix applied. */
export function u(path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  return `${BASE}${clean}` || '/';
}

/** Absolute canonical URL for a page path. */
export function canonical(path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  return `${SITE.baseUrl}${clean}`;
}

/** Every indexable path on the site — the single source for sitemap + nav. */
export function allPaths(): { path: string; changefreq: string; priority: string }[] {
  return [
    { path: '/', changefreq: 'weekly', priority: '1.0' },
    { path: '/prompts/', changefreq: 'weekly', priority: '0.9' },
    { path: '/categories/', changefreq: 'weekly', priority: '0.8' },
    { path: '/formulas/', changefreq: 'monthly', priority: '0.8' },
    { path: '/pov-guide/', changefreq: 'monthly', priority: '0.8' },
    { path: '/free-starter-kit/', changefreq: 'monthly', priority: '0.7' },
    { path: '/products/', changefreq: 'monthly', priority: '0.6' },
    { path: '/about/', changefreq: 'yearly', priority: '0.3' },
    { path: '/license/', changefreq: 'yearly', priority: '0.2' },
    ...prompts.map((p) => ({ path: p.url_path, changefreq: 'monthly', priority: '0.7' })),
    ...categories.map((c) => ({
      path: `/categories/${c.slug}/`,
      changefreq: 'weekly',
      priority: '0.6',
    })),
    ...formulas.map((f) => ({ path: f.url_path, changefreq: 'monthly', priority: '0.6' })),
  ];
}