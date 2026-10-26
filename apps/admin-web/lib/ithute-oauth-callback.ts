/** Validate OAuth callback input before any exchange or session issuance. */
import "server-only";
import {verifyOAuthState} from "./ithute-oauth-pkce";
export type CallbackResult={ok:true;code:string}|{ok:false;reason:string};
export function validateIthuteCallback(params:URLSearchParams,expectedState:string|undefined,secret:string):CallbackResult {
 if(params.has("error"))return {ok:false,reason:"provider_returned_error"};
 if(params.getAll("state").length!==1||params.getAll("code").length!==1)return {ok:false,reason:"invalid_callback_parameters"};
 const returnedState=params.get("state")??"";
 const code=params.get("code")??"";
 if(!expectedState||returnedState!==expectedState||!verifyOAuthState(returnedState,secret))
  return {ok:false,reason:"state_verification_failed"};
 if(!code||code.length>4096)return {ok:false,reason:"invalid_authorization_code"};
 return {ok:true,code};
}
