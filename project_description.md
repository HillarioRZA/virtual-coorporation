# DOKUMENTASI SISTEM & DESKRIPSI PROYEK
## Virtual Tech Startup Multi-Agent System & Universal Venture Incubator Hub
**Sistem Inkubasi Startup Otonom Berbasis Multi-Agent AI & Pabrik Perangkat Lunak Mandiri**

---

## 1. Project Ini Tentang Apa?

**Virtual Tech Startup Multi-Agent System & Universal Venture Incubator Hub** adalah platform inkubasi bisnis dan pabrik rekayasa perangkat lunak otonom (*Autonomous Software Engineering & Venture Factory*). Platform ini dirancang untuk mendemokratisasikan penciptaan startup teknologi: seorang *solo entrepreneur* (Founder tunggal) atau *Chief Executive Officer* (CEO) dapat memasukkan ide kasar produk digital ke dalam sistem, dan sistem akan mengorkestrasi sebuah "perusahaan virtual lengkap" berisi **12 agen kecerdasan buatan (AI Agents)** dengan peran profesional terpisah.

Para agen AI ini tidak sekadar menghasilkan teks percakapan biasa (*chat prompting*), melainkan bertindak layaknya tim eksekutif dan *engineering guild* di Silicon Valley:
* Berdebat dan memvalidasi model bisnis (*Executive Sparring*).
* Menulis dokumen spesifikasi produk (*Lean PRD*).
* Merancang sistem token visual dan komponen antarmuka (*UI/UX Design Tokens*).
* Mengompilasi dan meluncurkan purwarupa web interaktif ke lingkungan *sandbox* terisolasi (*Full-Stack Demo Day Prototype*).
* Mengaudit keamanan kode terhadap kerentanan OWASP (*DevSecOps Scanning*).
* Mengotomatisasi siklus hidup *Git Pull Request*, *Peer-to-Peer Code Review*, dan *Three-Way Merge Conflict Resolution*.
* Menerbitkan kode produksi dan mengelolanya ke platform PaaS (*Platform-as-a-Service* seperti Docker/Coolify) lengkap dengan pencatatan keuangan (*Unit Economics & Financial Ledger*).

---

## 2. Cara Kerja Project Ini

Sistem bekerja berdasarkan metodologi industri **Stage-Gate Innovation Process** yang dipadukan dengan **Deterministic Finite State Machine (FSM)**. Setiap venture (proyek startup) yang lahir dipandu melalui tahapan linier berdisiplin tinggi, di mana transisi antar-tahap dikunci oleh persetujuan resmi Founder (*Founder/CEO Gatekeeping*).

```
[ Founder Input: Ide Bisnis Kasar ]
                 │
                 ▼
     ┌───────────────────────┐
     │  1. SPARRING_ROOM     │ ◄── Diskusi Sokratik (CoS + CTO)
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  GATE 1: CEO APPROVAL │ ◄── Putusan Founder: APPROVE / REVISE / KILL
     └───────────┬───────────┘
                 │ (APPROVE)
                 ▼
     ┌───────────────────────┐
     │ 2. MOCK_PROTOTYPING   │ ◄── PM Spec + UI Tokens + Vite/React Sandbox
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  GATE 2: DEMO DAY     │ ◄── Founder uji coba aplikasi live di Iframe
     └───────────┬───────────┘
                 │ (APPROVE)
                 ▼
     ┌───────────────────────┐
     │3. PRODUCTION_HARDENING│ ◄── FastAPI Backend + PR Review + OWASP Audit
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  GATE 3: VAULT DEPLOY │ ◄── Penguncian Kredensial AES-256 + PaaS Launch
     └───────────┬───────────┘
                 │ (APPROVE)
                 ▼
     ┌───────────────────────┐
     │ 4. LIVE_OPERATIONS    │ ◄── Monitoring Kuota, Token Ledger & Kantor 3D
     └───────────────────────┘
```

### Prinsip Operasional Kunci:
1. **Pemisahan Peran Spesifik (Separation of Concerns)**: Setiap agen memiliki *system prompt*, konteks memori, dan tugas terbatas. Agen Frontend tidak pernah menulis kode backend database; Agen DevSecOps bertindak sebagai auditor independen yang berhak menolak rilis (*blocking release*) jika ditemukan celah SQL Injection atau *Hardcoded Secret*.
2. **Deterministic Governance Tanpa Halusinasi**: Transisi siklus hidup startup tidak diserahkan pada "asumsi" LLM semata, melainkan diatur oleh `VentureStateMachine` berbasis Python di backend.
3. **Keamanan Tanpa Kompromi (Zero-Trust Guardrails)**:
   * Seluruh rahasia API produksi disimpan dalam **Secret Vault** terenkripsi **AES-256-GCM**.
   * Akses cockpit dashboard dilindungi oleh **Telegram OTP Security Gate** dengan rotasi password otomatis berkala.
   * Setiap kode yang dihasilkan dieksekusi di dalam kontainer Docker ephemeral dan dilindungi Caddy Reverse Proxy dengan domain isolasi (`*.local.sandbox`).

---

## 3. Workflow Project dan Aliran Data (Data Flow)

Aliran data (*data flow*) menghubungkan interaksi Founder di browser Next.js dengan eksekutor orkestrasi FastAPI di backend melalui arsitektur berbasis event:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FRONTEND: NEXT.JS 14                                   │
│  Portfolio Hub • Sparring Room • Kanban • Preview Sandbox • Settings • Office 3D HQ    │
└───────────────────────────┬────────────────────────────────▲───────────────────────────┘
                            │ (REST HTTP / FormData)         │ (SSE / WebSockets)
                            ▼                                │
┌────────────────────────────────────────────────────────────┴───────────────────────────┐
│                              BACKEND GATEWAY: FASTAPI                                  │
│  ASGI Middlewares: ProcessTimeLogging • SecurityGate (Telegram OTP Session) • CORS     │
└─────────────┬────────────────────────────────────────────────────────────▲─────────────┘
              │                                                            │
              ▼                                                            │
┌───────────────────────────┐  Pub/Sub Mutasi Event  ┌─────────────────────┴────────────┐
│   VENTURE STATE MACHINE   ├───────────────────────►│        CORPORATE EVENT BUS        │
│ 7 Stages • 3 Stage-Gates  │                        │ In-Memory Asyncio Queue Broadcast │
└─────────────┬─────────────┘                        └───────────────────────────────────┘
              │
              ├──► 12 AI Agents (LangGraph / Ollama / Gemini / OpenAI Engine)
              ├──► PR Engine & P2P Reviewer (Git Branch Simulation & 3-Way Merge)
              ├──► OWASP Security Scanner (Static AST Regex & Secret Hunting)
              ├──► Sandbox Manager (Docker Daemon Client + Caddy Admin API)
              ├──► AES-256 Secret Vault (PBKDF2 HMAC-SHA256 Encryption)
              ├──► SQLite Database (WAL Mode • ACID State Ledger)
              └──► Office Simulator Engine (60 FPS Spatial Coordinates Math)
```

### Siklus Data Tahap demi Tahap:
1. **Inisiasi Ide**: Founder memasukkan ide di dashboard Next.js (`POST /api/v1/projects`). Data masuk ke database SQLite (WAL Mode), dan state proyek diatur ke `SPARRING_ROOM`.
2. **Debat Eksekutif**: Founder mengirim pesan di Sparring Room. `Chief of Staff (CoS)` membedah *market viability* dan *unit economics*, sementara `CTO` menganalisis kelayakan arsitektur teknologi.
3. **Penerbitan Artefak Gate 1**: CoS menghasilkan *Business Brief*, diagram arsitektur, dan ringkasan PRD. Founder meninjau dan menekan tombol `APPROVE`.
4. **Prototyping Ephemeral Sandbox**: Agen PM menulis *Lean PRD*, Agen UI merilis token warna, dan Agen Frontend membuat aplikasi prototipe. Docker Engine mem-build image prototipe dan mendaftarkan subdomain dinamis ke Caddy reverse proxy.
5. **Stage-Gate 2 Validation (Demo Day)**: Founder membuka halaman `/preview/[id]`. Iframe merender aplikasi prototipe langsung. Founder dapat mengetik perintah di Terminal Webview atau mengambil *Snapshot* restore point.
6. **Industrialisasi Kode & P2P Review**: Agen Frontend dan Backend bekerja pada branch terpisah (`feature/frontend`, `feature/backend`). PR Engine mensimulasikan P2P code review: Backend mereview PR Frontend, DevSecOps memindai 10 kategori OWASP. Jika bersih, branch di-merge otomatis via `branch_merge.py`.
7. **PaaS Launch**: Kredensial dimasukkan ke Secret Vault. Sistem mengirim perintah webhook deployment ke Coolify/Docker PaaS.

---

## 4. Arsitektur Project

Proyek ini dibangun menggunakan **Arsitektur Modular Heksagonal (Clean Decoupled Architecture)** dengan batasan ketat SRP (*Single Responsibility Principle*, $\le 150-200$ baris per file modul):

### 4.1. Arsitektur Backend (Python / FastAPI)
* **Directory Root**: `backend/`
  * `app/api/v1/`: Berisi 21 router modular yang memisahkan endpoint berdasarkan domain fungsional (Projects, Sparring, Gates, Vault, Settings, Auth, Corporate, Tickets, Workflow, WebSocket, Sandbox, Governance, Analytics, Pull Requests, Wisdom, Branch Merge, Office).
  * `app/core/`: Pusat konfigurasi (`config.py`), sistem logging terstruktur (`logger.py`), engine enkripsi Vault (`crypto_vault.py`), gembok akses Telegram (`auth_manager.py`), dan mutasi konfigurasi dinamis BYOK (`settings_manager.py`).
  * `app/db/`: Pengelolaan database SQLite asinkron (`init_db.py`, `database.py`) dengan skema tabel venture, log aktivitas, tiket kanban, dan audit trail.
  * `app/engine/`: Inti kecerdasan buatan dan orkestrasi otonom:
    * `state_machine.py`: Penegak aturan transisi 7 tahapan siklus venture.
    * `security_scanner.py` & `security_finding.py`: Auditor statis OWASP Top-10.
    * `pr_engine.py`: Mesin simulasi Pull Request dan P2P review antar-agen.
    * `branch_merger.py`: Algoritma *three-way git merge* dan resolusi konflik otomatis.
    * `event_bus.py`: Bus pesan *in-memory* non-blocking berbasis `asyncio.Queue`.
    * `corporate_wisdom.py`: Basis pengetahuan jangka panjang (*Organizational Memory*).
    * `office_simulator.py`: Simulator gerak dan koordinat spasial kampus virtual.
    * `sandbox_manager.py`: Pengendali kontainer Docker dan integrasi Caddy reverse proxy.

### 4.2. Arsitektur Frontend (Next.js 14 App Router)
* **Directory Root**: `frontend/`
  * **Framework**: Next.js 14.2 (React 18, TypeScript, Tailwind CSS, Lucide Icons).
  * **Routing Pages**:
    * `/`: Portfolio Hub (Kartu venture, metrik ROI, pembuatan startup baru).
    * `/sparring/[id]`: Executive Sparring Room (Debat Founder vs CoS/CTO).
    * `/preview/[id]`: Interactive Sandbox Preview (Iframe Webview, Terminal CLI, Snapshot Manager, Gate 2/3 Actions).
    * `/kanban/[id]`: Corporate Lounge & Kanban Board (Tiket tugas real-time antar-agen).
    * `/office`: 3D Cyber-Voxel Apple Park Mega-Campus Simulator (Three.js WebGL).
    * `/organization`: Bagan hierarki organisasi 12 agen dan status keaktifan.
    * `/analytics`: Financial Ledger, pembakaran token, dan unit economics per venture.
    * `/wisdom`: Repository memori korporat & SOP perusahaan.
    * `/settings`: Konfigurasi BYOK (Bring-Your-Own-Key LLM), Gembok Telegram, PaaS, dan Docker.

---

## 5. Daftar Fitur Lengkap di Project Ini

| Kategori Fitur | Nama Fitur | Deskripsi Fungsionalitas |
| :--- | :--- | :--- |
| **Orchestration** | **12 AI Agent Guilds** | 12 peran AI profesional: Founder (User), CoS, CFO, CTO, PM, Growth Lead, Frontend Dev, Backend Dev, QA Tester, DevSecOps, Copywriter, SEO Specialist. |
| **Orchestration** | **Deterministic State Machine** | 7 tahapan terisolasi: `IDEA_SUBMITTED`, `SPARRING_ROOM`, `GATE_1_WAITING`, `MOCK_PROTOTYPING`, `GATE_2_WAITING`, `PRODUCTION_HARDENING`, `GATE_3_WAITING`, `LIVE_OPERATIONS`. |
| **Governance** | **CEO Stage-Gates (1, 2, 3)** | Hak veto mutlak di tangan Founder untuk mengeksekusi aksi: `APPROVE`, `REVISE`, atau `KILL` pada setiap gerbang kematangan produk. |
| **Collaboration** | **The Sparring Room** | Ruang interaksi sokratik real-time antara Founder, CoS, dan CTO untuk mempertajam ide sebelum baris kode pertama ditulis. |
| **Prototyping** | **Ephemeral Sandbox Webview** | Pratinjau aplikasi instan di dalam iframe dengan selector mode viewport: *Desktop* (100%), *Tablet* (768px), dan *Mobile* (375px). |
| **Prototyping** | **Interactive Web Terminal** | Antarmuka CLI interaktif berbasis WebSocket langsung ke dalam kontainer Linux sandbox. |
| **Prototyping** | **Snapshot Manager & Rollback** | Fitur membuat *checkpoint* state kode sandbox dan melakukan pemulihan (*one-click rollback*) saat terjadi kesalahan kompilasi. |
| **Prototyping** | **Network Quota Inspector** | Pemantauan konsumsi lalu lintas jaringan kontainer (Inbound/Outbound KB/s) dan sisa kuota isolasi. |
| **Engineering** | **P2P PR & Automated Review** | Agen Backend dan Frontend menerbitkan Pull Request mandiri dan saling me-review kualitas kode sebelum digabungkan ke branch utama. |
| **Engineering** | **Three-Way Merge Conflict Resolver** | Pendeteksi dan penyelesai konflik merge otomatis pada file konfigurasi, routing, dan skema database. |
| **Security** | **OWASP Top-10 Security Scanner** | Pemindaian keamanan otomatis mendeteksi SQLi, Command Injection, XSS, Path Traversal, Insecure Deserialization, dan kebocoran Token API. |
| **Security** | **AES-256-GCM Secret Vault** | Brankas penyimpanan kredensial produksi terenkripsi berbasis salt dinamis dan derivasi PBKDF2 HMAC-SHA256. |
| **Security** | **Telegram OTP Gatekeeper** | Gembok akses personal yang mengirimkan one-time password dinamis ke bot Telegram pemilik dan merotasinya secara otomatis. |
| **Economics** | **Financial Ledger & Analytics** | Kalkulasi biaya pembakaran token per agen, *gross margin*, *burn rate*, dan prediksi kelayakan finansial venture. |
| **Operations** | **Corporate Wisdom & Memory** | Penyimpanan pengalaman kolektif masa lalu (*heuristik & solusi kegagalan*) yang diinjeksikan kembali ke agen pada proyek berikutnya. |
| **Simulation** | **3D Cyber-Voxel Apple Park HQ** | Kantor virtual 3D interaktif Three.js (272m The Grand Ring, 4 lantai, lift kaca, auditorium keynote) yang mengalirkan koordinat agen via WebSocket. |

---

## 6. Daftar Seluruh Endpoint API dan Kegunaannya

Berikut adalah inventaris lengkap seluruh 21 modul router REST API & WebSocket pada backend (`http://localhost:8000/api/v1`):

### 6.1. Manajemen Proyek & State (`projects.py`)
* `POST /projects`: Mendaftarkan ide bisnis baru dan menginisialisasi State Machine ke `SPARRING_ROOM`.
* `GET /projects`: Mengambil ringkasan seluruh venture untuk tampilan Portfolio Hub.
* `GET /projects/{project_id}`: Mengambil data detail, skema, dan status venture tertentu.
* `DELETE /projects/{project_id}`: Menghapus venture dan membersihkan alokasi sandbox terkait.
* `GET /projects/{project_id}/events`: Aliran SSE (*Server-Sent Events*) real-time untuk perubahan state dan aktivitas agen.

### 6.2. Executive Sparring Room (`sparring.py`)
* `GET /projects/{project_id}/sparring`: Mengambil riwayat percakapan antara Founder, CoS, dan CTO.
* `POST /projects/{project_id}/sparring/chat`: Mengirim pesan, revisi, atau instruksi Founder ke Sparring Room.

### 6.3. Pengambilan Keputusan CEO (`gates.py`)
* `POST /projects/{project_id}/gates/{gate_id}/decision`: Menyerahkan putusan gerbang (`gate_1`, `gate_2`, `gate_3`) dengan aksi `APPROVE`, `REVISE`, atau `KILL` beserta catatan umpan balik (*feedback*).

### 6.4. Sandboxing & Preview (`sandbox_snapshots.py`, `sandbox_terminal_ws.py`, `sandbox_network.py`)
* `GET /projects/{project_id}/preview/status`: Memeriksa ketersediaan URL preview sandbox (`http://demo-{id}.local.sandbox`).
* `GET /projects/{project_id}/sandbox/snapshots`: Mengambil daftar snapshot checkpoint cadangan kode sandbox.
* `POST /projects/{project_id}/sandbox/snapshots`: Membuat snapshot cadangan manual dari state kode sandbox saat ini.
* `POST /projects/{project_id}/sandbox/rollback`: Mengembalikan seluruh file kontainer sandbox ke versi snapshot tertentu.
* `GET /projects/{project_id}/sandbox/network`: Mengambil metrik konsumsi bandwidth dan sisa kuota transfer data kontainer.
* `POST /projects/{project_id}/sandbox/network/limit`: Mengonfigurasi batas kecepatan atau kuota maksimum transfer data sandbox.
* `WEBSOCKET /sandbox/ws/terminal/{project_id}`: Sesi shell terminal Linux PTY streaming dua arah langsung ke kontainer.

### 6.5. Keamanan & Secret Vault (`vault.py`, `auth.py`)
* `GET /projects/{project_id}/vault`: Mengambil daftar kunci rahasia (*secret keys*) yang tersimpan (nilai disensor `***`).
* `POST /projects/{project_id}/vault`: Menyimpan kunci rahasia baru yang langsung dienkripsi menggunakan AES-256-GCM.
* `DELETE /projects/{project_id}/vault/{key_name}`: Menghapus kredensial tertentu dari brankas proyek.
* `GET /auth/status`: Memeriksa apakah gembok autentikasi Telegram aktif dan apakah sesi browser valid.
* `POST /auth/verify`: Memverifikasi kode OTP Telegram untuk menerbitkan token sesi akses.
* `POST /auth/resend`: Mengirim ulang password rotasi baru ke akun Telegram Founder.
* `POST /auth/rotate`: Memaksa pergantian password baru secara instan (*manual rotation*).

### 6.6. Rekayasa Perangkat Lunak & Git Engine (`pull_requests.py`, `branch_merge.py`)
* `GET /projects/{project_id}/prs`: Mengambil daftar Pull Request aktif yang diajukan oleh agen.
* `POST /projects/{project_id}/prs`: Menerbitkan Pull Request baru dari feature branch.
* `GET /projects/{project_id}/prs/{pr_id}`: Mengambil rincian diff perubahan kode dan komentar review P2P.
* `POST /projects/{project_id}/prs/{pr_id}/review`: Agen atau Founder mengirimkan approval/request changes pada PR.
* `POST /projects/{project_id}/branch/merge`: Mengeksekusi penggabungan cabang kode via algoritma *three-way merge*.

### 6.7. Tata Kelola & Analitik Keuangan (`governance.py`, `analytics.py`, `wisdom.py`)
* `GET /projects/{project_id}/governance`: Mengambil status circuit-breaker, batas token, dan riwayat intervensi.
* `POST /projects/{project_id}/governance/circuit-breaker`: Memutus darurat atau melanjutkan eksekusi otonom agen (*kill-switch*).
* `GET /projects/{project_id}/analytics`: Mengambil breakdown biaya konsumsi LLM token per peran dan kalkulasi margin.
* `GET /corporate/wisdom`: Mengambil artikel basis pengetahuan korporat dan solusi kegagalan masa lalu.
* `POST /corporate/wisdom`: Menambahkan heuristik atau aturan operasional baru ke memori organisasi.

### 6.8. Kantor Virtual Spasial 3D (`office.py`, `office_ws.py`)
* `GET /corporate/office/state`: Mengambil snapshot tata letak gedung dan daftar koordinat awal seluruh agen.
* `POST /corporate/office/all-hands`: Mengirim sinyal panggilan darurat rapat umum seluruh agen ke auditorium.
* `POST /corporate/office/directive`: Mengirim instruksi tugas langsung ke agen tertentu via avatar 3D.
* `WEBSOCKET /corporate/ws/office/{project_id}`: Saluran streaming real-time berkecepatan 60 FPS yang menyinkronkan posisi koordinat $(X, Y, Z)$, status animasi (*CODING, MEETING, WALKING, BLOCKED*), dan balon ucapan (*speech bubble*) seluruh agen ke antarmuka Three.js WebGL.

### 6.9. Pengaturan Sistem Dinamis (`settings.py`)
* `GET /settings`: Mengambil konfigurasi dinamis sistem (Kunci API BYOK, Model LLM per agen, preferensi PaaS).
* `PUT /settings`: Memperbarui konfigurasi sistem secara runtime tanpa perlu me-restart server backend.
* `POST /settings/reset`: Mereset seluruh konfigurasi sistem ke nilai default `.env`.

---
*Dokumentasi ini mencakup kondisi arsitektur resmi per Oktober 2026.*
