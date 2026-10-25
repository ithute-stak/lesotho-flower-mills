import {NextRequest,NextResponse} from "next/server";
export const runtime="nodejs";export const dynamic="force-dynamic";
async function forward(req:NextRequest,path:string[]){
 const target=new URL("/api/v1/"+path.map(encodeURIComponent).join("/"),process.env.API_INTERNAL_URL??"http://127.0.0.1:8000");target.search=req.nextUrl.search;
 const headers=new Headers();for(const key of ["authorization","content-type"]){const value=req.headers.get(key);if(value)headers.set(key,value)}
 try{const response=await fetch(target,{method:req.method,headers,body:req.method==="GET"?undefined:await req.text(),cache:"no-store",redirect:"manual"});return new NextResponse(await response.text(),{status:response.status,headers:{"content-type":response.headers.get("content-type")??"application/json","cache-control":"no-store"}})}
 catch{return NextResponse.json({detail:"Server unavailable"},{status:503})}
}
export async function GET(req:NextRequest,c:{params:Promise<{path:string[]}>}){return forward(req,(await c.params).path)}
export async function POST(req:NextRequest,c:{params:Promise<{path:string[]}>}){return forward(req,(await c.params).path)}
