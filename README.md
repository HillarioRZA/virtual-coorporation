# 🪐 Virtual Tech Startup Multi-Agent System & Universal Corporate Operating System
### Autonomous AI Virtual Enterprise Platform, Dynamic Asynchronous Workflow Engine & 3D Spatial OS

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL%2060FPS-black?style=flat-square&logo=three.js&logoColor=white)](https://threejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLite WAL](https://img.shields.io/badge/Database-SQLite%20WAL-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 💡 Executive Overview

**Virtual Tech Startup Multi-Agent System** adalah sistem operasi korporat kecerdasan buatan mandiri (*Autonomous AI Virtual Enterprise OS*) dan platform inkubasi startup universal. Platform ini dirancang untuk memberdayakan seorang **Founder tunggal (Solo Entrepreneur / Chairman / CEO)** dalam menjalankan seluruh siklus hidup perusahaan teknologi: mulai dari formulasi ide mentah, riset pasar, penyusunan spesifikasi teknis, arsitektur sistem, rekayasa perangkat lunak paralel (Frontend & Backend), penjaminan mutu, audit keamanan OWASP, hingga peluncuran aplikasi live di sandbox produksi.

### ⚡ Pergeseran Paradigma: Fondasi Dasar vs Mesin Dinamis Modern
Dalam arsitektur awal (v1), sistem menggunakan 12 peran tetap dan alur *deterministic state machine* bertahap linier (waterfall). Pada arsitektur mutakhir (v2.4+), konsep 12 peran dan state machine awal tersebut **hanyalah sebuah baseline (Gold Standard Template)**. 

Platform modern kini telah berevolusi menjadi **Dynamic Asynchronous Corporate Operating System** yang sepenuhnya dapat dikustomisasi:
1. **Dynamic Asynchronous Kanban & Ticket-Driven State Machine**: Agen AI tidak lagi terkunci dalam alur sekuensial yang kaku. Agen bekerja secara otonom dan asinkron, mendengarkan antrean event (*Event Bus*), mengambil tiket dari papan virtual Kanban, saling berkomunikasi lintas peran, dan secara mandiri menyesuaikan alur kerja mereka berdasarkan status tiket, dependensi tugas, dan tingkat prioritas.
2. **Visual Organization & Division Studio (`/organization`)**: Founder dapat merancang struktur organisasi secara visual—menambah, memodifikasi, atau menghapus divisi kustom (misal: Divisi Software, Edukasi, Copywriting, Riset Pasar) dan mendaftarkan karyawan AI baru lengkap dengan kustomisasi persona, system prompt, batasan token, slider kreativitas (temperature), dan izin perkakas (*tool permissions*).
3. **Visual HTML5 Drag-and-Drop Looping Pipeline Builder**: Menyusun alur kerja produksi secara visual dengan dukungan alur berulang (*looping* seperti $A \rightarrow B \rightarrow C \rightarrow A$), pipeline multi-lini produk (Software/SaaS, Kursus Edukasi, Pemasaran Konten, Kustom), serta penempatan kartu **Gerbang Keputusan CEO** (*Approval Gate*, *Strategic Meeting*, *Direction Input*) secara langsung di kanvas.
4. **Desentralisasi BYOK (Bring-Your-Own-Key)**: Konfigurasi model LLM (OpenRouter, DeepSeek, Anthropic Claude, OpenAI, Google Gemini, Groq, dan Ollama Lokal) dilakukan langsung pada masing-masing peran karyawan AI dengan pil preset model gratis (`• FREE`), dipadukan dengan Secret Vault terenkripsi AES-256-GCM.
5. **Git-Style Organizational Branching & Forking**: Alur utama (`branch_main`) dilindungi dari modifikasi destruktif. Founder dapat melakukan forking ke branch eksperimen, menguji struktur organisasi atau alur pipeline baru, lalu melakukan merge kembali ke branch utama secara atomik dengan visualisasi *diff*.
6. **Executive Governance Hub & Anti-Infinite Loop Circuit Breaker**: Komunikasi antar-agen dibungkus dalam kontrak JSON terstruktur (`AgentDecisionEnvelope`). Jika terjadi perdebatan teknis melingkar $\ge 3$ putaran tanpa kemajuan kode, sistem secara otomatis membekukan tiket (`BLOCKED_LOOP_DETECTED`) dan memberikan kontrol penuh ke meja Founder untuk intervensi 1-klik (*Force Proceed*, *Intervene*, atau *Reassign*).
7. **3D Cyber-Voxel Apple Park Mega-Campus (`/office`)**: Simulator spasial digital twin berskala $272\text{ meter}$ berbasis Three.js/React Three Fiber yang mencerminkan seluruh aktivitas korporat, posisi divisi, pergerakan agen voxel, fisika tabrakan, dan telemetri kinerja secara real-time.

---

## 🏛️ Arsitektur Sistem Terpadu

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FOUNDER EXECUTIVE DASHBOARD                                        │
│                                  Next.js 14 App Router • TypeScript                                    │
│                                                                                                        │
│  /                 /organization         /kanban/[id]         /preview/[id]         /office            │
│  Portfolio Hub     Org Studio & DND      Mission Control      Live Sandbox, PTY     3D Apple Park      │
│  & Venture State   Pipeline Builder      & Live Lounge WS     Terminal & Snapshots  Spatial Campus     │
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
│  • Agent Circuit Breaker: Auto-Freeze Ticket on >= 3 Consecutive Debate Turns                          │
│  • 1-Click CEO Strategic Intervention & Veto (Force Proceed / Chat Directive / Reassign Role)          │
│  • Git-Style Branching & Forking: Isolated Corporate Workflows with 3-Way Structural Merge             │
└───────────────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      CORE EXECUTION & RUNTIME ENGINES                                  │
│                                                                                                        │
│  • Decentralized BYOK LLM Gateway (OpenRouter, DeepSeek, Claude, OpenAI, Gemini, Groq, Ollama)         │
│  • Ephemeral Dual-Engine Sandbox (Docker Container Isolation + Embedded Async HTTP Local Preview)      │
│  • Interactive Web PTY Terminal with Command Blacklist Guardrail & CoW Snapshots (Zero Data Loss)      │
│  • Python AST Real Static Security Scanner (OWASP Top 10 Vulnerability Detection)                      │
│  • Procedural 3D Spatial Simulator: Collision Mesh, Voxel Physics & Spatial Audio                      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Pilar Fitur Utama (v2.4+)

### 1. Dynamic Asynchronous Kanban & Ticket-Driven State Machine
Sistem tidak lagi dibatasi oleh model eksekusi waterfall yang kaku. Alur kerja korporat digerakkan secara penuh oleh **Sistem Tiket Kanban Asinkron**:
- **Otonomi Berbasis Tiket**: Setiap tahapan dalam venture dipecah menjadi tiket tugas (`corporate_tickets`) dengan metadata: `branch_id`, `project_id`, `division_id`, `assigned_role_id`, `product_line`, `priority`, dan `dependencies`.
- **Siklus Hidup 5 Kolom Adaptif**: `BACKLOG ➔ TODO ➔ IN_PROGRESS ➔ REVIEW ➔ DONE`. Tiket berpindah status secara dinamis melalui event-driven trigger.
- **Task Concurrency Dispatcher (`dispatcher.py`)**: Tugas-tugas independen (seperti sintesis prototipe antarmuka Next.js oleh Frontend Engineer dan pembangunan endpoint API oleh Backend Engineer) dieksekusi secara simultan menggunakan `asyncio.gather()`. Mekanisme ini memangkas durasi produksi hingga 40–50% tanpa menyebabkan race condition pada sistem berkas.
- **Corporate Event Bus (`event_bus.py`)**: Arsitektur asinkron berbasis `asyncio.Queue` yang memancarkan setiap event tugas (`TASK_CREATED`, `TASK_STARTED`, `TASK_STATUS_CHANGED`, `CIRCUIT_BREAKER_TRIGGERED`) ke seluruh subscriber aktif dan menyimpannya secara atomik ke tabel SQLite WAL.

### 2. Visual Organization & Division Studio (`/organization`)
Founder memiliki kebebasan mutlak dalam menyusun struktur perusahaan virtual secara visual:
- **Visual Corporate Hierarchy**: Menampilkan bagan organisasi yang terorganisasi rapi ke dalam Executive Suite, Core Engineering, dan Divisi Kustom.
- **Divisi Dinamis**: Tambah divisi baru (misal: Divisi Copywriting, Pemasaran Konten, Edukasi, Riset Hukum), atur aksen warna antarmuka HEX, pilih ikon Lucide React, dan tentukan mandat operasionalnya.
- **Karyawan AI Dinamis**: Daftarkan peran karyawan AI tanpa batas:
  - Personalisasi instruksi sistem (*System Prompt Persona*).
  - Penugasan model LLM independen per peran.
  - Pengaturan *temperature slider* (0.0 untuk deterministik presisi s/d 1.5 untuk kreativitas tinggi).
  - Alokasi anggaran token per tugas (*Token Budget* dari 1.000 s/d 100.000 token).
  - Izin perkakas modular (*Tool Permissions*): `read_file`, `write_file`, `terminal_exec`, dan `web_search`.

### 3. Visual HTML5 Drag-and-Drop Looping Pipeline Builder
Alur kerja antar-karyawan AI dapat dirangkai semudah menyusun balok puzzle visual:
- **Multi-Product-Line Pipelines**: Mendukung rantai alur kerja berbeda untuk berbagai lini produk:
  * 💻 **Software & SaaS (Tech Core)**: Alur rekayasa perangkat lunak kanonikal.
  * 📚 **Edukasi & Kursus Online**: Kurikulum, modul belajar, kuis interaktif, dan materi silabus.
  * ✍️ **Copywriting & Kampanye Pemasaran**: Riset audiens, formulasi hook, landing page copy, dan kampanye email.
  * 🧪 **Kustom & Riset Pasar**: Alur eksperimental modular sesuai kebutuhan Founder.
- **Looping & Cyclic Workflow**: Mendukung perulangan peran dalam satu alur (contoh: `Role A ➔ Role B ➔ Role C ➔ Role A ➔ Role C`).
- **Drag-and-Drop Fluid**: Tarik kartu peran langsung dari daftar divisi dan lepaskan (*drop*) ke posisi mana pun di atas kanvas pipeline horizontal, atau gunakan tombol cepat 1-klik `+ Pipeline`.
- **First-Class CEO Decision Gates**: Gerbang keputusan manusia (*Human-in-the-Loop*) diperlakukan sebagai node resmi yang dapat di-drag langsung ke kanvas:
  * 👑 **Stage-Gate Approval**: Evaluasi gerbang kelayakan formal sebelum produksi berlanjut.
  * 🤝 **Executive Strategic Meeting**: Rapat sinkronisasi strategi C-Level bersama Founder.
  * 🧭 **Founder Direction Input**: Penyisipan instruksi arah visi Founder di tengah rantai eksekusi.

### 4. Executive Governance, Decision Space & Anti-Infinite Loop Circuit Breaker
Platform memberikan otonomi kepada agen AI sembari menjamin keamanan dari pemborosan saldo API dan diskusi tanpa akhir:
- **Agent Decision Envelope**: Setiap agen mengembalikan amplop keputusan terstruktur berbasis JSON:
  ```json
  {
    "step_id": "backend_auth_implementation",
    "status": "NEED_CLARIFICATION",
    "decision": {
      "action": "CONSULT_ROLE",
      "target_role": "pm",
      "cc_roles": ["cto"],
      "urgency": "BLOCKING"
    },
    "dialogue": {
      "summary": "Ambigu skema autentikasi token pada OpenAPI Spec",
      "question_to_target": "Apakah token refresh menggunakan HttpOnly Cookie atau Authorization Header?",
      "suggested_solution": "Saya sarankan menggunakan HttpOnly Cookie demi keamanan OWASP."
    },
    "work_in_progress": {
      "completed_files": ["app/core/security.py"],
      "blocked_files": ["app/api/v1/auth.py"]
    }
  }
  ```
- **Anti-Infinite Loop Circuit Breaker (`circuit_breaker.py`)**: Pengawas otonom yang menghitung putaran diskusi antar-agen pada tiket yang sama. Jika diskusi mencapai **3 putaran berturut-turut** tanpa menghasilkan artefak kode baru, tiket secara otomatis dibekukan dengan status `BLOCKED_LOOP_DETECTED` dan event darurat dikirimkan ke lounge.
- **1-Click CEO Intervention & Veto**: Founder dapat membuka modal intervensi untuk:
  - `FORCE_PROCEED`: Melewati perdebatan dan memaksa tugas selesai (`DONE`).
  - `INTERVENE`: Memberikan instruksi tertulis yang mengikat agen, mengembalikan tiket ke status `IN_PROGRESS`.
  - `REASSIGN`: Mengalihkan kepemilikan tiket ke peran karyawan AI lain.
- **C-Level Direct Escalation**: CTO atau CoS dapat menyusun laporan eskalasi eksekutif berisi ringkasan kendala dan opsi solusi konkret (Opsi A vs Opsi B) untuk disetujui Founder dalam 1-klik.

### 5. Git-Style Organizational Branching & Forking
Mengadopsi konsep version control modern ke dalam struktur korporasi:
- **Branch Protection**: Alur utama (`branch_main`) berstatus dilindungi (*Gold Standard*). Modifikasi destruktif dicegah untuk menjaga stabilitas alur produksi inti.
- **1-Click Forking Workflow**: Pengguna dapat menduplikasi struktur organisasi dan alur kerja ke dalam branch eksperimen (misal: `agile-sprint`, `lean-mvp`) lengkap dengan pemetaan peran, divisi, tiket, dan pipeline yang terisolasi.
- **Atomic Branch Merging (`branch_merge.py`)**: Alur eksperimen yang terbukti berhasil dapat digabungkan kembali ke `branch_main` dengan kalkulasi *diff* struktural otomatis dan penanganan konflik.

### 6. Desentralisasi BYOK (Bring-Your-Own-Key) & Dynamic Model Architecture
Menghilangkan ketergantungan pada vendor LLM tunggal:
- **Konfigurasi Model Per Karyawan AI**: Setiap peran dapat menggunakan provider LLM yang berbeda sesuai kebutuhan tugasnya (misal: CTO menggunakan model penalaran tingkat tinggi seperti `deepseek-r1` atau `claude-3.5-sonnet`, sedangkan QA menggunakan model berkecepatan tinggi seperti `groq/llama-3.3-70b`).
- **Penyedia LLM yang Didukung**:
  * 🌐 **OpenRouter**: Akses ke ratusan model open-source dan komersial.
  * 🧠 **DeepSeek**: Model penalaran mendalam dan coding berbiaya hemat.
  * ⚡ **Google Gemini**: Dukungan context window masif (Gemini 2.0 Flash / Pro).
  * 🏎️ **Groq**: Inferensi ultra-cepat dengan latensi sub-detik (LPU chips).
  * 🤖 **OpenAI & Anthropic**: GPT-4o, Claude 3.5 Sonnet / Opus.
  * 🏠 **Ollama Lokal**: 100% offline dan privat tanpa koneksi internet.
- **Pil Preset Rekomendasi Bebas Biaya**: Dilengkapi tag visual `• FREE` berwarna hijau emerald pada antarmuka untuk memudahkan eksperimen tanpa saldo API.
- **Secret Vault Terenkripsi AES-256-GCM**: Kunci kredensial produksi dan API key disimpan secara terenkripsi dalam SQLite WAL. Founder dapat mengubah kunci atau mereset konfigurasi secara real-time tanpa perlu me-restart server backend.

### 7. 3D Cyber-Voxel Apple Park Mega-Campus Simulator (`/office`)
Antarmuka spasial interaktif Three.js/React Three Fiber beresolusi tinggi:
- **Denah Arsitektur Skala Besar (Radius $136\text{ meter}$, Diameter $272\text{ meter}$)**:
  * 🏢 **Procedural Main Ring Building**: Cincin kaca 4 lantai melingkar dengan perimeter dinding kaca transparan dan koridor divisi.
  * 🎭 **Steve Jobs Theater**: Paviliun silinder kaca dengan atap serat karbon melayang untuk sesi *Executive Sparring* dan presentasi *Demo Day*.
  * ⚡ **Server & Datacenter Building**: Gedung server monolitik tempat eksekusi sandbox dan pemindaian keamanan kode.
  * 🌿 **Inner Zen Park & Pond**: Kolam refleksi air dinamis, pepohonan voxel, dan jalur setapak hijau.
- **Karakter Agen Berbasis Voxel**: Karakter karyawan AI berpenampilan voxel modern dengan status glow dinamis:
  * 🟢 Hijau: Agen sedang aktif berpikir / menulis kode.
  * 🔵 Biru: Agen sedang dalam mode diskusi inter-agen.
  * 🟡 Emas: Menunggu keputusan Founder di Gerbang CEO.
  * 🔴 Merah: Tiket terblokir oleh Circuit Breaker.
- **Mesin Fisika & Navigasi**: First-Person Walkthrough dengan kontrol keyboard WASD dan pointer-lock mouse, dilengkapi sistem deteksi tabrakan AABB terhadap dinding dan perabotan.

### 8. Ephemeral Dual-Engine Sandbox, PTY Terminal & AST Security
Lingkungan eksekusi mandiri yang aman dan terisolasi:
- **Dual-Engine Runner (`runner.py`)**:
  * **Docker Engine Container**: Eksekusi terisolasi dengan batas resource CPU/RAM dan reverse proxy Caddy (`*.local.sandbox`).
  * **Embedded Async HTTP Fallback Server**: Berjalan pada port 4000–4999 untuk memastikan iframe live preview tetap menyala meskipun Docker daemon host sedang offline.
- **Interactive Web PTY Terminal**: Terminal CLI live dua arah berbasis WebSocket di antarmuka `/preview/[id]` dengan guardrail penyaring perintah destruktif OS (`rm -rf /`, `mkfs`, dll).
- **Copy-on-Write (CoW) Snapshots**: Pencatatan versi direktori kode otomatis dengan jaminan *Zero Data Loss*. Sistem secara otomatis membuat snapshot berlabel `AUTO_PRE_ROLLBACK` sebelum rollback kode dijalankan.
- **Real AST OWASP Top-10 Security Scanner (`security_scanner.py`)**: Pemindai kode statis berbasis Python Abstract Syntax Tree (AST) yang memeriksa kerentanan nyata: injeksi kode (`eval`, `exec`), hardcoded secret keys, SQL injection, CORS liar, dan kerentanan XSS React.

---

## 📡 Spesifikasi Lengkap 21 Router API Backend

Seluruh endpoint REST API dan WebSocket diorganisasikan secara modular di bawah prefix `/api/v1` dengan penegakan tipe data ketat via Pydantic v2:

| No | Modul Router | Prefix Endpoint | Tipe | Deskripsi & Fungsi Utama |
|:--:|:-------------|:----------------|:----:|:-------------------------|
| 1 | `corporate.py` | `/corporate` | REST | CRUD struktur organisasi korporat: manajemen branch, divisi, dan peran karyawan AI. |
| 2 | `corporate_workflow.py` | `/corporate/branches/{id}` | REST | Mengelola pipeline lini produk multi-cabang, urutan tahapan (DND), dan alur looping. |
| 3 | `corporate_tickets.py` | `/corporate/tickets` | REST | Manipulasi kartu tugas Kanban virtual (5 status), dependensi, dan prioritas tugas. |
| 4 | `corporate_events.py` | `/corporate/events` | REST | Membaca log pesan percakapan, diskusi inter-agen, dan event bus korporat. |
| 5 | `corporate_ws.py` | `/ws/corporate` | WS | WebSocket streaming dua arah untuk sinkronisasi tiket Kanban dan notifikasi real-time. |
| 6 | `governance.py` | `/governance` | REST | Pengawas interaksi agen: status circuit breaker, eskalasi C-Level, dan intervensi veto CEO. |
| 7 | `branch_merge.py` | `/corporate/branches` | REST | Analisis *diff* struktural antar-branch dan penggabungan atomik branch eksperimen ke main. |
| 8 | `projects.py` | `/projects` | REST | Siklus hidup venture: inisialisasi ide baru, muat checkpoint state, dan daftar portofolio. |
| 9 | `sparring.py` | `/projects/{id}/sparring` | REST / SSE | Sesi debat sokratik pra-PRD antara Founder, Chief of Staff (CoS), dan CTO. |
| 10 | `gates.py` | `/projects/{id}/gates` | REST | Stage-Gate keputusan Founder: persetujuan formal, revisi arahan, atau terminasi proyek. |
| 11 | `pull_requests.py` | `/projects/{id}/prs` | REST | Siklus hidup PR otomatis: automated peer-to-peer code review dan 3-way merge conflict resolution. |
| 12 | `vault.py` | `/projects/{id}/vault` | REST | Penyimpanan kredensial rahasia produksi terenkripsi AES-256-GCM (Secret Vault). |
| 13 | `analytics.py` | `/analytics` | REST | Metrik penggunaan token per agen, evaluasi unit economics, dan neraca keuangan korporat. |
| 14 | `settings.py` | `/settings` | REST | Pengaturan dinamis sistem (BYOK API keys, parameter PaaS, reset konfigurasi) tanpa restart. |
| 15 | `auth.py` | `/auth` | REST | Verifikasi PIN dinamis 6-digit gerbang keamanan Telegram dan penerbitan session token HMAC. |
| 16 | `wisdom.py` | `/wisdom` | REST | Corporate Wisdom Knowledge Base: penarikan best-practice dan aturan arsitektur lintas proyek. |
| 17 | `office.py` | `/office` | REST | Mengambil denah tata letak gedung spasial, zonasi divisi, dan telemetri kantor 3D. |
| 18 | `office_ws.py` | `/ws/office` | WS | WebSocket siaran posisi koordinat $(X, Y, Z)$ dan status animasi pergerakan agen 3D real-time. |
| 19 | `sandbox_snapshots.py` | `/projects/{id}/sandbox` | REST | Manajemen snapshot direktori proyek (CoW) dan pemulihan rollback instan anti-data-loss. |
| 20 | `sandbox_network.py` | `/projects/{id}/network` | REST | Pemeriksaan status isolasi kontainer Docker dan pemetaan routing proxy Caddy. |
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
│   │   │   ├── branch_merge.py       # Git-Style Branch Diff & Atomic Merge
│   │   │   ├── corporate.py          # Corporate Organization Hierarchy CRUD
│   │   │   ├── corporate_events.py   # Corporate Event Log & Message Queries
│   │   │   ├── corporate_tickets.py  # Kanban Virtual Tickets & Task Transitions
│   │   │   ├── corporate_workflow.py # Dynamic Workflow Pipeline & Stage Sequence
│   │   │   ├── corporate_ws.py       # Kanban Real-Time WebSocket Channel
│   │   │   ├── gates.py              # Founder Stage-Gate Decisions
│   │   │   ├── governance.py         # Executive Governance, Escalation & CEO Veto
│   │   │   ├── office.py             # 3D Spatial Layout & Telemetry Data
│   │   │   ├── office_ws.py          # 3D Agent Movement & Coordinates WebSocket
│   │   │   ├── projects.py           # Venture State & Checkpoint Persistence
│   │   │   ├── pull_requests.py      # Automated PR Engine & Peer Review
│   │   │   ├── sandbox_network.py    # Docker Network & Reverse Proxy Routing
│   │   │   ├── sandbox_snapshots.py  # Zero-Data-Loss CoW Snapshots & Rollbacks
│   │   │   ├── sandbox_terminal_ws.py# Interactive Web PTY Terminal Stream
│   │   │   ├── settings.py           # Dynamic BYOK & Runtime Settings Manager
│   │   │   ├── sparring.py           # Executive Sparring Room (CoS + CTO)
│   │   │   ├── vault.py              # AES-256-GCM Encrypted Secret Vault
│   │   │   └── wisdom.py             # Corporate Wisdom & Organizational Learning
│   │   ├── core/                     # Config, Logger, Security Gate, Settings Manager
│   │   ├── db/                       # Modul Repositori Basis Data SQLite Asinkron (aiosqlite)
│   │   │   ├── branch_repo.py        # Isolasi Branching & Forking Database
│   │   │   ├── corporate_repo.py     # Unified Corporate Facade Database
│   │   │   ├── division_repo.py      # Operasi Divisi Organisasi
│   │   │   ├── role_repo.py          # Operasi Peran Karyawan AI
│   │   │   ├── pipeline_repo.py      # Multi-Product Pipelines
│   │   │   ├── ticket_repo.py        # Virtual Kanban Tickets Storage
│   │   │   ├── workflow_repo.py      # Pipeline Stages & Ordering Storage
│   │   │   └── session.py            # SQLite WAL Connection Pool
│   │   ├── engine/                   # Core Cognitive Engines
│   │   │   ├── circuit_breaker.py    # Anti-Infinite Loop Guardrail
│   │   │   ├── dispatcher.py         # Task Concurrency Dispatcher (asyncio.gather)
│   │   │   ├── event_bus.py          # Asynchronous Actor Event Bus
│   │   │   ├── security_scanner.py   # Real Python AST OWASP Scanner
│   │   │   ├── state_machine.py      # Native Finite State Machine
│   │   │   └── office_simulator.py   # Procedural Spatial & Physics Simulator
│   │   ├── gateway/                  # Unified Multi-Provider LLM Client
│   │   └── sandbox/                  # Docker Sandbox Runner & Caddy Proxy Manager
│   ├── tests/                        # 107+ Pengujian Komprehensif (100% Passed)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                      # Next.js 14 App Router Pages
│   │   │   ├── organization/         # Visual Org Studio & Pipeline Builder
│   │   │   ├── kanban/[id]/          # Mission Control Kanban & Live Lounge
│   │   │   ├── preview/[id]/         # Live Sandbox Preview, PTY Terminal & Snapshots
│   │   │   ├── sparring/[id]/        # Executive Sparring Debate Room
│   │   │   ├── office/               # 3D Cyber-Voxel Apple Park Mega-Campus
│   │   │   ├── settings/             # Dynamic BYOK Key Vault & System Settings
│   │   │   └── analytics/            # Financial Unit Economics & Token Ledger
│   │   ├── components/               # Komponen Modular Antarmuka
│   │   │   ├── organization/         # WorkflowPipelineBuilder, RoleModal, BranchBar, dll.
│   │   │   ├── office/               # Three.js Apple Park Procedural Canvas & Controls
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
3. **Docker** *(Opsional tetapi sangat disarankan)*: Untuk isolasi kontainer sandbox penuh. Jika Docker tidak terpasang, sistem secara otomatis mengaktifkan *Embedded Async HTTP Server* lokal pada port 4000–4999.

### Langkah 1: Kloning Repositori
```bash
git clone https://github.com/HillarioRZA/virtual-coorporation.git
cd virtual-coorporation
```

### Langkah 2: Konfigurasi Kunci Lingkungan (`.env`)
Salin berkas contoh konfigurasi lingkungan:
```bash
cp .env.example .env
```
Buka `.env` dan masukkan API Key LLM yang Anda miliki (minimal satu provider, misal OpenRouter atau DeepSeek):
```ini
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
# Atau gunakan provider gratis:
# GEMINI_API_KEY="AIzaSy..."
# DEEPSEEK_API_KEY="sk-..."
```
*(Catatan: Anda juga dapat memasukkan kunci secara langsung melalui antarmuka web di menu `/settings` setelah aplikasi berjalan).*

### Langkah 3: Menjalankan Sistem Secara Otomatis (Universal Launcher)
Jalankan skrip peluncur universal terpadu:
```bash
python run.py
```
Skrip ini akan secara otomatis:
1. Memeriksa integritas dependensi Python dan Node.js.
2. Menginisialisasi basis data SQLite WAL (`backend/data/startup_system.db`) dan mengeksekusi migrasi seeding otomatis.
3. Menjalankan server backend FastAPI pada `http://localhost:8000`.
4. Menjalankan server frontend Next.js 14 pada `http://localhost:3000`.

Buka peramban (*browser*) Anda dan akses:
👉 **`http://localhost:3000`**

---

## 🧪 Pengujian Otomatis & Standar Kualitas

Sistem dibangun dengan mematuhi standar rekayasa perangkat lunak yang ketat:
- **Prinsip Single Responsibility (SRP)**: Setiap berkas backend dibatasi maksimal **150–200 baris kode** dengan pemisahan repositori terisolasi.
- **Type Annotations**: 100% fungsi dan metode memiliki anotasi tipe Python dan TypeScript lengkap.
- **Zero Raw Prints**: Seluruh operasi dicatat menggunakan *structured logging* (`app.core.logger`).
- **Resiliensi I/O**: Seluruh operasi basis data, jaringan HTTP, dan pertukaran JSON dibungkus dalam penanganan pengecualian (*exception handling*) spesifik.

Untuk menjalankan seluruh rangkaian pengujian backend:
```bash
pytest backend/tests -v
```
**Status Pengujian: 107 / 107 Pengujian Lolos (100% PASSED)**.

---

## 📄 Lisensi

Platform ini dirilis di bawah lisensi resmi **MIT License**. Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini untuk keperluan riset maupun komersial. Silakan merujuk ke berkas `LICENSE` untuk ketentuan hukum lengkap.

---
*Ditenagai oleh Inovasi Multi-Agent Corporation OS • Dirancang untuk Pengusaha Tunggal & Inovator Global.*
