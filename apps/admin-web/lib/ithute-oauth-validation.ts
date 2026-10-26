/** Callback preflight joins protected transaction and response checks without issuing a session. */
import "server-only";
import {unsealOAuthTransaction} from "./ithute-oauth-transaction";
import {validateIthuteCallback} from "./ithute-oauth-callback";
export function prepareIthuteCallback(query:URLSearchParams,sealed:string|undefined,secret:string){
 if(!sealed)return {ok:false as const,reason:"missing_transaction"};
 const tx=unsealOAuthTransaction(sealed,secret);
 if(!tx)return {ok:false as const,reason:"invalid_transaction"};
 const checked=validateIthuteCallback(query,tx.state,secret);
 if(!checked.ok)return checked;
 return {ok:true as const,code:checked.code,verifier:tx.verifier,nonce:tx.nonce,state:tx.state};
}
