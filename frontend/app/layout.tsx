import Link from "next/link";
import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "ARGOS",
  description: "Adaptive Reasoning & Global Ontology System",
};

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/query", label: "Query" },
  { href: "/graph", label: "Graph" },
  { href: "/alerts", label: "Alerts" },
  { href: "/scenarios", label: "Scenarios" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="relative mx-auto min-h-screen max-w-[1600px] px-4 pb-10 pt-5 md:px-6">
          <header className="panel sticky top-4 z-30 mb-6 flex items-center justify-between gap-4 px-5 py-4">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-500/30 bg-cyan-400/10 font-display text-lg tracking-[0.24em] text-cyan-200">
                AR
              </div>
              <div>
                <p className="font-display text-xl tracking-[0.24em] text-white">ARGOS</p>
                <p className="eyebrow">Adaptive Reasoning & Global Ontology System</p>
              </div>
            </div>
            <nav className="hidden items-center gap-2 lg:flex">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400/40 hover:bg-white/5 hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="data-pill hidden md:inline-flex">India Strategic Lens Active</div>
          </header>
          <main className="flex flex-col gap-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
