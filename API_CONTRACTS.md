# API & EVENT STREAMING CONTRACTS SPECIFICATION
## VIRTUAL TECH STARTUP MULTI-AGENT SYSTEM & UNIVERSAL VENTURE INCUBATOR HUB
**Spesifikasi Antarmuka RESTful API & Server-Sent Events (SSE)**  
*Versi: 1.0 (Strict Contract / Single Source of Truth)*  
*Base URL: `http://127.0.0.1:8000/api/v1`*  
*Target: Komunikasi antara FastAPI Orchestrator & Next.js Cockpit Dashboard*

---

## 1. STANDAR PROTOKOL & STATUS CODES

* **REST API Content-Type:** `application/json`
* **Real-time Event Streaming:** `text/event-stream` (Server-Sent Events / SSE)
* **Standard Response Codes:**
  * `200 OK`: Permintaan berhasil dieksekusi.
  * `201 Created`: Proyek atau resource baru berhasil dibuat.
  * `400 Bad Request`: Payload JSON tidak lolos validasi skema Pydantic.
  * `404 Not Found`: Proyek atau resource ID tidak ditemukan.
  * `422 Unprocessable Entity`: Validasi tipe data gagal.
  * `500 Internal Server Error`: Kesalahan runtime / circuit breaker dipicu.

---

## 2. DAFTAR ENDPOINT REST API

### 2.1 Manajemen Proyek (Venture Lifecycle)

#### 1. Inisialisasi Proyek Baru
* **Endpoint:** `POST /projects`
* **Deskripsi:** Mendaftarkan ide bisnis baru dan menginisialisasi State Machine ke tahap `SPARRING_ROOM`.
* **Request Body:**
```json
{
  "name": "DataPulse Analytics",
  "founder_idea": "Platform analitik prediktif untuk memprediksi churn pelanggan SaaS menggunakan file CSV.",
  "archetype_id": 4
}
```
* **Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj_a8f9c1b2",
    "name": "DataPulse Analytics",
    "stage": "SPARRING_ROOM",
    "created_at": "2026-09-30T01:50:00Z"
  }
}
```

#### 2. Dapatkan Daftar Seluruh Proyek (Portfolio Hub)
* **Endpoint:** `GET /projects`
* **Deskripsi:** Mengambil semua proyek untuk ditampilkan pada kartu portofolio di Dashboard.
* **Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "project_id": "proj_a8f9c1b2",
      "name": "DataPulse Analytics",
      "stage": "GATE_2_WAITING",
      "archetype_id": 4,
      "tokens_cost": 1.42,
      "gross_revenue": 0.0,
      "net_profit": -1.42,
      "status": "ACTIVE"
    }
  ]
}
```

#### 3. Dapatkan Detail & State Proyek Tertentu
* **Endpoint:** `GET /projects/{project_id}`
* **Deskripsi:** Mengambil snapshot state lengkap, artefak yang terkunci, dan riwayat langkah.
* **Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj_a8f9c1b2",
    "name": "DataPulse Analytics",
    "stage": "GATE_2_WAITING",
    "business_brief": {
      "monetization_model": "usage_credits",
      "market_feasibility_score": 92
    },
    "openapi_spec": { ... },
    "preview_url": "http://demo-proj_a8f9c1b2.local.sandbox"
  }
}
```

---

### 2.2 The Executive Sparring Room (Fase 1)

#### 4. Kirim Pesan / Diskusi ke Sparring Room
* **Endpoint:** `POST /projects/{project_id}/sparring/chat`
* **Deskripsi:** Mengirim instruksi atau tanggapan dari Founder ke CoS dan CTO.
* **Request Body:**
```json
{
  "message": "Saya ingin model monetisasinya menggunakan skema kuota kredit per-prediksi, bukan langganan flat bulanan.",
  "target_agent": "COS" // Opsional: "COS", "CTO", atau null (Broadcast)
}
```
* **Response (200 OK):**
```json
{
  "status": "queued",
  "message": "Instruksi diterima, agen sedang memproses feedback."
}
```

---

### 2.3 Stage-Gates & Pengambilan Keputusan CEO

#### 5. Eksekusi Keputusan Gerbang (Gate Approvals)
* **Endpoint:** `POST /projects/{project_id}/gates/{gate_id}/decision`
* **Parameter Path:** `gate_id` $\in$ `["gate_1", "gate_2", "gate_3"]`
* **Deskripsi:** Founder memutuskan kelanjutan proyek di setiap gerbang krusial.
* **Request Body:**
```json
{
  "action": "APPROVE", // "APPROVE" | "REVISE" | "KILL"
  "feedback": "Desain UI mock sudah sangat bagus, lanjutkan ke koding produksi backend."
}
```
* **Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "project_id": "proj_a8f9c1b2",
    "previous_stage": "GATE_2_WAITING",
    "current_stage": "PRODUCTION_HARDENING",
    "message": "Gerbang disetujui. Memulai industrialisasi produksi."
  }
}
```

---

### 2.4 Ephemeral Sandbox & Secret Vault

#### 6. Cek Status Preview Sandbox (Stage-Gate 2)
* **Endpoint:** `GET /projects/{project_id}/preview/status`
* **Deskripsi:** Memeriksa kesiapan kontainer Docker dan URL preview lokal.
* **Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "is_running": true,
    "port": 4015,
    "preview_url": "http://demo-proj_a8f9c1b2.local.sandbox",
    "uptime_seconds": 124
  }
}
```

#### 7. Injeksi Kunci API Produksi ke Secret Vault (Stage-Gate 3)
* **Endpoint:** `POST /projects/{project_id}/vault/secrets`
* **Deskripsi:** Menyimpan kredensial produksi terenkripsi (AES-256) sebelum deployment live.
* **Request Body:**
```json
{
  "secrets": {
    "STRIPE_SECRET_KEY": "sk_live_51Mxxxxxxxxxxxxxxxxxxx",
    "MIDTRANS_SERVER_KEY": "Mid-server-xxxxxxxxxxxxxxxxx",
    "PROD_DATABASE_URL": "postgresql://user:pass@db.railway.internal:5432/datapulse"
  }
}
```
* **Response (200 OK):**
```json
{
  "status": "success",
  "message": "3 kredensial berhasil dienkripsi dan disimpan di Secret Vault."
}
```

---

## 3. SPESIFIKASI REAL-TIME SERVER-SENT EVENTS (SSE)

### Endpoint SSE: `GET /api/v1/projects/{project_id}/stream`
Frontend Next.js membuka koneksi HTTP persistens dengan header `Accept: text/event-stream`. Backend secara otomatis memancarkan event berikut:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DAFTAR EVENT SSE RESMI                          │
├───────────────────┬────────────────────────────────────────────────────┤
│ Tipe Event        │ Kegunaan & Payload                                 │
├───────────────────┼────────────────────────────────────────────────────┤
│ `sparring_token`  │ Streaming chunk token obrolan dari CoS / CTO       │
│ `agent_status`    │ Status aktivitas agen (e.g. "CTO is thinking...")  │
│ `state_change`    │ Transisi state mesin (e.g. Masuk ke GATE_2_WAITING)│
│ `preview_ready`   │ Notifikasi saat Sandbox Webview siap di-load       │
│ `eval_scorecard`  │ Hasil tes akurasi AI & pemindaian OWASP Semgrep    │
│ `error`           │ Pelaporan error atau peringatan Circuit Breaker    │
│ `done`            │ Penanda selesainya rangkaian langkah saat ini      │
└───────────────────┴────────────────────────────────────────────────────┘
```

#### Contoh Payload Event SSE:

1. **Event: `sparring_token`**
```
event: sparring_token
data: {"sender_role": "COS", "token": "Berdasarkan ", "is_first": false}

event: sparring_token
data: {"sender_role": "COS", "token": "analisis pasar...", "is_first": false}
```

2. **Event: `state_change`**
```
event: state_change
data: {"from_stage": "SPARRING_ROOM", "to_stage": "GATE_1_WAITING", "timestamp": "2026-09-30T01:52:10Z"}
```

3. **Event: `preview_ready`**
```
event: preview_ready
data: {"url": "http://demo-proj_a8f9c1b2.local.sandbox", "port": 4015}
```

4. **Event: `eval_scorecard`**
```
event: eval_scorecard
data: {"hallucination_rate": 0.01, "owasp_vulnerabilities": 0, "status": "PASSED"}
```

---

## 4. TYPESCRIPT INTERFACES UNTUK FRONTEND NEXT.JS

Salin definisi tipe ini langsung ke `frontend/src/lib/types/api.ts`:

```typescript
export type StageName = 
  | 'SPARRING_ROOM'
  | 'GATE_1_WAITING'
  | 'PRD_AND_SPECS'
  | 'MOCK_PROTOTYPING'
  | 'GATE_2_WAITING'
  | 'PRODUCTION_HARDENING'
  | 'GATE_3_WAITING'
  | 'DEPLOY_LIVE'
  | 'LIVE_OBSERVABILITY'
  | 'PROJECT_KILLED';

export type GateDecision = 'APPROVE' | 'REVISE' | 'KILL';

export interface ProjectSummary {
  project_id: string;
  name: string;
  stage: StageName;
  archetype_id: number;
  tokens_cost: number;
  gross_revenue: number;
  net_profit: number;
  status: 'ACTIVE' | 'ARCHIVED' | 'KILLED';
}

export interface GateDecisionPayload {
  action: GateDecision;
  feedback?: string;
}

export interface SSETokenPayload {
  sender_role: string;
  token: string;
  is_first?: boolean;
}

export interface SSEStateChangePayload {
  from_stage: StageName;
  to_stage: StageName;
  timestamp: string;
}

export interface SSEPreviewReadyPayload {
  url: string;
  port: number;
}
```
