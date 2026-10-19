# 📚 KNOWLEDGE SYSTEM & ARCHITECTURAL MASTER SPECIFICATION
## Virtual Tech Startup Multi-Agent System & Sovereign Autonomous Corporate OS
**Dokumen Induk Pengetahuan, Arsitektur Sistem, Kontrak API, dan Tata Kelola Korporat Otonom**  
*Single Source of Truth (SSOT) untuk Pengembangan, Pemeliharaan, dan Operasional AI Multi-Agent*

---

## 1. Visi Eksekutif & Filosofi Desain

### 1.1 Latar Belakang & Visi Produk
**Virtual Tech Startup Multi-Agent System** adalah sistem operasi korporasi kecerdasan buatan mandiri (*Sovereign Autonomous AI Corporate Operating System*) dan platform inkubasi startup digital berbasis *Human-in-the-Loop*. Platform ini dirancang untuk memberdayakan seorang **Solo Founder / Chairman & CEO** dalam mengoperasikan konglomerasi digital berskala penuh secara mandiri:
- Mengubah ide bisnis mentah menjadi aplikasi perangkat lunak produksi siap pakai.
- Mengotomatisasi riset pasar, spesifikasi OpenAPI, rekayasa paralel Frontend & Backend, pengujian mutu, dan audit keamanan statis.
- Mengelola struktur organisasi multi-divisi dinamis, *branching workflow* bergaya Git, dan buku kas keuangan token riil.

### 1.2 Tiga Prinsip Rekayasa Inti
1. **Native-First & Zero Framework Lock-in:**
   - Logika orkestrasi dibangun murni menggunakan Python Asynchronous State Machine (< 200 baris per modul) tanpa dependensi runtime pihak ketiga yang rapuh (seperti LangChain atau LangGraph).
2. **Bring Your Own Key (BYOK) Universal Gateway:**
   - Kompatibilitas langsung dengan OpenRouter, DeepSeek, Anthropic, Gemini, OpenAI, Groq, dan Ollama lokal. Pergantian model dapat dilakukan secara dinamis per peran tanpa mematikan server.
3. **"Show, Don’t Tell" Ephemeral Prototyping:**
   - Sebelum menulis kode backend skala besar dan migrasi database yang memboroskan token, sistem memvalidasi purwarupa antarmuka di dalam *Pre-Warmed Ephemeral Sandbox* yang dapat diuji interaktif di browser.
4. **Contract-Driven & 100% Slug-Free Roles:**
   - Komunikasi dan penugasan peran tidak lagi mengandalkan kolom slug statis yang redundan. Peran dikelola secara dinamis di database organisasi (`corporate_roles`) berdasarkan nama, jobdesk, instruksi sistem, permission, dan model LLM.

---

## 2. Arsitektur Berlapis (Layered System Architecture)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FOUNDER EXECUTIVE DASHBOARD                                    │
│                              Next.js 14 App Router • TypeScript • Vanilla CSS                    │
│                                                                                                  │
│  /                 /organization         /kanban/[id]         /preview/[id]       /office        │
│  Portfolio Hub     Org Studio & DND      Mission Control      Live Sandbox, PTY   Global Oasis   │
│  & Venture State   Pipeline Builder      & Live Lounge WS     Terminal & Backup   Command HQ     │
│                                                                                                  │
│  /analytics        /settings             /wisdom              /sparring/[id]                     │
│  CFO Observability BYOK & Secret Vault   Vector RAG Base      Executive Sparring                 │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ REST API / WebSocket / SSE Streams
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI HIGH-CONCURRENCY BACKEND                                 │
│                                   Pure ASGI Middleware Engine                                    │
│                                                                                                  │
│  • SecurityGateMiddleware (Stealth Dynamic PIN + Telegram Bot Gate)                             │
│  • ProcessTimeLoggingMiddleware & SQLite WAL (`PRAGMA busy_timeout = 5000;`)                     │
│  • 21 Modular REST & WebSocket Routers                                                           │
└───────────────────────┬──────────────────────────────────────────────────┬───────────────────────┘
                        │                                                  │
                        ▼                                                  ▼
┌──────────────────────────────────────────────┐   ┌───────────────────────────────────────────────┐
│         DYNAMIC ASYNC KANBAN ENGINE          │   │         CORPORATE EVENT BUS (PUB/SUB)         │
│ • Ticket Lifecycle: BACKLOG ➔ TODO ➔         │   │ • Non-blocking asyncio.Queue per Project      │
│   IN_PROGRESS ➔ REVIEW ➔ DONE                │◄─►│ • SQLite WAL Message Ledger Persistence       │
│ • Task Concurrency Dispatcher (DAG Gather)   │   │ • Real-time WebSocket Lounge Broadcast       │
│ • Dependency Resolution & Priority Sorting   │   │ • Scoped @mention Targeted Context Injection  │
└───────────────────────┬──────────────────────┘   └───────────────────────┬───────────────────────┘
                        │                                                  │
                        ▼                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                EXECUTIVE GOVERNANCE & GUARDRAILS                                 │
│                                                                                                  │
│  • Agent Decision Envelope: { PROCEED | CONSULT_ROLE | ESCALATE_TO_C_LEVEL | REQUEST_REWORK }     │
│  • Anti-Infinite Loop Circuit Breaker: Auto-Freeze Ticket pada >= 3 putaran perdebatan berulang │
│  • Autonomous Financial Guardrail: Hard Quota ($1.50 / 350.000 tokens per tiket)                 │
│  • 1-Click CEO Strategic Intervention & Veto (Force Proceed / Chat Directive / Reassign Role)    │
│  • Three-Way Branch Merge Engine: LCA Graph Traversal untuk Corporate Branch Merging             │
└───────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                CORE COGNITIVE & EXECUTION ENGINES                                │
│                                                                                                  │
│  • Sovereign Model Router: Multi-Channel Failover (9router-style), sliding-window RPM/TPM radar  │
│  • Dynamic Thinking Level Control: Reasoning Effort (None, Low, Medium, High)                    │
│  • Corporate Wisdom Base: 128-dim Vector Memory RAG + Auto-Sync saat boot & mutasi organisasi   │
│  • Real AST OWASP Security Scanner: Deteksi celah keamanan statis pada kode yang dihasilkan      │
│  • Ephemeral Sandbox & CoW Snapshots: Backup direktori instan dan 1-Click Rollback               │
│  • Cascading Project Deletion: Zero-orphan cleanup database, tiket, log, dan folder disk        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Komponen Utama & Alur Kerja

### 3.1 Siklus Hidup Venture (Venture Lifecycle State Machine)
Siklus inkubasi produk teknologi berjalan melalui tahapan formal:
1. `SPARRING_ROOM`: Socratic briefing antara Founder, CoS, CTO, dan peran terkait.
2. `GATE_1_WAITING`: Evaluasi kelayakan bisnis (Market Feasibility & Tech Stack Approval oleh CEO).
3. `PRD_AND_SPECS`: Penyusunan PRD, Arsitektur Sistem, dan Kontrak OpenAPI 3.1 SSOT.
4. `MOCK_PROTOTYPING`: Pembuatan prototipe UI interaktif di Sandbox (HTML/Next.js).
5. `GATE_2_WAITING`: Persetujuan purwarupa visual oleh CEO sebelum alokasi anggaran produksi.
6. `PRODUCTION_HARDENING`: Penulisan kode produksi, integrasi database, unit test, dan AST OWASP security scan.
7. `PROJECT_KILLED`: Pembekuan proyek apabila tidak lolos validasi bisnis.

### 3.2 Dynamic Corporate Organization & Branching
- **Samsung Conglomerate Model**: Mendukung 1 perusahaan induk virtual dengan cabang (*branch*) independen.
- **Git-Style Branching**: Branch `branch_main` terisolasi sebagai lini produksi utama. Pengguna dapat melakukan `Fork Branch`, bereksperimen dengan struktur tim dan alur kerja baru, lalu mengajukan Pull Request (`corporate_pull_requests`) dengan algoritma penggabungan LCA (*Lowest Common Ancestor*).
- **100% Slug-Free Dynamic Roles**: Kolom `slug` telah dihapus secara permanen dari basis data dan runtime. Setiap agen dikenali melalui `role_id` unik dan nama deskriptif.

### 3.3 Dynamic Multi-Pipeline & HTML5 DND Builder
- **Bukan Sekuensial Kaku**: Mendukung pipeline yang dapat berulang (*dynamic looping pipeline*, misalnya QA me-reject tiket kembali ke Backend).
- **Multi-Product Line**: Template terpisah untuk Software SaaS, Edukasi, Copywriting, dan Custom.
- **CEO Stage Gate Node**: Simpul gerbang persetujuan CEO dapat digeser (*drag-and-drop*) langsung ke canvas pipeline.

### 3.4 Office HQ Command Center (`/office`)
- **Obsidian Liquid 2D Engine**: Antarmuka berkinerja tinggi, zero GPU bloat, dan elegan.
- **Kebijakan Ketat Zero-Token Saat Idle**: Tidak ada pemanggilan LLM latar belakang saat tidak ada tugas aktif.
- **Scoped `@mention` Dispatcher**: Menyebut agen tertentu (`@CTO`, `@Frontend Engineer`) hanya menyuntikkan pesan ke jendela konteks agen yang dituju tanpa membebani agen lain.
- **Live Stream Filters**: Kategori All Streams, Execution & Handoffs, CEO Decision Gates, dan Oasis Lounge.

### 3.5 Sovereign Model Router & CFO Observability
- **Sliding-Window Rate Limiter**: Memantau Request Per Minute (RPM) dan Token Per Minute (TPM) secara proaktif.
- **Auto-Failover Chain**: Jika kanal upstream (misal DeepSeek) mengalami timeout atau error 429 (Rate Limit), router otomatis mengalihkan permintaan ke kandidat berikutnya pada rantai fallback.
- **CFO Token Ledger**: Pencatatan riil seluruh inferensi ke tabel `corporate_token_ledger` dengan atribusi biaya per peran.
- **Hard Budget Cap**: Proteksi batas pengeluaran (default $50.00) dengan auto-freeze anti-cost runaway.

### 3.6 Corporate Wisdom Base
- **Embedded Vector RAG**: Menggunakan representasi vektor 128 dimensi untuk pencarian semantik terhadap SOP perusahaan, postmortem, dan keputusan arsitektur.
- **Sinkronisasi Otomatis Ganda**:
  1. *Boot Server*: Mengekstrak seluruh bagan divisi dan peran saat inisialisasi database.
  2. *Live Mutation*: Terpicu otomatis setiap kali ada penambahan, modifikasi, atau penghapusan divisi dan peran di `/organization`.

### 3.7 Ephemeral Sandbox & 1-Click Rollback
- Direktori workspace terisolasi di `workspaces/{project_id}` dan `sandbox_storage/{project_id}`.
- Pembuatan snapshot direktori instan dan tombol 1-Click Rollback untuk memulihkan kode ke kondisi stabil jika terjadi regresi.

---

## 4. Spesifikasi Kontrak API (RESTful & WebSocket)

Semua endpoint beroperasi di bawah base URL `/api/v1` dengan autentikasi header `Authorization: Bearer <session_token>`.

### 4.1 Projects API (`/projects`)
- `POST /projects`: Mendaftarkan venture baru (payload: `name`, `founder_idea`).
- `GET /projects`: Mengambil daftar portofolio venture beserta rekap biaya token dan P&L.
- `GET /projects/{project_id}`: Detail state machine dan artefak venture.
- `DELETE /projects/{project_id}`: **Cascading Clean Sweep** (menghapus record venture, checkpoints, event logs, tickets, messages, financial ledger, PRs, snapshots, sentinel findings, serta folder fisik disk).

### 4.2 Sparring API (`/projects/{project_id}/sparring`)
- `GET /projects/{project_id}/sparring/history`: Mengambil riwayat percakapan sparring.
- `POST /projects/{project_id}/sparring/chat`: Mengirim pesan ke sparring room. Mendukung `@mention` dinamis untuk melibatkan peran mana pun di organisasi.
- `POST /projects/{project_id}/sparring/reset`: Mengosongkan riwayat percakapan.

### 4.3 Governance & Stage Gates (`/projects/{project_id}/gates`)
- `GET /projects/{project_id}/gates/{gate_name}`: Memeriksa status persetujuan gerbang (`GATE_1` atau `GATE_2`).
- `POST /projects/{project_id}/gates/{gate_name}/approve`: Menyetujui gerbang dan memicu transisi state berikutnya.
- `POST /projects/{project_id}/gates/{gate_name}/reject`: Menolak gerbang dengan umpan balik revisi.

### 4.4 Corporate Management (`/corporate`)
- `GET /corporate/branches`: Mengambil seluruh branch kerja.
- `POST /corporate/branches/fork`: Melakukan fork branch aktif menjadi cabang eksperimen baru.
- `GET /corporate/branches/{branch_id}/full`: Mengambil struktur utuh divisi, peran, dan pipeline pada branch.
- `POST /corporate/divisions`: Membuat divisi baru.
- `POST /corporate/roles`: Mendaftarkan karyawan AI baru (payload: `name`, `division_id`, `jobdesk`, `system_instruction`, `permissions`, `model_name`, `provider`, `temperature`, `thinking_level`).
- `PUT /corporate/roles/{role_id}`: Memperbarui spesifikasi peran karyawan AI.
- `DELETE /corporate/roles/{role_id}`: Menghapus peran dari organisasi.
- `POST /corporate/pipelines`: Menyimpan struktur multi-pipeline dan node stage canvas.

### 4.5 Tickets & Kanban Engine (`/tickets`)
- `GET /tickets?project_id={id}`: Mengambil seluruh tiket Kanban per venture.
- `POST /tickets`: Membuat tiket kerja baru.
- `PUT /tickets/{ticket_id}/status`: Memperbarui status siklus tiket (`BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`).
- `POST /tickets/dispatch`: Memicu eksekusi agen asinkron untuk tiket berstatus TODO.

### 4.6 Office HQ & Streaming (`/office`)
- `GET /office/messages?project_id={id}`: Mengambil riwayat feed pesan komando.
- `POST /office/messages`: Mengirim instruksi dari Founder atau agen (mendukung `@mention`).
- `WS /office/ws/{project_id}`: WebSocket duplex untuk live stream pemikiran agen, handoff, dan lounge.

### 4.7 Analytics & CFO Observability (`/analytics`)
- `GET /analytics/token-summary`: Akumulasi total input/output token, biaya USD, dan rasio fallback.
- `GET /analytics/burn-rate`: Timeline pengeluaran biaya dan token per hari.
- `GET /analytics/role-costs`: Rincian pengeluaran token dan biaya per peran AI.
- `GET /analytics/channel-health`: Status kesehatan kanal upstream router, kuota RPM/TPM, dan cooldown.
- `POST /analytics/budget-cap`: Menetapkan batas anggaran maksimal (hard-stop limit).

### 4.8 Sandbox & Snapshots (`/sandbox`)
- `GET /sandbox/{project_id}/snapshots`: Daftar checkpoint snapshot direktori kode.
- `POST /sandbox/{project_id}/snapshots`: Membuat snapshot cadangan baru.
- `POST /sandbox/{project_id}/snapshots/{snapshot_id}/rollback`: 1-Click Rollback ke versi snapshot.
- `DELETE /sandbox/{project_id}/snapshots/{snapshot_id}`: Menghapus arsip snapshot.

### 4.9 Corporate Wisdom Base (`/wisdom`)
- `GET /wisdom/documents`: Daftar dokumen pengetahuan dan arsitektur korporat.
- `POST /wisdom/query`: Pencarian semantik vector RAG terhadap memori korporat.
- `POST /wisdom/import-github`: Impor skill/blueprint repositori GitHub menjadi wisdom korporat.

---

## 5. Standar Rekayasa & Kualitas Kode

Sesuai aturan ketat pada `code-quality-rules.md`:
1. **Single Responsibility Principle (SRP) & Batas Berkas**:
   - Maksimal 150–200 baris kode per berkas. Jika melebihi batas, modul wajib dipecah menjadi sub-komponen terfokus.
2. **Type Hints Lengkap**:
   - Wajib menyertakan type hint pada seluruh parameter dan nilai return fungsi/method Python dan TypeScript.
3. **Docstring Google-Style**:
   - Setiap kelas dan fungsi utama wajib memiliki docstring ringkas yang menjelaskan tugas dan argumennya.
4. **Logging Terpusat (Dilarang `print`)**:
   - Menggunakan logger terkonfigurasi (`loguru` atau logger internal). Penggunaan `print()` dilarang keras di seluruh kode produksi.
5. **Penanganan Eksepsi Spesifik**:
   - Wajib menggunakan `try-except` spesifik pada seluruh operasi I/O, koneksi basis data, network call, dan parsing data. Dilarang menggunakan bare `except:`.
6. **Code Hygiene**:
   - Wajib membersihkan *dead code*, variabel tidak terpakai, dan unused imports sebelum tugas diselesaikan.
7. **Jaminan Uji Menyeluruh**:
   - Setiap penambahan fitur wajib disertai unit test atau integration test di direktori `backend/tests/` dan diverifikasi dengan `pytest` (100% passed).
