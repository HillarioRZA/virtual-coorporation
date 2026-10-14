"use client";

import { useEffect, useState, useRef } from "react";
import { Lock, KeyRound, AlertCircle, ShieldCheck, RefreshCw, ShieldAlert } from "lucide-react";
import { fetchAuthStatus, verifyAuthPassword } from "../../lib/api";

const TOKEN_STORAGE_KEY = "venture_session_token";
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_SECONDS = 60;

export default function AuthGateModal() {
  const [isEnabled, setIsEnabled] = useState<boolean>(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [checking, setChecking] = useState<boolean>(true);

  const [password, setPassword] = useState<string>("");
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [shake, setShake] = useState<boolean>(false);
  const [failedCount, setFailedCount] = useState<number>(0);
  const [lockoutTimer, setLockoutTimer] = useState<number>(0);

  const inputRef = useRef<HTMLInputElement>(null);

  // Check auth status on mount
  useEffect(() => {
    async function checkStatus() {
      try {
        const storedToken = typeof window !== "undefined" ? sessionStorage.getItem(TOKEN_STORAGE_KEY) : null;
        const status = await fetchAuthStatus(storedToken);
        setIsEnabled(status.is_enabled);
        setIsAuthenticated(status.is_authenticated);
      } catch (err) {
        setIsAuthenticated(true);
      } finally {
        setChecking(false);
      }
    }
    checkStatus();
  }, []);

  // Lockout countdown timer
  useEffect(() => {
    if (lockoutTimer <= 0) return;
    const interval = setInterval(() => {
      setLockoutTimer((prev) => {
        if (prev <= 1) {
          setFailedCount(0);
          setErrorMsg("");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [lockoutTimer]);

  // Anti-Pentest & Anti-DevTools keyboard & mouse listeners while gate is locked
  useEffect(() => {
    if (!isEnabled || isAuthenticated) return;

    // 1. Disable Right-Click Context Menu
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };

    // 2. Disable Inspect Element & DevTools keyboard shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCtrlOrCmd = e.ctrlKey || e.metaKey;

      // F12
      if (e.key === "F12") {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }

      // Ctrl+Shift+I (Inspect), Ctrl+Shift+J (Console), Ctrl+Shift+C (Element picker)
      if (isCtrlOrCmd && e.shiftKey && ["I", "i", "J", "j", "C", "c"].includes(e.key)) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }

      // Ctrl+U (View Source), Ctrl+S (Save page)
      if (isCtrlOrCmd && ["U", "u", "S", "s"].includes(e.key)) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
    };

    // 3. Disable global clipboard copy/paste during login prompt
    const handleGlobalCopyPaste = (e: ClipboardEvent) => {
      e.preventDefault();
    };

    window.addEventListener("contextmenu", handleContextMenu, { capture: true });
    window.addEventListener("keydown", handleKeyDown, { capture: true });
    window.addEventListener("paste", handleGlobalCopyPaste, { capture: true });
    window.addEventListener("copy", handleGlobalCopyPaste, { capture: true });
    window.addEventListener("cut", handleGlobalCopyPaste, { capture: true });

    return () => {
      window.removeEventListener("contextmenu", handleContextMenu, { capture: true });
      window.removeEventListener("keydown", handleKeyDown, { capture: true });
      window.removeEventListener("paste", handleGlobalCopyPaste, { capture: true });
      window.removeEventListener("copy", handleGlobalCopyPaste, { capture: true });
      window.removeEventListener("cut", handleGlobalCopyPaste, { capture: true });
    };
  }, [isEnabled, isAuthenticated]);

  // Auto-focus input when modal opens
  useEffect(() => {
    if (isEnabled && !isAuthenticated && lockoutTimer === 0 && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEnabled, isAuthenticated, lockoutTimer]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim() || lockoutTimer > 0) return;

    try {
      setIsVerifying(true);
      setErrorMsg("");
      const res = await verifyAuthPassword(password.trim());
      if (typeof window !== "undefined") {
        sessionStorage.setItem(TOKEN_STORAGE_KEY, res.session_token);
      }
      setIsAuthenticated(true);
      setPassword("");
      setFailedCount(0);
    } catch (err: any) {
      const nextFailed = failedCount + 1;
      setFailedCount(nextFailed);
      setShake(true);
      setTimeout(() => setShake(false), 500);

      if (nextFailed >= MAX_FAILED_ATTEMPTS) {
        setLockoutTimer(LOCKOUT_SECONDS);
        setErrorMsg(`Terlalu banyak percobaan gagal. Akses dibekukan selama ${LOCKOUT_SECONDS} detik.`);
      } else {
        setErrorMsg(err.message || `Kode akses tidak valid. Sisa percobaan: ${MAX_FAILED_ATTEMPTS - nextFailed}`);
      }
    } finally {
      setIsVerifying(false);
    }
  };

  // If loading status or gate is disabled or user is authenticated, render nothing
  if (checking || !isEnabled || isAuthenticated) {
    return null;
  }

  const isFormDisabled = isVerifying || !password.trim() || lockoutTimer > 0;

  return (
    <div
      onContextMenu={(e) => e.preventDefault()}
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/90 backdrop-blur-2xl animate-in fade-in duration-300 select-none"
    >
      <div
        className={`liquid-glass-elevated max-w-md w-full p-8 rounded-3xl border border-white/15 shadow-2xl relative overflow-hidden ${
          shake ? "shake-animation" : ""
        }`}
      >
        {/* Ambient Top Chrome Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-white/40 to-transparent" />

        {/* Anonymous Modal Header */}
        <div className="text-center space-y-3 mb-6">
          <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/15 mx-auto flex items-center justify-center shadow-lg shadow-white/5">
            {lockoutTimer > 0 ? (
              <ShieldAlert className="w-6 h-6 text-rose-400 animate-pulse" />
            ) : (
              <Lock className="w-6 h-6 text-white" />
            )}
          </div>
          <div>
            <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
              Restricted Environment • Private Gateway
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight mt-1">
              Verifikasi Akses Studio
            </h2>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Sistem ini dilindungi oleh otentikasi privat. Masukkan kode akses dinamis Anda untuk melanjutkan.
            </p>
          </div>
        </div>

        {/* Notification feedback */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Password Form */}
        <form onSubmit={handleVerify} className="space-y-5">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
                Security Passcode
              </label>
              {lockoutTimer > 0 && (
                <span className="text-[11px] font-mono text-rose-400 font-bold">
                  Frozen ({lockoutTimer}s)
                </span>
              )}
            </div>
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                disabled={lockoutTimer > 0}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck="false"
                data-lpignore="true"
                onPaste={(e) => e.preventDefault()}
                onCopy={(e) => e.preventDefault()}
                onCut={(e) => e.preventDefault()}
                onContextMenu={(e) => e.preventDefault()}
                placeholder={lockoutTimer > 0 ? "Akses Sementara Terkunci" : "SEC-XXXXXX"}
                value={password}
                onChange={(e) => setPassword(e.target.value.toUpperCase())}
                className="w-full text-center tracking-widest font-mono text-lg font-bold py-3.5 px-4 rounded-2xl bg-black/60 border border-white/15 text-white placeholder-slate-700 focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/20 transition-all uppercase select-none disabled:opacity-40 disabled:cursor-not-allowed"
              />
              <KeyRound className="w-4 h-4 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          <div className="space-y-3">
            <button
              type="submit"
              disabled={isFormDisabled}
              className="w-full py-3.5 px-4 rounded-xl liquid-chrome-btn text-xs uppercase tracking-wider font-bold flex items-center justify-center space-x-2 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isVerifying ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Memvalidasi Kode...</span>
                </>
              ) : lockoutTimer > 0 ? (
                <span>Tunggu ({lockoutTimer}s)</span>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Buka Akses Studio</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Anonymous Footer info */}
        <div className="mt-6 pt-4 border-t border-white/5 text-center">
          <p className="text-[10px] text-slate-600 font-mono tracking-wider uppercase">
            Protected Gateway • Anti-Tamper & Bruteforce Shield Active
          </p>
        </div>
      </div>
    </div>
  );
}
