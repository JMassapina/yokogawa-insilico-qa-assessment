import { defineConfig, devices } from '@playwright/test';

const LOCAL_PORT = Number(process.env.PORT ?? 8899);

export default defineConfig({
  testDir: './tests',
  testIgnore: ['**/_original/**'],   // The reviewed junior test is kept as historical evidence, never executed
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [['github'], ['html', { open: 'never' }], ['list']]
    : [['list'], ['html', { open: 'never' }]],

  timeout: 45_000,
  expect: { timeout: 15_000 },

  use: {
    baseURL: `http://127.0.0.1:${LOCAL_PORT}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  // Automatically boot the isolated native standard library server on startup
  webServer: {
    command: 'node local-app/serve.mjs',
    url: `http://127.0.0.1:${LOCAL_PORT}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
