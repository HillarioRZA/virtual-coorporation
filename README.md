# 🪐 Virtual Tech Startup Multi-Agent System & Universal Venture Incubator Hub
### Autonomous AI Software Engineering Factory & 3D Spatial Operating System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL%2060FPS-black?style=flat-square&logo=three.js&logoColor=white)](https://threejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 💡 Overview

**Virtual Tech Startup Multi-Agent System** adalah platform inkubasi startup otonom dan pabrik rekayasa perangkat lunak mandiri (*Autonomous Software Factory*). 

Sistem ini memberdayakan seorang **Founder tunggal (Solo Entrepreneur / CEO)** untuk mengubah ide mentah produk teknologi menjadi aplikasi produksi yang siap di-deploy, ditenagai oleh **12 agen kecerdasan buatan (AI Agents)** dengan pembagian peran profesional Silicon Valley yang terisolasi dan berdisiplin tinggi.

Dilengkapi dengan antarmuka **3D Cyber-Voxel Apple Park Mega-Campus Simulator** (`/office`) berskala $272\text{ meter}$, Founder dapat berjalan langsung (*First-Person Walkthrough*) menjelajahi kantor virtual, memantau telemetri agen real-time, dan mengintervensi alur kerja melalui konsol komando terpadu.

---

## 🏛️ Architecture & System Topology

Sistem mengadopsi **Arsitektur Modular Heksagonal Decoupled** dengan penegakan batasan SRP (*Single Responsibility Principle*, $\le 150-200$ baris per file):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND COCKPIT DASHBOARD                      │
│                  Next.js 14 App Router • TypeScript                    │
│                                                                        │
│  /           /sparring/[id]   /preview/[id]   /kanban/[id]   /office   │
│  Portfolio   Executive Room   Sandbox & Gate  Lounge Tasks   3D Campus │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST / SSE / WebSockets
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        BACKEND ORCHESTRATION GATEWAY                   │
│                          FastAPI • Python 3.10+                        │
│                                                                        │
│  • ProcessTimeLogging & SecurityGate ASGI Middleware                   │
│  • 21 Modular API Routers (/projects, /sparring, /gates, /office, ...) │
└─────────────────┬────────────────────────────────────┬─────────────────┘
                  │                                    │
                  ▼                                    ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│      VENTURE STATE MACHINE       │  │       CORPORATE EVENT BUS        │
│ 7 Stages • 3 Founder Stage-Gates │  │ Non-blocking Asyncio Pub/Sub Q   │
└─────────────────┬────────────────┘  └────────────────┬─────────────────┘
                  │                                    │
                  ├────────────────────────────────────┘
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         CORE COGNITIVE ENGINES                         │
│                                                                        │
│  • 12 Agent Guilds (LangGraph / Ollama / Gemini / OpenAI BYOK)         │
│  • PR Engine & Automated P2P Code Reviewer                             │
│  • 3-Way Git Merge Conflict Resolution Algorithm                       │
│  • OWASP Top-10 Static Security Scanner                                │
│  • Docker Daemon Ephemeral Sandbox & Caddy Proxy (*.local.sandbox)     │
│  • AES-256-GCM Secret Vault (PBKDF2 HMAC-SHA256 Derivation)            │
│  • Telegram Dynamic OTP Security Gatekeeper (Auto-Rotating Access)     │
│  • SQLite WAL Mode ACID State Ledger & Financial Unit Economics        │
│  • Three.js WebGL 60 FPS Procedural Apple Park Mega-Campus Simulator   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Feature Highlights

### 1. 🤖 12 Specialized AI Agent Guilds
Setiap agen memiliki persona, batasan peran, memori kontekstual, dan wewenang yang tegas:
* **Executive Team**: Founder (User), Chief of Staff (CoS), Chief Financial Officer (CFO), Chief Technology Officer (CTO).
* **Product & Growth**: Product Manager (PM), Growth Lead, Copywriter, SEO Specialist.
* **Engineering & Security**: Frontend Lead, Backend Lead, QA Tester, DevSecOps Security Auditor.

### 2. 🚦 Deterministic 7-Stage State Machine & Stage-Gates
Menjamin proyek bergerak linier dan terstruktur tanpa halusinasi:
1. `SPARRING_ROOM` $\rightarrow$ **Gate 1: CEO Approval** (Validasi Bisnis & Arsitektur)
2. `MOCK_PROTOTYPING` $\rightarrow$ **Gate 2: Demo Day** (Validasi Purwarupa Interaktif Iframe)
3. `PRODUCTION_HARDENING` $\rightarrow$ **Gate 3: Production Vault** (Audit Keamanan & PaaS Launch)
4. `LIVE_OPERATIONS` (Monitoring Kuota, Finansial, dan Operasional Kantor)

Founder memegang hak veto mutlak pada setiap gerbang: **`APPROVE`**, **`REVISE`**, atau **`KILL`**.

### 3. 🧪 Ephemeral Sandboxing & Web Terminal
* Pratinjau aplikasi instan pada iframe dengan viewport multi-device (*Desktop 100%*, *Tablet 768px*, *Mobile 375px*).
* Terminal shell Linux PTY interaktif berbasis WebSocket langsung ke kontainer.
* **Snapshot & Instant Rollback**: Simpan checkpoint kode dan pulihkan (*one-click rollback*) saat terjadi error kompilasi.
* **Network Quota Inspector**: Pantau lalu lintas data kontainer secara real-time.

### 4. 🛡️ Enterprise Security & Secret Vault
* **Brankas Rahasia AES-256-GCM**: Kredensial produksi disimpan terenkripsi dengan salt dinamis.
* **Gembok Telegram OTP**: Akses web dashboard dilindungi kode rahasia berotasi otomatis ke bot Telegram Founder.
* **OWASP Static Scanner**: Audit otomatis mendeteksi SQLi, Command Injection, XSS, Path Traversal, dan kebocoran Token API sebelum kode diizinkan rilis.

### 5. 🪐 3D Cyber-Voxel Apple Park Mega-Campus (`/office`)
* **Skala Asli Megastruktur**: The Grand Ring berdiameter $272\text{ meter}$, 4 lantai penuh, Caffè Macs Great Atrium, Steve Jobs Theater, dan Tantau SecOps Datacenter.
* **Fisika & Kontrol Lengkap**: Mode *First-Person Walk*, lompat dengan gravitasi, sprint zoom FOV, dan *head-bobbing* sinematik.
* **Lift Kaca Interaktif 4 Lantai**: Kabin elevator fisik yang membawa posisi pemain naik/turun antarlantai.
* **Siklus Langit 24 Jam**: Orbit matahari parametrik dengan interpolasi suhu warna Kelvin alami ($2200\text{K} - 12000\text{K}$).
* **Sinkronisasi WebSocket Spasial**: Koordinat dan animasi agen (`CODING`, `MEETING`, `WALKING`) terhubung langsung ke mutasi backend.

---

## 🚀 Quickstart & Installation

### Prasyarat:
* **Python**: Versi `3.10` atau lebih baru
* **Node.js**: Versi `18.0` atau lebih baru (npm `9.0+`)
* **Docker** (Opsional, untuk kontainer ephemeral sandbox & Caddy)

### 1. Clone Repository
```bash
git clone https://github.com/HillarioRZA/virtual-coorporation.git
cd virtual-coorporation
```

### 2. Konfigurasi Environment Variables
Salin file `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```
Isi kunci API model AI yang Anda miliki (dukungan multi-provider: Google Gemini, OpenAI, Groq, atau Ollama lokal).

### 3. Jalankan via Universal Launcher (Rekomendasi)
Proyek ini dilengkapi script launcher otomatis satu perintah:
```bash
python run.py
```
Perintah ini akan secara otomatis:
* Memeriksa dependensi virtual environment Python.
* Menginisialisasi basis data SQLite (WAL Mode).
* Menjalankan server backend FastAPI pada port `8000`.
* Menjalankan server frontend Next.js 14 pada port `3000`.

---

## 🛠️ Menjalankan Secara Terpisah (Manual)

### Backend (FastAPI):
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
* API Documentation (Swagger UI): `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

### Frontend (Next.js 14):
```bash
cd frontend
npm install
npm run dev
```
* Cockpit Dashboard: `http://localhost:3000`
* 3D Virtual Mega-Campus: `http://localhost:3000/office`

### Menjalankan Unit Test Backend:
```bash
pytest backend/tests -v
```
*Status Test Suite:* **131 passed, 0 failures (100% Pass Rate)**.

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # 21 Modul Router REST API & WebSocket
│   │   ├── core/            # Config, Logger, Security Gate, Secret Vault, Settings
│   │   ├── db/              # Database SQLite Asinkron & Skema Tabel
│   │   ├── engine/          # State Machine, PR Reviewer, OWASP Scanner, EventBus, Simulator
│   │   └── models/          # Model Data Pydantic & Domain Schemas
│   ├── tests/               # 131+ Unit & Integration Test Suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js 14 App Router Pages (/, /office, /preview, /settings, ...)
│   │   ├── components/      # Subkomponen Modular (office/3d, preview, settings, sandbox, vault)
│   │   ├── hooks/           # Custom React Hooks (useSSEStream, useSystemSettings, ...)
│   │   └── lib/             # API Client, TypeScript Interfaces & Office Layout Constants
│   ├── package.json
│   └── tailwind.config.ts
├── sandboxes/               # Dockerfiles & Konfigurasi Caddy Reverse Proxy
├── project_description.md   # Dokumentasi Detail Aliran Data & 21 Router API
├── world_desc.md            # Dokumentasi Detail Arsitektur Spasial, Fisika & Shading 3D
├── world_v2.md              # Rencana Kerja Renovasi Spasial & Denah Masa Depan
└── run.py                   # Universal Launcher Otomatis
```

---

## 📚 Technical Documentation References

Untuk mempelajari rincian mendalam mengenai cara kerja sistem, silakan baca dokumentasi pendukung berikut:
* 📄 [**`project_description.md`**](project_description.md): Penjelasan alur data lengkap, arsitektur teknis, dan fungsi 21 router API.
* 📄 [**`world_desc.md`**](world_desc.md): Spesifikasi matematika prosedural 3D, material PBR, mesin fisika, dan telemetri kantor.
* 📄 [**`world_v2.md`**](world_v2.md): Strategi dan format perancangan denah interior tingkat lanjut.
* 📄 [**`API_CONTRACTS.md`**](API_CONTRACTS.md): Kontrak payload REST API & Server-Sent Events (SSE).

---

## 📄 License

Didistribusikan di bawah Lisensi **MIT**. Silakan lihat berkas `LICENSE` untuk informasi lebih lanjut.

---
*Created by [HillarioRZA](https://github.com/HillarioRZA) • Autonomous Multi-Agent Venture Incubator System.*
