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

test("ungranted administrator cannot read payment ledger or record a payment",async({request})=>{
 const token=await login(request,"e2e-warehouse@example.invalid","e2e-synthetic-only-password");
 const headers={authorization:"Bearer "+token};
 const id="00000000-0000-0000-0000-000000000001";
 const read=await request.get("http://127.0.0.1:8000/api/v1/admin/finance/orders/"+id+"/payments",{headers});
 expect(read.status()).toBe(403);
 const write=await request.post("http://127.0.0.1:8000/api/v1/admin/finance/payments",{
  headers,data:{order_id:id,provider:"synthetic",provider_reference:"synthetic-ref-001",amount:"1.00"}});
 expect(write.status()).toBe(403);
 const confirm=await request.post("http://127.0.0.1:8000/api/v1/admin/finance/orders/"+id+"/confirm-payment",{headers});
 expect(confirm.status()).toBe(403);
});
