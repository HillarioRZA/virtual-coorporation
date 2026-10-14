"use client";

import { useEffect, useState } from "react";
import { Lock, ShieldCheck, Plus, Key, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { fetchVaultSecrets, storeVaultSecrets } from "../../lib/api";

interface SecretVaultModalProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
}

const TEMPLATE_KEYS = [
  "STRIPE_SECRET_KEY",
  "MIDTRANS_SERVER_KEY",
  "PROD_DATABASE_URL",
  "RESEND_API_KEY",
  "OPENAI_API_KEY",
];

export function SecretVaultModal({ projectId, isOpen, onClose }: SecretVaultModalProps) {
  const [keys, setKeys] = useState<string[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>("STRIPE_SECRET_KEY");
  const [customKey, setCustomKey] = useState<string>("");
  const [secretValue, setSecretValue] = useState<string>("");
  const [showValue, setShowValue] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>("");

  const loadKeys = async () => {
    try {
      const data = await fetchVaultSecrets(projectId);
      setKeys(data);
    } catch (err) {
      console.error("Gagal load keys:", err);
    }
  };

  useEffect(() => {
    if (isOpen && projectId) {
      loadKeys();
      setStatusMsg("");
    }
  }, [isOpen, projectId]);

  if (!isOpen) return null;

  const handleSaveSecret = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalKey = selectedKey === "CUSTOM" ? customKey.trim().toUpperCase() : selectedKey;
    if (!finalKey || !secretValue.trim()) return;

    try {
      setIsLoading(true);
      setStatusMsg("");
      await storeVaultSecrets(projectId, { [finalKey]: secretValue.trim() });
      setStatusMsg(`Kredensial '${finalKey}' berhasil dienkripsi (AES-256-GCM) dan disimpan.`);
      setSecretValue("");
      setCustomKey("");
      await loadKeys();
    } catch (err: any) {
      setStatusMsg(`Gagal menyimpan: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-panel p-6 rounded-3xl max-w-lg w-full border border-slate-700 space-y-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Zero-Trust Secret Vault</h3>
              <p className="text-xs text-slate-400">Enkripsi AES-256-GCM Kredensial Produksi (Stage-Gate 3)</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-sm">
            ✕
          </button>
        </div>

        {statusMsg && (
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{statusMsg}</span>
          </div>
        )}

        {/* Form Input Secret */}
        <form onSubmit={handleSaveSecret} className="space-y-3.5">
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Pilih Nama Kunci Kredensial
            </label>
            <select
              value={selectedKey}
              onChange={(e) => setSelectedKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              {TEMPLATE_KEYS.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
              <option value="CUSTOM">+ Custom Secret Key...</option>
            </select>
          </div>

          {selectedKey === "CUSTOM" && (
            <div>
              <input
                type="text"
                required
                value={customKey}
                onChange={(e) => setCustomKey(e.target.value)}
                placeholder="Contoh: AWS_SECRET_ACCESS_KEY"
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}

          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Nilai Kredensial (Plaintext)
            </label>
            <div className="relative">
              <input
                type={showValue ? "text" : "password"}
                required
                value={secretValue}
                onChange={(e) => setSecretValue(e.target.value)}
                placeholder="sk_live_... atau postgresql://..."
                className="w-full px-3 py-2 pr-10 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={() => setShowValue(!showValue)}
                className="absolute right-3 top-2.5 text-slate-400 hover:text-white"
              >
                {showValue ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-semibold text-xs shadow-lg shadow-indigo-500/20 disabled:opacity-50 transition-all"
          >
            {isLoading ? "Mengenkripsi..." : "Enkripsi & Simpan ke Vault"}
          </button>
        </form>

        {/* Stored Keys Checklist */}
        <div className="pt-3 border-t border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
            Kredensial Tersimpan ({keys.length}):
          </span>
          {keys.length === 0 ? (
            <p className="text-xs text-slate-500 italic">Belum ada kredensial yang tersimpan.</p>
          ) : (
            <div className="space-y-1.5 max-h-36 overflow-y-auto">
              {keys.map((k) => (
                <div
                  key={k}
                  className="flex items-center justify-between p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono"
                >
                  <span className="text-slate-200 flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{k}</span>
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    <span>AES-256</span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
