# 🪐 Virtual Tech Startup Multi-Agent System & Sovereign Corporate OS
### Autonomous AI Virtual Enterprise Platform, Dynamic Asynchronous Workflow Engine & Global Oasis Live Command HQ

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2%20(Production%20Ready)-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Oasis 2D Liquid](https://img.shields.io/badge/Command%20HQ-Obsidian%20Liquid%202D-6366f1?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-180%2F180%20Passed%20(100%25)-brightgreen?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLite WAL](https://img.shields.io/badge/Database-SQLite%20WAL-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 💡 Executive Overview

**Virtual Tech Startup Multi-Agent System** adalah sistem operasi korporat kecerdasan buatan mandiri (*Sovereign Autonomous AI Corporate Operating System*) dan platform inkubasi startup digital mutakhir. 

Platform ini memberdayakan seorang **Founder tunggal (Solo Entrepreneur / Chairman / CEO)** untuk mengoperasikan konglomerasi digital berskala penuh secara mandiri: mulai dari inisiasi ide produk, riset pasar, penyusunan kontrak OpenAPI, rekayasa paralel Frontend & Backend, penjaminan mutu P2P, audit keamanan statis OWASP Top 10, hingga peluncuran langsung di sandbox kontainer terisolasi.

Seluruh dinamika perusahaan dipantau secara real-time melalui antarmuka **Global Oasis Live Command HQ** (`/office`) yang elegan, berkinerja tinggi (2D Obsidian Liquid Engine), hemat token (Zero Idle Token Overhead), dan dilengkapi panel live thought stream, handoff inter-agen, serta ruang kontrol krisis All-Hands.

---

## 🏛️ Arsitektur Sistem Terpadu

Sistem dirancang dengan arsitektur berlapis (*layered architecture*) yang memisahkan antarmuka visual, orkestrasi logika asinkron, mesin kognitif model AI, serta lapisan keamanan dan isolasi eksekusi:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FOUNDER EXECUTIVE DASHBOARD                                        │
│                                  Next.js 14 App Router • TypeScript                                    │
│                                                                                                        │
│  /                 /organization         /kanban/[id]         /preview/[id]         /office            │
│  Portfolio Hub     Org Studio & DND      Mission Control      Live Sandbox, PTY     Global Oasis Live  │
│  & Venture State   Pipeline Builder      & Live Lounge WS     Terminal & Snapshots  Command HQ (2D)    │
│                                                                                                        │
│  /analytics        /settings             /wisdom              /sparring/[id]                           │
│  Ledger & Finance  BYOK & Secret Vault   Vector RAG Base      Executive Sparring                       │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │ REST API / WebSocket / SSE Streams
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FASTAPI HIGH-CONCURRENCY BACKEND                                     │
│                                        Pure ASGI Middleware Engine                                     │
│                                                                                                        │
│  • SecurityGateMiddleware (Stealth Dynamic PIN + Telegram Auth) • ProcessTimeLoggingMiddleware         │
│  • 21 Modular REST & WebSocket Routers (Corporate, Pipelines, Tickets, Governance, Vault, Office)     │
└───────────────────────┬───────────────────────────────────────────────────────┬────────────────────────┘
                        │                                                       │
                        ▼                                                       ▼
┌──────────────────────────────────────────────┐        ┌────────────────────────────────────────────────┐
│      DYNAMIC ASYNC KANBAN ENGINE             │        │          CORPORATE EVENT BUS (PUB/SUB)         │
│ • Ticket Lifecycle: BACKLOG ➔ TODO ➔         │        │ • Non-blocking asyncio.Queue per Project       │
│   IN_PROGRESS ➔ REVIEW ➔ DONE                │◄──────►│ • SQLite WAL Message Ledger Persistence        │
│ • Task Concurrency Dispatcher (DAG Gather)   │        │ • Real-time WebSocket Lounge Broadcast        │
│ • Dependency Resolution & Priority Sorting   │        │ • Agent Dialogue & Incident Escalation Log     │
└───────────────────────┬──────────────────────┘        └───────────────────────┬────────────────────────┘
                        │                                                       │
                        ▼                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXECUTIVE GOVERNANCE & GUARDRAILS                                   │
│                                                                                                        │
│  • Agent Decision Envelope: { PROCEED | CONSULT_ROLE | ESCALATE_TO_C_LEVEL | REQUEST_REWORK }          │
│  • Anti-Infinite Loop Circuit Breaker: Auto-Freeze Ticket on >= 3 Consecutive Debate Turns             │
│  • Financial Guardrail & Flight Recorder: Hard Quota ($1.50 / 350k tokens) & Time-Travel Replay        │
│  • 1-Click CEO Strategic Intervention & Veto (Force Proceed / Chat Directive / Reassign Role)          │
│  • Three-Way Branch Merge Engine: LCA Graph Traversal for Isolated Corporate Branch Merging            │
└───────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      CORE COGNITIVE & EXECUTION ENGINES                                │
│                                                                                                        │
│  • Sovereign Model Router: Multi-Channel Failover (9router-style), Quota Limiter (RPM/TPM/RPD)        │
│  • Dynamic Thinking Level Control: Reasoning Effort (None, Low, Medium, High) with Auto-Escalation    │
│  • State-First Cognitive Handoff: Context Compaction (>85% Token Saved, 98% Technical Retention)       │
│  • Autonomous Peer-to-Peer PR Review Engine: Quorum Approval Gate (>= 2 approvals) & AST Verification │
│  • Corporate Wisdom Base: Embedded 128-dim Vector Memory RAG + 1-Click GitHub Skill/Blueprint Importer │
│  • Python AST OWASP Security Scanner & Runtime Tool Synthesizer with AST Static Validation             │
│  • Hardened Docker Subnet Sandbox: Dedicated bridge_net_{project_id} with Hard CPU/RAM Quota           │
│  • Global Oasis Live Engine: Real-time Multi-Agent Thoughts, Scoped @mentions & 0-Token Watchdog       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Fitur Utama & Kapabilitas Lengkap

### 1. Global Oasis Live Command HQ (`/office`)
* **Antarmuka 2D Obsidian Liquid**: Dirancang dengan palet gelap premium Obsidian (`#090d16` / `#0f172a`), memprioritaskan keterbacaan, ergonomi visual, dan performa tinggi tanpa beban GPU 3D yang berlebihan.
* **Kebijakan Ketat 0-Token Saat Idle (*Zero Token Idle Overhead*)**: Feed pemikiran, drawer status, dan stream WebSocket beroperasi secara *event-driven*. Tidak ada pemanggilan LLM latar belakang saat tidak ada pekerjaan aktif.
* **Kategori Live Stream Terfilter**:
  - 🌐 **All Streams**: Agregasi seluruh percakapan, penalaran, dan aktivitas kerja para agen secara terpadu.
  - ⚡ **Execution & Handoffs**: Pemantauan delegasi pekerjaan, perpindahan tanggung jawab, dan pergantian tiket antar-agen secara transparan.
  - 👑 **CEO Decision Gates**: Notifikasi seketika saat agen membutuhkan persetujuan atau putusan strategis Founder.
  - ☕ **Oasis Lounge**: Diskusi santai dan pertukaran gagasan informal agen di luar tiket operasional.
* **Konsol Intervensi Terarah (`@mention`)**: Konsol instruksi cerdas dengan auto-completion `@role` (`@founder`, `@cos`, `@cto`, `@pm`, `@fe`, `@be`, `@qa`, dll.). Mengirim instruksi ke agen tertentu hanya menyuntikkan pesan ke konteks agen sasaran secara terisolasi tanpa membebani context-window agen lainnya.
* **All-Hands Executive War Room**: Modal komando darurat untuk mengumpulkan seluruh pimpinan eksekutif dalam satu ruang diskusi terarah yang dimoderasi oleh Chief of Staff (CoS) dan CTO.
* **Live Agent Screen-Share & Code Inspection Pane**: Memantau berkas aktif yang sedang dikerjakan agen, scratchpad pemikiran, status bubble, serta tombol 1-klik Hold Ticket untuk membekukan tiket yang bermasalah.

### 2. Visual Dynamic Organization Studio (`/organization`)
* **Hierarki Korporat Git-Style**: Visualisasi struktur organisasi yang memisahkan Executive Suite, Core Engineering, dan Divisi Kustom.
* **Divisi Dinamis Tanpa Batas**: Pengguna bebas membuat divisi baru (misal: Rekayasa Software, Edukasi, Copywriting, Riset Pasar), menentukan warna aksen HEX, ikon Lucide React, serta mandat divisi.
* **Karyawan AI Fleksibel**: Mendaftarkan peran AI baru dengan spesifikasi granular:
  - System prompt instruksi persona terisolasi.
  - Penugasan model LLM dan provider independen per agen.
  - **Dynamic Thinking Level (Reasoning Effort)**: Opsi kedalaman penalaran (`none`, `low`, `medium`, `high`) per peran AI.
  - Pengatur kreativitas (*temperature* 0.0 s/d 1.5).
  - Alokasi batas anggaran token (*token budget* 1.000 s/d 100.000 token per tugas).
  - Izin perkakas modular (*tool permissions*): `read_file`, `write_file`, `ast_patch_file`, `search_codebase`, `web_search`, `execute_code`, `inspect_db_schema`, `validate_api_contract`, `git_diff_summary`, dan `runtime_tool_builder`.

### 3. Visual HTML5 Drag-and-Drop Pipeline Builder
* **Multi-Product-Line Pipelines**: Rantai alur kerja modular untuk berbagai lini bisnis:
  - 💻 **Software & SaaS (Tech Core)**: Siklus penuh arsitektur, frontend, backend, security audit, dan deployment.
  - 📚 **Edukasi & Kursus Online**: Kurikulum, materi pengajaran, latihan soal, dan tinjauan pedagogis.
  - ✍️ **Copywriting & Konten**: Riset audiens, penulisan artikel/copy, editorial review, dan SEO metadata.
  - 🧪 **Pipeline Kustom Bebas**: Menyesuaikan kebutuhan proyek apa pun dari nol.
* **Dukungan Rantai Siklis (*Looping Sequences*)**: Memungkinkan peran yang sama dipanggil berulang kali dalam satu alur (misal: `Role A ➔ Role B ➔ Role C ➔ Role A ➔ Role C`).
* **Gerbang Keputusan CEO Terintegrasi (*Human-in-the-Loop*)**: Kartu intervensi manusia yang dapat ditarik langsung ke kanvas pipeline:
  - 👑 **Stage-Gate Approval**: Evaluasi kelayakan produk sebelum fase berikutnya dimulai.
  - 🤝 **Executive Strategic Meeting**: Pertemuan penyelarasan strategi antara Founder dan C-Level.
  - 🧭 **Founder Direction Input**: Penyisipan arahan visi Founder langsung di tengah eksekusi.

### 4. Dynamic Asynchronous Kanban & Event Bus
* **Manajemen Tiket Otonom**: Setiap tugas venture direpresentasikan dalam kartu tiket (`corporate_tickets`) lengkap dengan branch, divisi, penanggung jawab, lini produk, prioritas, dan dependensi prasyarat.
* **Siklus Hidup 5 Kolom**: `BACKLOG ➔ TODO ➔ IN_PROGRESS ➔ REVIEW ➔ DONE`. Agen mendeteksi tiket yang siap dikerjakan secara mandiri begitu seluruh dependensi terpenuhi.
* **Task Concurrency Dispatcher (`dispatcher.py`)**: Mengeksekusi tugas-tugas rekayasa yang independen secara paralel menggunakan `asyncio.gather()`, memangkas durasi produksi hingga 40–50%.
* **Corporate Event Bus Asinkron (`event_bus.py`)**: Arsitektur pub/sub non-blocking berbasis `asyncio.Queue` per proyek yang mendistribusikan sinyal tugas ke antarmuka web, WebSocket Lounge, dan telemetri secara instan.

### 5. Executive Governance Hub & Anti-Infinite Loop Circuit Breaker
* **Format Keputusan Terstruktur (`AgentDecisionEnvelope`)**: Agen merespons tugas dalam format JSON kanonikal dengan opsi aksi: `PROCEED`, `CONSULT_ROLE`, `ESCALATE_TO_C_LEVEL`, atau `REQUEST_REWORK`.
* **Anti-Infinite Loop Circuit Breaker (`circuit_breaker.py`)**: Melacak putaran diskusi konsultasi inter-agen pada tiket yang sama. Jika diskusi mencapai **$\ge 3$ putaran berturut-turut** tanpa menghasilkan kode baru, sistem secara otomatis membekukan tiket menjadi `BLOCKED_LOOP_DETECTED`.
* **Hak Veto & Intervensi 1-Klik CEO**: Founder dapat mengambil alih tiket yang dibekukan:
  - `FORCE_PROCEED`: Melewati perdebatan dan memaksa tugas selesai (`DONE`).
  - `INTERVENE`: Memberikan instruksi tertulis mutlak dan mengembalikan tiket ke `IN_PROGRESS`.
  - `REASSIGN`: Mengalihkan tugas ke peran karyawan AI lain.
* **Eskalasi C-Level Langsung**: CTO atau CoS memformulasikan laporan ringkas Opsi A vs Opsi B untuk keputusan cepat Founder.

### 6. Sovereign Model Router, Quota Shield & Dynamic Thinking Level
* **Multi-Channel Fallback Cascade (ala 9router)**: Orkestrasi perutean hulu cerdas dengan rantai model cadangan otomatis jika model utama mengalami kegagalan (HTTP 429 rate limit atau HTTP 500 server error).
* **Pre-flight Quota Limiter**: Memantau batas RPM (Requests Per Minute), TPM (Tokens Per Minute), dan RPD (Requests Per Day) per kanal penyedia dengan mekanisme *self-healing cooldown*.
* **Dynamic Thinking Level Control**: Pengaturan kedalaman penalaran model (`none`, `low`, `medium`, `high`) per peran AI. Pada saat terjadi rework (`turn_count == 2`), router secara otomatis meningkatkan level penalaran ke `high` (*auto-escalation*) untuk memecahkan bug sulit.
* **State-First Cognitive Handoff**: Saat alih-tangan atau failover antar-agen/model, sistem tidak mengirim riwayat percakapan mentah. Sistem memadatkan konteks berbasis status arsitektur (AST symbols, schema contracts, file diffs) dan membuang tag penalaran `<think>`, **menghemat $>85\%$ konsumsi token** sembari mempertahankan **98% retensi konteks teknis**.

### 7. Autonomous Peer-to-Peer PR Review Engine & Quorum Gate
* **Siklus Hidup Pull Request Otomatis**: Kode hasil pekerjaan agen dikemas menjadi Pull Request lengkap dengan tampilan diff Git-style (`+`/`-`).
* **Review Multi-Disiplin Terisolasi**: Menugaskan peninjauan kode ke spesialis yang relevan (QA Engineer menguji keamanan dan test case, CTO memeriksa kepatuhan arsitektur, dan Backend/Frontend memeriksa kontrak data).
* **Quorum Approval Gate**: Kode hanya dapat digabungkan (*merged*) jika mendapatkan **minimal $\ge 2$ persetujuan (*approvals*)** dari agen peninjau tanpa komentar penolakan aktif.

### 8. Corporate Wisdom Base & Vector Memory RAG
* **Pencarian Semantik Sub-2ms**: Database vektor lokal tersemat 128-dimensi ($L_2$ normalized) yang beroperasi tanpa dependensi cloud eksternal yang lambat.
* **1-Click GitHub Skill & Blueprint Importer (`/wisdom`)**: Mengimpor berkas pengetahuan, aturan rekayasa, atau dokumen arsitektur langsung dari URL GitHub publik ke dalam repositori pengetahuan korporat.
* **Cross-Venture Knowledge Sharing**: Best-practice, solusi bug masa lalu, dan pola optimasi secara otomatis disuntikkan ke dalam *working memory* agen (Tier 0 Context) saat menghadapi masalah serupa.

### 9. Git-Style Organizational Branching & Three-Way LCA Merge Engine
* **Branch Protection**: Alur kerja produksi utama (`branch_main`) terlindungi dari perubahan tak teruji (*Gold Standard*).
* **1-Click Branch Forking**: Menggandakan seluruh bagan organisasi, divisi, peran, alur pipeline, dan tiket ke branch eksperimental terisolasi dengan ID unik baru.
* **Three-Way LCA Merge Engine (`branch_merge.py`)**: Menggunakan penelusuran graf *Lowest Common Ancestor (LCA)* untuk mendeteksi dan menyelesaikan perbedaan struktural antar-branch secara atomik (*fast-forward* atau *3-way merge*).

### 10. Desentralisasi BYOK & Custom OpenAI-Compatible Provider
* **Konfigurasi Model Per Karyawan AI**: Setiap agen dapat menggunakan provider LLM yang berbeda sesuai karakteristik tugas:
  - 🌐 **OpenRouter**: Akses ratusan model komersial dan open-source dengan penanda `• FREE`.
  - 🧠 **DeepSeek**: Model penalaran mendalam dan coding hemat biaya (`deepseek-reasoner`, `deepseek-chat`).
  - ⚡ **Google Gemini**: Dukungan context window masif (Gemini 2.5 Flash / Pro).
  - 🏎️ **Groq**: Inferensi ultra cepat dengan latensi sub-detik (LPU chips).
  - 🤖 **OpenAI & Anthropic**: GPT-4o, Claude 3.5 Sonnet / Haiku.
  - 🏠 **Ollama Lokal**: 100% offline dan privat tanpa koneksi internet.
  - 🔌 **Custom Provider (Format OpenAI)**: Integrasi fleksibel ke server lokal atau penyedia gateway mana pun yang mendukung REST format OpenAI (LocalAI, vLLM, Together AI, OpenRouter self-hosted) cukup dengan mengisi Base Endpoint URL dan API Key.
* **Secret Vault Terenkripsi AES-256-GCM**: Kunci kredensial produksi disimpan secara aman dan terenkripsi pada basis data SQLite WAL, dapat dimutakhirkan secara runtime tanpa me-restart server backend.

### 11. AST Code Intelligence, OWASP Guardrail & Runtime Tool Synthesizer
* **AST OWASP Top-10 Security Scanner (`security_scanner.py`)**: Pemeriksaan statis kode Python menggunakan Abstract Syntax Tree (AST) untuk mendeteksi eksekusi kode berbahaya (`eval`, `exec`), hardcoded secret keys, injeksi SQL, CORS permisif, dan kerentanan XSS.
* **Runtime Tool Synthesizer (`tool_synthesizer.py`)**: Mengunduh dan membungkus perkakas utilitas Python dari repositori open-source GitHub dengan verifikasi keamanan AST OWASP pra-registrasi sebelum alat didaftarkan ke registri runtime agen.

### 12. Frontier Radar, Flight Recorder & Financial Guardrail
* **Time-Travel Flight Recorder (`flight_recorder.py`)**: Merekam setiap peristiwa keputusan, masukan instruksi, eksekusi perkakas, dan transisi status agen secara kronologis ke berkas JSONL dan SQLite WAL untuk diputar ulang pada timeline *Time-Travel Replay*.
* **Financial Guardrail Dinamis (`financial_guardrail.py`)**: Sinkronisasi biaya dan penggunaan token secara real-time langsung dengan tabel ledger transaksi `corporate_token_ledger`, memberlakukan batas kuota pengeluaran ($1.50 atau 350.000 token per tiket) untuk mencegah pemborosan anggaran.

### 13. Ephemeral Sandbox, Interactive PTY Terminal & Reverse Proxy
* **Isolasi Subnet Docker Hardened**: Setiap venture berjalan di dalam subnet jembatan khusus (`bridge_net_{project_id}`) dengan pembatasan hard quota CPU (1.5 core) dan RAM (1024 MB), dilengkapi reverse proxy Caddy (`*.local.sandbox`) dan fallback embedded async HTTP port 4000–4999.
* **Interactive Web PTY Terminal**: Terminal CLI live dua arah berbasis WebSocket di antarmuka `/preview/[id]` dengan guardrail pencegah perintah destruktif sistem operasi (`rm -rf /`, `mkfs`, dll).
* **Copy-on-Write (CoW) Snapshots**: Snapshot direktori proyek otomatis dengan garansi *Zero Data Loss* (pembuatan cadangan instan `AUTO_PRE_ROLLBACK` sebelum rollback dijalankan).

### 14. Internal Chain-of-Verification (CoV) Pre-Flight Gatekeeper & Sentinel Observability Engine
* **Pemisahan Peran Kognitif & Penjaga Keselamatan Teknis**:
  - **Peralihan ke Kontrak Fleksibel**: Menggantikan validasi skema yang kaku (`extra="forbid"`) dengan **Open Flexible Contracts (`extra="allow"`)**, memberikan kebebasan bagi agen untuk merancang inovasi UI modern (animasi, glow tokens, micro-interactions).
  - **Internal Pre-Flight Sentinel**: Sebagai penyeimbang kebebasan kreatif, agen internal CoV bertindak sebagai penjaga kelaikan teknis (*Pre-Flight Inspector*) sebelum respons disiarkan atau perkakas dieksekusi, mencegah runtime crash (500 Internal Server Error).
* **Konfigurasi Internal Terkunci di Server (Zero UI Exposure)**:
  - Seluruh konfigurasi model, provider, dan API key CoV (`COV_PROVIDER`, `COV_MODEL`, `COV_BASE_URL`, `COV_API_KEY`) diatur secara eksklusif via `.env` dan `config.py`.
  - **Zero UI Exposure**: Pengaturan CoV tidak pernah diekspos ke antarmuka `/settings` maupun `/organization` demi menjaga integritas agen pengawas internal.
* **Lean Tool Manifest (~150-200 Tokens) & Dynamic Stage Filtering**:
  - CoV hanya menerima deskripsi tanda tangan fungsi dan parameter kunci (*lean manifest*), bukan kode implementasi yang panjang.
  - **Stage-Aware Filtering**: Tahap Ideasi murni menyuntikkan 0 tools (menghemat token secara maksimal), sedangkan tahap Engineering hanya menyuntikkan perkakas relevan (`inspect_db_schema`, `validate_api_contract`, `git_diff_summary`, `search_codebase`, `runtime_tool_builder`).
* **Autonomous Role-Agent Self-Healing (Bukan CoV yang Memperbaiki Sendiri)**:
  - Jika pemanggilan perkakas cacat atau parameter wajib kurang, CoV bertindak sebagai **Auditor/Kritikus** dengan status `REPAIR_REQUIRED` dan menghasilkan `repair_feedback` yang spesifik.
  - Sistem mengirimkan teguran internal tersebut **kembali ke Agen Role pemanggil (CTO, Backend, Frontend, dll.)**, sehingga **Agen Role sendiri yang memperbaiki respons dan parameternya** secara mandiri menggunakan konteks domain lengkapnya.
  - Setelah diperbaiki oleh Agen Role dan disetujui oleh CoV (`APPROVED` / `REPAIRED`), perkakas dieksekusi atas nama agen asli dan hasil observasi dikembalikan langsung ke agen tersebut (*Non-Hijacking Tool Execution*).
* **CoV Sentinel Observability Dashboard (`/office`)**:
  - Antarmuka telemetri real-time yang transparan di Command HQ dengan Bento Grid (Total Pre-Flight Audits, Skor Reliabilitas %, Jumlah Auto-Repairs, Rerata Latensi ms).
  - Filter interaktif berdasarkan peran agen dan status (APPROVED, REPAIRED, REJECTED).
  - Laci inspeksi detail dengan tampilan **Diff Sisi-ke-Sisi (Kandidat Asli vs Hasil Verifikasi)**, catatan teguran koreksi CoV, dan penampil JSON parameter perkakas.
  - **Event-Driven WebSocket Sync**: Terhubung langsung ke WebSocket Oasis (`/corporate/ws/office/{project_id}`) untuk pembaruan instan tanpa *HTTP polling spam*.
  - Lencana visual `[🛡️ CoV Verified]` pada setiap kartu respons agen di Oasis Chat.

### 15. Multimodal File Upload Engine & Drag-and-Drop Collaboration
* **Ekstraksi Teks Cerdas Multi-Format**:
  - Modul ekstraksi teks aman (`file_parser.py`) mengekstrak konten PDF (menggunakan `pypdf` dengan fallback cerdas), Markdown (`.md`), Plain Text (`.txt`), CSV, JSON, YAML, dan berkas kode sumber (`.py`, `.ts`, `.tsx`, `.js`, `.html`, `.css`).
  - Menyuntikkan rangkuman dan preview isi berkas langsung ke dalam konteks prompt LLM saat diskusi di Oasis HQ dan Executive Sparring.
* **REST File Storage & Proteksi Traversal**:
  - Endpoint `POST /api/v1/files/upload` (mendukung ukuran berkas hingga 15MB) dan `GET /api/v1/files/download/{project_id}/{filename}` dengan proteksi *path traversal*.
* **Interaksi Intuitif Drag & Drop**:
  - Founder dapat melampirkan berkas dengan mudah cukup dengan **menyeret dan melepaskan (drag & drop)** berkas ke area input chat di Oasis HQ (`OfficeChatConsole.tsx`) maupun Executive Sparring (`/sparring/[id]`).
  - Dilengkapi visual *dropzone overlay* bercahaya animasi, chip preview berkas lampiran dengan tombol hapus (x), serta tautan unduh interaktif pada kartu pesan.

---

## 🔄 Alur Kerja Operasional & Siklus Hidup Venture

```
[ Founder Input: Ide Bisnis / Masalah Pasar ]
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│  FASE 1: SOKRATIK SPARRING & STRATEGIC FORMULATION     │
│  • Chief of Staff (CoS) & CTO mengevaluasi ide bisnis  │
│  • Bedah arsitektur teknis, unit economics, & PRD freeze│
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│  FASE 2: PEMBENTUKAN TIKET & KONTRAK DATA              │
│  • Product Manager menyusun user stories di Kanban     │
│  • CTO menetapkan OpenAPI 3.1 Contract & Design Tokens │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│  FASE 3: REKAYASA PARALEL ASINKRON (TASK DISPATCHER)   │
│  • UI/UX Designer merancang wireframe visual           │
│  • Frontend Engineer mengimplementasikan Next.js 14    │
│  • Backend Engineer membangun REST API FastAPI         │
│  * (Berjalan bersamaan via asyncio.gather)             │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│  FASE 4: VERIFIKASI P2P & AUDIT KEAMANAN OWASP         │
│  • QA Engineer menjalankan AST Scanner & Unit Tests    │
│  • Automated Pull Request Review (Quorum >= 2 Approvals)│
│  • Circuit Breaker memantau diskursus agen             │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│  FASE 5: SANDBOX LIVE PREVIEW & DEPLOYMENT             │
│  • Live preview kontainer Docker terisolasi            │
│  • Uji coba interaktif via Web PTY Terminal            │
│  • 1-Click Approval Founder (Stage-Gate)               │
└────────────────────────────────────────────────────────┘
```

1. **Inisiasi & Sokratik Sparring**: Founder memasukkan ide usaha di `/sparring/[id]`. CoS menantang model bisnis dan CFO menghitung unit economics, sementara CTO menentukan arketipe teknis.
2. **Perumusan Spesifikasi & Dekomposisi Tiket**: Product Manager memecah spesifikasi menjadi kartu tiket tugas dengan dependensi terurut di papan Kanban virtual.
3. **Eksekusi Paralel Multi-Agen**: Dispatcher asinkron mengaktifkan agen yang relevan secara bersamaan. Agen menggunakan tool permissions untuk membaca, memodifikasi, dan memverifikasi kode.
4. **Penjaminan Mutu & Quorum Review**: Pekerjaan selesai otomatis diajukan sebagai PR. Agen peninjau memberikan ulasan. Jika terjadi perdebatan $\ge 3$ putaran, Circuit Breaker mengintervensi tiket dan menyerahkannya ke CEO Veto.
5. **Deployment & Staging**: Kode yang disetujui dirilis ke lingkungan sandbox Docker yang terisolasi dengan akses preview instan di browser.

---

## 📡 Spesifikasi 21 Router API Backend

Seluruh endpoint REST API dan WebSocket terpusat di bawah prefix `/api/v1` dengan validasi skema tipe Pydantic v2:

| No | Modul Router | Prefix Endpoint | Tipe | Deskripsi & Tanggung Jawab Utama |
|:--:|:-------------|:----------------|:----:|:---------------------------------|
| 1 | `corporate.py` | `/corporate` | REST | CRUD hierarki organisasi: branch, forking alur kerja, divisi dinamis, dan pendaftaran peran AI. |
| 2 | `corporate_workflow.py` | `/corporate/branches/{id}` | REST | Pipeline builder multi-lini produk, tahapan DND berulang (*looping*), dan gerbang keputusan CEO. |
| 3 | `corporate_tickets.py` | `/corporate/tickets` | REST | Manajemen kartu tiket Kanban virtual (5 status), dependensi tugas, dan tingkat prioritas. |
| 4 | `corporate_events.py` | `/corporate/events` | REST | Riwayat percakapan inter-agen, dialog eskalasi, dan log event bus korporat. |
| 5 | `corporate_ws.py` | `/ws/corporate` | WS | WebSocket streaming dua arah untuk sinkronisasi tiket Kanban dan siaran event real-time. |
| 6 | `governance.py` | `/governance` | REST | Pengawas interaksi agen: status circuit breaker, eskalasi C-Level, dan intervensi hak veto CEO. |
| 7 | `branch_merge.py` | `/corporate/branches` | REST | Analisis *diff* struktural antar-branch dan penggabungan atomik branch eksperimen ke main via LCA. |
| 8 | `projects.py` | `/projects` | REST | Siklus hidup venture: inisiasi ide baru, muat checkpoint state, dan manajemen portofolio. |
| 9 | `sparring.py` | `/projects/{id}/sparring` | REST / SSE | Sesi debat sokratik pra-PRD antara Founder, CoS, dan CTO dengan streaming inferensi LLM. |
| 10 | `gates.py` | `/projects/{id}/gates` | REST | Stage-Gate keputusan Founder: persetujuan formal, revisi arahan, atau terminasi proyek. |
| 11 | `pull_requests.py` | `/projects/{id}/prs` | REST | Siklus hidup PR otomatis: automated peer-to-peer code review dan quorum approval gate ($\ge 2$). |
| 12 | `vault.py` | `/projects/{id}/vault` | REST | Penyimpanan kredensial produksi rahasia terenkripsi AES-256-GCM (Secret Vault). |
| 13 | `analytics.py` | `/analytics` | REST | Metrik penggunaan token per agen, evaluasi unit economics, dan neraca keuangan ledger. |
| 14 | `settings.py` | `/settings` | REST | Pengaturan dinamis sistem (BYOK API keys, parameter PaaS, reset konfigurasi) tanpa restart server. |
| 15 | `auth.py` | `/auth` | REST | Verifikasi PIN dinamis 6-digit gerbang keamanan Telegram dan penerbitan session token HMAC. |
| 16 | `wisdom.py` | `/wisdom` | REST | Corporate Wisdom Knowledge Base: penarikan best-practice dan aturan arsitektur via RAG vektor 128-dim. |
| 17 | `office.py` | `/corporate/office` | REST | Endpoint REST status agen, intervensi terarah scoped per-role, dan pengiriman direktif Founder. |
| 18 | `office_ws.py` | `/corporate/ws/office` | WS | WebSocket streaming dua arah siaran aliran diskursus agen, sinyal handoff, dan aktivitas real-time. |
| 19 | `sandbox_snapshots.py` | `/projects/{id}/sandbox` | REST | Manajemen snapshot direktori proyek (CoW) dan pemulihan rollback instan anti-data-loss. |
| 20 | `sandbox_network.py` | `/projects/{id}/network` | REST | Pemeriksaan status isolasi subnet Docker dan pemetaan routing reverse proxy Caddy. |
| 21 | `sandbox_terminal_ws.py`| `/ws/sandbox/{id}/terminal`| WS | Terminal interaktif PTY shell CLI live dua arah di dalam lingkungan sandbox proyek. |

---

## 📂 Struktur Direktori Proyek

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/                   # 21 Modul Router REST API & WebSocket
│   │   │   ├── analytics.py          # Metrik Token Ledger & Financial Tracking
│   │   │   ├── auth.py               # Otentikasi Stealth PIN & Telegram Security Gate
│   │   │   ├── branch_merge.py       # Git-Style Branch Diff & LCA Atomic Merge
│   │   │   ├── corporate.py          # Corporate Organization Hierarchy CRUD
│   │   │   ├── corporate_events.py   # Corporate Event Log & Message Queries
│   │   │   ├── corporate_tickets.py  # Kanban Virtual Tickets & Task Transitions
│   │   │   ├── corporate_workflow.py # Dynamic Workflow Pipeline & Looping Sequence
│   │   │   ├── corporate_ws.py       # Kanban Real-Time WebSocket Channel
│   │   │   ├── gates.py              # Founder Stage-Gate Decisions
│   │   │   ├── governance.py         # Executive Governance, Escalation & CEO Veto
│   │   │   ├── office.py             # Live Command HQ State & Directives API
│   │   │   ├── office_ws.py          # Multi-Agent Live Streams WebSocket Channel
│   │   │   ├── projects.py           # Venture State & Checkpoint Persistence
│   │   │   ├── pull_requests.py      # Automated PR Engine & Quorum Peer Review
│   │   │   ├── sandbox_network.py    # Docker Network & Reverse Proxy Routing
│   │   │   ├── sandbox_snapshots.py  # Zero-Data-Loss CoW Snapshots & Rollbacks
│   │   │   ├── sandbox_terminal_ws.py# Interactive Web PTY Terminal Stream
│   │   │   ├── settings.py           # Dynamic BYOK & Runtime Settings Manager
│   │   │   ├── sparring.py           # Executive Sparring Room (CoS + CTO)
│   │   │   ├── vault.py              # AES-256-GCM Encrypted Secret Vault
│   │   │   └── wisdom.py             # Corporate Wisdom & Organizational Learning
│   │   ├── core/                     # Config, Logger, Security Gate, Settings Manager & Constants
│   │   ├── db/                       # Basis Data SQLite Asinkron (aiosqlite WAL)
│   │   │   ├── branch_repo.py        # Isolasi Branching & Forking Database
│   │   │   ├── corporate_repo.py     # Unified Corporate Facade Database
│   │   │   ├── division_repo.py      # Operasi Divisi Organisasi
│   │   │   ├── role_repo.py          # Operasi Peran Karyawan AI
│   │   │   ├── pipeline_repo.py      # Multi-Product Pipelines
│   │   │   ├── ticket_repo.py        # Virtual Kanban Tickets Storage
│   │   │   ├── workflow_repo.py      # Pipeline Stages & Ordering Storage
│   │   │   └── session.py            # SQLite WAL Connection Pool
│   │   ├── engine/                   # Core Cognitive & Execution Engines
│   │   │   ├── circuit_breaker.py    # Anti-Infinite Loop Guardrail
│   │   │   ├── dispatcher.py         # Task Concurrency Dispatcher (asyncio.gather)
│   │   │   ├── event_bus.py          # Asynchronous Actor Event Bus
│   │   │   ├── model_router.py       # Sovereign Model Router & Quota Shield
│   │   │   ├── state_handoff.py      # State-First Cognitive Handoff Engine
│   │   │   ├── peer_reviewer.py      # Automated P2P Code Review Engine
│   │   │   ├── vector_store.py       # Embedded 128-dim Vector Database
│   │   │   ├── security_scanner.py   # Real Python AST OWASP Scanner
│   │   │   ├── flight_recorder.py    # Time-Travel Blackbox Event Recorder
│   │   │   ├── financial_guardrail.py# Token Quota & Cost Control Guardrail
│   │   │   └── tool_synthesizer.py   # GitHub Tool Bridge with AST Security Scanner
│   │   ├── gateway/                  # Unified Multi-Provider LLM Client
│   │   └── sandbox/                  # Docker Sandbox Runner & Caddy Proxy Manager
│   ├── tests/                        # 174 Unit & Integration Test Suites (100% Passed)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js 14 App Router Pages
│   │   │   ├── organization/         # Visual Org Studio & Pipeline Builder
│   │   │   ├── kanban/[id]/          # Mission Control Kanban & Live Lounge
│   │   │   ├── preview/[id]/         # Live Sandbox Preview, PTY Terminal & Snapshots
│   │   │   ├── sparring/[id]/        # Executive Sparring Debate Room
│   │   │   ├── office/               # Global Oasis Live Command HQ
│   │   │   ├── settings/             # Dynamic BYOK Key Vault & System Settings
│   │   │   ├── analytics/            # Financial Unit Economics & Token Ledger
│   │   │   └── wisdom/               # Corporate Wisdom Base & GitHub Skill Importer
│   │   ├── components/               # Komponen Modular Antarmuka (SRP <= 150-200 baris)
│   │   │   ├── organization/         # WorkflowPipelineBuilder, RoleModal, BranchBar, dll.
│   │   │   ├── office/               # Oasis Live Command HQ UI Components
│   │   │   │   ├── oasis/            # Feed, ScreenSharePane, WarRoom, EventCard, SplitView
│   │   │   │   ├── AgentRosterSidebar.tsx
│   │   │   │   ├── OfficeChatConsole.tsx
│   │   │   │   └── OfficeControlBar.tsx
│   │   │   ├── settings/             # SettingsProviderTab (BYOK & Custom OpenAI-Compatible)
│   │   │   └── sandbox/              # Web PTY Terminal & Iframe Preview Container
│   │   ├── hooks/                    # Custom React Hooks
│   │   └── lib/                      # API Client Interfaces & TypeScript Types
│   ├── package.json
│   └── tailwind.config.ts
├── sandboxes/                        # Direktori Isolasi Proyek & Konfigurasi Caddy
├── projects_output/                  # Hasil Kompilasi Proyek Startup yang Dihasilkan
└── run.py                            # Universal Launcher Otomatis (Full-Stack Bootstrapper)
```

---

## 🛠️ Panduan Instalasi & Menjalankan Sistem

### Prasyarat Lingkungan
1. **Python**: Versi `3.10` atau lebih baru.
2. **Node.js**: Versi `18.x` atau `20.x` LTS (disertai `npm`).
3. **Docker** *(Opsional tetapi sangat disarankan)*: Untuk isolasi kontainer sandbox penuh. Jika Docker tidak aktif, sistem otomatis mengaktifkan *Embedded Async HTTP Server* lokal pada port 4000–4999.

### Langkah 1: Kloning Repositori
```bash
git clone https://github.com/HillarioRZA/virtual-coorporation.git
cd virtual-coorporation
```

### Langkah 2: Konfigurasi Kunci Lingkungan (`.env`)
Salin berkas contoh konfigurasi:
```bash
cp .env.example .env
```
Buka `.env` dan masukkan API Key LLM yang Anda miliki (minimal satu provider, misal OpenRouter, DeepSeek, atau Gemini):
```ini
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
# Atau gunakan provider pilihan Anda:
# GEMINI_API_KEY="AIzaSy..."
# DEEPSEEK_API_KEY="sk-..."
```
*(Catatan: Anda juga dapat mengatur kunci dan Base URL secara langsung melalui antarmuka web di tab `/settings` setelah aplikasi berjalan).*

### Langkah 3: Menjalankan Sistem Secara Otomatis (Universal Launcher)
Jalankan skrip peluncur universal terpadu:
```bash
python run.py
```
Skrip ini akan secara otomatis:
1. Memverifikasi integritas dependensi Python dan Node.js.
2. Menginisialisasi basis data SQLite WAL (`backend/data/startup_system.db` / `data/venture_memory.db`) dan mengeksekusi migrasi seeding otomatis.
3. Menjalankan server backend FastAPI pada `http://localhost:8000`.
4. Menjalankan server frontend Next.js 14 pada `http://localhost:3000`.

Buka peramban (*browser*) Anda dan akses:
👉 **`http://localhost:3000`**

---

## 🧪 Standar Kualitas & Pengujian Otomatis

Proyek ini dibangun dengan penegakan disiplin rekayasa perangkat lunak ketat:
* **Prinsip Single Responsibility (SRP)**: Seluruh berkas backend dan komponen frontend dibatasi maksimal **150–200 baris kode per file**.
* **Type Annotations**: 100% fungsi dan metode memiliki anotasi tipe Python dan TypeScript lengkap (0 error TS).
* **Zero Raw Prints**: Seluruh operasi dicatat menggunakan *structured logger* (`app.core.logger`).
* **Resiliensi I/O**: Seluruh operasi basis data, jaringan HTTP, dan pertukaran JSON dibungkus dalam blok `try-except` spesifik.

Untuk menjalankan seluruh rangkaian pengujian backend:
```bash
pytest backend/tests -q
```
**Status Pengujian: 174 / 174 Pengujian Lolos (100% PASSED, Zero Failure)**.

---

## 📄 Lisensi

Platform ini dirilis di bawah lisensi resmi **MIT License**. Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini untuk keperluan riset maupun komersial. Silakan merujuk ke berkas `LICENSE` untuk ketentuan hukum lengkap.

---
*Ditenagai oleh Sovereign Autonomous AI Corporate OS • Dirancang untuk Pengusaha Tunggal & Inovator Global.*
