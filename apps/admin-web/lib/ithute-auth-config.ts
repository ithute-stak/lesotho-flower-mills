/** Server-only preflight. This does not authenticate users or activate OAuth. */
import "server-only";
export type IthuteReadiness={ready:false;blockers:string[];enabled:false};
export function ithuteAuthReadiness(env:NodeJS.ProcessEnv=process.env):IthuteReadiness {
 const issuer=env.ITHUTE_AUTH_ISSUER?.trim()??"";
 const clientId=env.ITHUTE_AUTH_CLIENT_ID?.trim()??"";
 const callback=env.ITHUTE_AUTH_CALLBACK_URL?.trim()??"";
 const secret=env.ITHUTE_AUTH_SESSION_SECRET??"";
 const blockers:string[]=[];
 for(const [name,value] of [["issuer",issuer],["client_id",clientId],["callback",callback]])if(!value)blockers.push("missing_"+name);
 for(const [name,value] of [["issuer",issuer],["callback",callback]]){
  if(!value)continue;
  try {const url=new URL(value);if(url.protocol!=="https:"||url.username||url.password||url.hash||url.search)blockers.push("invalid_"+name);}
  catch{blockers.push("invalid_"+name);}
 }
 if(callback){
  try{if(new URL(callback).pathname!=="/api/auth/ithute/callback")blockers.push("callback_path_mismatch");}
  catch{/* invalid callback reported above */}
 }
 if(secret.length<32)blockers.push("missing_strong_session_secret");
 // Registration, SDK availability and live revocation still need independent evidence.
 blockers.push("client_registration_unverified","central_session_verification_unverified","oauth_sdk_not_integrated");
 return {ready:false,enabled:false,blockers};
}
