import { useEffect, useState } from "react";
import {
  fetchSystemSettings,
  updateSystemSettings,
  resetSystemSettings,
  resendAuthPassword,
  rotateAuthPassword,
} from "../lib/api";
import { SystemSettingsData } from "../lib/types/api";

export type SettingsTab = "providers" | "security" | "paas" | "system";

export function useSystemSettings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("providers");
  const [settingsData, setSettingsData] = useState<SystemSettingsData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const [providerForm, setProviderForm] = useState<Record<string, { key: string; base_url: string; model?: string }>>({});
  const [telegramForm, setTelegramForm] = useState({
    auth_gate_enabled: false,
    bot_token: "",
    chat_id: "",
    rotation_hours: 6,
  });
  const [paasForm, setPaasForm] = useState({ provider: "coolify", api_url: "", api_token: "" });
  const [sandboxForm, setSandboxForm] = useState({
    domain_suffix: ".local.sandbox",
    caddy_admin_api: "http://127.0.0.1:2019",
    frontend_image: "venture-sandbox-frontend:latest",
    backend_image: "venture-sandbox-backend:latest",
  });
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [isTestingTelegram, setIsTestingTelegram] = useState<boolean>(false);
  const [isRotatingPassword, setIsRotatingPassword] = useState<boolean>(false);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const data = await fetchSystemSettings();
      setSettingsData(data);
      if (data.providers) {
        const pf: Record<string, { key: string; base_url: string; model?: string }> = {};
        Object.entries(data.providers).forEach(([p, val]) => {
          pf[p] = { key: "", base_url: val.base_url || "", model: val.model || "" };
        });
        setProviderForm(pf);
      }
      if (data.telegram) {
        setTelegramForm({
          auth_gate_enabled: data.telegram.auth_gate_enabled,
          bot_token: "",
          chat_id: data.telegram.chat_id || "",
          rotation_hours: data.telegram.rotation_hours || 6,
        });
      }
      if (data.paas) {
        setPaasForm({ provider: data.paas.provider || "coolify", api_url: data.paas.api_url || "", api_token: "" });
      }
      if (data.sandbox) {
        setSandboxForm({
          domain_suffix: data.sandbox.domain_suffix || ".local.sandbox",
          caddy_admin_api: data.sandbox.caddy_admin_api || "http://127.0.0.1:2019",
          frontend_image: data.sandbox.frontend_image || "venture-sandbox-frontend:latest",
          backend_image: data.sandbox.backend_image || "venture-sandbox-backend:latest",
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal memuat pengaturan sistem.";
      setFeedback({ type: "error", message: msg });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadSettings(); }, []);

  const handleProviderChange = (prov: string, field: "key" | "base_url" | "model", value: string) => {
    setProviderForm((prev) => ({
      ...prev,
      [prov]: { ...(prev[prov] || { key: "", base_url: "" }), [field]: value },
    }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setFeedback(null);
      const updates: Record<string, unknown> = {};

      Object.entries(providerForm).forEach(([prov, val]) => {
        const keyName = prov === "gemini" ? "GEMINI_API_KEY" : `${prov.toUpperCase()}_API_KEY`;
        if (val.key.trim() && !val.key.includes("...")) updates[keyName] = val.key.trim();
        if (val.base_url.trim()) updates[`${prov.toUpperCase()}_BASE_URL`] = val.base_url.trim();
        if (val.model && val.model.trim()) updates[`${prov.toUpperCase()}_MODEL`] = val.model.trim();
      });

      updates["AUTH_GATE_ENABLED"] = telegramForm.auth_gate_enabled;
      updates["TELEGRAM_AUTH_GATE_ENABLED"] = telegramForm.auth_gate_enabled;
      if (telegramForm.bot_token.trim() && !telegramForm.bot_token.includes("...")) {
        updates["TELEGRAM_BOT_TOKEN"] = telegramForm.bot_token.trim();
      }
      if (telegramForm.chat_id.trim()) updates["TELEGRAM_CHAT_ID"] = telegramForm.chat_id.trim();
      updates["AUTH_ROTATION_HOURS"] = telegramForm.rotation_hours;
      updates["TELEGRAM_ROTATION_HOURS"] = telegramForm.rotation_hours;

      updates["PAAS_PROVIDER"] = paasForm.provider;
      if (paasForm.api_url.trim()) updates["PAAS_API_URL"] = paasForm.api_url.trim();
      if (paasForm.api_token.trim() && !paasForm.api_token.includes("...")) {
        updates["PAAS_API_TOKEN"] = paasForm.api_token.trim();
      }

      updates["SANDBOX_DOMAIN_SUFFIX"] = sandboxForm.domain_suffix;
      updates["CADDY_ADMIN_API"] = sandboxForm.caddy_admin_api;
      updates["DOCKER_BASE_FRONTEND_IMAGE"] = sandboxForm.frontend_image;
      updates["DOCKER_FRONTEND_IMAGE"] = sandboxForm.frontend_image;
      updates["DOCKER_BASE_BACKEND_IMAGE"] = sandboxForm.backend_image;
      updates["DOCKER_BACKEND_IMAGE"] = sandboxForm.backend_image;

      const res = await updateSystemSettings(updates);
      setFeedback({ type: "success", message: res.message || "Berhasil menyimpan pengaturan sistem!" });
      await loadSettings();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal menyimpan pengaturan.";
      setFeedback({ type: "error", message: msg });
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Peringatan: Seluruh konfigurasi akan di-reset ke default .env. Lanjutkan?")) return;
    try {
      setIsResetting(true);
      setFeedback(null);
      const res = await resetSystemSettings();
      setFeedback({ type: "success", message: res.message || "Pengaturan berhasil di-reset ke default." });
      await loadSettings();
    } catch (err: unknown) {
      setFeedback({ type: "error", message: err instanceof Error ? err.message : "Gagal mereset pengaturan." });
    } finally {
      setIsResetting(false);
    }
  };

  const handleTestTelegram = async () => {
    try {
      setIsTestingTelegram(true);
      setFeedback(null);
      const res = await resendAuthPassword();
      setFeedback({ type: "success", message: res.message || "Pesan tes berhasil dikirim ke Telegram!" });
    } catch (err: unknown) {
      setFeedback({ type: "error", message: err instanceof Error ? err.message : "Gagal mengirim tes ke Telegram." });
    } finally {
      setIsTestingTelegram(false);
    }
  };

  const handleRotatePasswordNow = async () => {
    try {
      setIsRotatingPassword(true);
      setFeedback(null);
      const res = await rotateAuthPassword();
      setFeedback({ type: "success", message: res.message || "Password berhasil dirotasi!" });
    } catch (err: unknown) {
      setFeedback({ type: "error", message: err instanceof Error ? err.message : "Gagal merotasi password." });
    } finally {
      setIsRotatingPassword(false);
    }
  };

  return {
    activeTab, setActiveTab, settingsData, isLoading, isSaving, isResetting,
    feedback, setFeedback, providerForm, handleProviderChange, telegramForm,
    setTelegramForm, paasForm, setPaasForm, sandboxForm, setSandboxForm,
    showKeys, setShowKeys, isTestingTelegram, isRotatingPassword, handleSave,
    handleReset, handleTestTelegram, handleRotatePasswordNow,
  };
}
