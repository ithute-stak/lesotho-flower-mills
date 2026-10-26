import {test,expect} from "@playwright/test";
test.skip(process.env.LFM_BACKEND_E2E!=="true","Disposable PostgreSQL required");
const base="http://127.0.0.1:8000/api/v1";
test("finance grant is checked on every request, including after revocation",async({request})=>{
 const login=await request.post(base+"/auth/login",{data:{email:"e2e-warehouse@example.invalid",password:"e2e-synthetic-only-password"}});
 expect(login.status()).toBe(200);
 const token=(await login.json()).access_token;
 const headers={authorization:"Bearer "+token};
 // No finance grant exists for this synthetic administrator.
 for(const route of ["/admin/finance-roles/grants","/admin/finance-roles/events"]){
  expect((await request.get(base+route,{headers})).status()).toBe(403);
 }
 expect((await request.post(base+"/admin/finance-roles/requests",{
  headers,data:{identity_subject:"synthetic-other",role:"finance_admin"}})).status()).toBe(403);
});
