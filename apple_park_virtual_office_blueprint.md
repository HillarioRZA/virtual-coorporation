# Master Blueprint: Apple Park Themed Three.JS Zero-Asset Virtual Office (v5.2)

**Proyek:** Virtual Tech Startup Multi-Agent System & Universal Venture Incubator Hub  
**Tema Spasial:** *Apple Park Cupertino Biophilic Minimalist Megastructure*  
**Engine Grafis:** *Three.js WebGL (60–120 FPS) | 100% Procedural Zero-Asset (Tanpa File .gltf/.glb)*  
**Target Visual & Feel:** *~80% Realistic Game-Look (Minecraft+RT Shaders / Cyberpunk / GTA V RT Mod Standard)*  
**Skala Dunia:** *Mega-Campus 640m Diameter | Full 360° Circular Torus Ring (Diameter 272m, 4 Lantai Penuh)*  
**Navigasi:** *Dual-Mode: Tactical Orbit Drone Cam & AAA-Grade First-Person Founder Walk (WASD + Pointer Lock)*  
**Siklus Waktu:** *Dynamic 24-Hour Day-to-Night Timeline (Pagi, Siang, Sore, Malam)*  
**Kepatuhan Arsitektur:** *Strict SRP (Single Responsibility Principle) & Batas ≤ 150–200 Baris per File*  

---

## 1. Visi Arsitektur Skala Penuh (True Cupertino Masterplan)

Berdasarkan keputusan strategis Founder:
1. **The Grand Ring (2x Lipat Skala Lebih Masif):**  
   Diameter luar The Grand Ring digandakan menjadi **272 meter** ($R_{\text{in}} = 98\text{m}$, $R_{\text{out}} = 136\text{m}$, lebar cincin 38 meter) dengan 4 lantai penuh (tinggi 16m). Skala raksasa ini memberikan proporsi ramping dan anggun (*sleek spaceship torus*) yang melingkari taman sentral (*Central Meadow*) selebar hampir 200 meter.
2. **Gedung Satelit di Luar Cincin (5x Lebih Besar & Dibuat Sangat Jauh):**  
   Mengikuti cetak biru otentik Cupertino City Hall:
   * **Steve Jobs Theater (5x Lebih Besar):** Diposisikan sangat jauh di atas perbukitan Selatan/Tenggara pada koordinat $(X = 40\text{m}, Z = 230\text{m})$. Memiliki silinder kaca struktural berdiameter 50 meter ($R = 25\text{m}$), atap piringan serat karbon berdiameter 68 meter ($R = 34\text{m}$), dan auditorium bawah tanah raksasa ($R = 38\text{m}$) dengan panggung keynote dan layar Micro-LED lengkung.
   * **Tantau SecOps & Datacenter (5x Lebih Besar):** Diposisikan sangat jauh di sepanjang Tantau Avenue Utara pada koordinat $(X = 60\text{m}, Z = -230\text{m})$. Kompleks megah 2 lantai berdimensi $52\text{m} \times 36\text{m}$ dengan 8 kabinet server monolith masif, airlock titanium, dan piringan komunikasi satelit.
3. **Founder’s Apex Omni-Panoramic Penthouse (Lantai 4 Paling Atas):**  
   Terletak di elevasi puncak ($Y = 12.0\text{m} - 16.0\text{m}$) dengan pemandangan 360°/180° menghadap taman sentral di bawahnya, dirancang ultra-mewah, cozy, futuristik, dan sangat luas dengan meja komando titanium, tri-holographic displays, lounge bouclé, perapian zen, dan private sky balcony.
4. **Caffè Macs 4-Storey Great Atrium:**  
   Menyatu langsung di busur dalam cincin barat ($R_{\text{in}} = 98\text{m}$) dengan gerbang kaca geser 440.000 lb setinggi 15.2 meter dan teras payung santai di tepi kebun.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               MASTERPLAN MEGA-KAMPUS APPLE PARK (BENTANGAN TOTAL 640 METER)            │
│                                                                                        │
│                                      [UTARA]                                           │
│                 Tantau SecOps & High-Security Datacenter 5X                            │
│                       (X = 60m, Z = -230m | 52m × 36m)                                 │
│                                         ▲                                              │
│                                         │ (Avenue Promenade)                           │
│               ┌────────────────────────────────────────────────────────┐               │
│               │         THE GRAND RING (2X ENLARGED SCALE 360°)        │               │
│               │            Outer R = 136m  |  Inner R = 98m            │               │
│               │                                                        │               │
│   [BARAT]     │   ┌────────────────────────────────────────────────┐   │    [TIMUR]    │
│  Caffè Macs   │   │         THE CENTRAL MEADOW (DIAMETER 196m)     │   │ Engineering   │
│ 4-Storey Great│   │    • Reflection Pond (R=22m) di Center (0,0,0) │   │  Silicon Lab  │
│ Atrium Glass  │   │    • Sacred Ancient Grand Sakura di (32, 16)   │   │  & Future Pods│
│ Sliding Doors │   │    • 120+ Sakura Groves & Benches              │   │               │
│               │   └────────────────────────────────────────────────┘   │               │
│               │                                                        │               │
│               │         LANTAI 4: FOUNDER'S APEX PENTHOUSE             │               │
│               │     (Panoramic Vista, Cozy Luxury, Futuristic Hub)     │               │
│               └────────────────────────────────────────────────────────┘               │
│                                         │                                              │
│                                         ▼ (Avenue Promenade)                           │
│                 Steve Jobs Theater 5X & Subterranean Keynote                           │
│                  (X = 40m, Z = 230m | Silinder R=25m, Atap R=34m)                      │
│                                     [SELATAN]                                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Peta Zona Arsitektur & Koordinat Spasial

| Zona Gedung | Tipologi Arsitektur | Dimensi / Radius | Ketinggian | Fungsi Utama & Penempatan Agen |
| :--- | :--- | :--- | :--- | :--- |
| **The Grand Ring** *(Spaceship 360°)* | Cincin torus penuh 360° 4-lantai dengan kanopi putih aerodinamis ganda & kaca kristal | $R_{\text{in}} = 98\text{m}$, $R_{\text{out}} = 136\text{m}$ (Lebar cincin $38\text{m}$, Diameter $272\text{m}$) | 4 Lantai ($16.0\text{m}$) | **Fl 1:** Silicon Lab (FE, BE, QA, DevSecOps), Atrium Caffè Macs, Future Pods<br/>**Fl 2:** Product & Growth Suites (PM, UI/UX, Growth, Copywriter, SEO)<br/>**Fl 3:** Strategic Leadership & Boardroom (CTO, CoS Bridge, CFO Treasury, Wellness Pods)<br/>**Fl 4:** **Founder's Apex Omni-Panoramic Penthouse Suite** |
| **Steve Jobs Theater 5X** | Silinder kaca struktural murni 360° dengan atap serat karbon melayang di bukit selatan jauh | $R = 25\text{m}$ (Silinder), $R = 34\text{m}$ (Atap), $R = 38\text{m}$ (Auditorium) | Ground ($7.5\text{m}$) + Subterranean ($-8.0\text{m}$) | **Ground:** Lobi melingkar transparan 360° dengan lift kaca silinder 16m & tangga spiral marmer<br/>**Basement:** Amfiteater All-Hands bertingkat 3 tier, layar Micro-LED melengkung 24m |
| **Tantau SecOps Cube 5X** | Kompleks megastruktur minimalis 2 lantai berpanel smart-glass, titanium, dan piringan radar satelit | $52\text{m} \times 36\text{m}$ (Luas lantai dasar $\approx 1,872\text{m}^2$) | 2 Lantai ($10.5\text{m}$) | **Fl 1:** Sandbox Testing Lab & 4 diagnostic islands<br/>**Fl 2:** Datacenter Vault dengan 8 server monoliths dan isolasi Docker |
| **The Central Meadow** | Lanskap taman dalam cincin berkontur alami | Lingkaran diameter $196\text{m}$ di dalam The Ring | Kontur $0\text{m} - 1.5\text{m}$ | Kolam Refleksi bundar kristal ($R=22\text{m}$), Sacred Ancient Grand Sakura di $(32, 16)$, bangku kayu jati, jalur pedestrian inner loop |
| **Outer Parkland Lawn** | Hamparan rumput hijau asri melingkari seluruh kampus | Radius $320\text{m}$ (Diameter $640\text{m}$) | Ground | Outer promenade ($R=154\text{m}$), avenue penghubung ke Theater dan Tantau, serta taburan pohon sakura rimbun |

---

## 3. Spesifikasi Pipeline Visual ~80% Realistic (Zero-Asset RTX/Shader Standard)

Untuk mewujudkan visual sekelas Minecraft dengan Shaders Ray Tracing / Cyberpunk tanpa membakar GPU:

1. **ACES Filmic Tone Mapping + Exposure Tuning:**
   * Menyingkirkan warna kartun WebGL flat; memberikan kontras sinematik dengan *highlight rolloff* sekelas Unreal Engine 5.
2. **Procedural PMREM (HDR Image-Based Lighting):**
   * Mengkalkulasi refleksi lingkungan 360° in-memory pada material logam titanium, kaca kristal, dan lantai marmer mengkilap (*Fresnel reflections*).
3. **GTAO / SSAO (Ground Truth Ambient Occlusion):**
   * Bayangan kontak realistis di setiap sudut pertemuan dinding, celah meja, dan bawah kursi agar objek terasa memiliki "bobot fisik".
4. **Procedural PBR Normal Maps:**
   * Pori-pori mikro marmer Calacatta, goresan halus *brushed titanium*, dan gelombang riak air kolam dihasilkan secara matematis pada kanvas 2D in-memory.
5. **Unreal Selective Bloom & Emissive Glow:**
   * Kilauan pendaran cahaya holografik transparan, lampu status LED server rack, dan nyala api perapian *zen hearth*.
6. **Batas Konsumsi GPU (Optimized 60–120 FPS):**
   * Menggunakan *screen-space approximations* (bukan brute-force path tracing), aman dan dingin dijalankan di GPU laptop/menengah.

---

## 4. Mekanik Gamifikasi & Kontroler First-Person AAA

1. **First-Person Controller Rasa Game AAA:**
   * **Inersia Gerak:** Akselerasi dan deselerasi halus berbasis momentum saat mulai berjalan dan berhenti.
   * **Headbobbing Organik:** Ayunan kamera ritmis kurva sinusoidal saat avatar berjalan, dan ayunan lebih cepat saat sprint (`Shift`).
   * **Dynamic FOV & Lean Strafe:** FOV melebar dinamis saat sprint, dan kemiringan roll kamera halus saat bergerak ke samping (`A`/`D`).
   * **Footstep Audio Sync:** Efek suara langkah kaki yang responsif terhadap jenis lantai (kayu, marmer, rumput, paving stone).
2. **Interactive Glass Elevator Mechanics:**
   * Tombol panggil lift fisik di setiap lantai.
   * Tabung lift meluncur vertikal halus membawa avatar dari Lantai 1 ($Y=0$) langsung ke Founder Penthouse ($Y=12\text{m}$) dengan panorama visual ke luar ring.
3. **Terrain Berkontur Sungguhan:**
   * Ketinggian tanah bergelombang lembut (*soft rolling hills*) pada South Hill tempat Steve Jobs Theater berdiri, dan cekungan alami pada kolam refleksi.

---

## 5. Status & Rencana Eksekusi

* **Tahap 1 & 2:** **SELESAI & STABIL** (Mega-Lanskap 640m, Eksterior Ring 272m 4-lantai, Theater 5x di selatan, Tantau 5x di utara, Kaca Kristal Transparan).
* **Tahap 3 (Interior & Furnitur Bertingkat Skala Penuh):** **SELESAI & STABIL** (Lantai 1 Silicon Lab, Lantai 2 Strategy & Design Studio, Lantai 3 Leadership & Oval Boardroom, Lantai 4 Founder Apex Penthouse, 15 Sayap Modular Ekspansi Masa Depan, Subterranean Keynote Auditorium 3-Tier, Tantau Datacenter Vault 2 Lantai).
* **Tahap 4 (Sirkulasi 360°, Lift Kaca 4-Lantai, Spatial XYZ & FPS Inspector, Living Agent Ecosystem):** **SELESAI & STABIL**.
* **Tahap 5 (Gamifikasi AAA, Fisika Gerak Inersia, Terrain Sungguhan Berkontur & Pipeline Visual 80% Realistic RTX):** **SELESAI & STABIL** (UnrealBloomPass Selective Glow, PMREM Radiance HDR IBL, ACES Filmic Tone Mapping, PBR Micro-Bumps, Procedural Web Audio Footsteps, Southern Hill Cupertino Topography, Proximity Sliding Doors).
