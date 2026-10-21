# 🪐 Virtual Tech Startup Multi-Agent System & Sovereign Corporate OS
### Autonomous AI Virtual Enterprise Platform, Dynamic Asynchronous Workflow Engine & Global Oasis Live Command HQ

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2%20(Production%20Ready)-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Oasis 2D Liquid](https://img.shields.io/badge/Command%20HQ-Obsidian%20Liquid%202D-6366f1?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-216%2F216%20Passed%20(100%25)-brightgreen?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org/)
[![3-Layer Prompting](https://img.shields.io/badge/Prompting-3--Layer%20(Soul%20•%20SOP%20•%20Context)-8B5CF6?style=flat-square)](backend/app/engine/roles/dynamic_node.py)
[![FastEmbed](https://img.shields.io/badge/Neural%20RAG-FastEmbed%20ONNX%20(384--dim)-00D26A?style=flat-square&logo=onnx&logoColor=white)](backend/app/engine/memory/vector_store.py)
[![CoV Gatekeeper](https://img.shields.io/badge/Sentinel-Two--Tier%20CoV%20(Critic--Only)-FF6B6B?style=flat-square)](backend/app/engine/sentinel/verifier.py)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLite WAL](https://img.shields.io/badge/Database-SQLite%20WAL-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 💡 Executive Overview

**Virtual Tech Startup Multi-Agent System** adalah sistem operasi korporat kecerdasan buatan mandiri (*Sovereign Autonomous AI Corporate Operating System*) dan platform inkubasi startup digital mutakhir. 

Platform ini memberdayakan seorang **Founder tunggal (Solo Entrepreneur / Chairman / CEO)** untuk mengoperasikan konglomerasi digital berskala penuh secara mandiri: mulai dari inisiasi ide produk, riset pasar, penyusunan kontrak OpenAPI, rekayasa paralel Frontend & Backend, penjaminan mutu P2P, audit keamanan statis OWASP Top 10, hingga peluncuran langsung di sandbox kontainer terisolasi.

Seluruh dinamika perusahaan dipantau secara real-time melalui antarmuka **Global Oasis Live Command HQ** (`/office`) yang elegan, berkinerja tinggi (2D Obsidian Liquid Engine dengan slotting workstation dinamis), hemat token (Zero Idle Token Overhead), dan dilengkapi panel live thought stream, handoff inter-agen, serta ruang kontrol krisis All-Hands.

---

## 🏛️ Arsitektur Sistem Terpadu

Sistem dirancang dengan arsitektur berlapis (*layered architecture*) yang memisahkan antarmuka visual, orkestrasi logika asinkron, mesin kognitif model AI, serta lapisan keamanan dan isolasi eksekusi:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FOUNDER EXECUTIVE DASHBOARD                                        │
│                                  Next.js 14 App Router • TypeScript                                    │
│                                                                                                        │
│  /                 /organization         /kanban/[id]         /preview/[id]         /office            │
│  Portfolio Hub     Org Studio & AI Board Mission Control      Live Sandbox, PTY     Global Oasis Live  │
│  & Venture State   (3-Layer Prompting)   & Live Lounge WS     Terminal & Snapshots  Command HQ (2D)    │
│                                                                                                        │
│  /mcp              /skills               /analytics           /settings             /wisdom            │
│  MCP Server Hub    Public Skill Library  Ledger & Finance     BYOK & Secret Vault   FastEmbed 384-dim  │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │ REST API / WebSocket / SSE Streams
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FASTAPI HIGH-CONCURRENCY BACKEND                                     │
│                                        Pure ASGI Middleware Engine                                     │
│                                                                                                        │
│  • SecurityGateMiddleware (Stealth Dynamic PIN + OpenClaw Trust Boundary) • ProcessTimeLoggingMiddleware│
│  • 27 Modular REST & WebSocket Routers (Corporate, Skills, MCP, Tickets, Governance, Vault, Office)   │
└───────────────────────┬───────────────────────────────────────────────────────┬────────────────────────┘
                        │                                                       │
                        ▼                                                       ▼
┌──────────────────────────────────────────────┐        ┌────────────────────────────────────────────────┐
│       AUTONOMOUS KANBAN RUNNER ENGINE        │        │          CORPORATE EVENT BUS (PUB/SUB)         │
│ • SQLite WAL Atomic Claim Query              │        │ • Non-blocking asyncio.Queue per Project       │
│   (UPDATE ... WHERE id=? AND status='TODO')  │◄──────►│ • SQLite WAL Message Ledger Persistence        │
│ • Task Concurrency Dispatcher (Semaphore)    │        │ • Real-time WebSocket Lounge Broadcast        │
│ • FileLockManager (Path Mutex Concurrency)   │        │ • Agent Dialogue & Incident Escalation Log     │
└───────────────────────┬──────────────────────┘        └───────────────────────┬────────────────────────┘
                        │                                                       │
                        ▼                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXECUTIVE GOVERNANCE & GUARDRAILS                                   │
│                                                                                                        │
│  • Agent Decision Envelope: { PROCEED | CONSULT_ROLE | ESCALATE_TO_C_LEVEL | REQUEST_REWORK }          │
│  • Table-Driven State Transition Matrix O(1) FSM: Evaluasi gerbang deterministik (Stage-Gate)          │
│  • Anti-Infinite Loop Circuit Breaker: Auto-Freeze Ticket on >= 3 Consecutive Debate Turns             │
│  • Financial Guardrail & Flight Recorder: Hard Quota ($1.50 / 350k tokens) & Dynamic Pricing Ledger    │
│  • 1-Click CEO Strategic Intervention & Veto (Force Proceed / Chat Directive / Reassign Role)          │
│  • Three-Way Branch Merge Engine: LCA Graph Traversal for Isolated Corporate Branch Merging            │
└───────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                TWO-TIER COGNITIVE & EXECUTION ENGINES                                  │
│                                                                                                        │
│  • Sovereign Model Router: Multi-Channel Failover (9router-style), Hermes Multi-Key Pool & Radar       │
│  • Two-Tier CoV Gatekeeper: Tier 1 Deterministic Guard (0ms, 0 Token) & Tier 2 LLM Pre-Flight Critic  │
│  • Worker Self-Repair Loop: CoV murni sebagai auditor; Agen Peran wajib memperbaiki parameter sendiri │
│  • Hermes Layered Context Compactor: Tool output pruning (>400 baris) & tail retention 4 giliran       │
│  • Corporate Wisdom Base: FastEmbed ONNX 384-dim Neural RAG (Thread-Offloaded & Pre-warmed)            │
│  • Dynamic Tool Registry: Local Tools, Persistent Custom Tools (corporate_custom_tools), & MCP Router │
│  • Telegram Secretary Daemon: Background Long Polling, Sender Whitelist & Inline Approval Gate         │
│  • Hardened Docker Subnet Sandbox: Dedicated bridge_net_{project_id} with Hard CPU/RAM Quota           │
│  • Global Oasis Live Engine: Real-time Multi-Agent Thoughts, Scoped @mentions & Dynamic Auto-Slotting  │
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
* **Karyawan AI Fleksibel & 100% Slug-Free**: Mendaftarkan peran AI baru dengan spesifikasi granular:
  - **Persona Prompt (Layer 1 - Soul)**: Temperamen dasar, filosofi kerja, dan identitas psikologis yang *immutable*.
  - **System Prompt Template (Layer 2 - SOP)**: Panduan operasional peran, format JSON Pydantic, dan standar kerja.
  - Penugasan model LLM dan provider independen per agen.
  - **Dynamic Thinking Level (Reasoning Effort)**: Opsi kedalaman penalaran (`none`, `low`, `medium`, `high`) per peran AI.
  - Pengatur kreativitas (*temperature* 0.0 s/d 1.5).
  - Alokasi batas anggaran token (*token budget* 1.000 s/d 100.000 token per tugas).
  - Izin perkakas modular (*tool permissions*): `read_file`, `write_file`, `ast_patch_file`, `search_codebase`, `web_search`, `execute_code`, `inspect_db_schema`, `validate_api_contract`, `git_diff_summary`, dan `runtime_tool_builder`.
  - Indikator visual badge `✦ Soul` pada kartu peran yang memiliki konfigurasi persona mandiri.

### 3. 3-Layer Prompting Architecture & Anti-Persona Drift
* **Tiga Lapisan Prompting Terisolasi (*Layered Cognition*)**:
  - 🧬 **Layer 1: Persona Prompt (Soul / DNA)**: Inti karakter psikologis dan gaya bahasa agen. Ketika model utama (seperti Claude 3.5 Sonnet atau GPT-4o) mengalami rate-limit atau kehabisan token, 9Router secara otomatis mengalihkan tugas ke model fallback yang lebih ringan (seperti Mistral, GPT-4o-mini, atau Llama 3). Layer 1 menjamin model pengganti **tidak mengalami krisis identitas (*anti-persona drift*)** dan tetap menjaga karakter aslinya.
  - 📋 **Layer 2: System Prompt Template (SOP & Directives)**: Standar operasional prosedur, instruksi kontrak output Pydantic v2, aturan anti-hallucination, dan direktif domain tugas.
  - ⚡ **Layer 3: User Context (Kanban & Dynamic Memory)**: Status kartu tugas aktif, dependensi tiket, ringkasan artefak blackboard, dan instruksi langsung Founder.
* **Perakitan Otomatis di Runtime (`dynamic_node.py`)**: Sistem menggabungkan Layer 1 dan Layer 2 menjadi satu system prompt kohesif dengan header pemisah yang tegas sebelum dikirim ke gateway inferensi.
* **Evolusi Otonom & Pemangkasan Visual n8n**: Modul canvas drag-and-drop bergaya n8n telah dipensiunkan untuk memangkas ukuran bundle JavaScript klien sebesar **28%** (menjadi 15.8 kB). Sistem bertransformasi penuh menuju eksekusi otonom berbasis tujuan (*goal-driven task dependencies*) dan Finite State Machine (FSM).

### 4. Dynamic Asynchronous Kanban, Autonomous Runner & File Locks
* **Manajemen Tiket Otonom**: Setiap tugas venture direpresentasikan dalam kartu tiket (`corporate_tickets`) lengkap dengan branch, divisi, penanggung jawab, lini produk, prioritas, dan dependensi prasyarat.
* **Siklus Hidup 5 Kolom**: `BACKLOG ➔ TODO ➔ IN_PROGRESS ➔ REVIEW ➔ DONE`. Agen mendeteksi tiket yang siap dikerjakan secara mandiri begitu seluruh dependensi terpenuhi.
* **Autonomous Non-Blocking Scheduler (`kanban_runner.py`)**: Daemon background task yang memantau tiket siap kerja secara kontinu dan mengeksekusi agen secara otonom tanpa memerlukan intervensi tombol manual di UI.
* **SQLite WAL Atomic Claim Query**:
  ```sql
  UPDATE corporate_tickets 
  SET status = 'IN_PROGRESS', updated_at = CURRENT_TIMESTAMP 
  WHERE id = ? AND status = 'TODO' 
  RETURNING *;
  ```
  Menjamin ketiadaan eksekusi ganda (*zero double-execution*) di antara beberapa worker paralel.
* **FileLockManager (`file_lock_manager.py`)**: Manajemen *mutex lock* asinkron per jalur berkas (`asyncio.Lock` per absolute file path), mengeliminasi tabrakan penulisan (*race conditions*) saat beberapa agen bekerja paralel pada kode sumber yang berdekatan.
* **Corporate Event Bus Asinkron (`event_bus.py`)**: Arsitektur pub/sub non-blocking berbasis `asyncio.Queue` per proyek yang mendistribusikan sinyal tugas ke antarmuka web, WebSocket Lounge, dan telemetri secara instan.

### 5. Executive Governance Hub & Stage-Gate Transition Matrix O(1)
* **Table-Driven State Transition Matrix $O(1)$ (`GATE_TRANSITION_TABLE`)**: Seluruh evaluasi persetujuan/penolakan gerbang di `routers.py` menggunakan matriks transisi deterministik berbasis dictionary, membuang ladder `if-elif` manual yang rapuh dan menjamin transisi state venture bersifat $O(1)$ instan.
* **Format Keputusan Terstruktur (`AgentDecisionEnvelope`)**: Agen merespons tugas dalam format JSON kanonikal dengan opsi aksi: `PROCEED`, `CONSULT_ROLE`, `ESCALATE_TO_C_LEVEL`, atau `REQUEST_REWORK`.
* **Anti-Infinite Loop Circuit Breaker (`circuit_breaker.py`)**: Melacak putaran diskusi konsultasi inter-agen pada tiket yang sama. Jika diskusi mencapai **$\ge 3$ putaran berturut-turut** tanpa menghasilkan kode baru, sistem secara otomatis membekukan tiket menjadi `BLOCKED_LOOP_DETECTED`.
* **Hak Veto & Intervensi 1-Klik CEO**: Founder dapat mengambil alih tiket yang dibekukan:
  - `FORCE_PROCEED`: Melewati perdebatan dan memaksa tugas selesai (`DONE`).
  - `INTERVENE`: Memberikan instruksi tertulis mutlak dan mengembalikan tiket ke `IN_PROGRESS`.
  - `REASSIGN`: Mengalihkan tugas ke peran karyawan AI lain.
* **Eskalasi C-Level Langsung**: CTO atau CoS memformulasikan laporan ringkas Opsi A vs Opsi B untuk keputusan cepat Founder.

### 6. Sovereign Model Router, Polymorphic Contracts & Dynamic Accounting
* **Polymorphic Contract Strategy (`contract_handlers.py`)**: Menghilangkan rantai `if-elif` rapuh dan menggantikannya dengan strategi handler polimorfik terstruktur untuk validasi arsitektur, PRD, komponen UI, berkas kode, dan scorecard penjaminan mutu.
* **Dynamic Pricing & Real CFO Ledger**: Menggantikan kalkulasi statis $0.02 dengan perhitungan riil per-token aktual sesuai model dan mencatat penggunaannya langsung ke tabel transaksi `corporate_token_ledger`.
* **Pre-Flight & Post-Flight Financial Guardrail**: Sinkronisasi aktif dengan `financial_guardrail.py`, memberlakukan *pre-flight validation* batas kuota pengeluaran ($1.50 atau 350.000 token per tiket) dengan pembekuan otomatis (*auto-freeze* `FROZEN_PENDING_APPROVAL`).
* **Multi-Channel Fallback Cascade & Hermes Credential Pool**: Orkestrasi perutean hulu cerdas dengan rantai model cadangan otomatis, rotasi multi-kunci, *exponential backoff*, dan *self-healing cooldown* saat menerima HTTP 429 atau 503.
* **Dynamic Thinking Level Control**: Pengaturan kedalaman penalaran model (`none`, `low`, `medium`, `high`) per peran AI dengan auto-escalation ke `high` saat terjadi rework.
* **State-First Cognitive Handoff**: Pemadatan konteks berbasis status arsitektur (AST symbols, schema contracts, file diffs) yang membuang tag penalaran `<think>`, **menghemat $>85\%$ konsumsi token** sembari mempertahankan **98% retensi konteks teknis**.

### 7. Autonomous Peer-to-Peer PR Review Engine & Quorum Gate
* **Siklus Hidup Pull Request Otomatis**: Kode hasil pekerjaan agen dikemas menjadi Pull Request lengkap dengan tampilan diff Git-style (`+`/`-`).
* **Review Multi-Disiplin Terisolasi**: Menugaskan peninjauan kode ke spesialis yang relevan (QA Engineer menguji keamanan dan test case, CTO memeriksa kepatuhan arsitektur, dan Backend/Frontend memeriksa kontrak data).
* **Quorum Approval Gate**: Kode hanya dapat digabungkan (*merged*) jika mendapatkan **minimal $\ge 2$ persetujuan (*approvals*)** dari agen peninjau tanpa komentar penolakan aktif.

### 8. Corporate Wisdom Base & FastEmbed ONNX Local Neural RAG
* **Local Neural Semantic Embeddings (384-Dimensi)**: Menggunakan model dense vector **FastEmbed ONNX** lokal (`BAAI/bge-small-en-v1.5`) dengan normalisasi $L_2$ dan cosine similarity, menghasilkan pencarian semantik berpresisi tinggi tanpa latensi API eksternal.
* **Non-Blocking Asynchronous Offloading**: Pembuatan vektor dijalankan terisolasi melalui thread worker pool menggunakan `asyncio.to_thread()`, menjamin *event loop* asyncio tetap responsif.
* **Lifespan Startup Pre-warming**: Model embedding diinisialisasi dan di-cache saat boot server FastAPI, mengeliminasi lonjakan latensi (*cold start penalty*) pada permintaan pertama.
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

### 14. Two-Tier Chain-of-Verification (CoV) Pre-Flight Gatekeeper & Worker Repair Loop
* **Arsitektur Dua Tingkat (Two-Tier Architecture)**:
  - **Tier 1 (Deterministik Python — 0ms, 0 Token)**: Memeriksa validitas skema Pydantic, tipe parameter, dan izin peran (*role tool permissions*). Seluruh pemanggilan alat baca (*read-only tools* seperti `read_codebase`, `search_codebase`, `inspect_db_schema`, `git_diff_summary`) yang lolos Tier 1 langsung disetujui (`APPROVED`) tanpa memanggil model LLM kedua.
  - **Tier 2 (LLM Pre-Flight Inspector)**: Khusus mengaudit pemanggilan alat mutasi (*mutating tools* seperti `write_codebase`, `synthesize_and_register_tool`, `lock_test_suite`) dan artefak kontrak data tonggak akhir.
* **Filosofi Ketat "Critic-Only" (Tanpa Pembajakan & Tanpa Self-Repair)**:
  - CoV **HANYA** bertindak sebagai auditor/kritikus teknis independen. CoV dilarang keras melakukan perbaikan mandiri atau mengeksekusi perkakas atas namanya sendiri.
  - Jika ada parameter yang kurang atau pemanggilan cacat, CoV menetapkan status `REPAIR_REQUIRED` dan menghasilkan `repair_feedback` yang spesifik (misal: "Alat OWASP membutuhkan parameter a, b, c, d, tetapi hanya a, b, c yang dikirim").
* **Autonomous Role-Worker Self-Repair Loop**:
  - Agen peran pemanggil menerima umpan balik koreksi CoV, memperbaiki parameternya secara mandiri menggunakan konteks domain lengkapnya, dan mengirimkan kembali respons hasil perbaikan.
  - Setelah CoV memvalidasi dan memberikan lampu hijau (`APPROVED`), **agen peran itu sendiri yang mengeksekusi perkakasnya** dan menerima observasi langsung (*Non-Hijacking Execution*).
* **Konfigurasi Internal Terkunci di Server (Zero UI Exposure)**:
  - Seluruh konfigurasi CoV (`COV_PROVIDER`, `COV_MODEL`, `COV_BASE_URL`, `COV_API_KEY`) diatur secara eksklusif via `.env` dan `config.py` tanpa pernah diekspos ke antarmuka `/settings` maupun `/organization`.
* **CoV Sentinel Observability Dashboard (`/office`)**:
  - Antarmuka telemetri real-time di Command HQ dengan Bento Grid (Total Pre-Flight Audits, Skor Reliabilitas %, Jumlah Auto-Repairs, Rerata Latensi ms).
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

### 16. Dynamic Polymorphic Role Node Engine & Single-Source Corporate Registry
* **Penghapusan Total Node Statis & Berkas Prompt**:
  - Seluruh berkas node peran statis di `backend/app/engine/nodes/` dan berkas `backend/prompts/*.md` telah dihapus secara fisik demi transisi ke arsitektur dinamis sejati.
  - Tabel SQLite `corporate_roles` bertindak sebagai **Satu-Satunya Sumber Kebenaran (*Single Source of Truth*)** untuk seluruh konfigurasi peran: nama, slug, deskripsi tugas & fokus jobdesk (`job_description`), instruksi persona sistem (`system_prompt_template`), model LLM, provider, temperature, batas token, dan izin perkakas.
* **Mesin Eksekusi Polimorfik Tunggal (`execute_dynamic_role_node`)**:
  - Seluruh peran dieksekusi oleh mesin tunggal di `app/engine/roles/dynamic_node.py` yang secara dinamis memuat konfigurasi peran, menjalankan loop perkakas (`_handle_agent_tools`), menyelaraskan skema output (`role_output_processor.py`), dan mencatat publikasi artefak ke memori blackboard (`role_event_logger.py`).
* **Injeksi Hierarki Pohon Organisasi (*Org-Tree Scoped Context*)**:
  - Agen eksekutif (CoS, CTO, PM) secara otomatis menerima konteks menyeluruh mengenai struktur organisasi perusahaan terkini: daftar divisi, tujuan/mandat divisi (`purpose`), seluruh peran AI di dalam divisi, serta fokus tugas dan jobdesk masing-masing (`job_description`).
* **Executive Baton Relay & `@mention` Routing Terarah**:
  - Percakapan antar-agen di Oasis HQ maupun Sparring Room mendukung pengalihan estafet tongkat komando (*Baton Relay*).
  - Dilengkapi guardrail batas estafet maksimum `MAX_RELAY_HOPS = 3` dan pengabaian *self-mention* untuk mencegah *infinite ping-pong loop* antar-agen.
* **Adversarial TDD Berbasis Izin Perkakas (*Tool Permission Decoupled*)**:
  - Logika isolasi penguncian berkas tes (*read-only* & `chmod 444`) kini dipisahkan sepenuhnya dari nama berkas python statis dan dialihkan menjadi izin perkakas `lock_test_suite` di antarmuka organisasi.
* **Manajemen Visual Tujuan Divisi & Jobdesk Peran di UI**:
  - Antarmuka visual `/organization` memungkinkan Founder mengubah Tujuan Divisi (*Division Purpose*) dan Fokus Jobdesk Karyawan AI (*Role Job Description*) secara langsung tanpa menyentuh kode backend.

### 17. Remote Executive Liaison: Telegram Secretary Daemon (5 Pilar Operasional)
* **Long Polling Daemon Background Worker (`telegram_daemon.py`)**: Berjalan di latar belakang menggunakan `httpx.AsyncClient` tanpa memerlukan konfigurasi webhook publik atau port forwarding rumit.
* **OpenClaw Trust Boundary (Whitelist Protection)**: Memeriksa identitas pengirim di gerbang terluar. Hanya pesan dari `user_id` yang terdaftar dalam `TELEGRAM_ALLOWED_USER_IDS` yang diproses. Upaya akses tanpa izin langsung ditolak dan dicatat sebagai *security probe* ke `flight_recorder.py`.
* **Dynamic Role Secretary Integration (`secretary_resolver.py`)**: Agen eksekutif personal Founder yang terdaftar resmi di tabel `corporate_roles` (memiliki permission `chat_telegram` atau peran Secretary di bawah divisi `div_exec`), menjembatani instruksi Founder di aplikasi Telegram dengan operasional multi-agen. Parameter model, prompt kustom, persona, dan izin perkakas dari UI `/organization` langsung digunakan secara dinamis.
* **Shared Bot Configuration**: Konfigurasi `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID` digunakan secara bersama (*shared credentials*) antara Gerbang Keamanan (pengiriman PIN dinamis 6-digit untuk login) dan Daemon Sekretaris (interaksi chat dua arah), sehingga Founder cukup mengonfigurasi satu bot Telegram tunggal di `.env`.
* **5 Pilar Operasional Sekretaris**:
  1. 💬 **Tactical Dialogue & Remote Sparring**: Konsultasi strategi, brainstorming ide bisnis, dan diskusi teknis dua arah kapan pun Founder berada jauh dari laptop.
  2. 📋 **Away-From-Desk Kanban Dispatcher (`secretary_task_bridge.py`)**: Memantau status beban kerja korporat via `/status` atau `/tasks`, serta membuat dan mendisposisikan tiket baru ke papan Kanban via perintah `/task <deskripsi>` atau instruksi verbal.
  3. 📢 **Proactive Autonomous Event Bus Reporting (`secretary_reporter.py`)**: Berlangganan langsung ke `corporate_event_bus` dan mengirimkan laporan proaktif (*push notification*) secara real-time saat tugas selesai (`TASK_COMPLETED`), gagal (`TASK_FAILED`), atau mengalami deadlock (`CIRCUIT_BREAKER_TRIGGERED`).
  4. 📦 **Dry-Run & Direct Skill/MCP Installer (`secretary_installer.py`)**: Analisis otomatis URL repositori git atau modul MCP, pratinjau keamanan dry-run, dan eksekusi instalasi nyata ke sistem backend saat Founder membalas `/confirm_skill <url>`.
  5. 🛠️ **Dynamic Tool Synthesis & Inline Approval**: Pembuatan perkakas Python baru saat Founder memintanya di chat Telegram, registrasi otomatis dengan status `PENDING_APPROVAL`, serta aktivasi instan via `/approve <nama_tool>` atau penolakan via `/reject <nama_tool>`.

### 18. Extensible Dynamic Tool Registry & SQLite Custom Tool Persistence
* **Dynamic Tool Registry (`dynamic_tool_registry.py`)**: Registri perkakas yang dapat diperluas (*extensible*), menggantikan percabangan statis dengan routing dinamis untuk perkakas internal, server eksternal berbasis **Model Context Protocol (MCP)**, dan perkakas kustom runtime.
* **SQLite Persistence (`corporate_custom_tools`)**: Menyimpan definisi perkakas yang disintesis (nama perkakas, deskripsi, skema JSON parameter, source code Python, peran pembuat, dan flag persetujuan) ke dalam database SQLite.
* **Crash-Resistant Startup Reloader**: Saat server FastAPI boot (`lifespan`), seluruh perkakas yang berstatus `is_approved = 1` secara otomatis dikompilasi ulang secara aman dan didaftarkan kembali ke registri runtime, mencegah *wipeout* saat restart.

### 19. Hermes Layered Context Compactor & Memory Optimization
* **Tool Output Pruning (`context_compactor.py`)**: Memotong keluaran observasi perkakas yang sangat panjang (>400 baris atau data biner) menjadi intisari status arsitektural padat.
* **Progressive Executive Summarization**: Jika akumulasi token mencapai $\ge 70\%$ dari batas jendela konteks model, riwayat pesan awal dipadatkan secara otomatis menjadi ringkasan status teknis.
* **Tail Retention Guarantee**: Mempertahankan 4 giliran percakapan terbaru (*last 4 turns*) secara utuh tanpa pemotongan agar agen tidak kehilangan instruksi dan konteks operasional terkini.

### 20. Model Context Protocol (MCP) Server Hub & Unified Role Permissions Pool (`/mcp`)
* **Instalasi & Manajemen Server MCP Tanpa Koding**: Antarmuka visual `/mcp` memungkinkan Founder memasang server MCP eksternal berbasis stdio JSON-RPC 2.0 (seperti GitHub MCP, Postgres MCP, Filesystem MCP) hanya dengan mengisi command, argumen, dan variabel lingkungan.
* **Brankas Rahasia Terenkripsi AES-256-GCM**: Variabel lingkungan sensitif (misal `GITHUB_PERSONAL_ACCESS_TOKEN`, `DATABASE_URL`) dienkripsi secara aman di tabel `corporate_mcp_servers` sebelum disimpan ke basis data SQLite.
* **Unified Role Permissions Catalog (`/api/v1/mcp/all-tools`)**: Endpoint ini mengagregasi seluruh perkakas yang tersedia di seluruh platform—mencakup perkakas bawaan sistem (`builtin`), seluruh perkakas dari server MCP aktif (`mcp_tools`), serta perkakas kustom buatan Sekretaris yang telah disetujui (`custom_tools` status `APPROVED`). Seluruh perkakas otomatis muncul di pemilih izin peran pada antarmuka `/organization` (dengan badge amber untuk custom tools).
* **Referential Dependency Guardrail (Anti-Accidental Deletion)**: Mencegah penghapusan server MCP jika masih ada peran AI aktif yang memegang izin perkakas dari server tersebut (mengembalikan HTTP 409 Conflict beserta daftar nama peran terkait).
* **Two-Tier CoV Routing Cerdas**: Perkakas pembacaan (`mcp:*:get_*`, `list_*`, `read_*`) dialirkan langsung ke Tier 1 Deterministic Verifier (0ms latency & 0 token overhead), sedangkan perkakas mutasi (`create_*`, `delete_*`, `execute_*`) dialirkan ke Tier 2 CoV LLM Critic.

### 21. Public Skills Library, Git Importer & Dynamic Taxonomy Hub (`/skills`)
* **Git & Remote Skill Importer (`git_importer.py` & `POST /skills/import-git`)**: Mampu mengimpor repositori keahlian kompleks yang memiliki banyak berkas (seperti `ui-ux-pro-max-skill`) langsung melalui URL repositori GitHub/GitLab. Sistem melakukan kloning dangkal (`--depth 1`), mengekstrak hierarki folder (`scripts/`, `examples/`, `references/`), mem-parsing metadata YAML `SKILL.md`, serta mengindeks seluruh manifest berkas ke mesin pencari teks penuh SQLite FTS5 (`corporate_skills_fts`).
* **Dual-Mode UI Importer (`/skills`)**: Modal instalasi menyediakan dua tab: **"Repository Git (Auto-Import)"** untuk impor otomatis instan dari repositori publik dan **"Manual SKILL.md"** untuk penulisan panduan mandiri.
* **Arsitektur Bundle Folder Terisolasi**: Skills disimpan sebagai bundle direktori mandiri di bawah `skills/<category>/<skill_name>/` yang memuat berkas `SKILL.md`, skrip pembantu, dan referensi aset.
* **0% Beban Vektor ONNX (Zero Vector Bloat)**: Berbeda dari Corporate Wisdom Base yang mengonsumsi kapasitas embedding neural ONNX 384-dim, Skills Library beroperasi murni sebagai perpustakaan publik berbasis indeks teks penuh SQLite FTS5 (BM25 ranking).
* **Dynamic Auto-Category Taxonomy**: Jika pengguna memasang skill dengan kategori baru (misal: `business-management`, `cloud-native`), sistem mendeteksi keberadaan kategori secara otomatis dan mendaftarkannya ke tabel `corporate_skill_categories` tanpa intervensi manual.
* **Proteksi Path Traversal Ketat**: Mekanisme sanitasi memblokir upaya eksploitasi path traversal (`../` atau `..\\`) saat ekstraksi bundle skill dari arsip zip atau git.
* **Autonomous Agent Self-Discovery**: Agen memiliki dua perkakas bawaan:
  - `consult_skill_library(category, keyword)`: Agen dapat menelusuri perpustakaan skill secara mandiri sesuai kebutuhan tugas.
  - `read_skill_detail(skill_name, category)`: Agen membaca panduan implementasi `SKILL.md` secara selektif saat mengerjakan tiket.

### 22. In-Sandbox Language Server Protocol (LSP) Engine & PR Gatekeeper
* **Dual-Mode LSP Diagnostics**:
  - **On-Demand Agent Tool (`run_lsp_diagnostics`)**: Agen perekayasa (Frontend & Backend) dapat menjalankan diagnostik tipe dan sintaksis kapan saja saat menyunting kode.
  - **Automated Pre-PR Quality Gate (`lsp_gatekeeper.py`)**: Sebelum Pull Request disetujui dalam quorum P2P (`peer_reviewer.py`), sistem memicu verifikasi diagnostik LSP. Jika terdeteksi galat fatal (`error`), PR otomatis ditolak dengan umpan balik perbaikan.
* **Project-Wide TypeScript Compiler Filtering**: Menjalankan `tsc --project tsconfig.json` pada root proyek, namun menyaring diagnostik fatal hanya pada berkas yang diubah dalam PR untuk mengeliminasi *false positives* dari berkas sandbox lain.
* **Python AST & Syntax Fallback**: Validasi sintaksis Python berbasis Abstract Syntax Tree (AST) untuk mendeteksi `SyntaxError` secara deterministik tanpa dependensi eksternal.

### 23. Telegram Secretary Dry-Run, Direct Installation & Secret Credential Interceptor
* **Dry-Run Intent Detection**: Saat Founder meminta instalasi MCP atau Skills melalui Telegram (misal: *"install skill https://github.com/..."* atau *"install mcp github token=ghp_xxx"*), Sekretaris mendeteksi niat, memverifikasi parameter, dan memberikan pratinjau dry-run sebelum mengeksekusi instalasi.
* **Direct Git Skill Installation via `/confirm_skill <url>`**: Founder dapat memicu instalasi nyata secara asinkron dari jarak jauh hanya dengan mengonfirmasi URL yang diajukan oleh Sekretaris.
* **Secret Interception & Vault Storage**: Token rahasia (`token=...`, `key=...`) diekstraksi sebelum pesan dikirimkan ke model LLM atau log publik, dan disimpan langsung ke brankas rahasia terenkripsi AES-256-GCM.
* **Scrubbing & Auto-Delete Telegram History**: Menyamarkan token dalam teks balasan (`token=***`) dan memanggil endpoint Telegram Bot API `deleteMessage` untuk menghapus pesan asli Founder dari riwayat obrolan Telegram demi keamanan maksimal.

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

## 📡 Spesifikasi 27 Router API Backend

Seluruh endpoint REST API dan WebSocket terpusat di bawah prefix `/api/v1` dengan validasi skema tipe Pydantic v2:

| No | Modul Router | Prefix Endpoint | Tipe | Deskripsi & Tanggung Jawab Utama |
|:--:|:-------------|:----------------|:----:|:---------------------------------|
| 1 | `corporate.py` | `/corporate` | REST | CRUD hierarki organisasi: branch, forking alur kerja, divisi dinamis, dan pendaftaran peran AI (100% Slug-Free, 3-Layer Prompting). |
| 2 | `corporate_workflow.py` | `/corporate/branches/{id}` | REST | Pengelolaan tahapan alur kerja dan gerbang keputusan CEO berbasis FSM deterministik. |
| 3 | `corporate_tickets.py` | `/corporate/tickets` | REST | Manajemen kartu tiket Kanban virtual (5 status), dependensi tugas, dan tingkat prioritas. |
| 4 | `corporate_events.py` | `/corporate/events` | REST | Riwayat percakapan inter-agen, dialog eskalasi, dan log event bus korporat. |
| 5 | `corporate_ws.py` | `/ws/corporate` | WS | WebSocket streaming dua arah untuk sinkronisasi tiket Kanban dan siaran event real-time. |
| 6 | `governance.py` | `/governance` | REST | Pengawas interaksi agen: status circuit breaker, eskalasi C-Level, dan intervensi hak veto CEO. |
| 7 | `branch_merge.py` | `/corporate/branches` | REST | Analisis *diff* struktural antar-branch dan penggabungan atomik branch eksperimen ke main via LCA. |
| 8 | `projects.py` | `/projects` | REST | Siklus hidup venture: inisiasi ide baru, muat checkpoint state, dan **Cascading Clean Sweep Deletion** (`DELETE /{id}`). |
| 9 | `project_artifacts.py` | `/projects/{id}/artifacts` | REST | Akses berkas artefak venture, OpenAPI specs, PRD, dan preview link. |
| 10 | `sparring.py` | `/projects/{id}/sparring` | REST / SSE | Sesi debat sokratik pra-PRD antar-agen dengan dukungan `@mention` dinamis seluruh peran aktif organisasi. |
| 11 | `gates.py` | `/projects/{id}/gates` | REST | Stage-Gate keputusan Founder: persetujuan formal, revisi arahan, atau terminasi proyek. |
| 12 | `pull_requests.py` | `/projects/{id}/prs` | REST | Siklus hidup PR otomatis: automated peer-to-peer code review dan quorum approval gate ($\ge 2$). |
| 13 | `vault.py` | `/projects/{id}/vault` | REST | Penyimpanan kredensial produksi rahasia terenkripsi AES-256-GCM (Secret Vault). |
| 14 | `analytics.py` | `/analytics` | REST | CFO Observability: token ledger summary, burn rate timeline, role costs, dan health radar sliding window. |
| 15 | `settings.py` | `/settings` | REST | Pengaturan dinamis sistem (BYOK API keys, parameter PaaS, reset konfigurasi) tanpa restart server. |
| 16 | `auth.py` | `/auth` | REST | Verifikasi PIN dinamis 6-digit gerbang keamanan Telegram dan penerbitan session token HMAC. |
| 17 | `wisdom.py` | `/wisdom` | REST | Corporate Wisdom Knowledge Base: penarikan best-practice RAG vektor 128-dim & auto-sync boot/mutasi. |
| 18 | `office.py` | `/corporate/office` | REST | Endpoint REST status agen, intervensi terarah scoped per-role, dan pengiriman direktif Founder. |
| 19 | `office_ws.py` | `/corporate/ws/office` | WS | WebSocket streaming dua arah siaran aliran diskursus agen, sinyal handoff, dan aktivitas real-time. |
| 20 | `sandbox_snapshots.py` | `/projects/{id}/sandbox` | REST | Manajemen snapshot direktori proyek (CoW) dan pemulihan 1-Click Rollback anti-data-loss. |
| 21 | `sandbox_network.py` | `/projects/{id}/network` | REST | Pemeriksaan status isolasi subnet Docker dan pemetaan routing reverse proxy Caddy. |
| 22 | `sandbox_terminal_ws.py`| `/ws/sandbox/{id}/terminal`| WS | Terminal interaktif PTY shell CLI live dua arah di dalam lingkungan sandbox proyek. |
| 23 | `files.py` | `/files` | REST | Upload dan unduh lampiran multimodal dengan verifikasi MIME dan proteksi path traversal. |
| 24 | `sentinel.py` | `/sentinel` | REST | Telemetri CoV (Chain-of-Verification) Pre-flight Guardrail dan audit celah keamanan. |
| 25 | `frontier_radar.py` | `/frontier-radar` | REST | Telemetri model router upstream health, token consumption rate, dan cooldown tracker. |
| 26 | `mcp_routes.py` | `/mcp` | REST | Manajemen server MCP eksternal, enkripsi AES-256 kredensial, dry-run discovery, dan Unified Role Permissions (`/mcp/all-tools`). |
| 27 | `skills_routes.py` | `/skills` | REST | Public Skills Library, SQLite FTS5 search, instalasi bundle lokal, dan Git & Remote Skill Importer (`POST /skills/import-git`). |

---

## 📂 Struktur Direktori Proyek

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/                   # 27 Modul Router REST API & WebSocket (SRP <= 200 baris)
│   │   │   ├── analytics.py          # Metrik Token Ledger & CFO Observability
│   │   │   ├── auth.py               # Otentikasi Stealth PIN & Telegram Security Gate
│   │   │   ├── branch_merge.py       # Git-Style Branch Diff & LCA Atomic Merge
│   │   │   ├── corporate.py          # Corporate Organization Hierarchy CRUD (Slug-Free)
│   │   │   ├── corporate_events.py   # Corporate Event Log & Message Queries
│   │   │   ├── corporate_tickets.py  # Kanban Virtual Tickets & Task Transitions
│   │   │   ├── corporate_workflow.py # Dynamic Workflow Pipeline & Looping Sequence
│   │   │   ├── corporate_ws.py       # Kanban Real-Time WebSocket Channel
│   │   │   ├── files.py              # File Upload & Multimodal Extraction
│   │   │   ├── frontier_radar.py     # Upstream Health & Model Router Radar
│   │   │   ├── gates.py              # Founder Stage-Gate Decisions
│   │   │   ├── governance.py         # Executive Governance, Escalation & CEO Veto
│   │   │   ├── mcp_routes.py         # MCP Server Dynamic Management & Unified Permissions
│   │   │   ├── office.py             # Live Command HQ State & Directives API
│   │   │   ├── office_ws.py          # Multi-Agent Live Streams WebSocket Channel
│   │   │   ├── projects.py           # Venture State & Cascading Clean Sweep Deletion
│   │   │   ├── project_artifacts.py  # Venture Artifacts & Preview Delivery
│   │   │   ├── pull_requests.py      # Automated PR Engine & Quorum Peer Review
│   │   │   ├── sandbox_network.py    # Docker Network & Reverse Proxy Routing
│   │   │   ├── sandbox_snapshots.py  # Zero-Data-Loss CoW Snapshots & 1-Click Rollbacks
│   │   │   ├── sandbox_terminal_ws.py# Interactive Web PTY Terminal Stream
│   │   │   ├── sentinel.py           # Chain-of-Verification Audit Logs & Findings
│   │   │   ├── settings.py           # Dynamic BYOK & Runtime Settings Manager
│   │   │   ├── skills_routes.py      # Public Skills Library & Git Repo Importer
│   │   │   ├── sparring.py           # Executive Sparring Room (Dynamic Org Roles)
│   │   │   ├── vault.py              # AES-256-GCM Encrypted Secret Vault
│   │   │   └── wisdom.py             # Corporate Wisdom Base & Vector RAG
│   │   ├── core/                     # Config, Logger, Security Gate, Settings & Constants
│   │   ├── db/                       # Basis Data SQLite Asinkron (aiosqlite WAL)
│   │   │   ├── branch_repo.py        # Isolasi Branching & Forking Database
│   │   │   ├── corporate_repo.py     # Unified Corporate Facade Database
│   │   │   ├── custom_tools_schema.py# DDL Tabel corporate_custom_tools (Secretary Tools)
│   │   │   ├── division_repo.py      # Operasi Divisi Organisasi
│   │   │   ├── role_repo.py          # Operasi Peran Karyawan AI (100% Slug-Free)
│   │   │   ├── pipeline_repo.py      # Multi-Product Pipelines
│   │   │   ├── ticket_repo.py        # Virtual Kanban Tickets Storage
│   │   │   ├── workflow_repo.py      # Pipeline Stages & Ordering Storage
│   │   │   ├── token_ledger_repo.py  # CFO Token Ledger & Cost Attribution
│   │   │   ├── wisdom_repo.py        # Corporate Wisdom Documents & Vectors
│   │   │   ├── sentinel_repo.py      # CoV Pre-flight Inspection Records
│   │   │   └── session.py            # SQLite WAL Connection Pool (`busy_timeout = 5000`)
│   │   ├── engine/                   # Modular Cognitive & Execution Engines
│   │   │   ├── runtime/              # Model Router, Autonomous Kanban Runner, State Machine
│   │   │   ├── roles/                # Dynamic Polymorphic Role Node, Contract Handlers
│   │   │   ├── governance/           # Circuit Breaker, Financial Guardrail, Flight Recorder
│   │   │   ├── memory/               # Blackboard Memory, Context Compactor, Vector Store (FastEmbed)
│   │   │   ├── tools/                # FileLockManager, DynamicToolRegistry, Tool Synthesizer
│   │   │   ├── secretary/            # Telegram Daemon (5 Pillars: Reporter, Task Bridge, Installer)
│   │   │   ├── skills/               # SkillsHub & Git Multi-File Bundle Importer
│   │   │   ├── quality/              # AST Security Scanner, P2P Reviewer, Visual Evaluator
│   │   │   ├── office/               # Actor Event Bus & Oasis Lounge Engine
│   │   │   └── sentinel/             # Two-Tier CoV Pre-Flight Gatekeeper & Inspector
│   │   ├── gateway/                  # Unified Multi-Provider BYOK Client (Adapters)
│   │   └── sandbox/                  # Docker Sandbox Runner & Caddy Proxy Manager
│   ├── tests/                        # Unit & Integration Test Suites (216 Passed / 100%)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js 14 App Router Pages
│   │   │   ├── organization/         # Visual Org Studio & AI Board (3-Layer Prompting)
│   │   │   ├── kanban/[id]/          # Mission Control Kanban & Live Lounge
│   │   │   ├── preview/[id]/         # Live Sandbox Preview, PTY Terminal & Snapshots
│   │   │   ├── sparring/[id]/        # Executive Sparring Room (Dynamic Roles)
│   │   │   ├── office/               # Global Oasis Live Command HQ (Obsidian 2D)
│   │   │   ├── settings/             # Dynamic BYOK Key Vault & System Settings
│   │   │   ├── analytics/            # CFO Observability & Token Burn Cockpit
│   │   │   └── wisdom/               # Corporate Wisdom Base & GitHub Skill Importer
│   │   ├── components/               # Komponen Modular Antarmuka (SRP <= 150-200 baris)
│   │   │   ├── organization/         # RoleModal (3-Layer Prompting), RoleCard, BranchBar
│   │   │   ├── office/               # Oasis Feed, ScreenShare, WarRoom, EventCard
│   │   │   ├── analytics/            # TokenSummaryCards, ChannelHealthRadar, RoleCostTable
│   │   │   ├── settings/             # SettingsProviderTab (BYOK & Custom Providers)
│   │   │   └── sandbox/              # Web PTY Terminal & Iframe Preview Container
│   │   ├── hooks/                    # Custom React Hooks
│   │   └── lib/                      # API Client Interfaces & TypeScript Types
│   ├── package.json
│   └── tailwind.config.ts
├── workspaces/                       # Direktori Sandbox Proyek Aktif
├── sandbox_storage/                  # Snapshot Arsip CoW Proyek
├── knowledge_systerm.md              # Master Knowledge Base & Architectural Specification
├── CLAUDE.md                         # Developer & AI Assistant Operational Guide
├── code-quality-rules.md             # Code Quality & Modularity Standards (SRP Rule)
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
**Status Pengujian: 216 / 216 Pengujian Lolos (100% PASSED, Zero Failure)**.

Rangkaian uji terbagi dalam 6 gelombang verifikasi ketat:
* **Gelombang 1 (Fondasi & Desentralisasi Kognitif)**: Pembersihan dead code legacy, Polymorphic Contract Handler (`contract_handlers.py`), Sovereign Router live token pricing ledger, dan FastEmbed ONNX 384-dim neural RAG.
* **Gelombang 2 (Keselamatan & Efisiensi Memori)**: Two-Tier CoV Pre-Flight Gatekeeper (Tier 1 0ms/0-token passing vs Tier 2 mutating critic), Autonomous Role-Worker Self-Repair Loop, dan Hermes Layered Context Compactor.
* **Gelombang 3 (Otonomi Korporat & Ekstensi Remote)**: Autonomous Kanban Runner dengan SQLite Atomic Claim Query, FileLockManager anti-race condition mutex, DynamicToolRegistry SQLite persistence (`corporate_custom_tools`), dan Telegram Secretary Daemon dengan dynamic tool synthesis.
* **Gelombang 4 (Integrasi Ekosistem & Gerbang Mutu LSP)**: MCP Server Dynamic Bridge & Dependency Guardrail (`test_mcp_manager.py`), Public Skills Hub & Auto-Taxonomy FTS5 (`test_skills_hub.py`), In-Sandbox LSP Diagnostics & Gatekeeper (`test_lsp_service.py`), serta Telegram Secretary Dry-Run & Secret Interceptor (`test_telegram_installer.py`).
* **Gelombang 5 (Layered Cognition & Anti-Drift Architecture)**: Pengujian `persona_prompt` pada skema database `corporate_roles`, migrasi otomatis & seeding 8 peran bawaan (termasuk Sekretaris Eksekutif), validasi kontrak API Pydantic, perakitan 3-layer system prompt (`dynamic_node.py`), eliminasi dead code denah furnitur statis, serta pencegahan persona drift saat fallback model router aktif (`test_persona_prompt_and_3layer.py`).
* **Gelombang 6 (Git Multi-File Skill Importer, Secretary 5-Pillars & Unified Role Permissions)**: Pengujian kloning dangkal git & ekstraksi hierarki multi-file repositori kompleks seperti `ui-ux-pro-max-skill` (`test_skills_git_importer.py`), alur kerja terpadu 5 pilar Telegram Secretary dari `/task` dispatch hingga event bus reporting (`test_secretary_full_workflow.py`), serta agregasi perizinan perkakas terpadu di `/api/v1/mcp/all-tools` (`test_unified_all_tools_permissions.py`).

---

## 📄 Lisensi

Platform ini dirilis di bawah lisensi resmi **MIT License**. Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini untuk keperluan riset maupun komersial. Silakan merujuk ke berkas `LICENSE` untuk ketentuan hukum lengkap.

---
*Ditenagai oleh Sovereign Autonomous AI Corporate OS • Dirancang untuk Pengusaha Tunggal & Inovator Global.*
