/**
 * Canonical Default Fallback Layout and Agents for Corporate Office Simulator.
 * Memastikan kanvas kantor tampil 100% lengkap pada resolusi 1376x768 Apple Park & Googleplex map.
 */

import { CampusLayout, AgentSpatialData } from "../../lib/types/office";

export const DEFAULT_CAMPUS_LAYOUT: CampusLayout = {
  campus_name: "Sovereign Silicon Campus",
  style: "apple_park_curved",
  dimensions: { width: 1376, height: 768 },
  wings: [
    {
      id: "wing_penthouse",
      name: "The Executive Penthouse",
      tier: "EXECUTIVE",
      theme_id: "luxury_marble",
      bounds: { x: 960, y: 40, width: 360, height: 240 },
      color: "#eab308",
      furniture: [
        { id: "desk_founder", type: "desk", x: 1120, y: 120, assigned_role: "role_founder", label: "Founder Desk" },
        { id: "desk_cos", type: "desk", x: 1240, y: 120, assigned_role: "role_cos", label: "CoS Desk" },
        { id: "desk_cfo", type: "desk", x: 1040, y: 180, assigned_role: "role_cfo", label: "CFO Desk" },
        { id: "boardroom_table", type: "table", x: 1140, y: 190, width: 140, height: 60, label: "Boardroom Table" },
        { id: "espresso_bar", type: "watercooler", x: 1280, y: 50, label: "Private Barista Bar" },
      ],
    },
    {
      id: "wing_management",
      name: "Product & Strategy Suites",
      tier: "LEAD_MANAGEMENT",
      theme_id: "scandinavian_wood",
      bounds: { x: 760, y: 310, width: 560, height: 240 },
      color: "#a855f7",
      furniture: [
        { id: "desk_cto", type: "desk", x: 860, y: 380, assigned_role: "role_cto", label: "CTO Suite" },
        { id: "desk_pm", type: "desk", x: 1020, y: 380, assigned_role: "role_pm", label: "PM Suite" },
        { id: "desk_growth", type: "desk", x: 1180, y: 380, assigned_role: "role_growth", label: "Growth Lead" },
        { id: "kpi_screen", type: "server_rack", x: 1020, y: 470, label: "Wall KPI Display" },
      ],
    },
    {
      id: "wing_engineering",
      name: "Silicon Collaborative Lab",
      tier: "WORKER_SPECIALIST",
      theme_id: "cyberpunk",
      bounds: { x: 60, y: 310, width: 660, height: 240 },
      color: "#06b6d4",
      furniture: [
        { id: "desk_fe", type: "desk", x: 140, y: 370, assigned_role: "role_fe", label: "Frontend Pod" },
        { id: "desk_be", type: "desk", x: 280, y: 370, assigned_role: "role_be", label: "Backend Pod" },
        { id: "desk_qa", type: "desk", x: 420, y: 370, assigned_role: "role_qa", label: "QA Testing Pod" },
        { id: "desk_devsecops", type: "desk", x: 560, y: 370, assigned_role: "role_devsecops", label: "DevSecOps Pod" },
        { id: "desk_ui_ux", type: "desk", x: 140, y: 460, assigned_role: "role_ui_ux", label: "UI/UX Station" },
        { id: "desk_copywriter", type: "desk", x: 280, y: 460, assigned_role: "role_copywriter", label: "Copywriting Desk" },
        { id: "desk_seo", type: "desk", x: 420, y: 460, assigned_role: "role_seo", label: "SEO Growth Desk" },
        { id: "server_cluster", type: "server_rack", x: 560, y: 460, label: "HPC Server Cluster" },
      ],
    },
    {
      id: "wing_courtyard",
      name: "The Ring Courtyard & Oasis",
      tier: "COMMONS",
      theme_id: "kawaii",
      bounds: { x: 60, y: 570, width: 840, height: 170 },
      color: "#10b981",
      furniture: [
        { id: "zen_fountain", type: "fountain", x: 880, y: 480, width: 80, height: 80, label: "Circular Water Fountain" },
        { id: "boba_counter", type: "watercooler", x: 600, y: 640, label: "Boba Barista Counter" },
        { id: "lounge_sofa", type: "sofa", x: 240, y: 640, width: 100, height: 40, label: "Plush Velvet Sofa" },
      ],
    },
  ],
};

export const DEFAULT_OFFICE_AGENTS: AgentSpatialData[] = [
  { role_id: "role_founder", name: "Founder / CEO", tier: "EXECUTIVE", x: 1140, y: 135, target_x: 1140, target_y: 135, activity_state: "IDLE", color: "#eab308", scratchpad: "Meninjau roadmap strategis perusahaan..." },
  { role_id: "role_cos", name: "Chief of Staff", tier: "EXECUTIVE", x: 1260, y: 135, target_x: 1260, target_y: 135, activity_state: "IDLE", color: "#eab308", scratchpad: "Menyelaraskan koordinasi antar-divisi..." },
  { role_id: "role_cfo", name: "Chief Financial Officer", tier: "EXECUTIVE", x: 1060, y: 195, target_x: 1060, target_y: 195, activity_state: "IDLE", color: "#eab308", scratchpad: "Mengaudit efisiensi token & burn rate..." },
  { role_id: "role_cto", name: "Chief Technology Officer", tier: "LEAD_MANAGEMENT", x: 880, y: 395, target_x: 880, target_y: 395, activity_state: "IDLE", color: "#a855f7", scratchpad: "Meninjau arsitektur mikro-layanan..." },
  { role_id: "role_pm", name: "Product Manager", tier: "LEAD_MANAGEMENT", x: 1040, y: 395, target_x: 1040, target_y: 395, activity_state: "IDLE", color: "#a855f7", scratchpad: "Menyusun PRD spesifikasi fitur..." },
  { role_id: "role_growth", name: "Growth Lead", tier: "LEAD_MANAGEMENT", x: 1200, y: 395, target_x: 1200, target_y: 395, activity_state: "IDLE", color: "#a855f7", scratchpad: "Menganalisis funnel konversi pengguna..." },
  { role_id: "role_fe", name: "Frontend Engineer", tier: "WORKER_SPECIALIST", x: 160, y: 385, target_x: 160, target_y: 385, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Menyiapkan komponen Next.js 14..." },
  { role_id: "role_be", name: "Backend Engineer", tier: "WORKER_SPECIALIST", x: 300, y: 385, target_x: 300, target_y: 385, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Menyiapkan endpoint REST FastAPI..." },
  { role_id: "role_qa", name: "QA & Security Auditor", tier: "WORKER_SPECIALIST", x: 440, y: 385, target_x: 440, target_y: 385, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Audit AST scanner OWASP & Pytest..." },
  { role_id: "role_devsecops", name: "DevSecOps Engineer", tier: "WORKER_SPECIALIST", x: 580, y: 385, target_x: 580, target_y: 385, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Isolasi Docker bridge network sandboxing..." },
  { role_id: "role_ui_ux", name: "UI/UX Designer", tier: "WORKER_SPECIALIST", x: 160, y: 475, target_x: 160, target_y: 475, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Mendesain kanvas liquid glass modern..." },
  { role_id: "role_copywriter", name: "Creative Copywriter", tier: "WORKER_SPECIALIST", x: 300, y: 475, target_x: 300, target_y: 475, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Merumuskan headline pitch startup..." },
  { role_id: "role_seo", name: "SEO Growth Hacker", tier: "WORKER_SPECIALIST", x: 440, y: 475, target_x: 440, target_y: 475, activity_state: "IDLE", color: "#06b6d4", scratchpad: "Riset kata kunci pasar bervolume tinggi..." },
];
