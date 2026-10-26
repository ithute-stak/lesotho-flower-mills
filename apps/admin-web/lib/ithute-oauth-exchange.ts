/** Server-only OAuth code exchange primitive. Not wired to login routes.
 * No cookies/tokens are persisted; callers must verify ID token, nonce,
 * central session and employee membership before issuing an app session.
 */
import "server-only";
export type TokenExchangeResult={access_token:string;id_token:string;token_type:"Bearer";expires_in:number};
export async function exchangeIthuteCode(input:{
 issuer:string;clientId:string;callbackUrl:string;code:string;verifier:string;
}, transport:typeof fetch=fetch):Promise<TokenExchangeResult>{
 const issuer=new URL(input.issuer);
 const callback=new URL(input.callbackUrl);
 if(issuer.protocol!=="https:"||issuer.username||issuer.password||issuer.search||issuer.hash||
    callback.protocol!=="https:"||callback.username||callback.password||callback.hash||
    !/^[A-Za-z0-9_-]{43,128}$/.test(input.verifier)||
    !input.clientId||!input.code||input.code.length>4096)throw new Error("Invalid OAuth exchange configuration");
 const url=new URL("/oauth/token",issuer);
 const body=new URLSearchParams({grant_type:"authorization_code",code:input.code,
  client_id:input.clientId,redirect_uri:callback.toString(),code_verifier:input.verifier});
 const response=await transport(url,{method:"POST",body,headers:{"content-type":"application/x-www-form-urlencoded"},
  cache:"no-store",redirect:"error",signal:AbortSignal.timeout(5000)});
 if(!response.ok)throw new Error("OAuth token exchange rejected");
 const data:unknown=await response.json();
 if(!data||typeof data!=="object")throw new Error("Invalid OAuth token response");
 const value=data as Record<string,unknown>;
 if(typeof value.access_token!=="string"||!value.access_token||
    typeof value.id_token!=="string"||!value.id_token||
    value.token_type!=="Bearer"||typeof value.expires_in!=="number"||
    !Number.isFinite(value.expires_in)||value.expires_in<=0)
   throw new Error("Invalid OAuth token response");
 return {access_token:value.access_token,id_token:value.id_token,
  token_type:"Bearer",expires_in:value.expires_in};
}
