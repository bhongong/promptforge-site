// @ts-check
import { defineConfig } from 'astro/config';

import cloudflare from "@astrojs/cloudflare";

// Custom domain for promptforge.ainovation.top (Cloudflare Pages)
const BASE = '/';

export default defineConfig({
  site: 'https://promptforge.ainovation.top',
  base: BASE,
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  compressHTML: true,
  adapter: cloudflare()
});