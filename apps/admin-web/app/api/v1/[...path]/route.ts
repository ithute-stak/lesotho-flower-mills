import {NextRequest,NextResponse} from "next/server";
export const runtime="nodejs";
export const dynamic="force-dynamic";
async function forward(request:NextRequest,path:string[]){
  const server=process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
  const target=new URL("/api/v1/"+path.map(encodeURIComponent).join("/"),server);target.search=request.nextUrl.search;
  const headers=new Headers();const type=request.headers.get("content-type");if(type)headers.set("content-type",type);const auth=request.headers.get("authorization");if(auth)headers.set("authorization",auth);
  try{const r=await fetch(target,{method:request.method,headers,body:request.method==="GET"?undefined:await request.text(),redirect:"manual",cache:"no-store"});return new NextResponse(await r.text(),{status:r.status,headers:{"content-type":r.headers.get("content-type")??"application/json","cache-control":"no-store"}})}
  catch{return NextResponse.json({detail:"Service unavailable"},{status:503})}
}
export async function GET(req:NextRequest,ctx:{params:Promise<{path:string[]}>}){return forward(req,(await ctx.params).path)}
export async function POST(req:NextRequest,ctx:{params:Promise<{path:string[]}>}){return forward(req,(await ctx.params).path)}
