# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM & UNIVERSAL VENTURE INCUBATOR HUB
**Dokumen Spesifikasi Produk & Cetak Biru Rekayasa Teknis**  
*Versi: 1.0 (Production-Ready / Native-First / Zero-Bloat)*  
*Status: Approved for Development*  
*Author: Founder & CEO (Human-in-the-Loop)*  
*Platform: Native Python Multi-Agent Engine + Next.js Cockpit Dashboard*

---

## 1. RINGKASAN EKSEKUTIF & VISI PRODUK

### 1.1 Visi Produk
Membangun platform **Autonomous Venture Studio / Inkubator Startup Otomatis** mandiri (*self-hosted*) yang mampu mentransformasikan ide bisnis mentah menjadi aplikasi perangkat lunak fungsional kelas produksi (*production-grade*) dalam hitungan menit hingga jam, di bawah kendali mutlak satu orang Founder & CEO (Human-in-the-Loop).

### 1.2 Filosofi Inti: Native-First & Zero-Bloat
Sistem ini dibangun di atas prinsip:
* **Zero Framework Lock-in:** Tidak menggunakan framework agen pihak ketiga yang rentan *breaking change* atau kelebihan abstraksi (seperti LangChain atau LangGraph). Logika orkestrasi dibangun menggunakan **Native Python Async State Machine (< 250 baris kode)**.
* **Bring Your Own Key (BYOK) Universal Gateway:** Menghilangkan perantara API pihak ketiga. Pengguna bebas menginjeksi API Key langsung (OpenAI, Anthropic, Gemini, DeepSeek, Groq, hingga Ollama lokal) dan mengganti model kapan saja tanpa menyentuh logika inti aplikasi.
* **"Show, Don’t Tell" Prototyping:** Sebelum menulis kode backend produksi dan database migrasi yang memboroskan token, sistem wajib mengeksekusi prototipe web interaktif (*Interactive MVP*) di browser melalui *Pre-Warmed Ephemeral Sandbox*.
* **Contract-First Architecture:** Komunikasi antar-agen menggunakan format skema terstruktur ketat (*Pydantic & OpenAPI 3.1 Spec as Single Source of Truth*) guna mengeliminasi halusinasi dan degradasi konteks (*context drift*).

---

## 2. GOALS & NON-GOALS

### 2.1 Goals (Tujuan Utama PoC)
1. **Validasi Super Cepat (Idea-to-Interactive Demo < 15 Menit):** Dari input ide bisnis mentah hingga tersajinya prototipe web yang dapat diklik di browser (Stage-Gate 2).
2. **Efisiensi Token (>60% Cost Reduction):** Menghemat pemborosan biaya inferensi LLM dengan memvalidasi UX di Fase Mock sebelum mengizinkan penulisan kode produksi di Fase 3.
3. **Zero UI Regression:** Memastikan transisi dari kode mock demo (Fase 2) ke kode produksi (Fase 3) tidak merusak tampilan antarmuka sama sekali dengan menerapkan *Adapter/Repository Pattern*.
4. **Keamanan & Kepatuhan Nyata:** Mengisolasi kredensial produksi di *Encrypted Secret Vault*, menjamin kelayakan hukum pembayaran (*Legal Document Bundle*), dan verifikasi *OWASP Security*.
5. **Observabilitas Keuangan Riil:** Menghitung laba/rugi dinamis secara otomatis (*Gross Revenue dikurangi Biaya Server & LLM Token*).

### 2.2 Non-Goals (Bukan Ruang Lingkup PoC Awal)
1. Tidak membangun mobile native app (iOS/Android) secara langsung pada tahap awal; output frontend awal difokuskan pada Responsive Web App (Next.js/PWA).
2. Tidak mengizinkan agen AI membuat akun bank / akun Stripe secara otonom (proses registrasi akun dan KYC tetap dilakukan oleh Founder secara manual).
3. Tidak mendukung arsitektur multi-tenant SaaS yang kompleks pada iterasi hari pertama; difokuskan pada arsitektur Single-Tenant / Independent Project Instance.

---

## 3. USER PERSONAS & ROLE MATRIX

### 3.1 Human User
* **Founder & CEO:** Pemegang otoritas tertinggi (Human-in-the-Loop). Menentukan visi awal produk, menguji prototipe di webview demo, menentukan persetujuan gerbang (Stage-Gates), dan mengotorisasi anggaran token.

### 3.2 Sistem AI: Rincian 11 Peran Agen
Sistem membagi 11 agen ke dalam 3 divisi hierarkis:

```
                     ┌─────────────────────────────────────────┐
                     │          FOUNDER & CEO (User)           │
                     │  - Visi & Arahan Strategis              │
                     │  - Pemegang Keputusan Mutlak (Gates)    │
                     └────────────────────┬────────────────────┘
                                          │
       ┌──────────────────────────────────┴──────────────────────────────────┐
       ▼                                                                     ▼
┌─────────────────────────────────┐                                   ┌─────────────────────────────────┐
│ Chief of Staff / CoS (AI)       │                                   │ Chief Technology Officer / CTO  │
│ [Business Co-Founder]           │                                   │ [Technical Co-Founder]          │
│ • Analisis Pasar, TAM, Unit Econ│                                   │ • Penentu Tech Stack & Arsitektur│
│ • Monetisasi & Strategi Harga   │                                   │ • Estimasi Biaya Token & Infra  │
│ • Audit P&L & Retensi Portofolio│                                   │ • Keamanan & Guardrails Koding  │
└────────────────┬────────────────┘                                   └────────────────┬────────────────┘
                 │                                                                     │
                 ▼                                                                     ▼
┌─────────────────────────────────┐                                   ┌─────────────────────────────────┐
│ Product & Governance Guild      │                                   │ Engineering & Data Guild        │
│ 1. Product Manager (PM)         │                                   │ 1. Frontend & UI Engineer       │
│ 2. Lead UI/UX Designer          │                                   │ 2. Backend & Systems Engineer   │
│ 3. Legal & Compliance Specialist│                                   │ 3. AI & Data Science Specialist │
│                                 │                                   │ 4. QA Automation & AI Evals     │
│                                 │                                   │ 5. DevSecOps & Cloud Engineer   │
└─────────────────────────────────┘                                   └─────────────────────────────────┘
```

| ID | Agen | Divisi | Model Rekomendasi (BYOK) | Tanggung Jawab Utama | Format Output (Schema) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A01** | **Founder / CEO** | Executive Board | Human | Otoritas visi, approval gerbang, input API keys | Strategic Intent & Gate Decision |
| **A02** | **Chief of Staff (CoS)** | Executive Board | DeepSeek-R1 / Gemini 2.5 Flash | Analisis pasar, pricing model, unit economics, P&L audit | `BusinessBriefSchema` (JSON) |
| **A03** | **CTO Agent** | Executive Board | Claude 3.5 Sonnet / DeepSeek-V3 | Pemilihan arketipe, estimasi biaya komputasi, guardrails | `SystemArchitectureSchema` (JSON) |
| **A04** | **Product Manager (PM)** | Product Guild | Gemini 2.5 Flash / Claude 3.5 Haiku | Lean PRD, Happy Path 3-langkah, acceptance criteria | `PRDContractSchema` (JSON) |
| **A05** | **Lead UI/UX Designer** | Product Guild | Claude 3.5 Haiku / Qwen-2.5-72B | Komponen visual, tata letak, Tailwind design tokens | `UIComponentSpecSchema` (JSON) |
| **A06** | **Legal & Compliance** | Governance Guild | DeepSeek-R1 / Claude 3.5 Haiku | Dokumen hukum lolos payment gateway & AI Disclaimers | `LegalBundle` (Markdown files) |
| **A07** | **Frontend Engineer** | Engineering Guild | Claude 3.5 Sonnet | Kode Next.js App Router, Tailwind, Adapter Pattern | TypeScript/JSX Source Files |
| **A08** | **Backend Engineer** | Engineering Guild | Claude 3.5 Sonnet / Qwen-Coder-32B | REST API FastAPI, SQLAlchemy, Alembic, Webhooks | Python/SQL Source Files |
| **A09** | **AI / Data Specialist** | Engineering Guild | Claude 3.5 Sonnet / DeepSeek-V3 | Logika RAG, LangGraph/State sub-agents, Polars/DuckDB | Python AI Modules |
| **A10** | **QA & AI Evals** | Engineering Guild | DeepSeek-R1 + Semgrep/Pytest | Audit keamanan OWASP, Unit test, LLM Hallucination test | `QualityGateScorecard` (JSON) |
| **A11** | **DevSecOps Engineer** | Engineering Guild | Qwen-2.5-Coder-32B / DeepSeek-V3 | Dockerization, Sandbox runner, PaaS deployment API | Dockerfile, Compose, Cloud Webhook |

---

## 4. SYSTEM ARCHITECTURE & TECH STACK SPECIFICATIONS

### 4.1 Native Python Orchestration Stack
* **State Machine:** Pure Native Python Async State Engine (`asyncio`, `typing`, `pydantic`).
* **HTTP & Gateway Layer:** `httpx` (Asynchronous HTTP/2 Client).
* **State Persistence / Checkpointer:** SQLite3 / JSON Flat-files (Snapshot state per-step).
* **Data Contracts & Validation:** Pydantic v2.

### 4.2 Application Golden Paths (Target Products Tech Stack)

| Arketipe | Frontend | Backend | Basis Data | Fitur Khusus |
| :--- | :--- | :--- | :--- | :--- |
| **1. Standard CRUD SaaS** | Next.js (TypeScript, App Router) + Tailwind CSS | FastAPI (Python) | PostgreSQL + SQLAlchemy + Alembic | Midtrans/Stripe Signature Webhooks, JWT Auth |
| **2. Autonomous Agentic AI** | Next.js + SSE Realtime Log Viewer | FastAPI | PostgreSQL + Redis (Celery) | Native State Engine, Execution Caps, Tool Calling |
| **3. Conversational RAG & Multimodal** | Next.js + Audio Streaming Waveform | FastAPI | Pgvector / Qdrant + Redis Cache | Native RAG, Whisper STT, Edge TTS, Vision API |
| **4. Data Science & Analytics** | Next.js + Apache ECharts / Recharts | FastAPI | DuckDB + Parquet / MinIO | Polars, Scikit-learn, XGBoost, Statsmodels |

### 4.3 Pre-Warmed Ephemeral Sandbox Architecture
* **Container Pool:** Base container Docker lokal (`venture-frontend-base` & `venture-backend-base`) dengan dependensi umum yang sudah terpasang.
* **Fast Code Injection:** Injeksi source code via Docker Volume Mount tanpa `npm install` berulang.
* **Routing Dinamis:** Reverse Proxy Caddy / Traefik mengalokasikan subdomain otomatis (`http://demo-<project_id>.local.sandbox`) menuju port kontainer ephemeral dalam waktu `< 5 detik`.

### 4.4 Spesifikasi Arsitektur Memori Multi-Agent (Persistent & Context Window Management)

Sistem menggunakan arsitektur **Single Shared Blackboard Event-Store dengan Role-Based Context Projection**. Seluruh agen membaca dan menulis ke satu basis data memori persisten terpusat, namun saat prompt dikirim ke LLM masing-masing agen, sistem menyaring konteks (*context projection*) agar jendela konteks (*context window*) tidak meledak dan bebas dari kebisingan informasi (*noise pollution*).

#### 4.4.1 Filosofi Memori: Mengapa 1 Storage Terpusat Berbasis Entity Role?
* **Single Source of Truth (SSOT):** Menghindari fenomena *split-brain* di mana agen Frontend dan Backend memiliki memori terpisah yang saling bertolak belakang.
* **Audit Trail Kronologis Lengkap:** Founder dapat melihat seluruh linimasa diskusi, revisi, dan keputusan antar-agen dalam satu urutan waktu linier yang utuh.
* **Zero Sync Overhead:** Tidak memerlukan protokol sinkronisasi antar-database memori agen yang lambat dan rawan desinkronisasi.

#### 4.4.2 Skema Tabel Persistent Memory (SQLite: `agent_event_logs`)
Memori disimpan secara persisten di SQLite lokal (`/data/venture_memory.db`) dengan skema tabel append-only berikut:

```sql
CREATE TABLE IF NOT EXISTS agent_event_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    stage TEXT NOT NULL,                  -- SPARRING, MOCK_DEMO, HARDENING, LIVE_OPS
    sender_role TEXT NOT NULL,             -- CEO, COS, CTO, PM, UI_UX, FRONTEND, BACKEND, QA, DEVOPS
    recipient_role TEXT NOT NULL,          -- BROADCAST, CTO, FRONTEND, BACKEND, dll.
    event_type TEXT NOT NULL,              -- CHAT, CRITIQUE, REVISE, ARTIFACT_PUBLISHED, GATE_APPROVAL
    content TEXT NOT NULL,                 -- Pesan teks atau instruksi
    artifact_ref TEXT,                     -- Key referensi ke Pydantic Schema (misal: 'openapi_spec')
    token_cost REAL DEFAULT 0.0,           -- Biaya inferensi langkah ini
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_stage ON agent_event_logs (project_id, stage);
CREATE INDEX idx_recipient ON agent_event_logs (recipient_role);
```

#### 4.4.3 Manajemen Context Window: The 3-Tier Assembly Pipeline
Jika seluruh riwayat 11 agen dimasukkan secara mentah ke dalam prompt LLM, token akan boros puluhan ribu token dan memicu halusinasi (misal: Frontend Engineer tidak perlu membaca 40 giliran debat antara CoS dan CEO mengenai ukuran TAM pasar).

Oleh karena itu, sebelum sebuah agen memanggil model LLM, modul `MemoryContextBuilder` merakit *Working Memory* menggunakan pipa 3-lapis:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PERSISTENT BLACKBOARD (SQLite Log)                   │
│   (100+ Pesan Lengkap dari Seluruh 11 Agen & Founder sejak Awal)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  [ FILTER CONTEXT BUILDER PER-ROLE ]
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PROYEKSI KONTEKS AKHIR (Masuk ke LLM Context Window: Max 4K-6K Token)   │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 1: PINNED CONTRACTS (Immutable Truth)                             │
│ • Hanya artefak resmi terkunci yang relevan untuk role tersebut.        │
│   Contoh untuk Frontend: `OpenAPISpec` + `UIComponentSpec`.            │
│   (Debat bisnis CoS diabaikan secara total).                           │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 2: ROLE-TARGETED SCOPED HISTORY (Direct Mentions)                 │
│ • Pesan yang `recipient_role` adalah Agen tersebut, ATAU               │
│ • Pesan yang dikirim oleh Agen tersebut (`sender_role`), ATAU          │
│ • Pengumuman global `BROADCAST` dari CEO / CTO.                        │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 3: SLIDING WINDOW & SEMANTIC COMPACTION                           │
│ • Mengambil maksimal N pesan percakapan terakhir (Default: 6 pesan).    │
│ • Percakapan lama yang melampaui N dirangkum menjadi 1 paragraf         │
│   "Executive State Summary" oleh CoS/CTO.                              │
└────────────────────────────────────────────────────────────────────────┘
```

#### 4.4.4 Guardrails Token & Memory Retention
1. **Hard Token Budget:** Alokasi riwayat memori percakapan dalam satu kali pemanggilan LLM dibatasi maksimal **4.000 token**, menyisakan ruang lapang bagi model untuk menghasilkan kode panjang (*output generation*).
2. **Context Compaction Trigger:** Apabila riwayat pesan dalam satu tahap melebihi 20 entri, sistem secara otomatis menjalankan *summarization job* di latar belakang untuk memadatkan riwayat menjadi poin-poin keputusan inti (*Decisions Log*), sehingga ukuran basis data tetap ringan dan pencarian tetap instan.

---

## 5. FITUR PRODUK & SPESIFIKASI MODUL (THE 4-STAGE LIFECYCLE)

```
[ IDE MENTAH DARI FOUNDER ]
            │
            ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 1: THE EXECUTIVE SPARRING ROOM (Discovery & Feasibility)          │
│ • CoS: Analisis Pasar, Unit Economics, Monetisasi (Kredit vs Flat).    │
│ • CTO: Pemilihan Arketipe (1/2/3/4), Estimasi Biaya Token & Infra.     │
│ • Output: Validated Business Brief & System Architecture Blueprint.    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ================================▼================================
    STAGE-GATE 1: FOUNDER APPROVES BUSINESS CONCEPT (ACC IDE)
    =================================================================
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 2: RAPID WORKING MVP PROTOTYPING (Interactive Demo Build)         │
│ • PM & UI/UX: Rancang Lean PRD & Kunci OpenAPI 3.1 Spec (SSOT).        │
│ • Frontend: Bangun UI Interaktif dengan Mock Adapter Service.          │
│ • DevSecOps: Mount kode ke Pre-Warmed Container -> Live Webview URL.   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ================================▼================================
    STAGE-GATE 2: CEO DEMO DAY (LIVE INTERACTIVE WEBVIEW PREVIEW)
    Founder menguji coba klik langsung di browser sandbox.
    [Pilihan: 1. GO TO PRODUCTION  |  2. REVISE PROTOTYPE  |  3. KILL]
    =================================================================
                                    │ (Pilihan 1: GO TO PRODUCTION)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 3: INDUSTRIALIZATION & PRODUCTION HARDENING                       │
│ • Backend: Implementasi API nyata (SQLAlchemy, Alembic, Payment Webhook│
│ • Frontend: Ubah Adapter dari Mock ke Real API Client (UI tidak disentuh│
│ • QA Specialist: Pytest (Unit/Integration), Semgrep (OWASP), Evals.   │
│ • Legal Agent: Generate /terms, /privacy, /refund, AI Disclaimers.     │
│ • DevSecOps: Build Production Container Image & Readiness Probes.      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ================================▼================================
    STAGE-GATE 3: PRE-LAUNCH CREDENTIAL & SANITY CHECK
    Founder memasukkan Kunci API Produksi via Encrypted Secret Vault.
    =================================================================
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ FASE 4: LIVE VENTURE OPERATIONS & POST-LAUNCH OBSERVABILITY            │
│ • DevSecOps memicu Deployment ke Cloud via PaaS API (Coolify/Railway). │
│ • Telemetry Collector: Pengunjung unik, retensi, error logs (Sentry).  │
│ • Real-Time P&L Engine: Gross Revenue - (LLM API Cost + Server Cost).  │
│ • Continuous Feedback Widget: Rekomendasi iterasi otomatis dari CoS.   │
└───────────────────────────────────┬────────────────────────────────────┘
```

---

## 6. DATA CONTRACTS & STATE SCHEMAS (SSOT)

Semua komunikasi antar-agen wajib tervalidasi menggunakan model Pydantic berikut:

### 6.1 State Mesin Orkestrasi (`VentureState`)
```python
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class VentureState(BaseModel):
    project_id: str
    project_name: str
    stage: str = Field(default="SPARRING_ROOM")  # FASE 1 s/d FASE 4
    founder_input: str
    selected_archetype: int = 1
    
    # Artefak Hasil Kerja Agen (Tervalidasi Skema)
    business_brief: Optional[Dict[str, Any]] = None
    system_architecture: Optional[Dict[str, Any]] = None
    prd_spec: Optional[Dict[str, Any]] = None
    openapi_spec: Optional[Dict[str, Any]] = None
    ui_spec: Optional[Dict[str, Any]] = None
    quality_scorecard: Optional[Dict[str, Any]] = None
    
    # Audit & Observability
    token_usage: Dict[str, float] = Field(default_factory=dict)
    event_logs: List[str] = Field(default_factory=list)
```

### 6.2 Kontrak Kelayakan Bisnis (`BusinessBriefSchema`)
```python
class BusinessBriefSchema(BaseModel):
    problem_statement: str
    proposed_solution: str
    target_audience: str
    monetization_model: str  # e.g., "flat_monthly", "usage_credits"
    pricing_tiers: List[Dict[str, Any]]
    projected_margin_percentage: float
    market_feasibility_score: int = Field(ge=1, le=100)
    risks_and_mitigations: List[str]
```

### 6.3 Kontrak Arsitektur Sistem (`SystemArchitectureSchema`)
```python
class SystemArchitectureSchema(BaseModel):
    archetype_id: int = Field(ge=1, le=4)
    frontend_framework: str = "Next.js 14 App Router"
    backend_framework: str = "FastAPI Python"
    database: str = "PostgreSQL"
    estimated_inference_cost_per_user: float
    circuit_breaker_limits: Dict[str, Any] = {
        "max_iterations": 5,
        "timeout_seconds": 90
    }
```

### 6.4 Kontrak Fitur Produk (`PRDContractSchema`)
```python
class UserStory(BaseModel):
    role: str
    action: str
    benefit: str
    acceptance_criteria: List[str]

class PRDContractSchema(BaseModel):
    product_name: str
    tagline: str
    core_happy_path_steps: List[str] = Field(min_length=3, max_length=5)
    in_scope_mvp_features: List[UserStory]
    out_of_scope_features: List[str]
```

---

## 7. ZERO-REGRESSION ADAPTER PATTERN SPECIFICATION

Untuk menjamin antarmuka hasil Fase 2 tidak rusak saat diimplementasikan ke Fase 3, agen frontend diwajibkan menulis kode dengan pola *Service Adapter*:

```typescript
// frontend/src/services/apiClient.ts
export interface ProductApiContract {
  authenticateUser(credentials: any): Promise<any>;
  fetchCoreData(): Promise<any>;
  processTransaction(payload: any): Promise<any>;
}

// 1. Digunakan pada FASE 2 (Mock Demo)
export class MockServiceAdapter implements ProductApiContract {
  async authenticateUser(credentials: any) {
    return { status: "success", token: "mock-jwt-token-preview", user: { name: "Demo Founder" } };
  }
  async fetchCoreData() {
    return { items: [{ id: 1, title: "Mock Synthetic Data Item", metric: 98.4 }] };
  }
  async processTransaction(payload: any) {
    return { status: "paid", transactionId: "mock-tx-12345" };
  }
}

// 2. Digunakan pada FASE 3 (Production Engine)
export class HttpServiceAdapter implements ProductApiContract {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL;
  async authenticateUser(credentials: any) {
    const res = await fetch(`${this.baseUrl}/auth/login`, { method: "POST", body: JSON.stringify(credentials) });
    return res.json();
  }
  async fetchCoreData() {
    const res = await fetch(`${this.baseUrl}/api/v1/core-data`);
    return res.json();
  }
  async processTransaction(payload: any) {
    const res = await fetch(`${this.baseUrl}/api/v1/checkout`, { method: "POST", body: JSON.stringify(payload) });
    return res.json();
  }
}

// Inisialisasi Dinamis Berdasarkan Tahap Lingkungan
export const api = process.env.NEXT_PUBLIC_APP_STAGE === "production" 
  ? new HttpServiceAdapter() 
  : new MockServiceAdapter();
```

---

## 8. SPESIFIKASI ANTARMUKA PENGGUNA (THE CEO COCKPIT DASHBOARD)

Antarmuka Dashboard dibangun menggunakan **Next.js + Tailwind CSS** dengan arsitektur *Split-Screen Workspace*:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              VENTURE INCUBATOR COCKPIT                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Project: DataPulse Analytics]   Status: STAGE-GATE 2 (DEMO DAY)   Tokens: $1.42       │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│           PANEL KIRI: LIVE DEMO           │           PANEL KANAN: CEO CONTROLS        │
│                                           │                                            │
│ ┌───────────────────────────────────────┐ │ 1. Executive Summary:                      │
│ │ [Webview: demo-datapulse.local.box]   │ │    • Archetype: Data Science SaaS          │
│ │                                       │ │    • Tech Stack: Next.js + FastAPI + Polars│
│ │ [ Upload CSV ] -> [ churn_data.csv ]  │ │    • Pricing: $39/mo (Usage-based)         │
│ │                                       │ │                                            │
│ │ > Running Churn Prediction Model...   │ │ 2. CEO Feedback & Prompt Tuning:           │
│ │ [ Interactive ECharts Generated ]     │ │    [ "Ubah warna grafik churn jadi merah" ]│
│ │                                       │ │                                            │
│ │                                       │ │ 3. Action Buttons:                         │
│ │                                       │ │    [ 🟢 APPROVE TO PRODUCTION ]            │
│ │                                       │ │    [ 🟡 ITERATE DEMO PROTOTYPE ]           │
│ │                                       │ │    [ 🔴 KILL PROJECT ]                     │
│ └───────────────────────────────────────┘ │                                            │
├───────────────────────────────────────────┴────────────────────────────────────────────┤
│ LIVE FEED: [CTO] OpenAPI Spec Locked | [QA] Evals Pass 98% | [Pre-Warmed Sandbox] Up   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Komponen & Modul Utama Cockpit
1. **The Executive Sparring Room (Fase 1):** Antarmuka obrolan 3 arah (Founder, CoS, CTO) dilengkapi *Feasibility Radar Chart* dan tombol *Approve Concept*.
2. **Interactive Sandbox Preview (Stage-Gate 2):** iFrame interaktif responsif (Desktop, Tablet, Mobile) yang mengeksekusi prototipe aplikasi secara langsung.
3. **The Industrialization Matrix & Secret Vault (Fase 3 & Gate 3):** Panel checklist kelulusan unit test, security scan OWASP, dan modal popup terenkripsi AES-256 untuk input API Key produksi.
4. **Portfolio Venture Hub & Dynamic P&L (Fase 4):** Kartu ringkasan seluruh proyek portofolio yang menampilkan metrik kunjungan, pengguna aktif, total pendapatan, biaya komputasi LLM, dan laba bersih riil (*Net Profit*).

---

## 9. NON-FUNCTIONAL REQUIREMENTS (NFR)

* **NFR-01 (Inference Latency & Streaming):** Seluruh komunikasi agen di Dashboard Cockpit wajib menggunakan Server-Sent Events (SSE) dengan latensi *Time to First Token (TTFT)* `< 800 ms`.
* **NFR-02 (Ephemeral Startup Time):** Pre-warmed container sandbox harus memuat kode baru dan menyajikan preview aktif di Webview dalam waktu `< 5 detik`.
* **NFR-03 (Security & Secret Isolation):** Kredensial produksi tidak boleh disimpan dalam plaintext di repository atau prompt log; wajib disimpan di SQLite lokal dengan enkripsi AES-256-GCM.
* **NFR-04 (Token Cost Circuit Breaker):** Jika sebuah agen mengalami loop perbaikan melebihi 5 kali iterasi atau durasi pemrosesan melebihi 90 detik, eksekusi wajib dihentikan otomatis (*force abort*).
* **NFR-05 (Memory Footprint):** Native state machine engine harus berbobot ringan dengan konsumsi memori runtime idle `< 150 MB RAM`.

---

## 10. ROADMAP IMPLEMENTASI PoC (VERTICAL SLICE - 6 MINGGU)

```
MINGGU 1-2: NATIVE CORE ENGINE & VERTICAL SLICE (ARKETIPE 1)
├── Bangun Native Python Async State Machine (< 250 baris kode).
├── Bangun Native BYOK Unified LLM Client (OpenAI/Anthropic/Gemini).
├── Implementasi interaksi Fase 1 (CEO + CoS + CTO Sparring Room).
├── Integrasi PM & UI Designer untuk menghasilkan OpenAPI Spec & UI Spec.
└── Setup Pre-Warmed Sandbox Pool (Docker + Reverse Proxy Dinamis).

MINGGU 3-4: COCKPIT DASHBOARD & STAGE-GATE 2 (DEMO DAY ENGINE)
├── Pembuatan antarmuka CEO Cockpit (Next.js + Tailwind + SSE Stream).
├── Pengujian iFrame Webview Preview untuk Arketipe 1 (SaaS CRUD).
├── Implementasi Adapter Pattern (Mock Service vs HTTP Client).
└── Uji coba validasi: Dari ide mentah hingga prototype interaktif dalam < 15 menit.

MINGGU 5-6: INDUSTRIAL HARDENING, REAL BRIDGES & EXPANSION
├── Integrasi Secret Vault (enkripsi AES-256) & Payment Webhook Handler.
├── Implementasi Automated QA Runner (Pytest + Semgrep + Evals).
├── Integrasi PaaS Deployment API (Coolify/Railway Engine).
├── Pemasangan Observability P&L Engine di Portfolio Hub.
└── Ekspansi Golden Path: Mengaktifkan Arketipe 2 (Agentic) & 3 (RAG Multimodal).
```

---

## 11. ACCEPTANCE CRITERIA CHECKLIST

Sistem dinyatakan lulus tahap PoC apabila memenuhi kriteria berikut:
- [ ] Mampu menjalankan alur Fase 1 (Sparring Room) dengan menghasilkan `BusinessBriefSchema` dan `SystemArchitectureSchema` yang valid.
- [ ] Berhasil menghasilkan prototipe interaktif fungsional di iFrame Webview dalam waktu `< 15 menit` sejak persetujuan Stage-Gate 1.
- [ ] Pengguna dapat mengganti model LLM agen secara instan via konfigurasi string BYOK tanpa terjadi crash atau perubahan kode inti.
- [ ] Berhasil menguji transisi dari Mock Adapter (Fase 2) ke HTTP Adapter nyata (Fase 3) tanpa merusak komponen antarmuka pengguna.
- [ ] Kunci API produksi terenkripsi aman di Secret Vault dan berhasil diinjeksi ke kontainer rilis di Stage-Gate 3.
- [ ] Dashboard Portfolio Hub mampu menampilkan kalkulasi laba bersih riil secara otomatis.

---

## 12. STRUKTUR DIREKTORI KANONIKAL PROYEK (CANONICAL DIRECTORY TREE)

Seluruh implementasi kode wajib mengikuti hierarki folder berikut agar struktur modul tetap terisolasi dan mudah di-maintain:

```
VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM/
├── backend/                              # FastAPI Backend & Orchestration Engine
│   ├── app/
│   │   ├── api/                          # REST Endpoints & SSE Streaming Routes
│   │   │   ├── v1/
│   │   │   │   ├── projects.py           # Project CRUD & Lifecycle Controls
│   │   │   │   ├── sparring.py           # Sparring Room Chat & SSE Stream
│   │   │   │   ├── gates.py              # Stage-Gate Approvals & Feedback Handlers
│   │   │   │   └── telemetry.py          # Portfolio P&L & Analytics Endpoints
│   │   │   └── deps.py                   # Dependency Injections
│   │   ├── core/                         # Konfigurasi & Utilitas Sistem
│   │   │   ├── config.py                 # Pydantic BaseSettings & Env Loader
│   │   │   ├── security.py               # AES-256 Vault Encryption/Decryption
│   │   │   └── logger.py                 # Structured JSON Logger
│   │   ├── engine/                       # Native Python Multi-Agent State Machine
│   │   │   ├── state.py                  # VentureState, Pydantic Schemas & SSOT Contracts
│   │   │   ├── state_machine.py          # Core FSM Engine (< 250 baris kode)
│   │   │   ├── memory.py                 # SQLite Blackboard Event Store & Context Builder
│   │   │   └── nodes/                    # 11 Fungsi Node Agen Terisolasi
│   │   │       ├── cos.py                # Chief of Staff Node
│   │   │       ├── cto.py                # CTO Architecture Node
│   │   │       ├── pm.py                 # Product Manager Lean PRD Node
│   │   │       ├── ui_ux.py              # UI/UX Specification Node
│   │   │       ├── frontend.py           # Next.js Code Generator Node
│   │   │       ├── backend.py            # FastAPI & Database Generator Node
│   │   │       ├── ai_specialist.py      # RAG / Agentic / Data Science Pipeline Node
│   │   │       ├── qa.py                 # Pytest, Semgrep & AI Evals Node
│   │   │       ├── legal.py              # ToS, Privacy, Disclaimer Generator Node
│   │   │       └── devsecops.py          # Docker Packaging & PaaS Deployer Node
│   │   ├── gateway/                      # Native BYOK LLM Multi-Provider Client
│   │   │   ├── client.py                 # Unified UnifiedLLMClient Interface
│   │   │   └── adapters/                 # HTTP Async Adapters (httpx)
│   │   │       ├── openai_compatible.py  # DeepSeek, Groq, Mistral, Ollama Local
│   │   │       ├── anthropic_adapter.py  # Claude 3.5 Sonnet / Haiku Native
│   │   │       └── gemini_adapter.py     # Gemini 2.5 Flash / Pro Native
│   │   ├── sandbox/                      # Pre-Warmed Ephemeral Runner Manager
│   │   │   ├── runner.py                 # Docker Volume Mount & Subprocess Manager
│   │   │   └── proxy.py                  # Caddy/Traefik Dynamic Routing Controller
│   │   └── db/                           # Database Persistence Engine
│   │       ├── session.py                # SQLite Async Engine
│   │       └── models.py                 # SQLAlchemy Table Definitions
│   ├── prompts/                          # Registry System Prompts per Role
│   │   ├── cos_prompt.md
│   │   ├── cto_prompt.md
│   │   ├── pm_prompt.md
│   │   └── ... (prompts untuk 11 agen)
│   ├── data/                             # SQLite Storage Files (git-ignored)
│   │   └── venture_memory.db             # Blackboard Event Log & Checkpoints
│   ├── requirements.txt                  # Python Minimal Dependencies
│   └── main.py                           # Entrypoint Server FastAPI
│
├── frontend/                             # The CEO Cockpit Dashboard (Next.js 14)
│   ├── src/
│   │   ├── app/                          # Next.js App Router Pages
│   │   │   ├── layout.tsx                # Base Layout with Navigation Sidebar
│   │   │   ├── page.tsx                  # Portfolio Venture Incubator Hub (Fase 4)
│   │   │   ├── sparring/[id]/page.tsx    # Executive Sparring Room (Fase 1)
│   │   │   ├── preview/[id]/page.tsx     # Split-Screen Live Webview Preview (Fase 2)
│   │   │   └── industrialize/[id]/page.tsx # Industrialization Matrix & Vault (Fase 3)
│   │   ├── components/                   # UI Modules
│   │   │   ├── sparring/                 # Sparring Chat Feed & Radar Charts
│   │   │   ├── preview/                  # Responsive iFrame Webview & Feedback Panel
│   │   │   ├── vault/                    # Encrypted Secret Vault Modal Form
│   │   │   ├── hub/                      # Dynamic P&L Cards & Project Grid
│   │   │   └── ui/                       # Reusable UI Primitives (Buttons, Badges)
│   │   ├── hooks/                        # Custom React Hooks
│   │   │   ├── useSSEStream.ts           # Server-Sent Events Listener
│   │   │   └── useProjectState.ts        # Zustand Project State Store
│   │   └── lib/                          # API Client & Utility Functions
│   ├── package.json                      # Next.js, Tailwind, Lucide, Zustand
│   └── tailwind.config.ts
│
├── sandboxes/                            # Pre-Warmed Docker Base Images
│   ├── base-frontend/                    # Dockerfile & pre-bundled node_modules
│   ├── base-backend/                     # Dockerfile & pre-bundled python packages
│   └── caddy/                            # Dynamic Local Reverse Proxy Configuration
│
├── projects_output/                      # Hasil Kode Proyek Startup yang Dihasilkan Agen
│   └── [project_id]/
│       ├── contracts/                    # OpenAPI Spec & Lean PRD JSON
│       ├── frontend/                     # Next.js Modular App
│       ├── backend/                      # FastAPI Modular Service
│       └── docker-compose.yml            # Deployment Bundle
│
├── .env.example                          # Template Konfigurasi Lingkungan Lengkap
├── proposal.md                           # Proposal Arsitektur & Cetak Biru Final
└── PRD.md                                # Dokumen Spesifikasi Produk & Context Anchor
```

---

## 13. TABEL TRANSISI FINITE STATE MACHINE (FSM DETAILED MATRIX)

Untuk mencegah kebuntuan eksekusi (*deadlock*) pada modul Native Python Engine, seluruh status, nama node, dan kondisi transisi dipetakan secara deterministik:

| State Asal (`current_state`) | Node yang Dieksekusi | Kondisi Transisi (Router Rule) | State Tujuan (`next_state`) |
| :--- | :--- | :--- | :--- |
| `INIT` | `start_project` | Project ID dibuat & valid | `SPARRING_ROOM` |
| `SPARRING_ROOM` | `node_sparring` (CoS + CTO) | Diskusi selesai & brief terbuat | `GATE_1_WAITING` |
| `GATE_1_WAITING` | `node_gate_1` (CEO Action) | Founder: APPROVE<br>Founder: REVISE<br>Founder: KILL | `PRD_AND_SPECS`<br>`SPARRING_ROOM`<br>`PROJECT_KILLED` |
| `PRD_AND_SPECS` | `node_spec_freeze` (PM + UI) | OpenAPI 3.1 & PRD tervalidasi | `MOCK_PROTOTYPING` |
| `MOCK_PROTOTYPING` | `node_generate_mock` (Frontend)| Mock code mounted ke Sandbox | `GATE_2_WAITING` |
| `GATE_2_WAITING` | `node_gate_2` (Demo Day) | Founder: GO_PRODUCTION<br>Founder: ITERATE<br>Founder: KILL | `PRODUCTION_HARDENING`<br>`MOCK_PROTOTYPING`<br>`PROJECT_KILLED` |
| `PRODUCTION_HARDENING`| `node_production_engine` | Backend, QA, Semgrep lolos | `GATE_3_WAITING` |
| `GATE_3_WAITING` | `node_gate_3` (Vault Injection) | API Keys injected & verified | `DEPLOY_LIVE` |
| `DEPLOY_LIVE` | `node_deploy_paas` (DevOps) | Health check return 200 OK | `LIVE_OBSERVABILITY` |
| `LIVE_OBSERVABILITY` | `node_telemetry_loop` | Berjalan kontinu di Hub | `LIVE_OBSERVABILITY` (Loop) |

---

## 14. SPESIFIKASI KONFIGURASI LINGKUNGAN (.env.example SPECIFICATION)

File `.env` mendefinisikan seluruh kunci BYOK, port sistem, dan pemilihan model untuk 11 agen:

```bash
# ==============================================================================
# VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM - ENVIRONMENT CONFIGURATION
# ==============================================================================

# Core System Settings
APP_ENV=development                       # development | production
APP_SECRET_KEY=change_this_to_a_random_32_byte_hex_key_for_jwt
VAULT_MASTER_KEY=change_this_to_a_32_byte_aes_key_for_secret_vault
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000
DATABASE_URL=sqlite+aiosqlite:///./data/venture_memory.db

# Universal BYOK API Keys & Base URLs
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=https://api.anthropic.com

GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

OLLAMA_BASE_URL=http://localhost:11434/v1

# Default Model Selection per Agent Role (Bebas diubah sewaktu-waktu)
MODEL_COS=deepseek-reasoner
PROVIDER_COS=deepseek

MODEL_CTO=claude-3-5-sonnet-20241022
PROVIDER_CTO=anthropic

MODEL_PM=gemini-2.5-flash
PROVIDER_PM=gemini

MODEL_UI_UX=claude-3-5-haiku-20241022
PROVIDER_UI_UX=anthropic

MODEL_FRONTEND=claude-3-5-sonnet-20241022
PROVIDER_FRONTEND=anthropic

MODEL_BACKEND=claude-3-5-sonnet-20241022
PROVIDER_BACKEND=anthropic

MODEL_AI_DATA=claude-3-5-sonnet-20241022
PROVIDER_AI_DATA=anthropic

MODEL_QA=deepseek-reasoner
PROVIDER_QA=deepseek

MODEL_LEGAL=deepseek-reasoner
PROVIDER_LEGAL=deepseek

MODEL_DEVSECOPS=qwen-2.5-coder-32b-instruct
PROVIDER_DEVSECOPS=openai_compatible

# Ephemeral Sandbox & Reverse Proxy Settings
SANDBOX_DOMAIN_SUFFIX=local.sandbox
CADDY_ADMIN_API=http://localhost:2019
DOCKER_BASE_FRONTEND_IMAGE=venture-frontend-base:latest
DOCKER_BASE_BACKEND_IMAGE=venture-backend-base:latest

# PaaS Deployment Bridge (Fase 4 Live Ops)
PAAS_PROVIDER=coolify                    # coolify | railway
PAAS_API_URL=
PAAS_API_TOKEN=
```

---

## 15. PROTOKOL SISTEM OPERASI WINDOWS & DOCKER SANDBOX MOUNTING

Mengingat lingkungan pengembangan host menggunakan **OS Windows**, modul `runner.py` wajib mematuhi standar penanganan path berikut untuk mencegah error saat injeksi kode ke kontainer Docker Linux:

1. **Normalisasi Windows Path ke POSIX Format:**  
   Path absolut Windows seperti `D:\my project\VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM\projects_output\[id]` wajib dikonversi menjadi format mount yang kompatibel dengan Docker Desktop WSL2 engine (misal: `/d/my project/...` atau menggunakan Docker Compose volume syntax standard).
2. **Port Collision Prevention:**  
   Modul Sandbox mengalokasikan port ephemeral secara dinamis menggunakan port scanner Python socket internal (mencari port bebas mulai dari `4000` s/d `4999`), lalu mendaftarkan port tersebut ke Reverse Proxy Caddy melalui REST API admin (`http://localhost:2019/load`).
3. **Hot-Reload Trigger:**  
   Kontainer base Next.js dan FastAPI dikonfigurasi dengan flag polling (`WATCHPACK_POLLING=true` untuk Next.js dan `--reload` untuk Uvicorn) agar perubahan file yang ditulis oleh agen di host Windows langsung memicu refresh instan pada Webview browser tanpa perlu me-restart kontainer.

