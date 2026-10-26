/** Cryptographically strong OAuth PKCE/state helpers. Server-side only. */
import "server-only";
import {createHash,createHmac,randomBytes,timingSafeEqual} from "node:crypto";

const STATE_LIFETIME_SECONDS=600;
function b64url(value:Buffer):string{return value.toString("base64url");}
export function newOAuthTransaction(secret:string,nowSeconds=Math.floor(Date.now()/1000)){
 if(Buffer.byteLength(secret,"utf8")<32)throw new Error("Ithute Auth session secret is too short");
 const verifier=b64url(randomBytes(48));
 const challenge=b64url(createHash("sha256").update(verifier).digest());
 const nonce=b64url(randomBytes(32));
 const stateId=b64url(randomBytes(32));
 const issued=String(nowSeconds);
 const signed=stateId+"."+issued;
 const mac=b64url(createHmac("sha256",secret).update(signed).digest());
 return {verifier,challenge,nonce,state:signed+"."+mac,issuedAt:nowSeconds};
}
export function verifyOAuthState(state:string,secret:string,nowSeconds=Math.floor(Date.now()/1000)):boolean{
 if(Buffer.byteLength(secret,"utf8")<32)return false;
 const parts=state.split(".");
 if(parts.length!==3||!parts[0]||!/^\d+$/.test(parts[1])||!parts[2])return false;
 const issued=Number(parts[1]);
 if(!Number.isSafeInteger(issued)||issued>nowSeconds+30||nowSeconds-issued>STATE_LIFETIME_SECONDS)return false;
 const signed=parts[0]+"."+parts[1];
 const expected=createHmac("sha256",secret).update(signed).digest();
 let supplied:Buffer;
 try{ supplied=Buffer.from(parts[2],"base64url"); }catch{return false;}
 return supplied.length===expected.length&&timingSafeEqual(supplied,expected);
}
