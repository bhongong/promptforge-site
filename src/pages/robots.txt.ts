import type { APIRoute } from 'astro';
import { SITE } from '../config';

export const prerender = true;

export const GET: APIRoute = () => {
  const body = `# robots.txt for ${SITE.name}
# Everything here is public marketing content — crawl it all.
User-agent: *
Allow: /
Disallow: /404/

Sitemap: ${SITE.baseUrl}/sitemap.xml
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
