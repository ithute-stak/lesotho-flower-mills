import type { ReactNode } from "react";
import "./style.css";

export const metadata = { title: "Lesotho Flour Mills", description: "Customer ordering portal" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
