import { test, expect, type Page, type TestInfo } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * PromptForge site — flow tests with screenshots.
 *
 * For every page flow this spec asserts the SEO/content invariants the site is
 * built to guarantee (one <title> < 80 chars, unique meta description <= 160,
 * canonical, a single H1, JSON-LD) *and* captures a full-page screenshot.
 *
 * The screenshot set under tests/screenshots/<project>/ is the QA artifact the
 * `frontend` role reviews; tests/screenshots/manifest.json indexes it.
 */

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SHOTS_DIR = path.join(HERE, '..', 'screenshots');
const CANONICAL_ROOT = 'https://bhongong.github.io/promptforge-site';

interface Flow {
  /** stable id -> screenshot file name */
  name: string;
  /** path relative to the deploy base, e.g. '' or 'prompts/' */
  url: string;
  /** substring that must be visible on the rendered page */
  expectText: string;
  /** skip the canonical-tag assertion (the 404 page is intentionally noindex) */
  skipCanonical?: boolean;
  /** skip the JSON-LD assertion (noindex error page carries no structured data) */
  skipJsonLd?: boolean;
}

const FLOWS: Flow[] = [
  { name: '01-home', url: '', expectText: 'PromptForge' },
  { name: '02-prompts-index', url: 'prompts/', expectText: 'prompt' },
  { name: '03-prompt-detail', url: 'prompts/sd15-pov-cinematic/', expectText: 'POV' },
  { name: '04-categories-index', url: 'categories/', expectText: 'categor' },
  { name: '05-category-detail', url: 'categories/image-sd15/', expectText: 'SD' },
  { name: '06-formulas-index', url: 'formulas/', expectText: 'CO-STAR' },
  { name: '07-formula-detail', url: 'formulas/co-star/', expectText: 'CO-STAR' },
  { name: '08-pov-guide', url: 'pov-guide/', expectText: 'POV' },
  { name: '09-free-starter-kit', url: 'free-starter-kit/', expectText: 'Starter Kit' },
  { name: '10-products', url: 'products/', expectText: 'PromptForge' },
  { name: '11-about', url: 'about/', expectText: 'PromptForge' },
  { name: '12-license', url: 'license/', expectText: 'licen' },
  { name: '13-404', url: 'this-page-does-not-exist/', expectText: '404', skipCanonical: true, skipJsonLd: true },
];

function shotPath(testInfo: TestInfo, name: string): string {
  const dir = path.join(SHOTS_DIR, testInfo.project.name);
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, `${name}.png`);
}

/** Collects uncaught page errors / console errors so a broken flow fails loudly. */
function watchConsole(page: Page): string[] {
  const errors: string[] = [];
  page.on('pageerror', (err) => errors.push(`pageerror: ${err.message}`));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(`console.error: ${msg.text()}`);
  });
  return errors;
}

async function assertSeo(page: Page, skipCanonical = false, skipJsonLd = false) {
  const title = await page.title();
  expect(title.length, `title too long: ${title}`).toBeGreaterThan(0);
  expect(title.length, `title >= 80 chars: ${title}`).toBeLessThan(80);
  expect(await page.locator('head title').count()).toBe(1);

  const desc = await page.locator('head meta[name="description"]').first().getAttribute('content');
  expect(desc, 'missing meta description').toBeTruthy();
  expect((desc ?? '').length).toBeLessThanOrEqual(160);

  if (!skipCanonical) {
    const canonical = await page.locator('head link[rel="canonical"]').first().getAttribute('href');
    expect(canonical, 'missing canonical').toContain(CANONICAL_ROOT);
    expect(canonical?.endsWith('/')).toBe(true);
  }

  expect(await page.locator('h1').count(), 'page needs exactly one H1').toBeGreaterThanOrEqual(1);
  if (!skipJsonLd) {
    expect(
      await page.locator('script[type="application/ld+json"]').count(),
      'missing JSON-LD structured data',
    ).toBeGreaterThanOrEqual(1);
  }
}

test.describe('PromptForge — page flows (SEO + screenshots)', () => {
  for (const flow of FLOWS) {
    test(`${flow.name} renders and passes the SEO invariants`, async ({ page }, testInfo) => {
      // the browser itself logs a console error for the 404 document, so that
      // single expected message is filtered out for the error page.
      const expectedStatus = flow.name === '13-404' ? 404 : 200;
      const errors = watchConsole(page);
      const response = await page.goto(flow.url, { waitUntil: 'load' });
      expect(response?.status(), `HTTP status for ${flow.url}`).toBe(expectedStatus);

      await expect(page.locator('body')).toContainText(new RegExp(flow.expectText, 'i'));
      await assertSeo(page, flow.skipCanonical, flow.skipJsonLd);

      const file = shotPath(testInfo, flow.name);
      await page.screenshot({ path: file, fullPage: true });
      await testInfo.attach(flow.name, { path: file, contentType: 'image/png' });

      const fatal = expectedStatus === 404
        ? errors.filter((e) => !/Failed to load resource/.test(e))
        : errors;
      expect(fatal, `console/page errors on ${flow.url}`).toEqual([]);
    });
  }
});

test.describe('PromptForge — conversion flows', () => {
  test('lead form rejects an invalid email and confirms a valid one (preview mode)', async ({ page }, testInfo) => {
    await page.goto('free-starter-kit/');
    const form = page.locator('form.lead-form').first();
    await expect(form).toBeVisible();

    const status = form.locator('[data-role="status"]');
    const email = form.locator('input[name="email"]');

    await email.fill('not-an-email');
    await form.locator('button[type="submit"]').click();
    await expect(status).toHaveText(/valid email/i);

    await email.fill('ceo@example.com');
    await form.locator('button[type="submit"]').click();
    await expect(status).toHaveText(/Preview mode|on its way/i);
    await expect(status).toHaveAttribute('data-state', /pending|ok/);

    await page.screenshot({ path: shotPath(testInfo, '14-lead-form-states'), fullPage: true });
  });

  test('every product CTA carries UTM attribution and points at a storefront', async ({ page }, testInfo) => {
    await page.goto('products/');
    const ctas = page.locator('a[data-sku]');
    const count = await ctas.count();
    expect(count, 'products page must expose tracked SKU CTAs').toBeGreaterThan(0);

    for (let i = 0; i < count; i++) {
      const href = await ctas.nth(i).getAttribute('href');
      expect(href, `CTA #${i} href`).toBeTruthy();
      expect(href, `CTA #${i} lost its UTM params`).toContain('utm_source=site');
      expect(href, `CTA #${i} lost utm_campaign`).toContain('utm_campaign=');
    }

    await page.screenshot({ path: shotPath(testInfo, '15-products-ctas'), fullPage: true });
  });

  test('internal navigation from the home hero reaches a prompt page', async ({ page }, testInfo) => {
    await page.goto('');
    const link = page.locator('a[href*="/prompts/"]').first();
    await expect(link).toBeVisible();
    await link.click();
    await page.waitForLoadState('load');
    await expect(page).toHaveURL(/\/prompts\//);
    await assertSeo(page);
    await page.screenshot({ path: shotPath(testInfo, '16-nav-home-to-prompt'), fullPage: true });
  });
});

test.describe('PromptForge — full-site crawl', () => {
  test('every URL in sitemap.xml returns 200 with a canonical tag', async ({ request }) => {
    const sitemap = await request.get('sitemap.xml');
    expect(sitemap.status()).toBe(200);
    const xml = await sitemap.text();
    const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    expect(urls.length, 'sitemap must list the full page inventory').toBeGreaterThanOrEqual(70);

    const failures: string[] = [];
    for (const url of urls) {
      const res = await request.get(url);
      if (res.status() !== 200) {
        failures.push(`${url} -> HTTP ${res.status()}`);
        continue;
      }
      const html = await res.text();
      if (!html.includes('rel="canonical"')) failures.push(`${url} -> no canonical tag`);
      if (!/<meta name="description"/.test(html)) failures.push(`${url} -> no meta description`);
    }
    expect(failures, `${failures.length}/${urls.length} sitemap pages failed`).toEqual([]);
  });
});
