import type { APIRoute } from 'astro';
import { allPaths, canonical } from '../lib/routes';
import { generatedAt } from '../lib/content';

export const prerender = true;

export const GET: APIRoute = () => {
  const lastmod = generatedAt.slice(0, 10);
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allPaths()
  .map(
    (entry) => `  <url>
    <loc>${canonical(entry.path)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${entry.changefreq}</changefreq>
    <priority>${entry.priority}</priority>
  </url>`,
  )
  .join('\n')}
</urlset>
`;

  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
