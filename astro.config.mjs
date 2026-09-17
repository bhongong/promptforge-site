// @ts-check
import { defineConfig } from 'astro/config';

// GitHub Pages project site: https://bhongong.github.io/promptforge-site/
// To move to a custom domain (promptforge.com), set BASE to '/' and update
// src/config.ts -> SITE.baseUrl, then rebuild + redeploy.
const BASE = '/promptforge-site';

export default defineConfig({
  site: 'https://bhongong.github.io',
  base: BASE,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  compressHTML: true,
});