/**
 * Default Autonomous Agents for Global Oasis Live Command HQ.
 * 13 Specialized roles across Executive, Management, and Engineering divisions.
 */

import { AgentSpatialData } from "../../lib/types/office";

export const DEFAULT_OFFICE_AGENTS: AgentSpatialData[] = [
  { role_id: "role_founder", name: "Founder / CEO", tier: "EXECUTIVE", activity_state: "IDLE", color: "#eab308", scratchpad: "Meninjau roadmap strategis perusahaan..." },
  { role_id: "role_cos", name: "Chief of Staff", tier: "EXECUTIVE", activity_state: "IDLE", color: "#eab308", scratchpad: "Menyelaraskan koordinasi antar-divisi..." },
  { role_id: "role_cfo", name: "Chief Financial Officer", tier: "EXECUTIVE", activity_state: "IDLE", color: "#eab308", scratchpad: "Mengaudit efisiensi token & burn rate..." },
  { role_id: "role_cto", name: "Chief Technology Officer", tier: "LEAD_MANAGEMENT", activity_state: "IDLE", color: "#a855f7", scratchpad: "Meninjau arsitektur mikro-layanan..." },
  { role_id: "role_pm", name: "Product Manager", tier: "LEAD_MANAGEMENT", activity_state: "IDLE", color: "#a855f7", scratchpad: "Menyusun PRD spesifikasi fitur..." },
  { role_id: "role_growth", name: "Growth Lead", tier: "LEAD_MANAGEMENT", activity_state: "IDLE", color: "#a855f7", scratchpad: "Menganalisis funnel konversi pengguna..." },
  { role_id: "role_fe", name: "Frontend Engineer", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Menyiapkan antarmuka pengguna..." },
  { role_id: "role_be", name: "Backend Engineer", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Menyiapkan endpoint REST FastAPI..." },
  { role_id: "role_qa", name: "QA & Security Auditor", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Audit AST scanner OWASP & Pytest..." },
  { role_id: "role_devsecops", name: "DevSecOps Engineer", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Isolasi Docker sandboxing & deployment..." },
  { role_id: "role_ui_ux", name: "UI/UX Designer", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Mendesain kanvas liquid glass modern..." },
  { role_id: "role_copywriter", name: "Creative Copywriter", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Merumuskan headline pitch startup..." },
  { role_id: "role_seo", name: "SEO Growth Hacker", tier: "WORKER_SPECIALIST", activity_state: "IDLE", color: "#06b6d4", scratchpad: "Riset kata kunci pasar bervolume tinggi..." },
];
