"use client";

import Link from "next/link";
import {
  ArrowLeft,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Key,
  Cloud,
  Terminal,
  Settings,
  Lock,
} from "lucide-react";
import { useSystemSettings, SettingsTab } from "../../hooks/useSystemSettings";
import { SettingsProviderTab } from "../../components/settings/SettingsProviderTab";
import { SettingsSecurityTab } from "../../components/settings/SettingsSecurityTab";
import { SettingsPaasTab } from "../../components/settings/SettingsPaasTab";
import { SettingsSystemTab } from "../../components/settings/SettingsSystemTab";

export default function SystemSettingsPage() {
  const {
    activeTab,
    setActiveTab,
    settingsData,
    isLoading,
    isSaving,
    isResetting,
    feedback,
    setFeedback,
    providerForm,
    handleProviderChange,
    telegramForm,
    setTelegramForm,
    paasForm,
    setPaasForm,
    sandboxForm,
    setSandboxForm,
    showKeys,
    setShowKeys,
    isTestingTelegram,
    isRotatingPassword,
    handleSave,
    handleReset,
    handleTestTelegram,
    handleRotatePasswordNow,
  } = useSystemSettings();

  return (
    <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <Link href="/" className="inline-flex items-center text-xs font-mono font-semibold text-slate-400 hover:text-white transition-colors mb-1.5">
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            Kembali ke Portfolio Hub
          </Link>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Settings className="w-6 h-6 text-white" />
            <span>Pengaturan Sistem & Model Agen</span>
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Konfigurasi model LLM tiap agen, kunci API BYOK, gembok akses Telegram, dan PaaS deploy secara dinamis.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button onClick={handleReset} disabled={isResetting || isLoading} className="liquid-dark-btn inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-mono transition-all disabled:opacity-50">
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
            <span>{isResetting ? "Mereset..." : "Reset Default"}</span>
          </button>
          <button onClick={handleSave} disabled={isSaving || isLoading} className="liquid-chrome-btn inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs uppercase font-bold text-black shadow-lg transition-all disabled:opacity-50">
            <Save className={`w-4 h-4 ${isSaving ? "animate-spin" : ""}`} />
            <span>{isSaving ? "Menyimpan..." : "Simpan Perubahan"}</span>
          </button>
        </div>
      </div>

      {feedback && (
        <div className={`p-4 rounded-2xl flex items-center justify-between gap-3 text-xs font-medium border ${feedback.type === "success" ? "bg-emerald-500/10 border-emerald-500/25 text-emerald-300" : "bg-rose-500/10 border-rose-500/25 text-rose-300"}`}>
          <div className="flex items-center gap-2.5">
            {feedback.type === "success" ? <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />}
            <span>{feedback.message}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-[11px] opacity-70 hover:opacity-100 uppercase font-mono">Tutup</button>
        </div>
      )}

      <div className="flex flex-wrap gap-2 border-b border-white/10 pb-3">
        {(["providers", "security", "paas", "system"] as SettingsTab[]).map((tab) => {
          const icons = { providers: Key, security: Lock, paas: Cloud, system: Terminal };
          const labels = { providers: "Kunci API (BYOK)", security: "Gembok Telegram", paas: "PaaS Deployment", system: "Sandbox & Lingkungan" };
          const Icon = icons[tab];
          return (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${activeTab === tab ? "bg-white/15 text-white border border-white/25 shadow-sm" : "text-slate-400 hover:text-white hover:bg-white/5"}`}>
              <Icon className="w-4 h-4" />
              <span>{labels[tab]}</span>
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="p-16 text-center text-slate-400 liquid-glass rounded-2xl animate-pulse font-mono text-xs">Memuat konfigurasi sistem dinamis...</div>
      ) : (
        <div className="space-y-6">
          {activeTab === "providers" && (
            <SettingsProviderTab providers={settingsData?.providers || {}} providerForm={providerForm} showKeys={showKeys} onProviderChange={handleProviderChange} onToggleKeyVisibility={(k) => setShowKeys((p) => ({ ...p, [k]: !p[k] }))} />
          )}
          {activeTab === "security" && (
            <SettingsSecurityTab isTokenSet={!!settingsData?.telegram?.is_token_set} telegramForm={telegramForm} showToken={!!showKeys["telegram"]} isTesting={isTestingTelegram} isRotating={isRotatingPassword} setTelegramForm={setTelegramForm} onToggleShowToken={() => setShowKeys((p) => ({ ...p, telegram: !p["telegram"] }))} onTestTelegram={handleTestTelegram} onRotatePassword={handleRotatePasswordNow} />
          )}
          {activeTab === "paas" && (
            <SettingsPaasTab isTokenSet={!!settingsData?.paas?.is_token_set} paasForm={paasForm} setPaasForm={setPaasForm} />
          )}
          {activeTab === "system" && (
            <SettingsSystemTab sandboxForm={sandboxForm} systemMeta={settingsData?.system} setSandboxForm={setSandboxForm} />
          )}
        </div>
      )}
    </div>
  );
}
