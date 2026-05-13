import { test, expect } from '@playwright/test';

test('注册→预约→取消', async ({ page }) => {
  await page.goto('https://staging.nekocafe.local');
  // TODO 完整旅程
});
