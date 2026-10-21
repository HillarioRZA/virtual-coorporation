"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Cpu,
  Plus,
  Trash2,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Terminal,
  Shield,
  Layers,
  Search,
  ExternalLink,
  Lock,
} from "lucide-react";
import { getAuthHeaders } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface MCPTool {
  name: string;
  description?: string;
}

interface MCPServer {
  id: string;
  name: string;
  transport: string;
  command_or_url: string;
  status: string;
  tools: MCPTool[];
  active_agents: string[];
  created_at: string;
}

export default function MCPPage() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [conflictError, setConflictError] = useState<string | null>(null);

  // Form State
  const [formName, setFormName] = useState("");
  const [formTransport, setFormTransport] = useState("stdio");
  const [formCommand, setFormCommand] = useState("npx -y @modelcontextprotocol/server-github");
  const [formEnv, setFormEnv] = useState('{"GITHUB_TOKEN": ""}');
  const [dryRunLoading, setDryRunLoading] = useState(false);
  const [dryRunResult, setDryRunResult] = useState<any | null>(null);
  const [installLoading, setInstallLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchServers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/mcp/servers`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setServers(data);
      }
    } catch (err) {
      console.error("Gagal mengambil server MCP:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  const handleDryRun = async () => {
    setDryRunLoading(true);
    setFormError(null);
    setDryRunResult(null);
    try {
      let parsedEnv = {};
      if (formEnv.trim()) {
        parsedEnv = JSON.parse(formEnv);
      }
      const res = await fetch(`${API_BASE}/mcp/dry-run`, {
        method: "POST",
        headers: getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          command_or_url: formCommand,
          transport: formTransport,
          env_vars: parsedEnv,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Gagal menguji koneksi server MCP.");
      setDryRunResult(data);
    } catch (err: any) {
      setFormError(err.message || "Gagal melakukan dry-run.");
    } finally {
      setDryRunLoading(false);
    }
  };

  const handleInstall = async (e: React.FormEvent) => {
    e.preventDefault();
    setInstallLoading(true);
    setFormError(null);
    try {
      let parsedEnv = {};
      if (formEnv.trim()) {
        parsedEnv = JSON.parse(formEnv);
      }
      const res = await fetch(`${API_BASE}/mcp/install`, {
        method: "POST",
        headers: getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          name: formName.trim().toLowerCase(),
          command_or_url: formCommand,
          transport: formTransport,
          env_vars: parsedEnv,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Gagal menginstal server MCP.");
      setIsModalOpen(false);
      setFormName("");
      setDryRunResult(null);
      fetchServers();
    } catch (err: any) {
      setFormError(err.message || "Gagal menginstal server MCP.");
    } finally {
      setInstallLoading(false);
    }
  };

  const handleDelete = async (server: MCPServer) => {
    if (!confirm(`Hapus server MCP [${server.name}]?`)) return;
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${server.id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });
      if (res.status === 409) {
        const data = await res.json();
        setConflictError(data.detail || "Server MCP ini masih digunakan oleh agen aktif!");
        return;
      }
      if (!res.ok) throw new Error("Gagal menghapus server MCP.");
      fetchServers();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white font-mono">
              MCP SERVER HUB
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple-500/10 text-purple-300 border border-purple-500/20">
              Protocol v2024-11
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Integrasi server Model Context Protocol (MCP) terisolasi on-demand dengan proteksi referensial anti-delete.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchServers}
            className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white transition-all"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => {
              setIsModalOpen(true);
              setFormError(null);
              setDryRunResult(null);
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-medium transition-all shadow-lg shadow-purple-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Pasang Server MCP</span>
          </button>
        </div>
      </div>

      {/* Dependency Guard Alert Modal */}
      {conflictError && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md rounded-2xl bg-[#0e0f17] border border-rose-500/30 p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-rose-400">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h3 className="font-semibold text-sm text-white">Guardrail Proteksi Ketergantungan</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{conflictError}</p>
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setConflictError(null)}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-xs text-white transition-all font-medium"
              >
                Saya Mengerti
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Servers Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 rounded-2xl bg-white/5 border border-white/5 animate-pulse" />
          ))}
        </div>
      ) : servers.length === 0 ? (
        <div className="text-center py-16 rounded-2xl bg-white/[0.02] border border-dashed border-white/10 space-y-3">
          <Cpu className="w-8 h-8 text-slate-500 mx-auto" />
          <h3 className="text-sm font-medium text-slate-300">Belum Ada Server MCP Terpasang</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Pasang server MCP (seperti GitHub, Postgres, atau Slack) untuk memperkaya perkakas yang dapat diakses oleh peran karyawan AI.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {servers.map((server) => (
            <div
              key={server.id}
              className="rounded-2xl bg-white/[0.03] border border-white/10 p-5 flex flex-col justify-between hover:border-purple-500/30 transition-all space-y-4 shadow-xl"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      {server.transport}
                    </span>
                    <h3 className="font-bold text-base text-white mt-1.5">{server.name}</h3>
                  </div>
                  <button
                    onClick={() => handleDelete(server)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                    title="Hapus Server"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 font-mono text-[11px] text-slate-400 truncate">
                  {server.command_or_url}
                </div>

                {/* Active Agents Badge */}
                <div>
                  <label className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                    Penggunaan Izin Agen
                  </label>
                  {server.active_agents?.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {server.active_agents.map((agent) => (
                        <span
                          key={agent}
                          className="px-2 py-0.5 rounded-md text-[10px] bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-medium"
                        >
                          {agent}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-[11px] text-slate-500 italic">Belum ada agen yang memegang izin</span>
                  )}
                </div>

                {/* Tools Manifest */}
                <div>
                  <label className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                    Perkakas ({server.tools?.length || 0})
                  </label>
                  <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto pr-1">
                    {server.tools?.map((tool) => (
                      <span
                        key={tool.name}
                        title={tool.description || ""}
                        className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-mono text-slate-300"
                      >
                        {tool.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  Active On-Demand
                </span>
                <Link
                  href="/organization"
                  className="text-purple-400 hover:text-purple-300 transition-colors flex items-center gap-1"
                >
                  Beri Izin Agen &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Install Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
          <div className="w-full max-w-lg rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative space-y-4">
            <h3 className="text-base font-semibold text-white">Pasang Server Model Context Protocol (MCP)</h3>
            <p className="text-xs text-slate-400">
              Daftarkan endpoint tool eksekusi eksternal ke dalam pool permission korporat.
            </p>

            {formError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleInstall} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Nama Server</label>
                <input
                  type="text"
                  required
                  placeholder="github"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Transport</label>
                <select
                  value={formTransport}
                  onChange={(e) => setFormTransport(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-purple-500"
                >
                  <option value="stdio" className="bg-[#0c0d14]">stdio (Subprocess / Docker On-Demand)</option>
                  <option value="sse" className="bg-[#0c0d14]">sse (Remote Server-Sent Events URL)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Command / URL</label>
                <input
                  type="text"
                  required
                  placeholder="npx -y @modelcontextprotocol/server-github"
                  value={formCommand}
                  onChange={(e) => setFormCommand(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Environment Variables (JSON Kredensial - Terenkripsi AES-GCM)
                </label>
                <textarea
                  rows={2}
                  placeholder='{"GITHUB_TOKEN": "ghp_xxx"}'
                  value={formEnv}
                  onChange={(e) => setFormEnv(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-purple-500"
                />
              </div>

              {dryRunResult && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs space-y-1.5">
                  <div className="font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Handshake Sukses: {dryRunResult.tools_count} perkakas terdeteksi!
                  </div>
                  <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                    {dryRunResult.tools.map((t: any) => (
                      <span key={t.name} className="px-2 py-0.5 rounded bg-black/40 text-[10px] font-mono">
                        {t.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-2 flex items-center justify-between">
                <button
                  type="button"
                  onClick={handleDryRun}
                  disabled={dryRunLoading}
                  className="px-3.5 py-2 text-xs font-medium text-purple-300 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 rounded-xl transition-all disabled:opacity-50"
                >
                  {dryRunLoading ? "Menguji..." : "Uji Koneksi (Dry-Run)"}
                </button>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    disabled={installLoading}
                    className="px-4 py-2 text-xs font-medium text-white bg-purple-600 hover:bg-purple-500 rounded-xl transition-all disabled:opacity-50"
                  >
                    {installLoading ? "Memasang..." : "Pasang Server"}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
