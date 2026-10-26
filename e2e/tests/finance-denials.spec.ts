import {test,expect} from "@playwright/test";
test.skip(process.env.LFM_BACKEND_E2E!=="true","Requires isolated PostgreSQL API");
async function login(request:any,email:string,password:string){
 const response=await request.post("http://127.0.0.1:8000/api/v1/auth/login",{data:{email,password}});
 expect(response.status()).toBe(200);
 return (await response.json()).access_token as string;
}
test("admin without finance grant cannot cancel unpaid orders",async({request})=>{
 const token=await login(request,"e2e-warehouse@example.invalid","e2e-synthetic-only-password");
 const result=await request.post("http://127.0.0.1:8000/api/v1/admin/orders/00000000-0000-0000-0000-000000000001/cancel",{
 headers:{authorization:"Bearer "+token}});
 expect(result.status()).toBe(403);
 expect((await result.json()).detail).toBe("Active finance permission required");
});
test("customer and anonymous callers cannot cancel orders",async({request})=>{
 const token=await login(request,"e2e-customer@example.invalid","e2e-customer-test-password");
 const url="http://127.0.0.1:8000/api/v1/admin/orders/00000000-0000-0000-0000-000000000001/cancel";
 expect((await request.post(url,{headers:{authorization:"Bearer "+token}})).status()).toBe(403);
 expect((await request.post(url)).status()).toBe(401);
});
