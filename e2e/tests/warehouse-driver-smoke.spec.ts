import {test,expect} from "@playwright/test";

test("warehouse portal requires staff sign-in before stock tools",async({page})=>{
 await page.goto("http://127.0.0.1:3102");
 await expect(page.getByRole("heading",{name:"Warehouse Operations"})).toBeVisible();
 await expect(page.getByRole("heading",{name:"Staff login"})).toBeVisible();
 await expect(page.locator('input[type="password"]')).toBeVisible();
 await expect(page.getByRole("navigation",{name:"Warehouse sections"})).toHaveCount(0);
});

test("driver portal requires sign-in before viewing delivery assignments",async({page})=>{
 await page.goto("http://127.0.0.1:3103");
 await expect(page.getByRole("heading",{name:"Driver Portal"})).toBeVisible();
 await expect(page.getByRole("heading",{name:"Driver sign in"})).toBeVisible();
 await expect(page.locator('input[type="password"]')).toBeVisible();
});
