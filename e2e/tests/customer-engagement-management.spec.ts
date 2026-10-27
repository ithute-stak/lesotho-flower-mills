import {test,expect} from "@playwright/test";

test.skip(process.env.LFM_BACKEND_E2E!=="true","Requires isolated CI browser environment");

test("ungranted finance identities cannot access engagement reporting",async({request})=>{
 const root="http://127.0.0.1:8000/api/v1";
 const login=await request.post(root+"/auth/login",{data:{email:"e2e-warehouse@example.invalid",password:"e2e-synthetic-only-password"}});
 expect(login.status()).toBe(200);
 const token=(await login.json()).access_token;
 for(const path of ["/admin/customer-engagement/reports/management","/admin/customer-engagement/reports/management.pdf","/admin/customer-engagement/reports/review-audit"]){
  const result=await request.get(root+path,{headers:{authorization:"Bearer "+token}});
  expect(result.status(),path).toBe(403);
 }
});

test("customer engagement management filters and authenticated PDF export",async({page})=>{
 const api="http://127.0.0.1:3101/api/v1";
 await page.route("**/api/v1/**",async route=>{
  const url=new URL(route.request().url()),path=url.pathname;
  if(path.endsWith("/auth/login"))return route.fulfill({status:200,contentType:"application/json",body:JSON.stringify({access_token:"browser-fixture-token"})});
  if(path.endsWith("/admin/customer-engagement/summary"))return route.fulfill({json:{draft_loyalty_enrolments:0,draft_repeat_order_templates:0,cancelled_repeat_order_templates:0,approved_repeat_order_templates:0,rejected_repeat_order_templates:0,draft_referrals:0,points_enabled:false,automatic_ordering_enabled:false,referral_rewards_enabled:false}});
  if(path.endsWith("/admin/customer-engagement/referrals")||path.endsWith("/admin/customer-engagement/repeat-orders")||path.endsWith("/products"))return route.fulfill({json:[]});
  if(path.endsWith("/admin/customer-engagement/reports/planning"))return route.fulfill({json:{basis:"planning_only",draft_loyalty_enrolments:0,draft_referrals:0,repeat_order_frequency_breakdown:[],top_referrers:[],actual_repeat_orders:null,actual_retention_rate:null,actual_referral_conversions:null,actual_revenue:null}});
  if(path.endsWith("/admin/customer-engagement/reports/management"))return route.fulfill({json:{basis:"planning_review_only",kpis:{total_decisions:4,approvals:3,rejections:1,approval_share_percent:75},reviewer_activity:[],monthly_trends:[],actual_sales:null,actual_customer_retention:null,automatic_ordering_enabled:false}});
  if(path.endsWith("/admin/customer-engagement/reports/management.pdf")){
   expect(route.request().headers()["authorization"]).toBe("Bearer browser-fixture-token");
   expect(url.searchParams.get("start")).toMatch(/^\\d{4}-\\d{2}-01$/);
   return route.fulfill({status:200,contentType:"application/pdf",body:Buffer.from("%PDF-1.4 fake browser fixture")});
  }
  return route.fulfill({status:404,json:{detail:"Unexpected mocked route"}});
 });
 await page.goto("http://127.0.0.1:3101");
 await page.locator('input[type="email"]').fill("staff@example.invalid");
 await page.locator('input[type="password"]').fill("fixture-password");
 await page.getByRole("button",{name:"Sign in"}).click();
 await page.getByRole("button",{name:"Customer Engagement"}).click();
 await expect(page.getByRole("heading",{name:/Management intelligence/})).toBeVisible();
 await page.getByRole("button",{name:"This month"}).click();
 await page.getByRole("button",{name:"Refresh management report"}).click();
 await expect(page.getByText("Approval share:")).toBeVisible();
 await expect(page.getByText("75%")).toBeVisible();
 await page.getByRole("button",{name:"Download PDF report"}).click();
 await expect(page.getByRole("heading",{name:/Management intelligence/})).toBeVisible();
});
