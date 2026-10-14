# WORK BREAKDOWN STRUCTURE (WBS) & ACTIONABLE IMPLEMENTATION TASKS
## VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM & UNIVERSAL VENTURE INCUBATOR HUB
**Daftar Tugas Rekayasa Perangkat Lunak Langkah demi Langkah (Sprint Backlog)**  
*Versi: 1.0 (Actionable Checklist / 6-Week Vertical Slice)*  
*Status Progress: [ ] 0% Completed*  

---

## PANDUAN PENGGUNAAN DOKUMEN INI
Dokumen ini adalah kompas pengerjaan harian Anda dan AI pair-programmer. Setiap tugas dirancang modular dan mandiri.
* `[ ]` : Belum dikerjakan (*To Do*)
* `[/]` : Sedang dikerjakan (*In Progress*)
* `[x]` : Selesai dan terverifikasi lolos uji (*Done*)
* `[-]` : Ditunda atau dibatalkan (*Skipped/Blocked*)

---

## SPRINT 1: NATIVE STATE MACHINE & REPOSITORY FOUNDATION (MINGGU 1)
*Fokus: Membangun fondasi folder, skema data Pydantic, dan mesin Finite State Machine (FSM) native tanpa framework eksternal.*

### 1.1 Inisialisasi Repositori & Environment
- [x] **TASK-1.1.1:** Setup struktur folder kanonikal sesuai [PRD.md](file:///d:/my%20project/VIRTUAL%20TECH%20STARTUP%20MULTI-AGENT%20SYSTEM/PRD.md#L453) (`backend/`, `frontend/`, `sandboxes/`, `prompts/`).
- [x] **TASK-1.1.2:** Buat file `.env.example` dan `.env` lokal berdasarkan template di PRD Section 14.
- [x] **TASK-1.1.3:** Setup virtual environment Python 3.11+ dan buat file `backend/requirements.txt` minimal (`fastapi`, `uvicorn`, `pydantic`, `httpx`, `aiosqlite`, `cryptography`).
- [x] **TASK-1.1.4:** Buat file `backend/app/core/config.py` menggunakan `pydantic-settings` untuk memuat konfigurasi `.env`.

### 1.2 State Container & Pydantic Data Contracts (SSOT)
- [x] **TASK-1.2.1:** Buat file `backend/app/engine/state.py` yang memuat class `VentureState`.
- [x] **TASK-1.2.2:** Definisikan skema kontrak data ketat di `state.py`:
  - `BusinessBriefSchema` (CoS output)
  - `SystemArchitectureSchema` (CTO output)
  - `PRDContractSchema` (PM output)
  - `UIComponentSpecSchema` (UI Designer output)
  - `QualityGateScorecard` (QA output)
- [x] **TASK-1.2.3:** Buat unit test awal `tests/test_state.py` untuk memvalidasi serialisasi dan parsing JSON Pydantic.

### 1.3 Native Asynchronous State Machine Engine
- [x] **TASK-1.3.1:** Buat file `backend/app/engine/state_machine.py` (< 250 baris kode murni).
- [x] **TASK-1.3.2:** Implementasikan method `register_node(state_name, handler)` dan `register_router(state_name, router_func)`.
- [x] **TASK-1.3.3:** Implementasikan method `step(state)` dengan mekanisme checkpointing otomatis.
- [x] **TASK-1.3.4:** Buat unit test `tests/test_state_machine.py` untuk menguji transisi state dummy dari `INIT` $\to$ `SPARRING` $\to$ `GATE_1`.

---

## SPRINT 2: BYOK UNIVERSAL LLM GATEWAY & PERSISTENT MEMORY (MINGGU 2)
*Fokus: Mengintegrasikan koneksi ke berbagai model LLM (DeepSeek, Claude, Gemini, Ollama) dan SQLite Blackboard Memory.*

### 2.1 Native BYOK LLM Multi-Provider Client
- [x] **TASK-2.1.1:** Buat file `backend/app/gateway/client.py` yang mendefinisikan class `UnifiedLLMClient`.
- [x] **TASK-2.1.2:** Buat adapter `backend/app/gateway/adapters/openai_compatible.py` untuk DeepSeek, Groq, Mistral, OpenRouter, dan Ollama lokal.
- [x] **TASK-2.1.3:** Buat adapter `backend/app/gateway/adapters/anthropic_adapter.py` untuk Claude 3.5 Sonnet / Haiku.
- [x] **TASK-2.1.4:** Buat adapter `backend/app/gateway/adapters/gemini_adapter.py` untuk Gemini 2.5 Flash / Pro.
- [x] **TASK-2.1.5:** Implementasikan fungsi generator asinkron `stream_tokens()` pada `UnifiedLLMClient` untuk streaming SSE.
- [x] **TASK-2.1.6:** Implementasikan fallback cascade otomatis jika API utama mengalami *rate limit* (429) atau downtime.

### 2.2 SQLite Blackboard Memory & 3-Tier Context Projection
- [x] **TASK-2.2.1:** Buat file `backend/app/db/session.py` untuk inisialisasi koneksi `aiosqlite` dengan WAL mode.
- [x] **TASK-2.2.2:** Buat skrip migrasi database awal untuk membuat tabel `projects`, `agent_event_logs`, `state_checkpoints`, dan `vault_secrets`.
- [x] **TASK-2.2.3:** Buat file `backend/app/engine/memory.py` yang mendefinisikan class `MemoryManager`.
- [x] **TASK-2.2.4:** Implementasikan method `log_event()` untuk mencatat percakapan dengan penanda `sender_role` dan `recipient_role`.
- [x] **TASK-2.2.5:** Implementasikan pipa 3-lapis `build_context_for_agent()`:
  - Tier 1: Pinned Contracts (OpenAPI & PRD).
  - Tier 2: Role Direct Mentions & Broadcast.
  - Tier 3: Sliding Window N percakapan terakhir + summarization trigger.

---

## SPRINT 3: THE EXECUTIVE SPARRING ROOM & STAGE-GATE 1 (MINGGU 3)
*Fokus: Mengaktifkan interaksi nyata antara Founder (Anda), CoS Agent, dan CTO Agent hingga menghasilkan konsep produk yang disetujui.*

### 3.1 System Prompts Registry
- [x] **TASK-3.1.1:** Buat file prompt `backend/prompts/cos_prompt.md` (Persona business partner, kritis terhadap profit, kalkulasi TAM/SAM/SOM).
- [x] **TASK-3.1.2:** Buat file prompt `backend/prompts/cto_prompt.md` (Persona technical architect, pengunci 4 Golden Paths, kalkulasi biaya token).
- [x] **TASK-3.1.3:** Buat loader prompt otomatis di `backend/app/core/prompts.py`.

### 3.2 Implementasi Node Agen Eksekutif
- [x] **TASK-3.2.1:** Buat file `backend/app/engine/nodes/cos.py` (Node CoS menghasilkan `BusinessBriefSchema`).
- [x] **TASK-3.2.2:** Buat file `backend/app/engine/nodes/cto.py` (Node CTO menghasilkan `SystemArchitectureSchema`).
- [x] **TASK-3.2.3:** Integrasikan auto-correction loop jika output LLM tidak sesuai dengan JSON schema Pydantic (maksimal 2x perbaikan).
- [x] **TASK-3.2.4:** Implementasikan router transisi `router_gate_1()` di state machine untuk menangani keputusan CEO: `APPROVE`, `REVISE`, atau `KILL`.

---

## SPRINT 4: EPHEMERAL SANDBOX & DEMO DAY ENGINE (MINGGU 4)
*Fokus: Mengotomatisasi eksekusi prototipe mock di dalam kontainer Docker lokal dan routing dinamis Caddy (Stage-Gate 2).*

### 4.1 Docker Base Images & Dynamic Reverse Proxy
- [x] **TASK-4.1.1:** Buat Dockerfile base `sandboxes/base-frontend/Dockerfile` dengan Next.js 14, Tailwind, dan Lucide pre-installed.
- [x] **TASK-4.1.2:** Buat file konfigurasi Caddy `sandboxes/caddy/Caddyfile` dengan admin API aktif di port `2019`.
- [x] **TASK-4.1.3:** Buat modul `backend/app/sandbox/runner.py` untuk alokasi port dinamis (range 4000-4999) dan Docker volume mounting.
- [x] **TASK-4.1.4:** Buat modul `backend/app/sandbox/proxy.py` untuk mendaftarkan subdomain `demo-<id>.local.sandbox` ke Caddy via REST API.

### 4.2 Prototyping Code Generator (Product & Frontend Guild)
- [x] **TASK-4.2.1:** Buat node `backend/app/engine/nodes/pm.py` (Menghasilkan Lean PRD dan mengunci OpenAPI 3.1 Spec).
- [x] **TASK-4.2.2:** Buat node `backend/app/engine/nodes/ui_ux.py` (Menghasilkan UI Spec dan skema komponen visual).
- [x] **TASK-4.2.3:** Buat node `backend/app/engine/nodes/frontend.py` untuk menghasilkan kode Next.js berbasis `MockServiceAdapter`.
- [x] **TASK-4.2.4:** Uji coba end-to-end: Kode mock yang dihasilkan otomatis termount ke kontainer dan tampil di browser dalam waktu `< 5 detik`.

---

## SPRINT 5: FASTAPI API & THE CEO COCKPIT DASHBOARD (MINGGU 5)
*Fokus: Membangun backend REST/SSE dan antarmuka web interaktif Next.js split-screen.*

### 5.1 FastAPI Backend Endpoints
- [x] **TASK-5.1.1:** Implementasikan router `backend/app/api/v1/projects.py` (CRUD proyek venture).
- [x] **TASK-5.1.2:** Implementasikan endpoint SSE streaming `backend/app/api/v1/sparring.py` (`/projects/{id}/stream`).
- [x] **TASK-5.1.3:** Implementasikan endpoint gerbang `backend/app/api/v1/gates.py` (`/projects/{id}/gates/{gate_id}/decision`).
- [x] **TASK-5.1.4:** Buat file `backend/main.py` yang mengintegrasikan CORS, middleware logging, dan router API.

### 5.2 Next.js 14 Cockpit Dashboard UI
- [x] **TASK-5.2.1:** Inisialisasi proyek `frontend/` menggunakan Next.js 14 App Router, TypeScript, dan Tailwind CSS.
- [x] **TASK-5.2.2:** Buat hook `frontend/src/hooks/useSSEStream.ts` untuk mendengarkan event token dan status agen secara real-time.
- [x] **TASK-5.2.3:** Buat halaman Sparring Room `frontend/src/app/sparring/[id]/page.tsx` (Chat bubble streaming CoS & CTO).
- [x] **TASK-5.2.4:** Buat halaman Split-Screen Demo Preview `frontend/src/app/preview/[id]/page.tsx` (iFrame Webview di kiri, CEO Control Buttons di kanan).
- [x] **TASK-5.2.5:** Buat halaman Portfolio Hub `frontend/src/app/page.tsx` untuk menampilkan daftar proyek aktif dan metrik P&L.

---

## SPRINT 6: INDUSTRIALIZATION, SECRET VAULT & PAAS DEPLOY (MINGGU 6)
*Fokus: Mengaktifkan koding produksi backend, enkripsi AES-256 kredensial, QA testing, dan deployment live.*

### 6.1 Secret Vault & Production Hardening
- [x] **TASK-6.1.1:** Buat modul `backend/app/core/security.py` yang mengimplementasikan class `SecretVaultManager` (AES-256-GCM).
- [x] **TASK-6.1.2:** Buat modal form input Secret Vault di Dashboard Frontend (Stage-Gate 3).
- [x] **TASK-6.1.3:** Buat node `backend/app/engine/nodes/backend.py` yang menghasilkan FastAPI endpoints riil, model SQLAlchemy, dan skrip migrasi Alembic.
- [x] **TASK-6.1.4:** Implementasikan peralihan frontend dari `MockServiceAdapter` ke `HttpServiceAdapter` tanpa mengubah komponen UI.

### 6.2 QA Evals, Legal Bundle & Deployment Bridge
- [x] **TASK-6.2.1:** Buat node `backend/app/engine/nodes/qa.py` yang menjalankan pemindaian Semgrep (OWASP Top 10) dan evaluasi akurasi LLM.
- [x] **TASK-6.2.2:** Buat node `backend/app/engine/nodes/legal.py` yang meng-generate file `/terms`, `/privacy`, dan `/refund`.
- [x] **TASK-6.2.3:** Buat modul `backend/app/engine/nodes/devsecops.py` yang berkomunikasi dengan Coolify API atau Railway API untuk deploy produksi otomatis.
- [x] **TASK-6.2.4:** Uji coba validasi final: Menjalankan satu siklus penuh dari ide mentah $\to$ Sparring $\to$ Demo Prototype $\to$ Production Deployment pada Arketipe 1 (CRUD SaaS).

---

## DEFINITION OF DONE (DoD) TINGKAT PROYEK (PoC RELEASE)
Proyek ini dinyatakan berhasil menyelesaikan fase PoC apabila:
1. Seluruh checkbox tugas di atas telah berstatus `[x]`.
2. Dari input ide bisnis di dashboard, prototipe web interaktif dapat diklik di Webview dalam waktu `< 15 menit`.
3. Kunci API produksi terbukti aman dienkripsi menggunakan AES-256 dan tidak pernah terekspos dalam log plaintext.
4. Model LLM untuk CoS/CTO/Engineering dapat diganti dengan model lain cukup dengan mengubah konfigurasi file `.env`.
