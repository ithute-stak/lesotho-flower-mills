import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

async function forward(request: NextRequest, parts: string[]) {
  const server = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
  const target = new URL("/api/v1/" + parts.map(encodeURIComponent).join("/"), server);
  target.search = request.nextUrl.search;
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const authorization = request.headers.get("authorization");
  if (authorization) headers.set("authorization", authorization);
  try {
    const response = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      redirect: "manual",
      cache: "no-store",
    });
    const data = await response.text();
    return new NextResponse(data, {
      status: response.status,
      headers: {"content-type": response.headers.get("content-type") ?? "application/json", "cache-control": "no-store"},
    });
  } catch {
    return NextResponse.json({detail: "Service unavailable"}, {status: 503});
  }
}
export async function GET(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const {path} = await context.params; return forward(request,path);
}
export async function POST(request: NextRequest, context: {params: Promise<{path: string[]}>}) {
  const {path} = await context.params; return forward(request,path);
}
