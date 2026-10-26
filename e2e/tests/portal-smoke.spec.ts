import {test,expect} from "@playwright/test";

test("customer portal navigation and unauthenticated quote controls",async({page})=>{
 await page.goto("http://127.0.0.1:3100");
 await expect(page.getByText("LESOTHO FLOUR MILLS")).toBeVisible();
 await page.getByRole("button",{name:"Explore products"}).click();
 await expect(page.getByRole("heading",{name:"Available products"})).toBeVisible();
 await expect(page.getByRole("button",{name:"Request draft quotation"})).toBeDisabled();
 await page.getByRole("button",{name:"Account",exact:true}).click();
 await expect(page.getByRole("heading",{name:"Create an account"})).toBeVisible();
 await page.getByRole("button",{name:"Sign in"}).click();
 await expect(page.getByRole("heading",{name:"Sign in"})).toBeVisible();
});

test("admin portal renders without granting anonymous access",async({page})=>{
 await page.goto("http://127.0.0.1:3101");
 await expect(page.locator("body")).toContainText("LESOTHO");
 await expect(page.locator("input[type=password]")).toBeVisible();
});
