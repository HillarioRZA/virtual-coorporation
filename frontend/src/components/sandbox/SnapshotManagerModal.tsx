"use client";

import { useEffect, useState } from "react";
import { History, Plus, RotateCcw, Trash2, ShieldCheck, AlertTriangle, Loader2 } from "lucide-react";
import { createSnapshot, deleteSnapshot, fetchSnapshots, rollbackSnapshot } from "../../lib/sandboxApi";
import { SnapshotItem } from "../../lib/types/sandbox";

interface SnapshotManagerProps {
  projectId: string;
  onRollbackComplete?: () => void;
}

export function SnapshotManagerView({ projectId, onRollbackComplete }: SnapshotManagerProps) {
  const [snapshots, setSnapshots] = useState<SnapshotItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [tag, setTag] = useState("MANUAL");
  const [description, setDescription] = useState("");
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadSnapshots = async () => {
    try {
      setLoading(true);
      const data = await fetchSnapshots(projectId);
      setSnapshots(data);
    } catch (err: any) {
      setMsg({ type: "error", text: err.message || "Gagal memuat snapshot" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) loadSnapshots();
  }, [projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      await createSnapshot(projectId, tag, description);
      setShowCreateModal(false);
      setDescription("");
      setMsg({ type: "success", text: "Snapshot baru berhasil dibekukan!" });
      await loadSnapshots();
    } catch (err: any) {
      setMsg({ type: "error", text: err.message || "Gagal membuat snapshot" });
    } finally {
      setActionLoading(false);
    }
  };

  const handleRollback = async (snap: SnapshotItem) => {
    const confirm = window.confirm(
      `Yakin ingin rollback ke snapshot [${snap.tag}: ${snap.id}]?\nSistem akan membuat safety backup otomatis sebelum menimpa berkas.`
    );
    if (!confirm) return;

    try {
      setActionLoading(true);
      await rollbackSnapshot(projectId, snap.id);
      setMsg({ type: "success", text: `Rollback berhasil! Proyek dipulihkan ke ${snap.tag}.` });
      await loadSnapshots();
      if (onRollbackComplete) onRollbackComplete();
    } catch (err: any) {
      setMsg({ type: "error", text: err.message || "Gagal melakukan rollback" });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (snapId: string) => {
    if (!window.confirm("Hapus checkpoint snapshot ini?")) return;
    try {
      await deleteSnapshot(projectId, snapId);
      setSnapshots((prev) => prev.filter((s) => s.id !== snapId));
    } catch (err: any) {
      setMsg({ type: "error", text: err.message || "Gagal menghapus snapshot" });
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl p-4 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-sm font-bold text-white">Filesystem Snapshots & 1-Click Rollback</h3>
            <p className="text-xs text-slate-400">Ambil checkpoint atau kembalikan state kode jika terjadi error.</p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all active:scale-95"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Ambil Snapshot</span>
        </button>
      </div>

      {msg && (
        <div className={`p-3 rounded-xl text-xs flex items-center justify-between ${msg.type === "success" ? "bg-emerald-950/40 text-emerald-300 border border-emerald-500/30" : "bg-rose-950/40 text-rose-300 border border-rose-500/30"}`}>
          <span>{msg.text}</span>
          <button onClick={() => setMsg(null)} className="text-[10px] underline">Tutup</button>
        </div>
      )}

      {/* Snapshot List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {loading ? (
          <div className="py-12 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Memuat checkpoint...
          </div>
        ) : snapshots.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs">Belum ada snapshot tersimpan. Klik tombol di atas untuk membuat checkpoint.</div>
        ) : (
          snapshots.map((s) => (
            <div key={s.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 flex items-center justify-between gap-4 transition-all">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${s.tag.includes("ROLLBACK") ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : s.tag.includes("HARDENING") ? "bg-purple-500/20 text-purple-300 border border-purple-500/30" : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"}`}>
                    {s.tag}
                  </span>
                  <span className="text-xs text-white font-semibold">{s.description}</span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono flex items-center gap-3">
                  <span>{new Date(s.created_at).toLocaleString()}</span>
                  <span>• {s.file_count} files</span>
                  <span>• {formatBytes(s.total_bytes)}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleRollback(s)}
                  disabled={actionLoading}
                  className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 active:scale-95 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Rollback</span>
                </button>
                <button
                  onClick={() => handleDelete(s.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 max-w-md w-full space-y-4 shadow-2xl">
            <h4 className="text-sm font-bold text-white">Ambil Snapshot Filesystem</h4>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Tag Checkpoint</label>
              <input
                type="text"
                value={tag}
                onChange={(e) => setTag(e.target.value.toUpperCase())}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs font-mono"
                required
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Deskripsi Catatan</label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Catatan perubahan sebelum modifikasi..."
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-3 py-1.5 rounded-lg text-slate-400 text-xs hover:text-white"
              >
                Batal
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-500/20"
              >
                {actionLoading ? "Menyimpan..." : "Simpan Snapshot"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
