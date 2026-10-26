import {NextRequest,NextResponse} from "next/server";
import {ithuteAuthReadiness} from "../../../../../lib/ithute-auth-config";
export const runtime="nodejs";
export const dynamic="force-dynamic";
export async function GET(_request:NextRequest,{params}:{params:Promise<{action:string}>}){
 const {action}=await params;
 if(action==="status")return NextResponse.json(ithuteAuthReadiness(),{headers:{"cache-control":"no-store"}});
 if(action==="login"||action==="callback")return NextResponse.json(
  {detail:"Ithute Auth sign-in is not enabled. Use existing local login."},
  {status:503,headers:{"cache-control":"no-store"}}
 );
 return NextResponse.json({detail:"Not found"},{status:404});
}
export async function POST(_request:NextRequest,{params}:{params:Promise<{action:string}>}){
 const {action}=await params;
 if(action==="logout")return NextResponse.json({detail:"Ithute Auth session is not active"},{status:503});
 return NextResponse.json({detail:"Not found"},{status:404});
}
