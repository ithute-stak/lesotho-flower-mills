/** Sealed OAuth transaction envelope for future HttpOnly cookie storage.
 * Encryption protects PKCE verifier and nonce. Does not itself prevent replay.
 */
import "server-only";
import {createCipheriv,createDecipheriv,createHash,randomBytes} from "node:crypto";
import {verifyOAuthState} from "./ithute-oauth-pkce";

export type PendingOAuth={state:string;verifier:string;nonce:string;issuedAt:number};
const ttl=600;
function key(secret:string):Buffer {
 if(Buffer.byteLength(secret,"utf8")<32)throw new Error("OAuth secret too short");
 return createHash("sha256").update("lfm-oauth-transaction-v1:").update(secret).digest();
}
export function sealOAuthTransaction(tx:PendingOAuth,secret:string):string {
 const iv=randomBytes(12);
 const cipher=createCipheriv("aes-256-gcm",key(secret),iv);
 cipher.setAAD(Buffer.from("lfm-ithute-oauth-v1"));
 const ciphertext=Buffer.concat([cipher.update(JSON.stringify(tx),"utf8"),cipher.final()]);
 return [iv,cipher.getAuthTag(),ciphertext].map(b=>b.toString("base64url")).join(".");
}
export function unsealOAuthTransaction(value:string,secret:string,now=Math.floor(Date.now()/1000)):PendingOAuth|null {
 try{
  const fields=value.split(".");
  if(fields.length!==3||value.length>4096)return null;
  const [iv,tag,data]=fields.map(x=>Buffer.from(x,"base64url"));
  if(iv.length!==12||tag.length!==16||data.length>2048)return null;
  const decipher=createDecipheriv("aes-256-gcm",key(secret),iv);
  decipher.setAAD(Buffer.from("lfm-ithute-oauth-v1"));
  decipher.setAuthTag(tag);
  const tx=JSON.parse(Buffer.concat([decipher.update(data),decipher.final()]).toString("utf8")) as PendingOAuth;
  if(!tx||typeof tx.state!=="string"||typeof tx.verifier!=="string"||typeof tx.nonce!=="string"||!Number.isSafeInteger(tx.issuedAt))return null;
  if(tx.issuedAt>now+30||now-tx.issuedAt>ttl||!verifyOAuthState(tx.state,secret,now))return null;
  if(tx.verifier.length<43||tx.verifier.length>128||tx.nonce.length<32)return null;
  return tx;
 }catch{return null;}
}
export const oauthCookieOptions={
 httpOnly:true,secure:true,sameSite:"lax" as const,path:"/api/auth/ithute",maxAge:600,
};
