import { test, expect } from "@playwright/test";

test("customer books a NekoCafe reservation", async ({ page }) => {
  await page.goto("http://127.0.0.1:8000/");
  await expect(page.getByText("预约制猫咖体验")).toBeVisible();
  await page.getByText("体验会员入口").click();
  await page.getByRole("button", { name: "进入会员体验" }).click();
  await expect(page.getByText("立即预约")).toBeVisible();
  await page.getByRole("button", { name: "确认预约" }).click();
  await expect(page.getByText("预约详情")).toBeVisible();
});
