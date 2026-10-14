/**
 * Canonical Multi-Building Tech Mega-Campus Layout Schema.
 * Defines rooms, 4 floors, modular expansion sectors, and furniture entities.
 */

export interface CampusRoom {
  id: string;
  name: string;
  buildingId: "the_ring" | "steve_jobs_theater" | "tantau_secops" | "caffe_macs" | "apollo" | "davinci" | "olympus";
  floor: 1 | 2 | 3 | 4;
  x: number;
  y: number;
  w: number;
  h: number;
  floorType:
    | "cherry_wood"
    | "navy_carpet"
    | "industrial_slate"
    | "terrazzo_tile"
    | "datacenter_raised"
    | "cyber_grid"
    | "zen_garden"
    | "arcade_neon"
    | "music_studio"
    | "blonde_oak"
    | "walnut_calacatta";
  color: string;
}

export interface FurnitureEntity {
  id: string;
  type:
    | "desk"
    | "meeting_table"
    | "podium"
    | "server_rack"
    | "water_cooler"
    | "arcade_machine"
    | "ping_pong"
    | "music_instruments"
    | "nap_pod"
    | "ramen_bar"
    | "koi_pond"
    | "elevator"
    | "hologram_console"
    | "hearth";
  x: number;
  y: number;
  w: number;
  h: number;
  buildingId: "the_ring" | "steve_jobs_theater" | "tantau_secops" | "caffe_macs" | "apollo" | "davinci" | "olympus";
  floor: 1 | 2 | 3 | 4;
  label?: string;
  assignedRole?: string;
}

export const CAMPUS_ROOMS: CampusRoom[] = [
  // --- THE GRAND RING (Fl 1: Silicon Lab, Caffe Macs Atrium & Future Engineering Wing) ---
  { id: "ring_lab", name: "Silicon Engineering Lab", buildingId: "the_ring", floor: 1, x: 50, y: 70, w: 420, h: 320, floorType: "industrial_slate", color: "#38bdf8" },
  { id: "ring_caffe", name: "Caffè Macs 4-Storey Great Atrium", buildingId: "the_ring", floor: 1, x: 50, y: 410, w: 420, h: 290, floorType: "terrazzo_tile", color: "#f59e0b" },
  { id: "ring_future_fl1", name: "Engineering Modular Expansion Wing", buildingId: "the_ring", floor: 1, x: 490, y: 70, w: 400, h: 630, floorType: "blonde_oak", color: "#94a3b8" },

  // --- THE GRAND RING (Fl 2: Product Strategy, UX & Growth Pods + Future Creative Wing) ---
  { id: "ring_product", name: "Product Design & UX Studio", buildingId: "the_ring", floor: 2, x: 50, y: 70, w: 420, h: 630, floorType: "blonde_oak", color: "#ec4899" },
  { id: "ring_future_fl2", name: "Creative Modular Expansion Wing", buildingId: "the_ring", floor: 2, x: 490, y: 70, w: 400, h: 630, floorType: "blonde_oak", color: "#94a3b8" },

  // --- THE GRAND RING (Fl 3: Strategic Leadership, CFO & Strategic Boardroom) ---
  { id: "ring_leadership", name: "Executive Leadership & Boardroom", buildingId: "the_ring", floor: 3, x: 50, y: 70, w: 420, h: 630, floorType: "cherry_wood", color: "#eab308" },
  { id: "ring_future_fl3", name: "Leadership Modular Expansion Wing", buildingId: "the_ring", floor: 3, x: 490, y: 70, w: 400, h: 630, floorType: "blonde_oak", color: "#94a3b8" },

  // --- THE GRAND RING (Fl 4: Founder's Apex Omni-Panoramic Penthouse Suite) ---
  { id: "ring_penthouse", name: "Founder's Apex Omni-Panoramic Sanctum", buildingId: "the_ring", floor: 4, x: 50, y: 70, w: 600, h: 450, floorType: "walnut_calacatta", color: "#fbbf24" },
  { id: "ring_sky_balcony", name: "Founder's Private Sky Observatory", buildingId: "the_ring", floor: 4, x: 670, y: 70, w: 220, h: 450, floorType: "terrazzo_tile", color: "#38bdf8" },

  // --- SATELLITE BUILDINGS ---
  { id: "theater_keynote", name: "Steve Jobs Theater Keynote Auditorium", buildingId: "steve_jobs_theater", floor: 1, x: 910, y: 70, w: 410, h: 630, floorType: "navy_carpet", color: "#6366f1" },
  { id: "tantau_secops", name: "Tantau SecOps & High-Security Datacenter", buildingId: "tantau_secops", floor: 1, x: 910, y: 70, w: 410, h: 630, floorType: "datacenter_raised", color: "#10b981" },
];

export const CAMPUS_FURNITURE: FurnitureEntity[] = [
  // Fl 1 Ring: Silicon Engineering Workstations
  { id: "desk_fe", type: "desk", x: 100, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 1, assignedRole: "role_fe", label: "Frontend Pod" },
  { id: "desk_be", type: "desk", x: 200, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 1, assignedRole: "role_be", label: "Backend Pod" },
  { id: "desk_qa", type: "desk", x: 300, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 1, assignedRole: "role_qa", label: "QA Security Pod" },
  { id: "desk_devsecops", type: "desk", x: 100, y: 220, w: 70, h: 45, buildingId: "the_ring", floor: 1, assignedRole: "role_devsecops", label: "DevSecOps Pod" },
  { id: "caffe_espresso_bar", type: "ramen_bar", x: 120, y: 450, w: 160, h: 60, buildingId: "the_ring", floor: 1, label: "Artisan Espresso & Boba Bar" },
  { id: "caffe_communal_table", type: "meeting_table", x: 140, y: 550, w: 140, h: 60, buildingId: "the_ring", floor: 1, label: "Arco Communal Table" },
  { id: "ring_elevator_1", type: "elevator", x: 410, y: 200, w: 45, h: 60, buildingId: "the_ring", floor: 1, label: "Glass Elevator Fl 1" },

  // Fl 2 Ring: Product Strategy & Growth Pods
  { id: "desk_pm", type: "desk", x: 100, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 2, assignedRole: "role_pm", label: "Product Strategy Office" },
  { id: "desk_uiux", type: "desk", x: 200, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 2, assignedRole: "role_uiux", label: "UI/UX Design Studio" },
  { id: "desk_growth", type: "desk", x: 300, y: 130, w: 70, h: 45, buildingId: "the_ring", floor: 2, assignedRole: "role_growth", label: "Growth Hacker Pod" },
  { id: "desk_copywriter", type: "desk", x: 100, y: 220, w: 70, h: 45, buildingId: "the_ring", floor: 2, assignedRole: "role_copywriter", label: "Brand Copywriter Pod" },
  { id: "desk_seo", type: "desk", x: 200, y: 220, w: 70, h: 45, buildingId: "the_ring", floor: 2, assignedRole: "role_seo", label: "SEO Intelligence Pod" },
  { id: "ring_elevator_2", type: "elevator", x: 410, y: 200, w: 45, h: 60, buildingId: "the_ring", floor: 2, label: "Glass Elevator Fl 2" },

  // Fl 3 Ring: Strategic Leadership & Boardroom
  { id: "desk_cto", type: "desk", x: 100, y: 130, w: 80, h: 45, buildingId: "the_ring", floor: 3, assignedRole: "role_cto", label: "CTO Architecture Bridge" },
  { id: "desk_cfo", type: "desk", x: 200, y: 130, w: 80, h: 45, buildingId: "the_ring", floor: 3, assignedRole: "role_cfo", label: "CFO Treasury Office" },
  { id: "desk_cos", type: "desk", x: 300, y: 130, w: 80, h: 45, buildingId: "the_ring", floor: 3, assignedRole: "role_cos", label: "Chief of Staff Command" },
  { id: "boardroom_oval_table", type: "meeting_table", x: 150, y: 260, w: 180, h: 80, buildingId: "the_ring", floor: 3, label: "Strategic Oval Boardroom" },
  { id: "nap_pod_ring", type: "nap_pod", x: 100, y: 460, w: 65, h: 40, buildingId: "the_ring", floor: 3, label: "MetroNap Capsule" },
  { id: "music_synth_ring", type: "music_instruments", x: 220, y: 460, w: 110, h: 60, buildingId: "the_ring", floor: 3, label: "Acoustic Music Studio" },
  { id: "ring_elevator_3", type: "elevator", x: 410, y: 200, w: 45, h: 60, buildingId: "the_ring", floor: 3, label: "Glass Elevator Fl 3" },

  // Fl 4 Ring: Founder's Apex Omni-Panoramic Penthouse
  { id: "desk_founder_apex", type: "desk", x: 180, y: 160, w: 120, h: 60, buildingId: "the_ring", floor: 4, assignedRole: "role_founder", label: "Founder's Command Island" },
  { id: "founder_hologram", type: "hologram_console", x: 180, y: 110, w: 90, h: 30, buildingId: "the_ring", floor: 4, label: "Tri-Holo Strategic Feed" },
  { id: "founder_lounge_hearth", type: "hearth", x: 350, y: 160, w: 100, h: 50, buildingId: "the_ring", floor: 4, label: "Zen Digital Flame Hearth" },
  { id: "founder_lounge_sofa", type: "meeting_table", x: 350, y: 260, w: 140, h: 70, buildingId: "the_ring", floor: 4, label: "Curved Bouclé Lounge" },
  { id: "ring_elevator_4", type: "elevator", x: 410, y: 200, w: 45, h: 60, buildingId: "the_ring", floor: 4, label: "Executive Private Lift Fl 4" },

  // Satellite Buildings
  { id: "podium_keynote", type: "podium", x: 235, y: 440, w: 50, h: 35, buildingId: "steve_jobs_theater", floor: 1, label: "Steve Jobs Theater Podium" },
  { id: "server_rack_mesh", type: "server_rack", x: 100, y: 140, w: 80, h: 120, buildingId: "tantau_secops", floor: 1, label: "HPC SecOps Datacenter" },
];
