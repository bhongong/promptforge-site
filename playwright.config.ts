import { defineConfig, devices } from '@playwright/test';

/**
 * PromptForge site — automated frontend tests.
 *
 * Runs against the *built* static site (`astro preview`), so the tests exercise
 * exactly what GitHub Pages serves. Every flow captures a full-page screenshot
 * into `tests/screenshots/<project>/` — that screenshot set is the artifact the
 * `frontend` role reviews as the QA gate.
 *
 * Commands:
 *   npm run test:e2e            # both viewports
 *   npm run test:e2e -- --project=desktop-chromium
 */
const PORT = 4321;
const BASE_URL = `http://127.0.0.1:${PORT}/promptforge-site/`;

export default defineConfig({
  testDir: './tests/e2e',
  outputDir: './tests/.artifacts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  timeout: 45_000,
  expect: { timeout: 7_500 },
  reporter: [
    ['list'],
    ['json', { outputFile: 'tests/report/playwright-report.json' }],
    ['html', { outputFolder: 'tests/report/html', open: 'never' }],
  ],
  use: {
    baseURL: BASE_URL,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop-chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 5'] } },
  ],
  webServer: {
    command: 'npm run serve',
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
