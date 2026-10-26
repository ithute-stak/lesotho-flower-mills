/** Verify Ithute ID token with pinned HTTPS JWKS. Not connected to live login. */
import "server-only";
import {createPublicKey,verify as verifySignature} from "node:crypto";

function decodePart(part:string):Record<string,unknown>{
 const value=JSON.parse(Buffer.from(part,"base64url").toString("utf8")) as unknown;
 if(!value||typeof value!=="object"||Array.isArray(value))throw new Error("Invalid JWT document");
 return value as Record<string,unknown>;
}
export async function verifyIthuteIdToken(input:{
 token:string;issuer:string;audience:string;nonce:string;
},transport:typeof fetch=fetch,now=Math.floor(Date.now()/1000)){
 const issuer=new URL(input.issuer);
 if(issuer.protocol!=="https:"||issuer.username||issuer.password||issuer.search||issuer.hash)
  throw new Error("Invalid issuer");
 const parts=input.token.split(".");
 if(parts.length!==3||input.token.length>16000)throw new Error("Malformed ID token");
 const header=decodePart(parts[0]);
 if(header.alg!=="RS256"||typeof header.kid!=="string"||!header.kid||
    header.jku||header.jwk||header.x5u)throw new Error("Unsupported JWT header");
 const jwksUrl=new URL("/.well-known/jwks.json",issuer);
 const response=await transport(jwksUrl,{cache:"no-store",redirect:"error",signal:AbortSignal.timeout(5000)});
 if(!response.ok)throw new Error("Signing keys unavailable");
 const jwks=await response.json() as {keys?:Record<string,unknown>[]};
 if(!Array.isArray(jwks.keys)||jwks.keys.length>100)throw new Error("Invalid JWKS");
 const candidates=jwks.keys.filter(k=>k.kid===header.kid&&k.kty==="RSA"&&(!k.alg||k.alg==="RS256")&&(!k.use||k.use==="sig"));
 if(candidates.length!==1)throw new Error("Signing key not uniquely identified");
 const key=createPublicKey({key:candidates[0] as JsonWebKey,format:"jwk"});
 if(!verifySignature("RSA-SHA256",Buffer.from(parts[0]+"."+parts[1]),key,Buffer.from(parts[2],"base64url")))
  throw new Error("Invalid ID token signature");
 const claims=decodePart(parts[1]);
 if(claims.iss!==issuer.toString().replace(/\/$/,"")||claims.aud!==input.audience||
    claims.nonce!==input.nonce||typeof claims.sub!=="string"||!claims.sub||
    typeof claims.exp!=="number"||typeof claims.iat!=="number"||
    claims.exp<=now||claims.iat>now+30||claims.exp-claims.iat>86400)
  throw new Error("Invalid ID token claims");
 return {sub:claims.sub,iss:claims.iss,aud:claims.aud,exp:claims.exp};
}
