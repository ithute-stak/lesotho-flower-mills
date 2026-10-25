"use client";
import {useState} from "react";
type Section="Overview"|"Products"|"Businesses"|"Pricing";
type Product={id:string;name:string;sku:string;stock_unit:string};
type Business={id:string;display_name:string;customer_number:string};
type Book={id:string;name:string;code:string;active:boolean};
const sections:Section[]=["Overview","Products","Businesses","Pricing"];
export default function Admin(){
  const [section,setSection]=useState<Section>("Overview");
  const [token,setToken]=useState("");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [products,setProducts]=useState<Product[]>([]);
  const [businesses,setBusinesses]=useState<Business[]>([]);
  const [books,setBooks]=useState<Book[]>([]);
  const [sku,setSku]=useState("");const [name,setName]=useState("");const [unit,setUnit]=useState("bag");
  const [code,setCode]=useState("");const [bookName,setBookName]=useState("");
  const [error,setError]=useState("");const [message,setMessage]=useState("");
  async function call<T>(path:string,method="GET",body?:object,session=token):Promise<T>{
    const r=await fetch("/api/v1"+path,{method,headers:{"content-type":"application/json",...(session?{"authorization":"Bearer "+session}:{})},body:body?JSON.stringify(body):undefined,cache:"no-store"});
    const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==="string"?data.detail:"Request failed");return data as T;
  }
  async function load(sectionName:Section=section,session=token){
    setError("");try{
      if(sectionName==="Products")setProducts(await call<Product[]>("/products","GET",undefined,session));
      if(sectionName==="Businesses")setBusinesses(await call<Business[]>("/admin/businesses/pending","GET",undefined,session));
      if(sectionName==="Pricing")setBooks(await call<Book[]>("/admin/price-books","GET",undefined,session));
    }catch(e){setError(e instanceof Error?e.message:"Unable to load");}
  }
  async function login(e:React.FormEvent){e.preventDefault();setError("");try{const data=await call<{access_token:string}>("/auth/login","POST",{email,password},"");setToken(data.access_token);setPassword("");setMessage("Signed in. Access to staff features is permission controlled.");}catch(e){setError(e instanceof Error?e.message:"Sign in failed");}}
  async function createProduct(e:React.FormEvent){e.preventDefault();setError("");setMessage("");try{await call("/admin/products","POST",{sku,name,stock_unit:unit});setSku("");setName("");setMessage("Product created");await load("Products");}catch(e){setError(e instanceof Error?e.message:"Unable to save");}}
  async function createBook(e:React.FormEvent){e.preventDefault();setError("");setMessage("");try{await call("/admin/price-books","POST",{code,name:bookName});setCode("");setBookName("");setMessage("Inactive price book created");await load("Pricing");}catch(e){setError(e instanceof Error?e.message:"Unable to save");}}
  async function approve(id:string){if(!window.confirm("Confirm business verification was completed for this applicant?"))return;try{await call("/businesses/"+id+"/approve","POST");setMessage("Business marked approved");await load("Businesses");}catch(e){setError(e instanceof Error?e.message:"Approval failed");}}
  return <><header><small>LESOTHO FLOUR MILLS</small><h1>Operations Administration</h1></header><main>
  {!token?<section className="panel"><h2>Staff sign in</h2><p>Only provisioned staff accounts can administer company records.</p><form onSubmit={login}><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/><label>Password</label><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/><button>Sign in</button></form></section>:<>
    <nav aria-label="Administration sections">{sections.map(s=><button key={s} aria-current={section===s?"page":undefined} onClick={()=>{setSection(s);setError("");setMessage("");void load(s)}}>{s}</button>)}<button onClick={()=>{setToken("");setMessage("");setProducts([]);setBusinesses([]);setBooks([])}}>Sign out</button></nav>
    {section==="Overview"&&<div className="grid"><section className="panel"><h2>Products</h2><p>Maintain the authoritative catalogue.</p></section><section className="panel"><h2>Businesses</h2><p>Review new wholesale applications.</p></section><section className="panel"><h2>Price books</h2><p>Configure price schedules before publishing.</p></section></div>}
    {section==="Products"&&<><section className="panel"><h2>Add product</h2><form onSubmit={createProduct}><label>SKU</label><input value={sku} onChange={e=>setSku(e.target.value)} required/><label>Product name</label><input value={name} onChange={e=>setName(e.target.value)} required/><label>Stock unit</label><select value={unit} onChange={e=>setUnit(e.target.value)}><option value="bag">Bag</option><option value="kg">Kilogram</option><option value="unit">Unit</option></select><button>Create product</button></form></section><section className="panel"><h2>Product catalogue</h2><button onClick={()=>void load("Products")}>Refresh</button><ul className="listing">{products.map(p=><li key={p.id}><b>{p.name}</b><span>{p.sku} · {p.stock_unit}</span></li>)}</ul></section></>}
    {section==="Businesses"&&<section className="panel"><h2>Pending business applications</h2><p>Confirm registration evidence outside this screen before approval. Formal verification evidence workflow is still pending.</p><button onClick={()=>void load("Businesses")}>Refresh</button><ul className="listing">{businesses.map(b=><li key={b.id}><span>{b.display_name} · {b.customer_number}</span><button onClick={()=>void approve(b.id)}>Approve</button></li>)}</ul></section>}
    {section==="Pricing"&&<><section className="panel"><h2>Create price book</h2><p>Books are created inactive and cannot yet be published to customer checkout.</p><form onSubmit={createBook}><label>Code</label><input value={code} onChange={e=>setCode(e.target.value)} required/><label>Book name</label><input value={bookName} onChange={e=>setBookName(e.target.value)} required/><button>Create inactive book</button></form></section><section className="panel"><h2>Price books</h2><button onClick={()=>void load("Pricing")}>Refresh</button><ul className="listing">{books.map(b=><li key={b.id}><b>{b.name}</b><span>{b.code} · {b.active?"Active":"Inactive"}</span></li>)}</ul><p>Quantity-tier editing UI is the next step; its authenticated API is available.</p></section></>}
  </>}
  {error&&<p className="error" role="alert">{error}</p>}{message&&<p className="success" role="status">{message}</p>}
  </main></>;
}
