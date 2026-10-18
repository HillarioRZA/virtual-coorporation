"use client";

import { Dispatch, SetStateAction } from "react";
import { Eye, EyeOff, Lock, RefreshCw, Send } from "lucide-react";

interface TelegramFormData {
  auth_gate_enabled: boolean;
  bot_token: string;
  chat_id: string;
  rotation_hours: number;
}

interface SettingsSecurityTabProps {
  isTokenSet: boolean;
  telegramForm: TelegramFormData;
  showToken: boolean;
  isTesting: boolean;
  isRotating: boolean;
  setTelegramForm: Dispatch<SetStateAction<TelegramFormData>>;
  onToggleShowToken: () => void;
  onTestTelegram: () => void;
  onRotatePassword: () => void;
}

export function SettingsSecurityTab({
  isTokenSet,
  telegramForm,
  showToken,
  isTesting,
  isRotating,
  setTelegramForm,
  onToggleShowToken,
  onTestTelegram,
  onRotatePassword,
}: SettingsSecurityTabProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 liquid-glass p-6 rounded-3xl border border-white/10 space-y-6">
        <div className="border-b border-white/10 pb-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Lock className="w-5 h-5 text-emerald-400" />
            <span>Gembok Akses Cloud Personal (Telegram Gate)</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Dashboard di-blur total dan meminta password acak yang diganti otomatis via Telegram Bot API.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-2xl bg-black/40 border border-white/10">
            <div>
              <span className="text-sm font-bold text-white block">Status Gembok Autentikasi</span>
              <span className="text-xs text-slate-400">
                {telegramForm.auth_gate_enabled
                  ? "Gembok aktif. Setiap pengguna wajib memasukkan password yang dikirim ke Telegram."
                  : "Gembok nonaktif. Studio dapat dibuka langsung di browser lokal."}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setTelegramForm((p) => ({ ...p, auth_gate_enabled: !p.auth_gate_enabled }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                telegramForm.auth_gate_enabled ? "bg-emerald-500" : "bg-white/20"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  telegramForm.auth_gate_enabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block">
                Telegram Bot Token (@BotFather)
              </label>
              <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${isTokenSet ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border-amber-500/20"}`}>
                {isTokenSet ? "Kunci Aktif Tersimpan" : "Belum Diatur"}
              </span>
            </div>
            <div className="relative">
              <input
                type={showToken ? "text" : "password"}
                value={telegramForm.bot_token}
                onChange={(e) => setTelegramForm((p) => ({ ...p, bot_token: e.target.value }))}
                placeholder={isTokenSet ? "Token aktif terkonfigurasi (Ketik baru jika ingin mengganti)" : "Contoh: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"}
                className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 pr-10 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
              />
              <button
                type="button"
                onClick={onToggleShowToken}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">
              {isTokenSet ? "Token tersimpan aman di SQLite Vault. Masukkan nilai baru jika ingin mengganti." : "Dapatkan token dari @BotFather di aplikasi Telegram."}
            </span>
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Telegram Chat ID Pribadi (@userinfobot)
            </label>
            <input
              type="text"
              value={telegramForm.chat_id}
              onChange={(e) => setTelegramForm((p) => ({ ...p, chat_id: e.target.value }))}
              placeholder="Contoh: 987654321"
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Interval Rotasi Password Otomatis
            </label>
            <select
              value={telegramForm.rotation_hours}
              onChange={(e) => setTelegramForm((p) => ({ ...p, rotation_hours: Number(e.target.value) }))}
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2.5 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
            >
              <option value={1}>1 Jam</option>
              <option value={3}>3 Jam</option>
              <option value={6}>6 Jam (Standar Rekomendasi)</option>
              <option value={12}>12 Jam</option>
              <option value={24}>24 Jam (1 Hari)</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="liquid-glass p-5 rounded-3xl border border-white/10 space-y-4">
          <h4 className="text-xs font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Send className="w-4 h-4 text-cyan-400" />
            <span>Uji Coba Pengiriman</span>
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Kirim pesan notifikasi password aktif saat ini langsung ke akun Telegram Anda untuk memastikan Bot Token dan Chat ID bekerja.
          </p>
          <button
            type="button"
            onClick={onTestTelegram}
            disabled={isTesting || !telegramForm.chat_id}
            className="w-full py-2.5 px-3 rounded-xl liquid-dark-btn text-xs font-semibold flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            <Send className={`w-3.5 h-3.5 ${isTesting ? "animate-spin" : ""}`} />
            <span>{isTesting ? "Mengirim..." : "Kirim Pesan Tes"}</span>
          </button>
        </div>

        <div className="liquid-glass p-5 rounded-3xl border border-white/10 space-y-4">
          <h4 className="text-xs font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <RefreshCw className="w-4 h-4 text-amber-400" />
            <span>Rotasi Manual Seketika</span>
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Paksa penerbitan password baru detik ini juga tanpa menunggu interval timer 6 jam.
          </p>
          <button
            type="button"
            onClick={onRotatePassword}
            disabled={isRotating || !telegramForm.chat_id}
            className="w-full py-2.5 px-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-xs font-semibold text-white flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRotating ? "animate-spin" : ""}`} />
            <span>{isRotating ? "Memproses..." : "Rotasi Password Sekarang"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
