# 📘 SPESIFIKASI TEKNIS & PANDUAN ARSITEKTUR SISTEM (v2.4+)
## Virtual Tech Startup Multi-Agent System & Universal Corporate Operating System
**Panduan Internal AI Agent: Arsitektur Otonom, Asynchronous Kanban State Machine, Multi-Product Looping Pipeline, BYOK, dan 21 Router API**

---

## 1. Project Ini Tentang Apa?

**Virtual Tech Startup Multi-Agent System** adalah sistem operasi korporat berbasis kecerdasan buatan mandiri (*Autonomous AI Virtual Enterprise OS*) dan platform inkubasi startup digital terpadu. 

Platform ini dibangun untuk memecahkan hambatan terbesar inovasi teknologi: **ketergantungan pada tim fisik yang mahal dan alur birokrasi manual yang lambat**. Dengan sistem ini, seorang **Solo Entrepreneur / Founder Tunggal** bertindak sebagai **Chairman & Chief Executive Officer (CEO)** yang mengendalikan sebuah konglomerasi virtual berskala penuh. 

Sistem ini tidak bekerja seperti chatbot percakapan biasa (*conversational chat prompting*), melainkan mensimulasikan operasional perusahaan teknologi Silicon Valley secara nyata:
- Merancang struktur organisasi multi-divisi (Divisi Rekayasa Perangkat Lunak, Divisi Edukasi & Kursus, Divisi Copywriting & Pemasaran Konten, Divisi Riset Pasar, hingga divisi kustom).
- Merekrut, mengonfigurasi, dan menugaskan karyawan AI dengan instruksi sistem terisolasi, batasan anggaran token, dan perkakas eksekusi riil.
- Menjalankan rekayasa perangkat lunak secara konkuren non-blocking (Frontend Next.js & Backend FastAPI dibangun bersamaan).
- Mengaudit celah keamanan menggunakan pemindai Abstract Syntax Tree (AST) untuk mendeteksi kerentanan OWASP Top 10 nyata.
- Menguji prototipe interaktif di lingkungan *ephemeral sandbox* dengan terminal PTY live dan sistem snapshot anti-data-loss.
- Menvisualisasikan seluruh dinamika organisasi, pergerakan karyawan AI, dan telemetri kinerja dalam lingkungan digital twin spasial **3D Cyber-Voxel Apple Park Mega-Campus** berskala $272\text{ meter}$.

### ⚠️ Klarifikasi Konsep Inti: 12 Peran & State Machine Awal adalah Baseline Template!
Banyak pengembang keliru mengira sistem ini hanya memiliki 12 peran statis dan state machine waterfall 7-tahap. Perlu ditekankan:
> **12 peran kanonikal Silicon Valley (CoS, CTO, PM, UI/UX, FE, BE, QA, DevSecOps, Copywriter, SEO, dll.) dan alur deterministik 7-tahap tersebut HANYALAH STANDAR DASAR (Baseline Gold Standard Template) yang tersimpan di `branch_main`.**

Pada arsitektur modern (v2.4+), sistem telah berevolusi menjadi **Dynamic Asynchronous Corporate Operating System**:
- Struktur organisasi dapat diubah, ditambah divisi baru, dan didaftarkan peran AI baru secara visual.
- Alur kerja bukan lagi sekuensial linear, melainkan mendukung **looping dinamis** ($A \rightarrow B \rightarrow C \rightarrow A$) dan **multi-lini produk**.
- State machine bersifat **asinkron dan digerakkan oleh tiket Kanban (Ticket-Driven)**, di mana agen mengambil, mengeksekusi, dan menyesuaikan alur kerja mereka secara mandiri berdasarkan antrean tiket, dependensi, dan prioritas.

---

## 2. Cara Kerja Project Ini Secara Mendalam

### A. Dynamic Asynchronous Ticket-Driven State Machine
Sistem menggantikan model eksekusi waterfall yang kaku dengan mesin alur kerja asinkron yang digerakkan oleh tiket tugas pada papan virtual Kanban:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CORPORATE EVENT BUS (PUB/SUB)                           │
│                     asyncio.Queue per Project • SQLite WAL Persistence                 │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Siaran Event Tugas & Sinyal Status
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              MISSION CONTROL VIRTUAL KANBAN                            │
│                                                                                        │
│   [ BACKLOG ] ──────► [ TODO ] ──────► [ IN_PROGRESS ] ──────► [ REVIEW ] ────► [ DONE ]
│        │                 │                    │                     │              ▲
│        │                 │                    │                     │              │
│        ▼                 ▼                    ▼                     ▼              │
│   Dependensi &     Pekerjaan Siap      Task Concurrency      P2P Code Review       │
│   Prioritas Tugas  Diambil Agen         Dispatcher DAG       & QA Validation ──────┘
└───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             AGENT AUTONOMOUS DECISION SPACE                            │
│                              (AgentDecisionEnvelope JSON)                              │
│                                                                                        │
│   • PROCEED          : Tugas sukses, otomatis transisi ke kolom Kanban berikutnya      │
│   • CONSULT_ROLE     : Meminta klarifikasi teknis ke peran lain (Diawasi Guardrail)   │
│   • ESCALATE_C_LEVEL : Eskalasi hambatan kritis ke meja CTO / CoS / CEO                │
│   • REQUEST_REWORK   : Reviewer meminta revisi kode spesifik ke pembuat sebelumnya     │
└───────────────────────────────────────────────┬────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             EXECUTIVE GOVERNANCE & GUARDRAILS                          │
│                                                                                        │
│   • AgentCircuitBreaker : Memantau giliran diskusi inter-agen pada tiket.              │
│                           Jika turn >= 3 tanpa kemajuan kode -> BLOCKED_LOOP_DETECTED  │
│   • CEO Intervensi 1-Klik: FORCE_PROCEED | INTERVENE (Instruksi Chat) | REASSIGN       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Struktur Data Tiket Kanban (`corporate_tickets`)**:
   - `id`: Pengenal unik tiket (misal: `tkt_fe_auth_ui`).
   - `branch_id`: ID branch alur kerja organisasi (default: `branch_main`).
   - `project_id`: ID unik proyek venture yang sedang diinkubasi.
   - `division_id`: Divisi pemilik tanggung jawab pekerjaan.
   - `assigned_role_id`: Karyawan AI spesifik penanggung jawab tugas.
   - `product_line`: Lini produk (`SOFTWARE`, `EDUCATION`, `COPYWRITING`, `RESEARCH`, `CUSTOM`).
   - `priority`: Tingkat urgensi (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
   - `status`: Kolom Kanban aktif (`BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`, `BLOCKED_LOOP_DETECTED`).
   - `dependencies`: Daftar array `ticket_id` yang wajib berstatus `DONE` sebelum tiket ini dapat masuk ke kolom `TODO`.

2. **Pengambilan Keputusan Otonom Agen (`AgentDecisionEnvelope`)**:
   Setiap karyawan AI memproses tugas dan merespons dalam format amplop keputusan terstruktur:
   - **`PROCEED`**: Tugas selesai tervalidasi. Tiket berpindah ke `REVIEW` atau `DONE`, dan event bus memicu tiket berikutnya yang bergantung padanya.
   - **`CONSULT_ROLE`**: Agen menemui ketidakjelasan teknis dan mengajukan pertanyaan spesifik ke peran lain (misal: Backend bertanya ke PM mengenai skema autentikasi). Pertanyaan dicatat ke event bus dan memicu `AgentCircuitBreaker`.
   - **`ESCALATE_TO_C_LEVEL`**: Hambatan arsitektur tingkat tinggi diteruskan ke direksi (CTO/CoS) untuk dirumuskan menjadi opsi strategis bagi Founder.
   - **`REQUEST_REWORK`**: QA Engineer menolak hasil kerja dan meminta perbaikan berkas kode tertentu disertai daftar error pengujian.

3. **Mekanisme Anti-Infinite Loop Circuit Breaker (`circuit_breaker.py`)**:
   Mencegah pembengkakan biaya API akibat agen yang saling melempar pertanyaan tanpa kemajuan konkret:
   - Sistem mencatat counter giliran konsultasi (`turn_count`) untuk setiap tiket.
   - Jika perdebatan mencapai **$\ge 3$ putaran berturut-turut**, circuit breaker seketika membekukan tiket menjadi `BLOCKED_LOOP_DETECTED`.
   - Tiket yang dibekukan memicu alert darurat ke Founder melalui Lounge WebSocket.
   - Founder membuka modal intervensi (`CeoInterventionModal.tsx`) untuk menentukan putusan mutlak:
     * `FORCE_PROCEED`: Melewati perdebatan dan memaksa tugas selesai.
     * `INTERVENE`: Memberikan instruksi tertulis yang wajib dipatuhi agen, lalu mengembalikan status tiket ke `IN_PROGRESS`.
     * `REASSIGN`: Memindahkan tugas ke karyawan AI lain dan mereset status ke `TODO`.

4. **Task Concurrency Dispatcher (`dispatcher.py`)**:
   - Untuk tugas-tugas rekayasa yang bersifat independen (misal: Frontend UI Mockup dan Backend Database/API Scaffolding), orkestrator mengeksekusi kedua node secara paralel menggunakan `asyncio.gather()`.
   - Papan Kanban memindahkan status kedua tiket ke `IN_PROGRESS` secara bersamaan, memangkas durasi produksi hingga separuhnya.

---

## 3. Workflow Proyek & Aliran Data (Data Flow)

### A. Siklus Hidup Venture (The Venture Lifecycle)

1. **Inisialisasi Ide & Sparring Room (`/sparring/[id]`)**:
   - Founder memasukkan visi ide bisnis kasar di antarmuka web.
   - Chief of Staff (CoS) dan Chief Technology Officer (CTO) menggelar sesi debat sokratik (*Executive Sparring*) untuk menguji kelayakan bisnis, unit economics, dan tantangan teknis.
   - Output: *Executive Summary* dan *Business Brief*.
2. **Stage-Gate 1: CEO Inception Approval**:
   - Founder meninjau hasil sparring dan memberikan putusan: `APPROVE`, `REVISE`, atau `TERMINATE`.
3. **Penyusunan Spesifikasi Teknis & Kunci Kontrak OpenAPI**:
   - Product Manager (PM) menyusun *Lean PRD*.
   - CTO mengunci spesifikasi antarmuka API ke dalam kontrak resmi *OpenAPI 3.1.0 JSON Specification* (`state.openapi_spec`).
4. **Sintesis Konkuren & Prototyping Paralel**:
   - Dispatcher mengeksekusi sintesis paralel:
     * Frontend Engineer membangun prototipe antarmuka Next.js 14 lengkap dengan Tailwind CSS.
     * Backend Engineer membangun skema database SQLite, model SQLAlchemy/SQLModel, dan endpoint FastAPI.
5. **Peer-to-Peer Review & Automated Pull Request Engine**:
   - Kode yang dihasilkan dikirimkan ke modul PR (`pull_requests.py`).
   - QA Engineer mengeksekusi pengujian otomatis dan peer review.
   - Algoritma *3-Way Merge Conflict Resolution* memastikan perubahan kode digabungkan tanpa merusak integritas berkas.
6. **Pemindaian Keamanan Statis Riil (Real AST Security Scanner)**:
   - DevSecOps Engineer menjalankan audit keamanan menggunakan Python Abstract Syntax Tree (`security_scanner.py`).
   - Memeriksa injeksi kode (`eval`, `exec`), kunci API/rahasia yang tertulis langsung (*hardcoded secrets*), SQL injection, CORS yang terlalu permisif (`*`), dan kerentanan XSS React (`dangerouslySetInnerHTML`).
7. **Stage-Gate 2: Live Demo Day di Sandbox (`/preview/[id]`)**:
   - Aplikasi dijalankan secara otomatis di lingkungan *dual-engine sandbox* (Docker atau Embedded Async HTTP port 4000–4999).
   - Founder menguji aplikasi secara langsung melalui iframe live preview, berinteraksi melalui terminal PTY live, dan dapat mengambil snapshot direktori (CoW) untuk pemulihan instan anti-data-loss.
8. **Injeksi Kredensial Produksi ke Secret Vault (`/projects/{id}/vault`)**:
   - Founder menginjeksi kredensial produksi rahasia (seperti Stripe Secret Key, AWS S3, Resend API Key) yang dienkripsi menggunakan algoritma AES-256-GCM.
9. **Stage-Gate 3: Deployment Produksi**:
   - Founder menyetujui peluncuran akhir ke infrastruktur PaaS (Docker/Coolify) dan sistem mencatat biaya penggunaan token ke *Token Financial Ledger*.

---

### B. Alur Perancangan Visual Pipeline (Visual Workflow Builder)

1. **Pemilihan Lini Produk**:
   Pengguna memilih tab pipeline lini produk di `/organization`:
   - `pipe_software_main`: Rekayasa Perangkat Lunak & SaaS.
   - `pipe_education_main`: Edukasi, Silabus, dan Kursus Digital.
   - `pipe_content_main`: Copywriting, Kampanye Pemasaran, dan SEO.
   - `CUSTOM`: Pipeline kustom dinamis untuk produk baru apa pun.
2. **Penyusunan Alur Kerja Bebas (HTML5 Drag & Drop)**:
   - Pengguna men-drag kartu peran dari daftar divisi dan menjatuhkannya (*drop*) ke kanvas sekuensial alur kerja.
   - Pengguna dapat menduplikasi peran untuk membentuk alur looping (misal: `FE ➔ BE ➔ QA ➔ FE ➔ QA`).
   - Pengguna dapat men-drag kartu **Gerbang Keputusan CEO** (*Stage-Gate*, *Strategic Meeting*, *Direction Input*) ke titik mana pun di antara tahapan.
3. **Penyimpanan Atomik & Reset Pipeline**:
   - Seluruh tahapan disimpan ke tabel `corporate_pipeline_stages` dengan penomoran urut otomatis dan UUID unik (`stg_xxxxxxxx`), mencegah konflik *UNIQUE constraint* saat forking branch.

---

### C. Alur Kerja Git-Style Organizational Branching & Forking

```
[ branch_main (Gold Standard / Protected) ]
                   │
                   ▼ (1-Klik Forking)
[ branch_experiment (Isolated Sandbox Workflow) ]
   ├── Modifikasi Divisi & Peran Kustom
   ├── Penyusunan Pipeline Looping Baru
   └── Eksekusi & Pengujian Tiket Kanban Terisolasi
                   │
                   ▼ (1-Klik Merge to Main)
[ Atomic Branch Merger & Structural Diff Resolution ]
                   │
                   ▼
[ branch_main Diperbarui dengan Inovasi Terverifikasi ]
```

1. **Forking**: `corporate_repo.fork_branch` mengkloning seluruh entri divisi, peran karyawan AI, pipeline, tahapan alur kerja, dan tiket tugas dari branch sumber ke branch baru secara terisolasi dengan relasi ID yang sinkron.
2. **Eksperimentasi**: Pengguna dapat mengubah alur kerja atau prompt agen pada branch eksperimen tanpa memengaruhi alur produksi aktif di `branch_main`.
3. **Merging**: `branch_merge.py` menghitung perbedaan (*diff*) struktur organisasi antara branch eksperimen dan branch tujuan, lalu melakukan penggabungan atomik ke branch utama.

---

## 4. Arsitektur Proyek (System Architecture)

Sistem mengadopsi prinsip **Clean Architecture & Hexagonal Decoupling** dengan penegakan ketat standar kualitas kode:
- **Prinsip Tanggung Jawab Tunggal (SRP)**: Setiap berkas backend dibatasi ketat maksimal **150–200 baris kode**. Berkas yang membesar wajib dipecah menjadi modul repositori atau skema terpisah.
- **Backend Stack**:
  * **Framework**: FastAPI (Python 3.10+) dengan ASGI Middleware murni (`SecurityGateMiddleware` dan `ProcessTimeLoggingMiddleware`) untuk latensi sub-milidetik.
  * **Basis Data**: SQLite dalam mode **Write-Ahead Logging (WAL)** melalui pustaka asinkron `aiosqlite`, menjamin konkurensi pembacaan tinggi tanpa *database lock*.
  * **Event Bus**: In-memory asynchronous pub/sub berbasis `asyncio.Queue` per proyek dengan pencatatan otomatis ke tabel database.
  * **LLM Gateway**: Klien terpadu `UnifiedLLMClient` yang mendukung OpenRouter, DeepSeek, Anthropic, OpenAI, Google Gemini, Groq, dan Ollama lokal.
  * **Sandbox Engine**: Docker Engine SDK terintegrasi dengan reverse proxy Caddy (`*.local.sandbox`) dan fallback *Embedded Async HTTP Server* lokal.
- **Frontend Stack**:
  * **Framework**: Next.js 14 (App Router) dengan TypeScript murni.
  * **Styling**: Tailwind CSS dengan palet Obsidian Cyber-Noir (`#050507`), High-Refraction Frosted Glass, dan aksen dinamis.
  * **Interaktivitas**: Native HTML5 Drag and Drop API untuk kanvas alur kerja.
  * **3D Spasial**: Three.js dan React Three Fiber untuk visualisasi kampus kantor Apple Park $272\text{ meter}$.
  * **Komunikasi Real-time**: Klien WebSocket native untuk PTY terminal, live lounge, dan pergerakan agen 3D, dipadukan dengan Server-Sent Events (SSE) untuk streaming inferensi LLM.

---

## 5. Fitur-Fitur Lengkap Proyek (v2.4+)

### 1. Visual Organization & Division Studio (`/organization`)
- Bagan struktur organisasi visual interaktif.
- CRUD divisi dinamis: penamaan, slug, deskripsi mandat, aksen warna HEX, dan ikon Lucide React.
- CRUD peran karyawan AI dinamis: system prompt persona, penugasan model LLM, temperature slider, token budget per tugas, dan seleksi perkakas eksekusi.

### 2. Desentralisasi BYOK (Bring-Your-Own-Key) Terintegrasi
- Konfigurasi model dan provider LLM dilakukan langsung pada modal peran karyawan AI (`RoleModal.tsx`).
- Dukungan 7 provider utama: OpenRouter, DeepSeek, Anthropic Claude, OpenAI, Google Gemini, Groq, dan Ollama Lokal.
- Pil preset rekomendasi cepat dengan penanda visual `• FREE` berwarna hijau emerald untuk model tanpa biaya.
- Penyimpanan kunci rahasia terenkripsi AES-256-GCM pada Secret Vault dan pembaruan konfigurasi runtime instan tanpa me-restart server backend.

### 3. Visual HTML5 Drag-and-Drop Looping Pipeline Builder
- Navigasi tab multi-lini produk: Software & SaaS, Edukasi, Copywriting, dan Kustom.
- Drag-and-drop kartu peran dari divisi ke kanvas sekuensial alur kerja atau tombol cepat `+ Pipeline`.
- Fleksibilitas alur looping ($A \rightarrow B \rightarrow C \rightarrow A$).
- Kartu Gerbang Keputusan CEO (*Approval Gate*, *Strategic Meeting*, *Direction Input*) yang dapat di-drag dan disisipkan di posisi mana pun.

### 4. Dynamic Asynchronous Virtual Kanban Board (`/kanban/[id]`)
- 5 kolom status tugas adaptif: `BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`.
- Transisi tiket otomatis saat tugas dieksekusi oleh Dispatcher.
- Visualisasi dependensi tugas dan prioritas.
- Live Lounge WebSocket (`/ws/lounge/{project_id}`) untuk memantau dialog koordinasi inter-agen secara real-time dan memberikan arahan langsung sebagai Chairman.

### 5. Executive Governance, Decision Space & Circuit Breaker
- Kontrak pertukaran keputusan terstruktur `AgentDecisionEnvelope` (JSON).
- `AgentCircuitBreaker`: Otomatis membekukan tugas (`BLOCKED_LOOP_DETECTED`) jika terjadi perdebatan inter-agen $\ge 3$ putaran tanpa kode baru.
- Modal Hak Veto CEO: `FORCE_PROCEED`, `INTERVENE` (instruksi tertulis), dan `REASSIGN`.
- Eskalasi Strategis C-Level: Laporan eksekutif terstruktur dengan formulasi Opsi A vs Opsi B untuk putusan 1-klik Founder.

### 6. Git-Style Organizational Branching & Forking
- Perlindungan alur utama `branch_main` (*Gold Standard*).
- 1-klik forking struktur organisasi ke branch eksperimen dengan kloning data terisolasi.
- 1-klik merge kembali ke `branch_main` dengan kalkulasi *diff* struktural otomatis.

### 7. Interactive Live Sandbox & Web PTY Terminal (`/preview/[id]`)
- Iframe live preview purwarupa aplikasi Next.js/FastAPI yang dihasilkan.
- Terminal CLI live dua arah interaktif berbasis Web PTY WebSocket dengan guardrail proteksi perintah berbahaya.
- Copy-on-Write (CoW) Snapshots dengan auto-backup bertag `AUTO_PRE_ROLLBACK` sebelum rollback dijalankan (*Zero Data Loss Guarantee*).

### 8. Real AST OWASP Top-10 Security Scanner
- Audit keamanan kode statis berbasis Python Abstract Syntax Tree (AST).
- Mendeteksi code injection (`eval`, `exec`), hardcoded secrets/API keys, SQL injection, permissive CORS, dan React XSS vulnerabilities.

### 9. Stealth Telegram Security Gate (`/auth`)
- Pengamanan cloud pribadi tanpa halaman login konvensional.
- Modal Liquid Glass dengan PIN dinamis 6-digit yang berganti otomatis setiap 6 jam via background worker dan dikirimkan instan ke bot Telegram pribadi Founder.
- Perlindungan anti-pentest: pemblokiran DevTools/F12, penonaktifan klik kanan dan copy/paste pada form PIN, serta anti-bruteforce limiter.

### 10. 3D Cyber-Voxel Apple Park Mega-Campus Simulator (`/office`)
- Rekonstruksi spasial digital twin berskala $272\text{ meter}$ dari Apple Park: Main Ring Building, Steve Jobs Theater, Datacenter Server Building, Zen Pond, dan Fitness Center.
- Karakter karyawan AI berpenampilan voxel dengan status glow dinamis (aktif coding, berdiskusi, menunggu CEO gate, terblokir circuit breaker).
- First-Person Walkthrough dengan deteksi tabrakan AABB dan sinkronisasi koordinat real-time via WebSocket.

### 11. Corporate Wisdom Knowledge Base & Financial Ledger
- `CorporateWisdomEngine`: Mengonsolidasikan best-practice, aturan arsitektur, dan solusi bug lintas proyek ke dalam basis pengetahuan korporat terpusat.
- `TokenLedger`: Pencatatan konsumsi token dan estimasi biaya operasional per agen secara transparan untuk evaluasi *unit economics*.

---

## 6. Daftar Lengkap 21 Endpoint Router API Backend

Seluruh endpoint terdaftar di bawah prefix `/api/v1` dan terisolasi dalam berkas-berkas router di direktori `backend/app/api/v1/`:

| No | Berkas Router | Prefix Endpoint | Tipe | Metode HTTP & Path | Deskripsi & Kegunaan Teknis |
|:--:|:--------------|:----------------|:----:|:-------------------|:----------------------------|
| 1 | `corporate.py` | `/corporate` | REST | `GET /corporate/branches`<br>`POST /corporate/branches`<br>`POST /corporate/branches/fork`<br>`GET /corporate/branches/{id}/divisions`<br>`POST /corporate/branches/{id}/divisions`<br>`GET /corporate/branches/{id}/roles`<br>`POST /corporate/branches/{id}/roles` | **Manajemen Organisasi Korporat**: Mengelola pendaftaran branch, forking alur organisasi, pendaftaran divisi, serta pembuatan dan modifikasi peran karyawan AI beserta spesifikasi prompt dan tool permissions. |
| 2 | `corporate_workflow.py` | `/corporate/branches/{id}` | REST | `GET /pipelines`<br>`POST /pipelines`<br>`DELETE /pipelines/{pipe_id}`<br>`GET /pipeline`<br>`PUT /pipeline`<br>`POST /pipeline/reset`<br>`PUT /reorder-divisions` | **Workflow Pipeline Builder**: Mengelola multi-pipeline produk (Software, Edukasi, Copywriting, Kustom), menyimpan urutan tahapan alur kerja kanvas (DND), mendukung alur looping, serta mereset pipeline ke baseline. |
| 3 | `corporate_tickets.py` | `/corporate/tickets` | REST | `GET /{project_id}`<br>`POST /`<br>`POST /{ticket_id}/transition`<br>`DELETE /{ticket_id}` | **Virtual Kanban Board**: Mengambil daftar tiket tugas proyek, membuat tiket baru, memindahkan status kolom tiket (`BACKLOG` s/d `DONE`), serta menghapus tiket. |
| 4 | `corporate_events.py` | `/corporate/events` | REST | `GET /{project_id}`<br>`POST /` | **Event Bus Log & Messaging**: Mengambil riwayat pesan percakapan, notifikasi tugas, dan event bus antar-agen pada proyek tertentu. |
| 5 | `corporate_ws.py` | `/ws/corporate` | WS | `WS /ws/corporate/{project_id}` | **Real-Time Kanban WebSocket**: Sinkronisasi instan pembaruan status tiket Kanban, siaran event tugas baru, dan koordinasi real-time. |
| 6 | `governance.py` | `/governance` | REST | `GET /status/{ticket_id}`<br>`POST /override`<br>`POST /escalate`<br>`POST /decision` | **Executive Governance & Circuit Breaker**: Memeriksa status pembekuan tiket oleh circuit breaker, mengeksekusi hak veto CEO (`FORCE_PROCEED`, `INTERVENE`, `REASSIGN`), serta mengelola eskalasi C-Level. |
| 7 | `branch_merge.py` | `/corporate/branches` | REST | `GET /{src}/diff/{target}`<br>`POST /{target}/merge` | **Git-Style Branch Merging**: Menghitung perbedaan struktural (*diff*) divisi, peran, dan pipeline antar-branch, serta menggabungkan branch eksperimen kembali ke `branch_main`. |
| 8 | `projects.py` | `/projects` | REST | `GET /`<br>`POST /`<br>`GET /{id}`<br>`GET /{id}/state`<br>`DELETE /{id}` | **Venture State Management**: Inisialisasi proyek startup baru dari ide Founder, memuat checkpoint snapshot state aktif, dan manajemen portofolio venture. |
| 9 | `sparring.py` | `/projects/{id}/sparring` | REST / SSE | `GET /`<br>`POST /`<br>`GET /stream` | **Executive Sparring Room**: Memfasilitasi debat sokratik antara Founder, CoS, dan CTO sebelum PRD disusun, dengan dukungan streaming teks respon LLM (SSE). |
| 10 | `gates.py` | `/projects/{id}/gates` | REST | `GET /status`<br>`POST /decision` | **Founder Stage-Gates**: Mengelola gerbang persetujuan formal Founder (Stage-Gate 1 Inception, Stage-Gate 2 Demo Day, Stage-Gate 3 Production). |
| 11 | `pull_requests.py` | `/projects/{id}/prs` | REST | `GET /`<br>`POST /`<br>`POST /{pr_id}/review`<br>`POST /{pr_id}/merge` | **Automated PR Engine**: Siklus hidup Pull Request otomatis, eksekusi peer code review oleh QA, dan 3-way merge conflict resolution. |
| 12 | `vault.py` | `/projects/{id}/vault` | REST | `POST /secrets`<br>`GET /secrets` | **Encrypted Secret Vault**: Menyimpan dan membaca nama kunci kredensial produksi terenkripsi AES-256-GCM tanpa mengekspos plaintext. |
| 13 | `analytics.py` | `/analytics` | REST | `GET /ledger/{project_id}`<br>`GET /summary` | **Financial Analytics & Token Ledger**: Memantau konsumsi token, estimasi biaya inferensi LLM per peran, dan evaluasi unit economics. |
| 14 | `settings.py` | `/settings` | REST | `GET /`<br>`PUT /`<br>`POST /reset` | **Dynamic System Settings**: Membaca dan memperbarui kunci API BYOK, parameter PaaS, dan konfigurasi runtime tanpa me-restart server backend. |
| 15 | `auth.py` | `/auth` | REST | `POST /verify-pin`<br>`GET /status` | **Telegram Security Gate Auth**: Memvalidasi PIN dinamis 6-digit gerbang keamanan dan menerbitkan session token HMAC-SHA256 valid. |
| 16 | `wisdom.py` | `/wisdom` | REST | `GET /`<br>`POST /query`<br>`POST /record` | **Corporate Wisdom Engine**: Mengakses dan merekam best practice, aturan arsitektur, dan wisdom organisasional lintas proyek. |
| 17 | `office.py` | `/office` | REST | `GET /layout`<br>`GET /telemetry` | **3D Spatial Layout**: Menyediakan denah arsitektur procedural kampus Apple Park, koordinat divisi, dan data telemetri kantor. |
| 18 | `office_ws.py` | `/ws/office` | WS | `WS /ws/office` | **3D Real-Time Spatial WebSocket**: Siaran langsung koordinat $(X, Y, Z)$, rotasi, dan status animasi agen 3D di dalam kantor virtual. |
| 19 | `sandbox_snapshots.py` | `/projects/{id}/sandbox` | REST | `GET /snapshots`<br>`POST /snapshots`<br>`POST /rollback` | **Zero-Data-Loss CoW Snapshots**: Mengelola snapshot direktori kode proyek dan memulihkan kode secara instan dengan auto-backup pre-rollback. |
| 20 | `sandbox_network.py` | `/projects/{id}/network` | REST | `GET /status`<br>`POST /restart` | **Sandbox Network & Proxy**: Memeriksa isolasi kontainer Docker dan status reverse proxy Caddy (`*.local.sandbox`). |
| 21 | `sandbox_terminal_ws.py`| `/ws/sandbox/{id}/terminal`| WS | `WS /ws/sandbox/{id}/terminal` | **Interactive Web PTY Terminal Stream**: Sesi shell CLI interaktif dua arah langsung ke dalam sandbox dengan guardrail penyaring perintah OS berbahaya. |

---

## 7. Standar Mutu Kode & Integritas Repositori

Sistem dibangun dengan mematuhi seperangkat aturan kualitas yang tidak dapat ditawar (*Strict Code Quality Guidelines*):
1. **Batas Baris Kode per Berkas**: Seluruh berkas backend wajib berada pada rentang maksimal **150–200 baris kode** (kepatuhan *Single Responsibility Principle*). Modul yang melebihi batas wajib dipecah menjadi sub-modul terisolasi.
2. **Type Annotations Penuh**: Seluruh parameter dan nilai kembalian (*return value*) pada fungsi dan metode Python wajib menyertakan type hints lengkap.
3. **Dokumentasi Google-Style Docstring**: Setiap kelas dan fungsi utama wajib memiliki deskripsi ringkas mengenai parameter, nilai kembalian, dan kemungkinan *exception* yang dilempar.
4. **Structured Logging**: Menggunakan `logger` dari `app.core.logger`. Dilarang keras menggunakan pemanggilan fungsi `print()`.
5. **Penanganan Pengecualian I/O Spesifik**: Seluruh operasi I/O, koneksi basis data SQLite (`aiosqlite.Error`), panggilan jaringan HTTP, dan parsing JSON wajib dibungkus dalam blok `try-except` spesifik. Dilarang menggunakan *bare except*.
6. **Code Hygiene**: Repositori wajib selalu dibersihkan dari *dead code*, berkas sementara yang tidak terpakai, dan *unused imports*.

---
*Dokumen ini merupakan spesifikasi teknis dan panduan operasional AI Agent internal untuk pengembangan dan pemeliharaan Virtual Tech Startup Multi-Agent System.*
