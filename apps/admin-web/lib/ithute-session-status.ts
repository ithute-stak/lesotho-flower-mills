/** Online central session validation, fail closed. Not wired to login. */
import "server-only";
export async function verifyIthuteCentralSession(issuer:string,accessToken:string,transport:typeof fetch=fetch):Promise<boolean>{
 const base=new URL(issuer);
 if(base.protocol!=="https:"||base.username||base.password||base.search||base.hash||!accessToken)throw new Error("Invalid session check configuration");
 const endpoint=new URL("/v1/account/session-status",base);
 const response=await transport(endpoint,{method:"GET",headers:{"authorization":"Bearer "+accessToken},
  cache:"no-store",redirect:"error",signal:AbortSignal.timeout(5000)});
 if(!response.ok)return false;
 const data:unknown=await response.json();
 return Boolean(data&&typeof data==="object"&&!Array.isArray(data)&&(data as Record<string,unknown>).active===true);
}
