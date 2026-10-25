"use client";
import {useState} from "react";
type Assignment={id:string;status:string;created_at:string;order_number:string;vehicle_registration:string};
export default function Driver(){
 const [token,setToken]=useState("");const [email,setEmail]=useState("");const [password,setPassword]=useState("");
 const [tab,setTab]=useState<"deliveries"|"account">("deliveries");
 const [items,setItems]=useState<Assignment[]>([]);const [error,setError]=useState("");const [notice,setNotice]=useState("");
 async function api<T>(path:string,method="GET",body?:object,auth=token):Promise<T>{
  const r=await fetch("/api/v1"+path,{method,headers:{"content-type":"application/json",...(auth?{"authorization":"Bearer "+auth}:{})},body:body?JSON.stringify(body):undefined,cache:"no-store"});
  const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==="string"?data.detail:"Request failed");return data as T;
 }
 async function login(e:React.FormEvent){e.preventDefault();setError("");try{
 const response=await api<{access_token:string}>("/auth/login","POST",{email,password},"");
 const assigned=await api<Assignment[]>("/driver/assignments","GET",undefined,response.access_token);
 setItems(assigned);setToken(response.access_token);setPassword("");setNotice("Signed in.");
 }catch(e){setError(e instanceof Error?e.message:"Sign in failed")}}
 async function refresh(){setError("");try{setItems(await api<Assignment[]>("/driver/assignments"))}catch(e){setError(e instanceof Error?e.message:"Refresh failed")}}
 return <><header><small>LESOTHO FLOUR MILLS</small><h1>Driver Portal</h1></header><main>
 {!token?<section className="panel"><h2>Driver sign in</h2><p>Your account must be registered as an active driver by authorised staff.</p><form onSubmit={login}><label>Email</label><input type="email" required value={email} onChange={e=>setEmail(e.target.value)}/><label>Password</label><input type="password" required value={password} onChange={e=>setPassword(e.target.value)}/><button>Sign in</button></form></section>:<>
 {tab==="deliveries"?<section className="panel"><h2>My deliveries</h2><button onClick={()=>void refresh()}>Refresh assignments</button>{items.length===0?<p>No assigned deliveries yet.</p>:items.map(item=><div className="entry" key={item.id}><strong>{item.order_number}</strong><p>Vehicle: {item.vehicle_registration}</p><p>Status: {item.status}</p><small>Assigned: {new Date(item.created_at).toLocaleString()}</small></div>)}<p>Dispatch, GPS tracking and customer handover are not enabled yet.</p></section>:<section className="panel"><h2>Driver account</h2><p>Authenticated driver access is active. Location tracking is off.</p><button onClick={()=>{setToken("");setItems([]);setNotice("")}}>Sign out</button></section>}
 <nav aria-label="Driver tabs"><button aria-current={tab==="deliveries"?"page":undefined} onClick={()=>setTab("deliveries")}>Deliveries</button><button aria-current={tab==="account"?"page":undefined} onClick={()=>setTab("account")}>Account</button></nav>
 </>}
 {error&&<p role="alert" className="error">{error}</p>}{notice&&<p role="status" className="success">{notice}</p>}
 </main></>
}
