import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { Sparkles, Settings, LayoutGrid, ShieldCheck, Terminal, Network, Activity, Building2, Cpu, BookOpen } from "lucide-react";
import AuthGateModal from "../components/auth/AuthGateModal";

export const metadata: Metadata = {
  title: "Venture Incubator Hub | Obsidian Studio Cockpit",
  description: "Autonomous Multi-Agent Startup Builder & Orchestration Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#050507] text-slate-100 flex flex-col relative selection:bg-white/20 selection:text-white">
        {/* Dynamic Telegram Security Gate Modal */}
        <AuthGateModal />

        {/* Ambient Liquid Fluid Mesh Background Layers */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
          <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-indigo-500/10 blur-[120px] animate-liquid-1" />
          <div className="absolute top-1/3 -right-40 w-[30rem] h-[30rem] rounded-full bg-cyan-500/10 blur-[140px] animate-liquid-2" />
          <div className="absolute -bottom-40 left-1/3 w-96 h-96 rounded-full bg-purple-500/10 blur-[130px] animate-liquid-1" />
          {/* Subtle noise grid texture */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
        </div>

        {/* Floating Obsidian Liquid Glass Header */}
        <header className="sticky top-0 z-40 px-4 md:px-8 py-3.5 border-b border-white/10 bg-[#050507]/80 backdrop-blur-2xl transition-all">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="w-9 h-9 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center shadow-lg shadow-white/5 group-hover:scale-105 group-hover:border-white/40 transition-all">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-sm tracking-tight text-white font-mono">
                    VENTURE HUB
                  </span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-white/10 text-slate-300 border border-white/15">
                    Studio
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-sans hidden sm:block">
                  Obsidian Liquid Multi-Agent Orchestrator
                </p>
              </div>
            </Link>

            {/* Navigation links & System status */}
            <nav className="flex items-center space-x-2 md:space-x-3">
              <Link
                href="/"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <LayoutGrid className="w-3.5 h-3.5 text-slate-400" />
                <span className="hidden sm:inline">Portfolio</span>
              </Link>

              <Link
                href="/office"
                className="hidden lg:flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <Building2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Office HQ</span>
              </Link>

              <Link
                href="/organization"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <Network className="w-3.5 h-3.5 text-slate-400" />
                <span>Organization</span>
              </Link>

              <Link
                href="/mcp"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span>MCP Hub</span>
              </Link>

              <Link
                href="/skills"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                <span>Skills</span>
              </Link>

              <Link
                href="/analytics"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <Activity className="w-3.5 h-3.5 text-amber-400" />
                <span>CFO & Router</span>
              </Link>

              <Link
                href="/settings"
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all"
              >
                <Settings className="w-3.5 h-3.5 text-slate-400" />
                <span>Settings</span>
              </Link>

              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="hidden md:inline">Orchestrator Online</span>
                <span className="md:hidden">v1.0</span>
              </div>
            </nav>
          </div>
        </header>

        {/* Main Viewport Content */}
        <main className="flex-1 flex flex-col relative z-10">{children}</main>
      </body>
    </html>
  );
}
