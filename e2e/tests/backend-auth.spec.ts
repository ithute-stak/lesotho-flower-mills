import {test,expect} from "@playwright/test";
test.skip(process.env.LFM_BACKEND_E2E!=="true","Requires isolated PostgreSQL-backed API");

test("warehouse authenticates against real isolated FastAPI and PostgreSQL",async({page})=>{
 await page.goto("http://127.0.0.1:3102");
 await page.locator('input[type="email"]').fill("e2e-warehouse@example.invalid");
 await page.locator('input[type="password"]').fill("e2e-synthetic-only-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("navigation",{name:"Warehouse sections"})).toBeVisible();
 await expect(page.getByRole("heading",{name:"Stock availability"})).toBeVisible();
 await page.getByRole("button",{name:"Sign out"}).click();
 await expect(page.getByRole("heading",{name:"Staff login"})).toBeVisible();
});

test("unknown staff identity cannot log into real backend",async({page})=>{
 await page.goto("http://127.0.0.1:3102");
 await page.locator('input[type="email"]').fill("unknown@example.invalid");
 await page.locator('input[type="password"]').fill("incorrect-synthetic-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("heading",{name:"Staff login"})).toBeVisible();
 await expect(page.getByText("Incorrect credentials")).toBeVisible();
});
