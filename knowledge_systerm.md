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
│  /mcp              /skills               /analytics           /settings           /wisdom        │
│  MCP Server Hub    Public Skill Library  CFO Observability    BYOK & Vault        FastEmbed ONNX │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ REST API / WebSocket / SSE Streams
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI HIGH-CONCURRENCY BACKEND                                 │
│                                   Pure ASGI Middleware Engine                                    │
│                                                                                                  │
│  • SecurityGateMiddleware (Stealth Dynamic PIN + OpenClaw Trust Boundary)                       │
│  • ProcessTimeLoggingMiddleware & SQLite WAL (`PRAGMA busy_timeout = 5000;`)                     │
│  • 21 Modular REST & WebSocket Routers                                                           │
└───────┬───────────────────────────────────────────────────────────────────┬──────────────────────┘
        │                                                                   │
        ▼                                                                   ▼
┌──────────────────────────────────────────────┐    ┌──────────────────────────────────────────────┐
│       AUTONOMOUS KANBAN RUNNER ENGINE        │    │        CORPORATE EVENT BUS (PUB/SUB)         │
│ • SQLite WAL Atomic Claim Query              │    │ • Non-blocking asyncio.Queue per Project     │
│   (UPDATE ... WHERE id=? AND status='TODO')  │◄──►│ • SQLite WAL Message Ledger Persistence      │
│ • Task Concurrency Dispatcher (Semaphore)    │    │ • Real-time WebSocket Lounge Broadcast      │
│ • FileLockManager (Path Mutex Concurrency)   │    │ • Scoped @mention Targeted Context Injection │
└───────────────────────┬──────────────────────┘    └──────────────────────┬───────────────────────┘
                        │                                                  │
                        ▼                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                EXECUTIVE GOVERNANCE & GUARDRAILS                                 │
│                                                                                                  │
│  • Agent Decision Envelope: { PROCEED | CONSULT_ROLE | ESCALATE_TO_C_LEVEL | REQUEST_REWORK }     │
│  • Anti-Infinite Loop Circuit Breaker: Auto-Freeze Ticket pada >= 3 putaran perdebatan berulang │
│  • Autonomous Financial Guardrail: Hard Quota ($1.50 / 350.000 tokens) & Dynamic Pricing Ledger   │
│  • 1-Click CEO Strategic Intervention & Veto (Force Proceed / Chat Directive / Reassign Role)    │
│  • Three-Way Branch Merge Engine: LCA Graph Traversal untuk Corporate Branch Merging             │
└───────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             TWO-TIER COGNITIVE & EXECUTION ENGINES                               │
│                                                                                                  │
│  • Sovereign Model Router: Multi-Channel Failover (9router-style), Hermes Credential Pool        │
│  • Two-Tier CoV Gatekeeper: Tier 1 Deterministic Guard (0ms, 0 Token) & Tier 2 LLM Critic       │
│  • Worker Self-Repair Loop: CoV murni sebagai auditor; Agen Peran wajib memperbaiki parameter    │
│  • Hermes Layered Context Compactor: Tool output pruning (>400 baris) & tail retention          │
│  • Corporate Wisdom Base: FastEmbed ONNX 384-dim Neural RAG (Thread-Offloaded & Pre-warmed)      │
│  • Dynamic Tool Registry: Local Tools, Custom Tools (corporate_custom_tools), & MCP Dispatcher  │
│  • Telegram Secretary Daemon: Background Long Polling, Sender Whitelist & Inline Approval Gate   │
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

### 3.5 Sovereign Model Router, Polymorphic Cost Accounting & Hermes Credential Pool
- **Polymorphic Contract Strategy (`contract_handlers.py`)**: Menggantikan logika rantai `if-elif` statis dengan arsitektur polymorphic handler berorientasi objek (`BaseContractHandler`) untuk validasi output: `ArchitectureContractHandler`, `PRDContractHandler`, `UIComponentContractHandler`, `CodeBundleContractHandler`, dan `QualityScorecardContractHandler`.
- **Dynamic Pricing & Real Accounting**: Menghapus biaya token statis flat `$0.02`. Biaya dihitung secara riil berdasarkan harga token aktual per juta token (input & output) sesuai model yang digunakan dan dicatat ke `corporate_token_ledger` melalui `token_ledger_repo.py`.
- **Pre-Flight & Post-Flight Financial Guardrail**: Terintegrasi langsung dengan `financial_guardrail.py`. Sebelum inferensi dijalankan, router memvalidasi kuota tiket. Jika melebihi $1.50 atau 350.000 token, tiket otomatis dibekukan (`FROZEN_PENDING_APPROVAL`). Pasca-inferensi, router mencatat penggunaan aktual secara atomik.
- **Hermes Multi-Key Pool & Sliding-Window Cooldown**: Mendukung rotasi kunci jamak (*multi-credential pooling*), *exponential backoff*, dan pendinginan status kanal secara otomatis saat menerima HTTP 429 atau 503.

### 3.6 Corporate Wisdom Base & FastEmbed ONNX Local Neural RAG
- **Local Neural Embeddings (384 Dimensi)**: Menggunakan engine **FastEmbed ONNX** lokal (`BAAI/bge-small-en-v1.5`) yang menghasilkan representasi dense vector 384 dimensi dengan normalisasi $L_2$, menggantikan hashing non-semantik CRC32.
- **Asynchronous Non-Blocking Inference**: Eksekusi ONNX dijalankan secara terisolasi via worker thread pool menggunakan `asyncio.to_thread()`, menjamin *event loop* asyncio FastAPI tidak pernah mengalami *blocking*.
- **Lifespan Pre-warming**: Model embedding di-cache dan di-prewarm satu kali saat server FastAPI boot via `lifespan` di `backend/main.py`.
- **Graceful Fallback**: Dilengkapi mekanisme fallback 128-dimensi deterministik apabila dependensi FastEmbed belum terunduh secara lengkap di lingkungan cold start.

### 3.7 Ephemeral Sandbox & 1-Click Rollback
- Direktori workspace terisolasi di `workspaces/{project_id}` dan `sandbox_storage/{project_id}`.
- Pembuatan snapshot direktori instan dan tombol 1-Click Rollback untuk memulihkan kode ke kondisi stabil jika terjadi regresi.

### 3.8 Two-Tier Chain-of-Verification (CoV) Pre-Flight Gatekeeper & Worker Repair Loop
- **Two-Tier Architecture (`verifier.py`)**:
  - **Tier 1 (Deterministik Python — 0ms, 0 Token)**: Memverifikasi validitas skema Pydantic, tipe parameter, dan izin perkakas peran (*role tool permissions*). Operasi pembacaan aman (*read-only tools* seperti `read_codebase`, `search_codebase`, `inspect_db_schema`, `git_diff_summary`) langsung berstatus `APPROVED` tanpa memanggil model LLM kedua.
  - **Tier 2 (LLM Pre-Flight Inspector)**: Khusus memeriksa pemanggilan alat mutasi (*mutating tools* seperti `write_codebase`, `synthesize_and_register_tool`, `lock_test_suite`) dan artefak kontrak tonggak akhir. Memastikan parameter lengkap dan aman sebelum eksekusi.
- **Filosofi Ketat "Critic-Only" (Tanpa Pembajakan & Tanpa Self-Repair)**:
  - CoV **HANYA** bertindak sebagai auditor/kritikus teknis independen. CoV dilarang keras melakukan perbaikan mandiri atau mengeksekusi perkakas atas namanya sendiri.
  - Jika parameter tidak lengkap atau pemanggilan cacat, CoV menetapkan status `REPAIR_REQUIRED` beserta `repair_feedback` yang spesifik (misal: "Alat OWASP membutuhkan parameter a, b, c, d, tetapi hanya a, b, c yang dikirim").
- **Autonomous Role-Worker Self-Repair Loop**:
  - Agen peran pemanggil menerima umpan balik koreksi dari CoV, memperbaiki parameternya secara mandiri menggunakan konteks domain lengkapnya, dan mengirimkan kembali respons hasil perbaikan.
  - Setelah CoV memvalidasi dan memberikan lampu hijau (`APPROVED`), **agen peran itu sendiri yang mengeksekusi perkakasnya** dan menerima observasi langsung (*Non-Hijacking Execution*).

### 3.9 Autonomous Kanban Runner, Atomic Claim & File-Path Mutex Concurrency
- **Non-Blocking Background Scheduler (`kanban_runner.py`)**: Berjalan secara kontinu sebagai background task di siklus hidup aplikasi FastAPI, mengawasi tiket `TODO` yang seluruh dependensinya telah selesai.
- **SQLite WAL Atomic Claim Query**:
  ```sql
  UPDATE corporate_tickets 
  SET status = 'IN_PROGRESS', updated_at = CURRENT_TIMESTAMP 
  WHERE id = ? AND status = 'TODO' 
  RETURNING *;
  ```
  Menjamin tidak akan pernah terjadi eksekusi ganda (*double-execution*) pada tiket yang sama di antara beberapa worker paralel.
- **Concurrency Control & Active Lease Registry**: Eksekusi paralel dibatasi oleh `asyncio.Semaphore(MAX_CONCURRENT_AGENTS)` (default: 3 agen simultan) dan himpunan in-memory `active_ticket_ids` untuk mencegah kelebihan beban server.
- **FileLockManager (`file_lock_manager.py`)**: Manajemen *mutex lock* asinkron berbasis jalur berkas (`asyncio.Lock` per absolute file path). Mencegah tabrakan tulis (*race conditions*) saat beberapa agen bekerja paralel pada berkas atau modul yang berdekatan.

### 3.10 Dynamic Tool Registry & Persistent Synthesized Tools
- **Dynamic Tool Registry (`dynamic_tool_registry.py`)**: Registri perkakas yang dapat diperluas (*extensible*), menggantikan percabangan kaku dengan registrasi dinamis untuk perkakas bawaan, modul MCP (*Model Context Protocol*), dan perkakas kustom runtime.
- **SQLite Persistence (`corporate_custom_tools`)**: Menyimpan definisi perkakas yang disintesis (nama perkakas, deskripsi, skema JSON parameter, source code Python, peran pembuat, dan status persetujuan) ke dalam database SQLite.
- **Startup Auto-Reload**: Saat FastAPI memulai proses (`lifespan`), seluruh perkakas yang berstatus `is_approved = 1` secara otomatis dikompilasi ulang secara aman dan didaftarkan ke registri runtime, mencegah *wipeout* saat server di-restart.

### 3.11 Remote Executive Liaison: Telegram Secretary Daemon & Dynamic Tool Synthesis
- **Long Polling Daemon (`telegram_daemon.py`)**: Berjalan di latar belakang menggunakan `httpx.AsyncClient` tanpa memerlukan webhook publik dengan port forwarding rumit.
- **OpenClaw Trust Boundary (Whitelist Protection)**: Verifikasi identitas pengirim di gerbang terluar. Hanya pesan dari `user_id` yang terdaftar dalam `TELEGRAM_ALLOWED_USER_IDS` yang diproses. Upaya akses tanpa izin langsung ditolak dan dicatat sebagai *security probe* ke `flight_recorder.py`.
- **Dynamic Role Secretary Integration (`secretary_resolver.py`)**: Agen eksekutif personal Founder yang terdaftar resmi di tabel `corporate_roles` (di bawah `div_exec` atau memiliki permission `chat_telegram`), menjembatani instruksi Founder di Telegram dengan operasi internal organisasi. Konfigurasi model, persona, dan prompt yang diatur di UI langsung dipakai secara dinamis.
- **Remote Dynamic Tool Synthesis**: Founder dapat berdiskusi bebas dan memerintahkan sekretaris untuk merancang perkakas baru langsung dari chat Telegram. Sekretaris menghasilkan fungsi Python yang secara otomatis diajukan ke `dynamic_tool_registry.py` dengan status `PENDING_APPROVAL`.
- **Inline Tool Approval Gate**: Saat Secretary menyintesis perkakas baru, instruksi disematkan ke chat Telegram Founder. Founder dapat langsung mengaktifkannya dengan membalas `/approve <nama_tool>` atau menolak via `/reject <nama_tool>`.

### 3.12 Hermes Layered Context Compactor & Memory Optimization
- **Tool Output Pruning (`context_compactor.py`)**: Memotong keluaran perkakas observasi yang sangat panjang (>400 baris atau data biner) menjadi intisari status arsitektural padat.
- **Progressive Executive Summarization**: Jika akumulasi token mencapai $\ge 70\%$ dari batas jendela konteks model, riwayat pesan awal dipadatkan secara otomatis menjadi ringkasan status teknis `[EXECUTIVE STATE SUMMARY (Compacted X Earlier Turns)]`.
- **Tail Retention Guarantee**: Mempertahankan 4 giliran percakapan terbaru (*last 4 turns*) secara utuh tanpa pemotongan agar agen tidak kehilangan instruksi dan konteks operasional terkini.

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
- `POST /corporate/tickets/{project_id}/dispatch`: Memicu eksekusi agen asinkron untuk tiket berstatus TODO yang siap jalan.

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

### 4.10 MCP Server Hub & Dynamic Permissions (`/mcp`)
- `GET /mcp/servers`: Daftar seluruh server MCP terpasang, status, konfigurasi, dan daftar perkakas.
- `POST /mcp/dry-run`: Uji coba instan server MCP (discovery tool & simulasi payload) tanpa commit database.
- `POST /mcp/install`: Instalasi/pembaruan server MCP dari UI tanpa menyentuh kode. Environment variables terenkripsi aman via AES-256-GCM. Perkakas MCP otomatis didaftarkan sebagai permission korporat (`mcp:<server_name>:<tool_name>`).
- `DELETE /mcp/servers/{server_id}`: Uninstal server MCP dengan **Referential Dependency Guardrail** (HTTP 409 Conflict jika ada peran AI aktif yang masih memegang izin perkakas tersebut).
- `GET /mcp/all-tools`: Mengembalikan katalog perkakas MCP terdaftar untuk picker izin peran dinamis di `/organization`.
- **Two-Tier CoV Routing**: Perkakas pembacaan (`mcp:*:get_*`, `list_*`, dll) diarahkan ke Tier 1 Deterministic Verifier (0 token overhead), sedangkan perkakas mutasi dialirkan ke Tier 2 Chain-of-Verification Critic.

### 4.11 Public Skills Library & Auto-Taxonomy (`/skills`)
- `GET /skills/categories`: Daftar seluruh kategori keahlian publik dengan statistik jumlah skill.
- `GET /skills`: Katalog keahlian publik dengan filter kategori dan pencarian instan via SQLite FTS5 (BM25 ranking).
- `POST /skills/install`: Instalasi open-source skill bundle (arsitektur folder `skills/<category>/<skill_name>/` berisi `SKILL.md`, skrip, aset) tanpa perlu RAG embedding (0% ONNX vector bloat).
- **Dynamic Auto-Category**: Otomatis mendeteksi atau menambahkan kategori baru jika belum terdaftar.
- **Path Traversal Guard**: Mencegah serangan path traversal (`../` atau `..\\`) saat ekstraksi bundle.
- **Autonomous Agent Tools**: Agen dapat berkonsultasi mandiri ke perpustakaan skill via perkakas bawaan `consult_skill_library` dan membaca detail via `read_skill_detail`.

### 4.12 In-Sandbox LSP (Language Server Protocol)
- **Dual-Mode Diagnostics**: Agen pengembang dapat memanggil perkakas `run_lsp_diagnostics` secara mandiri saat menyunting berkas, dan sistem secara otomatis menjalankan gatekeeper pra-PR (`lsp_gatekeeper.py` terintegrasi ke `peer_reviewer.py`).
- **Project-Wide TypeScript Compiler**: Diagnostik TypeScript menggunakan `tsc --project tsconfig.json` dan memfilter galat fatal hanya pada berkas terkait (mencegah false positive dari berkas sandbox lain).
- **Python AST & Syntax Fallback**: Validasi sintaksis Python berbasis Abstract Syntax Tree (AST) untuk mendeteksi `SyntaxError` secara deterministik.

### 4.13 Telegram Secretary Dry-Run & Secret Interceptor
- **Dry-Run Intent Detection**: Sekretaris Telegram mendeteksi perintah instalasi MCP/Skill, memvalidasi URL/format, dan menampilkan ringkasan perkakas sebelum eksekusi.
- **Secret Token Interception & Scrubbing**: Mendeteksi pola kredensial sensitif (`token=...`, `key=...`), menyimpannya langsung ke brankas AES-256-GCM, menyamarkan pesan balasan (`token=***`), dan memanggil Telegram API `deleteMessage` untuk menghapus riwayat obrolan sensitif secara permanen.

---

## 5. Standar Rekayasa & Kualitas Kode

Sesuai aturan ketat pada `code-quality-rules.md`:
1. **Single Responsibility Principle (SRP) & Batas Berkas**:
   - Maksimal 150–200 baris kode per berkas. Jika melebihi batas, modul wajib dipecah menjadi sub-komponen terfokus. Seluruh berkas backend kini mematuhi limit ini (<= 200 baris).
2. **Type Hints Lengkap**:
   - Wajib menyertakan type hint pada seluruh parameter dan nilai return fungsi/method Python dan TypeScript.
3. **Docstring Google-Style**:
   - Setiap kelas dan fungsi utama wajib memiliki docstring ringkas yang menjelaskan tugas dan argumennya.
4. **Logging Terpusat (Dilarang `print`)**:
   - Menggunakan logger terkonfigurasi (`loguru` atau logger internal). Penggunaan `print()` dilarang keras di seluruh kode produksi.
5. **Penanganan Eksepsi Spesifik**:
   - Wajib menggunakan `try-except` spesifik pada seluruh operasi I/O, koneksi basis data, network call, dan parsing data. Dilarang menggunakan bare `except:`.
6. **Code Hygiene & Anti-Heuristic (Point B Solved)**:
   - Pembersihan dead code, ladder `if-elif` statis 50 baris diganti registri dinamis, HTML DOM parser menggantikan substring regex, dan AST syntax parser menggantikan hardcoded verdict.
7. **Jaminan Uji Menyeluruh (203/203 Tests Passed — 100% Green)**:
   - Setiap modul diverifikasi secara ketat melalui 4 gelombang pengujian otomatis di `backend/tests/`:
     - **Gelombang 1**: Pembersihan dead code, Polymorphic Contract Handler (`contract_handlers.py`), Sovereign Router live pricing ledger, dan FastEmbed ONNX local RAG.
     - **Gelombang 2**: Two-Tier CoV Pre-Flight Gatekeeper (Tier 1 0ms/0-token & Tier 2 critic), Autonomous Worker Self-Repair Loop, dan Hermes Context Compactor.
     - **Gelombang 3**: Autonomous Kanban Runner (`kanban_runner.py` atomic claim), FileLockManager mutex per path, DynamicToolRegistry SQLite persistence (`corporate_custom_tools`), dan Telegram Secretary Daemon dengan dynamic tool synthesis.
     - **Gelombang 4**: MCP Server Dynamic Bridge & Dependency Guardrail (`test_mcp_manager.py`), Public Skills Hub & Auto-Taxonomy FTS5 (`test_skills_hub.py`), In-Sandbox LSP Diagnostics & Gatekeeper (`test_lsp_service.py`), serta Telegram Secretary Dry-Run & Secret Interceptor (`test_telegram_installer.py`).
   - Status akhir pengujian: **203 / 203 Passed (100% PASSED, Zero Failure)**.
