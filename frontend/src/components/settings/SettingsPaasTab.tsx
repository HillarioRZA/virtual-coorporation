"use client";

import { Dispatch, SetStateAction } from "react";
import { Cloud } from "lucide-react";

interface PaasFormData {
  provider: string;
  api_url: string;
  api_token: string;
}

interface SettingsPaasTabProps {
  isTokenSet: boolean;
  paasForm: PaasFormData;
  setPaasForm: Dispatch<SetStateAction<PaasFormData>>;
}

export function SettingsPaasTab({
  isTokenSet,
  paasForm,
  setPaasForm,
}: SettingsPaasTabProps) {
  return (
    <div className="liquid-glass p-6 rounded-3xl border border-white/10 max-w-2xl space-y-5">
      <div>
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Cloud className="w-5 h-5 text-white" />
          <span>PaaS & Cloud Webhook Integration</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Konfigurasikan integrasi deployment cloud Coolify atau Railway untuk automasi rilis aplikasi produksi.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            PaaS Provider
          </label>
          <select
            value={paasForm.provider}
            onChange={(e) => setPaasForm((p) => ({ ...p, provider: e.target.value }))}
            className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 text-slate-200 focus:outline-none focus:border-white/40"
          >
            <option value="coolify">Coolify (Self-Hosted PaaS)</option>
            <option value="railway">Railway</option>
            <option value="custom">Custom Webhook / Internal Runner</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            PaaS Webhook / API URL
          </label>
          <input
            type="text"
            value={paasForm.api_url}
            onChange={(e) => setPaasForm((p) => ({ ...p, api_url: e.target.value }))}
            placeholder="https://coolify.my-domain.com/api/v1/deploy?uuid=..."
            className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
          />
        </div>

        <div>
          <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            PaaS API Token (Opsional)
          </label>
          <input
            type="password"
            value={paasForm.api_token}
            onChange={(e) => setPaasForm((p) => ({ ...p, api_token: e.target.value }))}
            placeholder={isTokenSet ? "Token aktif terkonfigurasi (biarkan kosong jika tidak diubah)" : "Bearer token..."}
            className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
          />
        </div>
      </div>
    </div>
  );
}
