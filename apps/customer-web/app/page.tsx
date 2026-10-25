"use client";
import { useEffect, useState } from "react";
import { api, type Product } from "./api";
const tabs = ["Home","Shop","Orders","Account"] as const;
type Tab = typeof tabs[number];
type AuthMode = "register"|"login";
type Quote = {id:string;quotation_number:string;status:string;subtotal:string;currency:string};
export default function Home(){
  const [tab,setTab]=useState<Tab>("Home");
  const [products,setProducts]=useState<Product[]>([]);
  const [quantities,setQuantities]=useState<Record<string,number>>({});
  const [quotes,setQuotes]=useState<Quote[]>([]);
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(false);
  const [authMode,setAuthMode]=useState<AuthMode>("register");
  const [name,setName]=useState("");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [kind,setKind]=useState<"individual"|"business">("individual");
  const [notice,setNotice]=useState("");
  useEffect(()=>{if(tab!=="Shop")return;let alive=true;setLoading(true);setError("");api<Product[]>("/api/v1/products").then(items=>{if(alive)setProducts(items)}).catch((e:Error)=>{if(alive)setError(e.message)}).finally(()=>{if(alive)setLoading(false)});return()=>{alive=false}},[tab]);
  async function requestQuote(){setError("");setNotice("");setLoading(true);try{
    const token=sessionStorage.getItem("lfm_access_token");
    if(!token)throw new Error("Please sign in through Account first.");
    const items=Object.entries(quantities).filter(([,qty])=>qty>0).map(([product_id,quantity])=>({product_id,quantity}));
    if(items.length===0)throw new Error("Choose at least one product quantity.");
    const response=await api<{quotation_number:string}>("/api/v1/my/quotations",{method:"POST",
      headers:{"Authorization":"Bearer "+token},body:JSON.stringify({items})});
    setNotice("Draft quotation created: "+response.quotation_number);
    setQuantities({});
  }catch(e){setError(e instanceof Error?e.message:"Quotation could not be created");}finally{setLoading(false)}}
  async function loadQuotes(){setError("");try{
    const token=sessionStorage.getItem("lfm_access_token");
    if(!token)throw new Error("Please sign in through Account first.");
    const response=await api<Quote[]>("/api/v1/my/quotations",{headers:{"Authorization":"Bearer "+token}});
    setQuotes(response);
  }catch(e){setError(e instanceof Error?e.message:"Could not load quotations");}}
  async function submit(event:React.FormEvent<HTMLFormElement>){
    event.preventDefault();setNotice("");setError("");setLoading(true);
    try{
      if(authMode==="register"){
        await api("/api/v1/auth/register",{method:"POST",body:JSON.stringify({name,email,password,customer_type:kind})});
        setNotice(kind==="business"?"Business account submitted. Approval is required before wholesale privileges.":"Account created. You can now sign in.");setAuthMode("login");setPassword("");
      } else {
        const result=await api<{access_token:string}>("/api/v1/auth/login",{method:"POST",body:JSON.stringify({email,password})});
        // Temporary session-only storage; production will use BFF/httpOnly session cookies.
        sessionStorage.setItem("lfm_access_token",result.access_token);
        setPassword("");setNotice("Signed in for this browser session.");
      }
    }catch(e){setError(e instanceof Error?e.message:"Something went wrong");}finally{setLoading(false)}
  }
  return <main className="app">
    <header><small>LESOTHO FLOUR MILLS</small><h1>{tab==="Home"?"Welcome":tab}</h1><p className="subtitle">Shop, quote, order and manage your account.</p></header>
    {tab==="Home"&&<section className="panel hero"><span className="eyebrow">CUSTOMER PORTAL</span><h2>From our mills to your doorstep.</h2><p>Discover products and request competitive quantity-based prices.</p><button onClick={()=>setTab("Shop")}>Explore products</button></section>}
    {tab==="Shop"&&<section className="panel"><h2>Available products</h2><p>Only products published by LFM will appear below. Pricing is not displayed until approved price books are connected.</p>
      {loading&&<p role="status">Loading catalogue…</p>}{!loading&&!error&&products.length===0&&<p>No products are published yet.</p>}
      <div className="product-grid">{products.map(p=><article className="product-card" key={p.id}><span className="eyebrow">{p.sku}</span><h3>{p.name}</h3><p>Unit: {p.stock_unit}</p><span className="subtle">Price confirmed through approved quotation</span><label htmlFor={"qty-"+p.id}>Quantity</label><input id={"qty-"+p.id} type="number" min={0} max={1000000} value={quantities[p.id]??0} onChange={e=>setQuantities(prev=>({...prev,[p.id]:Math.max(0,Math.floor(Number(e.target.value)||0))}))}/></article>)}</div><button type="button" disabled={loading||products.length===0} onClick={()=>void requestQuote()}>Request draft quotation</button><p>Draft requests do not reserve stock or confirm an order.</p></section>}
    {tab==="Orders"&&<section className="panel"><h2>My quotations</h2><p>Draft quotations are estimates only, not confirmed orders. Payments and delivery tracking will be added later.</p><button onClick={()=>void loadQuotes()}>Load my quotations</button><ul className="listing">{quotes.map(q=><li key={q.id}><strong>{q.quotation_number}</strong> — {q.status} · {q.currency} {q.subtotal}</li>)}</ul><button onClick={()=>setTab("Account")}>Manage account</button></section>}
    {tab==="Account"&&<section className="panel"><h2>{authMode==="register"?"Create an account":"Sign in"}</h2><p>Individuals can create customer accounts. Business profiles require staff approval.</p>
      <div className="switcher"><button type="button" aria-pressed={authMode==="register"} onClick={()=>{setAuthMode("register");setError("");setNotice("")}}>Register</button><button type="button" aria-pressed={authMode==="login"} onClick={()=>{setAuthMode("login");setError("");setNotice("")}}>Sign in</button></div>
      <form onSubmit={submit}>
        {authMode==="register"&&<><label htmlFor="account-kind">Account type</label><select id="account-kind" value={kind} onChange={e=>setKind(e.target.value as "individual"|"business")}><option value="individual">Individual</option><option value="business">Business / Distributor</option></select><label htmlFor="full-name">Name or business name</label><input id="full-name" value={name} onChange={e=>setName(e.target.value)} required minLength={2} maxLength={200}/></>}
        <label htmlFor="email">Email address</label><input id="email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required/>
        <label htmlFor="password">Password</label><input id="password" type="password" autoComplete={authMode==="register"?"new-password":"current-password"} minLength={authMode==="register"?12:1} value={password} onChange={e=>setPassword(e.target.value)} required/>
        <button disabled={loading} type="submit">{loading?"Working…":authMode==="register"?"Create account":"Sign in"}</button>
      </form></section>}
    {error&&<p className="error" role="alert">{error}</p>}{notice&&<p className="notice" role="status">{notice}</p>}
    <nav aria-label="Bottom navigation">{tabs.map(t=><button key={t} aria-current={tab===t?"page":undefined} onClick={()=>{setTab(t);setError("");setNotice("")}}>{t}</button>)}</nav>
  </main>
}
