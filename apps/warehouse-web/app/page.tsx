"use client";
import {useState} from "react";
type Section="Stock"|"Receive"|"Transfer"|"Adjust"|"History";
type Balance={warehouse_id:string;product_id:string;on_hand:number;reserved:number;available:number};
type Movement={id:string;warehouse_id:string;product_id:string;delta:number;movement_type:string;reference:string;created_at:string};
const tabs:Section[]=["Stock","Receive","Transfer","Adjust","History"];
export default function Warehouse(){
 const [token,setToken]=useState("");const [email,setEmail]=useState("");const [password,setPassword]=useState("");
 const [tab,setTab]=useState<Section>("Stock");const [balances,setBalances]=useState<Balance[]>([]);
 const [history,setHistory]=useState<Movement[]>([]);const [warehouse,setWarehouse]=useState("");const [destination,setDestination]=useState("");
 const [product,setProduct]=useState("");const [quantity,setQuantity]=useState(1);const [reference,setReference]=useState("");
 const [direction,setDirection]=useState("increase");const [message,setMessage]=useState("");const [error,setError]=useState("");const [busy,setBusy]=useState(false);
 async function api<T>(path:string,method="GET",body?:object,auth=token):Promise<T>{
 const response=await fetch("/api/v1"+path,{method,headers:{"content-type":"application/json",...(auth?{"authorization":"Bearer "+auth}:{})},body:body?JSON.stringify(body):undefined,cache:"no-store"});
 const value=await response.json();if(!response.ok)throw new Error(typeof value.detail==="string"?value.detail:"Request failed");return value as T;
 }
 async function login(e:React.FormEvent){e.preventDefault();setError("");setBusy(true);try{const response=await api<{access_token:string}>("/auth/login","POST",{email,password},"");await api("/admin/inventory/balances","GET",undefined,response.access_token);setToken(response.access_token);setPassword("");setMessage("Signed in with staff access");}catch(e){setError(e instanceof Error?e.message:"Login failed")}finally{setBusy(false)}}
 async function load(current:Section=tab){setError("");try{if(current==="Stock")setBalances(await api<Balance[]>("/admin/inventory/balances"));if(current==="History")setHistory(await api<Movement[]>("/admin/warehouse/movements"));}catch(e){setError(e instanceof Error?e.message:"Unable to load")}}
 async function post(e:React.FormEvent){e.preventDefault();setBusy(true);setError("");setMessage("");try{
 const base={operation_key:crypto.randomUUID(),warehouse_id:warehouse,product_id:product,quantity,reference};
 if(!Number.isInteger(quantity)||quantity<1)throw new Error("Quantity must be a positive whole number");
 if(!window.confirm("Post this stock movement to the permanent warehouse journal?"))return;
 if(tab==="Receive")await api("/admin/warehouse/receipts","POST",base);
 if(tab==="Adjust")await api("/admin/warehouse/adjustments","POST",{...base,direction});
 if(tab==="Transfer")await api("/admin/warehouse/transfers","POST",{operation_key:base.operation_key,from_warehouse_id:warehouse,to_warehouse_id:destination,product_id:product,quantity,reference});
 setMessage("Stock operation posted");setQuantity(1);setReference("");
 }catch(e){setError(e instanceof Error?e.message:"Posting failed")}finally{setBusy(false)}}
 return <><header><small>LESOTHO FLOUR MILLS</small><h1>Warehouse Operations</h1></header><main>
 {!token?<section className="panel"><h2>Staff login</h2><form onSubmit={login}><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/><label>Password</label><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/><button disabled={busy}>Sign in</button></form></section>:<>
 <nav aria-label="Warehouse sections">{tabs.map(t=><button aria-current={t===tab?"page":undefined} key={t} onClick={()=>{setTab(t);void load(t)}}>{t}</button>)}<button onClick={()=>{setToken("");setBalances([]);setHistory([])}}>Sign out</button></nav>
 {tab==="Stock"&&<section className="panel"><h2>Stock availability</h2><button onClick={()=>void load("Stock")}>Refresh balances</button><div className="table-wrap"><table><thead><tr><th>Warehouse ID</th><th>Product ID</th><th>On hand</th><th>Reserved</th><th>Available</th></tr></thead><tbody>{balances.map(b=><tr key={b.warehouse_id+b.product_id}><td>{b.warehouse_id}</td><td>{b.product_id}</td><td>{b.on_hand}</td><td>{b.reserved}</td><td>{b.available}</td></tr>)}</tbody></table></div></section>}
 {tab==="History"&&<section className="panel"><h2>Stock movement journal</h2><button onClick={()=>void load("History")}>Refresh movements</button><div className="table-wrap"><table><thead><tr><th>Time</th><th>Type</th><th>Quantity delta</th><th>Reference</th><th>Warehouse</th></tr></thead><tbody>{history.map(m=><tr key={m.id}><td>{new Date(m.created_at).toLocaleString()}</td><td>{m.movement_type}</td><td>{m.delta}</td><td>{m.reference}</td><td>{m.warehouse_id}</td></tr>)}</tbody></table></div></section>}
 {["Receive","Transfer","Adjust"].includes(tab)&&<section className="panel"><h2>{tab} stock</h2><p>Every confirmed operation is recorded in the stock journal. Use approved source references.</p><form onSubmit={post}><label>Warehouse ID</label><input value={warehouse} onChange={e=>setWarehouse(e.target.value)} placeholder="Warehouse UUID" required/>{tab==="Transfer"&&<><label>Destination warehouse ID</label><input value={destination} onChange={e=>setDestination(e.target.value)} required/></>}<label>Product ID</label><input value={product} onChange={e=>setProduct(e.target.value)} placeholder="Product UUID" required/><label>Quantity (whole bags/units)</label><input type="number" min={1} step={1} value={quantity} onChange={e=>setQuantity(Number(e.target.value))} required/>{tab==="Adjust"&&<><label>Adjustment direction</label><select value={direction} onChange={e=>setDirection(e.target.value)}><option value="increase">Increase</option><option value="decrease">Decrease</option></select></>}<label>Source document / reason</label><input value={reference} onChange={e=>setReference(e.target.value)} required/><button disabled={busy}>Post {tab.toLowerCase()}</button></form></section>}
 </>}
 {error&&<p role="alert" className="error">{error}</p>}{message&&<p role="status" className="ok">{message}</p>}
 </main></>
}
