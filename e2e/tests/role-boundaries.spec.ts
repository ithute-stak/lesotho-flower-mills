import {test,expect} from "@playwright/test";
test.skip(process.env.LFM_BACKEND_E2E!=="true","Requires disposable backend and database");

test("customer credentials cannot open warehouse staff portal",async({page})=>{
 await page.goto("http://127.0.0.1:3102");
 await page.locator('input[type="email"]').fill("e2e-customer@example.invalid");
 await page.locator('input[type="password"]').fill("e2e-customer-test-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("heading",{name:"Staff login"})).toBeVisible();
 await expect(page.getByRole("navigation",{name:"Warehouse sections"})).toHaveCount(0);
 await expect(page.getByText("Staff authorisation required")).toBeVisible();
});

test("customer token is denied by real staff inventory endpoint",async({request})=>{
 const login=await request.post("http://127.0.0.1:8000/api/v1/auth/login",{
  data:{email:"e2e-customer@example.invalid",password:"e2e-customer-test-password"}});
 expect(login.status()).toBe(200);
 const auth=await login.json();
 const denied=await request.get("http://127.0.0.1:8000/api/v1/admin/inventory/balances",{
  headers:{authorization:"Bearer "+auth.access_token}});
 expect(denied.status()).toBe(403);
 const anonymous=await request.get("http://127.0.0.1:8000/api/v1/admin/inventory/balances");
 expect(anonymous.status()).toBe(401);
});
