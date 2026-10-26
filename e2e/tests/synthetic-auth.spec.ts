import {test,expect} from "@playwright/test";

// Deterministic browser contract tests: synthetic responses, no real credentials.
test("warehouse accepts synthetic staff login and renders inventory",async({page})=>{
 await page.route("**/api/v1/auth/login",async route=>route.fulfill({
  status:200,contentType:"application/json",body:JSON.stringify({access_token:"synthetic-test-token"})}));
 await page.route("**/api/v1/admin/inventory/balances",async route=>{
  expect(route.request().headers().authorization).toBe("Bearer synthetic-test-token");
  await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify([
   {warehouse_id:"synthetic-w",product_id:"synthetic-p",on_hand:5,reserved:4,available:1}
  ])});
 });
 await page.goto("http://127.0.0.1:3102");
 await page.locator('input[type="email"]').fill("synthetic@example.invalid");
 await page.locator('input[type="password"]').fill("synthetic-test-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("navigation",{name:"Warehouse sections"})).toBeVisible();
 await expect(page.getByRole("heading",{name:"Stock availability"})).toBeVisible();
 await page.getByRole("button",{name:"Sign out"}).click();
 await expect(page.getByRole("heading",{name:"Staff login"})).toBeVisible();
});

test("admin login failure does not grant access",async({page})=>{
 await page.route("**/api/v1/auth/login",async route=>route.fulfill({
  status:401,contentType:"application/json",body:JSON.stringify({detail:"Incorrect credentials"})}));
 await page.goto("http://127.0.0.1:3101");
 await page.locator('input[type="email"]').fill("synthetic@example.invalid");
 await page.locator('input[type="password"]').fill("incorrect-test-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("heading",{name:"Staff sign in"})).toBeVisible();
 await expect(page.getByText("Incorrect credentials")).toBeVisible();
});
