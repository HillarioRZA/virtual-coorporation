/**
 * Campus Architect No-Code Room & Building Creator Modal.
 * Allows Founder to dynamically expand the campus layout with custom rooms without writing code.
 */

import { useState } from "react";
import { Plus, X, Building, Layers, Sparkles } from "lucide-react";
import { CampusRoom, FurnitureEntity } from "./officeLayoutData";
import { OfficeCanvasRenderer } from "./OfficeCanvasRenderer";
import { createOfficeRoom } from "../../lib/officeApi";

interface CampusArchitectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRoomCreated?: (room: CampusRoom) => void;
}

export function CampusArchitectModal({ isOpen, onClose, onRoomCreated }: CampusArchitectModalProps) {
  const [name, setName] = useState("");
  const [buildingId, setBuildingId] = useState<CampusRoom["buildingId"]>("the_ring");
  const [floor, setFloor] = useState<CampusRoom["floor"]>(1);
  const [floorType, setFloorType] = useState<CampusRoom["floorType"]>("industrial_slate");
  const [deskCount, setDeskCount] = useState<number>(4);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);

    try {
      const roomId = `room_custom_${Date.now()}`;
      // Calculate dynamic offset so new room doesn't collide
      const newRoom: CampusRoom = {
        id: roomId,
        name: name.trim(),
        buildingId,
        floor,
        x: buildingId === "apollo" ? 60 : buildingId === "davinci" ? 500 : 920,
        y: 80 + Math.floor(Math.random() * 200),
        w: 360,
        h: 220,
        floorType,
        color: "#38bdf8",
      };

      const newFurniture: FurnitureEntity[] = [];
      for (let i = 0; i < deskCount; i++) {
        newFurniture.push({
          id: `desk_cust_${roomId}_${i}`,
          type: "desk",
          x: newRoom.x + 30 + (i % 3) * 90,
          y: newRoom.y + 60 + Math.floor(i / 3) * 65,
          w: 70,
          h: 45,
          buildingId,
          floor,
          label: `Workstation ${i + 1}`,
        });
      }

      OfficeCanvasRenderer.addCustomRoom(newRoom, newFurniture);
      await createOfficeRoom({ room: newRoom, furniture: newFurniture }).catch(() => {});
      if (onRoomCreated) onRoomCreated(newRoom);
      onClose();
    } catch {
      // Fallback local update
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-5 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Building className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-bold text-white tracking-wide">Campus Architect (No-Code Room)</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 text-xs">
          <div>
            <label className="text-slate-300 font-semibold block mb-1">Nama Ruangan</label>
            <input
              type="text"
              placeholder="Contoh: Digital Education Pod, AI Red-Teaming Lab"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-slate-300 font-semibold block mb-1">Gedung Kampus</label>
              <select
                value={buildingId}
                onChange={(e) => setBuildingId(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-2.5 py-2 text-white focus:outline-none"
              >
                <option value="apollo">🏛️ Apollo Engineering</option>
                <option value="davinci">🎨 Da Vinci Commons</option>
                <option value="olympus">🌟 Olympus Executive</option>
              </select>
            </div>

            <div>
              <label className="text-slate-300 font-semibold block mb-1">Lantai</label>
              <select
                value={floor}
                onChange={(e) => setFloor(Number(e.target.value) as any)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-2.5 py-2 text-white focus:outline-none"
              >
                <option value={1}>Lantai 1</option>
                <option value={2}>Lantai 2</option>
                <option value={3}>Lantai 3</option>
                <option value={4}>Lantai 4 (Apex Penthouse)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-slate-300 font-semibold block mb-1">Tipe Material Lantai</label>
            <select
              value={floorType}
              onChange={(e) => setFloorType(e.target.value as any)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-2.5 py-2 text-white focus:outline-none"
            >
              <option value="industrial_slate">Industrial Slate (Engineering)</option>
              <option value="navy_carpet">Navy Acoustic Carpet (Auditorium/Suites)</option>
              <option value="cherry_wood">Cherry Hardwood (Executive Penthouse)</option>
              <option value="terrazzo_tile">Terrazzo Tile (Canteen/Pantry)</option>
              <option value="datacenter_raised">Raised Floor Datacenter (SecOps)</option>
              <option value="arcade_neon">Arcade Neon Grid (Gaming)</option>
              <option value="music_studio">Music Acoustic Studio</option>
              <option value="zen_garden">Biophilic Zen Garden</option>
            </select>
          </div>

          <div>
            <label className="text-slate-300 font-semibold block mb-1">Jumlah Meja Workstation ({deskCount})</label>
            <input
              type="range"
              min={1}
              max={8}
              value={deskCount}
              onChange={(e) => setDeskCount(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800">
          <button onClick={onClose} className="px-3 py-1.5 rounded-xl text-slate-400 hover:text-white text-xs">
            Batal
          </button>
          <button
            onClick={handleCreate}
            disabled={loading || !name.trim()}
            className="flex items-center space-x-1.5 px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>{loading ? "Menyimpan..." : "Bangun Ruangan"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
