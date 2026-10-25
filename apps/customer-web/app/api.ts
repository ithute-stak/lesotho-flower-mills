export type Product = {id:string;sku:string;name:string;stock_unit:string};
const base = "";
export async function api<T>(path:string, init?:RequestInit):Promise<T> {
  const response=await fetch(base+path,{...init,headers:{"Content-Type":"application/json",...init?.headers},cache:"no-store"});
  if(!response.ok){let detail="Request failed";try {const data=await response.json();detail=typeof data.detail==="string"?data.detail:detail;}catch{}throw new Error(detail);}
  return response.json() as Promise<T>;
}
