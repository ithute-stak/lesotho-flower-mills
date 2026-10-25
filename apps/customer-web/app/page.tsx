"use client";
import { useState } from "react";

const tabs = ["Home", "Shop", "Orders", "Account"] as const;
type Tab = typeof tabs[number];

export default function Home() {
  const [tab, setTab] = useState<Tab>("Home");
  return <main className="app">
    <header><small>LESOTHO FLOUR MILLS</small><h1>{tab === "Home" ? "Welcome" : tab}</h1></header>
    {tab === "Home" && <section className="panel"><h2>Order with confidence</h2><p>Explore LFM products, request quotations and track fulfilment.</p><button onClick={() => setTab("Shop")}>Browse products</button></section>}
    {tab === "Shop" && <section className="panel"><h2>Product catalogue</h2><p>Verified LFM products and quantity-based pricing will appear here when the catalogue API is connected.</p></section>}
    {tab === "Orders" && <section className="panel"><h2>Your orders</h2><p>Sign-in, orders and delivery tracking will be available in the next phases.</p></section>}
    {tab === "Account" && <section className="panel"><h2>Customer account</h2><p>Individual and approved business profiles will be supported.</p></section>}
    <nav aria-label="Bottom navigation">{tabs.map(t => <button key={t} aria-current={tab === t ? "page" : undefined} onClick={() => setTab(t)}>{t}</button>)}</nav>
  </main>;
}
