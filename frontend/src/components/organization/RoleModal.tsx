"use client";

import React, { useEffect, useState } from "react";
import { UserPlus, Edit3, X, AlertCircle } from "lucide-react";
import { DivisionResponse, RoleResponse, ThinkingLevel } from "@/lib/types/corporate";
import { FallbackChannelConfig } from "@/lib/types/analytics";
import { createRole, updateRole } from "@/lib/corporateApi";
import { RECOMMENDED_PRESETS } from "@/lib/constants/llmPresets";
import RoleModelFields from "./RoleModelFields";
import RoleToolSelector from "./RoleToolSelector";
import { RoleFallbackList } from "./RoleFallbackList";

interface RoleModalProps {
  isOpen: boolean;
  branchId: string;
  divisions: DivisionResponse[];
  initialData?: RoleResponse | null;
  preselectedDivisionId?: string | null;
  onClose: () => void;
  onSuccess: (role: RoleResponse) => void;
}

export default function RoleModal({
  isOpen, branchId, divisions, initialData, preselectedDivisionId, onClose, onSuccess,
}: RoleModalProps) {
  const [divisionId, setDivisionId] = useState("");
  const [name, setName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [modelProvider, setModelProvider] = useState("openrouter");
  const [modelName, setModelName] = useState("deepseek/deepseek-r1:free");
  const [temperature, setTemperature] = useState(0.2);
  const [tools, setTools] = useState<string[]>(["read_file", "write_file"]);
  const [tokenBudget, setTokenBudget] = useState(8000);
  const [thinkingLevel, setThinkingLevel] = useState<ThinkingLevel>("medium");
  const [fallbacks, setFallbacks] = useState<FallbackChannelConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setDivisionId(initialData.division_id);
      setName(initialData.name);
      setJobDescription(initialData.job_description || "");
      setSystemPrompt(initialData.system_prompt_template);
      setModelProvider(initialData.model_provider || "openrouter");
      setModelName(initialData.model_name || "deepseek/deepseek-r1:free");
      setTemperature(initialData.temperature ?? 0.2);
      setTools(initialData.tool_permissions || ["read_file", "write_file"]);
      setTokenBudget(initialData.token_budget_per_task || 8000);
      setThinkingLevel((initialData.thinking_level as ThinkingLevel) || "medium");
      setFallbacks(initialData.fallback_chain || []);
    } else {
      setDivisionId(preselectedDivisionId || divisions[0]?.id || "");
      setName("");
      setJobDescription("");
      setSystemPrompt("Anda adalah agen spesialis yang berdedikasi tinggi.");
      setModelProvider("openrouter");
      setModelName("deepseek/deepseek-r1:free");
      setTemperature(0.2);
      setTools(["read_file", "write_file"]);
      setTokenBudget(8000);
      setThinkingLevel("medium");
      setFallbacks([]);
    }
    setError(null);
  }, [initialData, preselectedDivisionId, divisions, isOpen]);

  if (!isOpen) return null;

  const handleProviderChange = (prov: string) => {
    setModelProvider(prov);
    const presets = RECOMMENDED_PRESETS[prov];
    if (presets?.length) setModelName(presets[0]);
  };
  const toggleTool = (id: string) => setTools((p) => (p.includes(id) ? p.filter((t) => t !== id) : [...p, id]));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || systemPrompt.trim().length < 10) {
      return setError("Nama dan prompt (min 10 karakter) wajib diisi.");
    }
    setLoading(true);
    setError(null);
    try {
      const payload = {
        division_id: divisionId,
        name: name.trim(),
        job_description: jobDescription.trim(),
        system_prompt_template: systemPrompt.trim(),
        model_provider: modelProvider,
        model_name: modelName.trim(),
        temperature,
        tool_permissions: tools,
        token_budget_per_task: tokenBudget,
        thinking_level: thinkingLevel,
        fallback_chain: fallbacks,
      };
      const res = initialData
        ? await updateRole(initialData.id, payload)
        : await createRole({ ...payload, branch_id: branchId, division_id: divisionId });
      onSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || "Gagal menyimpan role.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="w-full max-w-xl rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative my-8 max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            {initialData ? <Edit3 className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">{initialData ? "Edit Karyawan AI" : "Tambah Karyawan AI"}</h3>
            <p className="text-xs text-slate-400">Konfigurasi mandat peran, model LLM, fallback chain & perkakas agen</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Nama Peran</label>
              <input
                type="text" required value={name} onChange={(e) => setName(e.target.value)}
                placeholder="Senior Backend Engineer"
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500/50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Divisi Organisasi</label>
              <select
                value={divisionId} onChange={(e) => setDivisionId(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500/50"
              >
                {divisions.map((d) => (
                  <option key={d.id} value={d.id} className="bg-[#0c0d14]">{d.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Fokus Tugas & Jobdesk</label>
            <input
              type="text"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="e.g. Merancang REST API FastAPI & arsitektur basis data..."
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-white/30"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">System Instruction</label>
            <textarea
              rows={3} required value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Instruksi sistem yang mendefinisikan kepribadian..."
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          <RoleModelFields
            modelProvider={modelProvider} modelName={modelName} temperature={temperature}
            tokenBudget={tokenBudget} thinkingLevel={thinkingLevel}
            onProviderChange={handleProviderChange} onModelNameChange={setModelName}
            onTemperatureChange={setTemperature} onTokenBudgetChange={setTokenBudget}
            onThinkingLevelChange={setThinkingLevel}
          />

          {/* Multi-Channel Fallback Chain (9router Style) */}
          <RoleFallbackList fallbacks={fallbacks} onChange={setFallbacks} />

          <RoleToolSelector selectedTools={tools} onToggleTool={toggleTool} />

          <div className="pt-2 flex items-center justify-end gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-xs text-slate-400 hover:text-white">Batal</button>
            <button
              type="submit" disabled={loading}
              className="px-4 py-2 text-xs font-medium text-white bg-cyan-600 hover:bg-cyan-500 rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? "Menyimpan..." : initialData ? "Perbarui Role" : "Simpan Role"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
