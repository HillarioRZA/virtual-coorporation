# DOKUMENTASI SPASIAL & TEKNIS 3D WORLD BUILDING
## Apple Park Sovereign Multi-Agent Virtual Mega-Campus Simulator
**Spesifikasi Desain Spasial, Kalkulasi Geometri Prosedural, Fisika, Shading, & Telemetri Agen**

---

## 1. Fitur Apa Ini dan Apa Fungsinya?

Fitur ini adalah **Virtual 3D World Office Simulator** (diakses melalui rute `/office`), sebuah kembaran digital spasial (*Spatial Digital Twin*) berskala megastruktur yang memvisualisasikan seluruh aktivitas 12 agen AI otonom dari proyek startup inkubasi di dalam replika 3D dari **Apple Park Mega-Campus (Cupertino, California)**.

### Fungsi Utama Fitur Ini:
1. **Representasi Visual Nyata atas Komputasi Agen AI**:  
   Mengubah proses abstrak di balik layar (eksekusi LLM, penulisan PRD, pembuatan kode, pemindaian OWASP, simulasi PR review) menjadi aksi spasial yang hidup di layar: agen berjalan antar-gedung, duduk mengetik di workstation meja kerja, berkumpul di amfiteater, atau mengobrol santai di Caffè Macs.
2. **Founder First-Person Walkthrough**:  
   Memberikan pengalaman bagi Founder untuk "berjalan masuk" ke dalam perusahaannya sendiri menggunakan sudut pandang orang pertama (*First-Person PoV*), menaiki lift kaca antarlantai, dan menginspeksi pekerjaan para agen layaknya CEO yang berkeliling di kantor fisik.
3. **Pusat Komando & Intervensi Spasial (Spatial Command & Control)**:  
   Founder dapat memberikan instruksi langsung melalui konsol obrolan terpadu (*Oasis Console*) menggunakan mention (`@fe`, `@be`, `@cto`, `@all`). Perintah ini mengubah rute jalan agen, status animasi, dan memicu rapat darurat secara langsung (*All-Hands Meeting*).

---

## 2. Deskripsi Detail World Building & Kompleks Bangunan

Dunia virtual ini mengadopsi tata letak melingkar (*concentric campus layout*) yang mereplikasi landmark arsitektur Apple Park secara penuh:

```
                              [ UTARA ]
                     Tantau SecOps & Datacenter
                        (X: 60, Y: 0, Z: -230)
                                 │
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
              │         THE GRAND RING              │
              │     (Radius 98m s.d 136m, D=272m)   │
 [ BARAT ]    │                                     │    [ TIMUR ]
Caffè Macs ───┤           [ Taman Tengah ]          ├─── East Portal
  Atrium      │          Reflection Pool            │    (X: 117, Z: 0)
              │         (X: 0, Y: 0, Z: 0)          │
              │                                     │
              └──────────────────┬──────────────────┘
                                 │
                                 │
                        Steve Jobs Theater
                       (X: 40, Y: 0, Z: 230)
                             [ SELATAN ]
```

### 2.1. Bangunan 1: The Grand Ring (The Spaceship)
* **Bentuk & Geometri**: Struktur cincin melingkar sempurna (*torus cylinder*) $360^\circ$.
* **Dimensi**:
  * Radius Dalam ($R_{in}$): $98.0\text{ meter}$.
  * Radius Luar ($R_{out}$): $136.0\text{ meter}$.
  * Lebar Koridor Gedung: $38.0\text{ meter}$ ($R_{out} - R_{in}$).
  * Diameter Total ($D$): $272.0\text{ meter}$.
* **Ketinggian & Tingkat Lantai**:
  * Terdiri dari **4 lantai fisik penuh** dengan ketinggian $4.0\text{ meter}$ per lantai (Tinggi puncak atap $16.0\text{ meter}$ + kanopi panel surya).
  * **Lantai 1 ($Y = 0.0 - 4.0\text{m}$)**: Silicon Lab (Engineering Guild: Frontend, Backend, QA) dan East Reception Portal.
  * **Lantai 2 ($Y = 4.0 - 8.0\text{m}$)**: Product & Growth Suites (PM Guild, Growth Lead, Copywriting, SEO Hub).
  * **Lantai 3 ($Y = 8.0 - 12.0\text{m}$)**: Executive Boardroom & Leadership Suites (CTO Suite, CFO Desk, Chief of Staff).
  * **Lantai 4 ($Y = 12.0 - 16.0\text{m}$)**: Founder Apex Penthouse (Sanctuary pribadi Founder dengan pemandangan cakrawala $360^\circ$).
* **Luas Bangunan**:
  $$\text{Luas Permukaan per Lantai} = \pi \left( R_{out}^2 - R_{in}^2 \right) = \pi \left( 136^2 - 98^2 \right) \approx 27.935\text{ m}^2$$
  $$\text{Total Luas 4 Lantai} \approx 111.740\text{ m}^2$$
* **Fasad & Sirip Aerodinamis**:
  * Dikelilingi oleh dinding tirai kaca lengkung tanpa sambungan vertikal tebal.
  * Di setiap lantai terpasang **Dual Aerodynamic Cantilevered Sun Fins**: sirip peneduh komposit putih yang menjorok keluar sepanjang $4.5\text{ meter}$ (sisi luar) dan $3.8\text{ meter}$ (sisi dalam).
  * Atap dilapisi penuh oleh matriks panel fotovoltaik surya (*Solar Roof Grid*).

### 2.2. Bangunan 2: Caffè Macs Great Atrium
* **Posisi**: Terintegrasi pada busur dalam The Grand Ring sisi barat ($\theta = \pi$, rentang busur $\approx 20^\circ$).
* **Rancangan**: Atrium terbuka setinggi 4 lantai monumental dengan fasad kaca geser raksasa.
* **Interior**:
  * Barista Counter & Boba Island berbahan stainless steel brushed ($10.5\text{m} \times 1.1\text{m} \times 2.2\text{m}$) di koordinat radius $R = 110\text{m}$.
  * Meja komunal panjang kayu oak Eropa (*Arco European Solid Oak Tables*) tersusun radial.
  * Teras terbuka berbatasan langsung dengan rumput padang rumput dalam.

### 2.3. Bangunan 3: Steve Jobs Theater
* **Posisi**: Terletak di atas perbukitan selatan pada koordinat $(X: 40, Y: 0, Z: 230)$.
* **Bentuk & Geometri**: Paviliun silinder kaca transparan $360^\circ$ tanpa tiang penopang internal (*unsupported glass cylinder*).
* **Dimensi**:
  * Radius Silinder Kaca ($R_{cyl}$): $25.0\text{ meter}$ (Diameter $50.0\text{ meter}$).
  * Ketinggian Silinder Kaca: $7.5\text{ meter}$.
  * Radius Atap Cakram Karbon: $34.0\text{ meter}$ (Diameter $68.0\text{ meter}$) yang tampak melayang.
* **Pondasi & Akses Bawah Tanah**:
  * Bertumpu di atas plinth marmer Italian Travertine 2 tingkat (Tingkat bawah $R=28.5\text{m}$, tingkat atas $R=26.0\text{m}$).
  * Inti silinder pusat memuat lift kaca tabung dan tangga spiral marmer heliks (*Helical Marble Staircase*) yang mengarah ke amfiteater keynote bawah tanah sedalam $9.0\text{ meter}$ ($R = 38.0\text{m}$).

### 2.4. Bangunan 4: Tantau SecOps & Datacenter Complex
* **Posisi**: Terletak di sepanjang koridor Tantau Avenue sisi utara pada koordinat $(X: 60, Y: 0, Z: -230)$.
* **Bentuk & Geometri**: Gedung persegi panjang monolitik modern berlapis panel titanium gelap dan kaca hitam.
* **Dimensi**:
  * Lebar: $52.0\text{ meter}$.
  * Kedalaman: $36.0\text{ meter}$.
  * Ketinggian per Lantai: $5.0\text{ meter}$ (Total tinggi $10.5\text{ meter}$).
* **Zonasi Ruang**:
  * **Lantai 1**: Sandbox R&D Lab & Stasiun Hardware Isolasi.
  * **Lantai 2**: High-Density Server Datacenter Vault (deretan rak server dengan lampu LED status berkedip).
  * **Atap**: Penthouse ventilasi mekanikal dan parabola komunikasi satelit uplink.

### 2.5. Lanskap Luar: Taman Lingkar Dalam & Danau Refleksi
* **Central Meadow**: Taman melingkar berdiameter $196\text{ meter}$ di dalam lingkaran The Grand Ring.
* **Reflection Pool**: Danau buatan melingkar di titik pusat $(0, 0, 0)$ dengan radius $24.5\text{ meter}$ berkedalaman $0.8\text{ meter}$ dengan pantulan air langit dinamis.
* **Vegetasi**: Dikelilingi oleh jalur jogging kerikil granit lengkung (*granite paver loop*), pohon ek asli California, dan deretan pohon sakura mekar (*cherry blossoms*).

---

## 3. Apa Saja yang Sudah Dikerjakan?

Implementasi teknis yang telah tuntas 100% dan beroperasi pada kode sumber saat ini:

1. **Procedural Geometry Engine Penuh (Zero-External Asset)**:
   * Seluruh geometri (The Ring 272m, 4 lantai, lift, pilar, kanopi peneduh, silinder Theater, Tantau complex) dikonstruksi secara parametrik melalui kode matematika Three.js tanpa bergantung pada unduhan file 3D `.obj` atau `.gltf` berukuran ratusan megabyte.
2. **First-Person Founder Walk & Controller**:
   * Kontrol FPS lengkap menggunakan keyboard WASD, spasi untuk melompat (*jump*), Shift untuk berlari (*sprint*), dan mouse pointer lock.
   * Tombol `Alt` untuk melepaskan kursor (*free cursor*) agar dapat berinteraksi dengan tombol UI.
   * Tombol `Tab` untuk berganti ke mode *God-Mode Spectator* (terbang bebas menembus dinding) atau *Tactical Orbit* (kamera pengawas helikopter).
3. **Lift Kaca Interaktif 4 Lantai (*Interactive Glass Elevator*)**:
   * Sistem elevator fisik yang mendeteksi jarak Founder saat mendekat ($< 3.5\text{ meter}$), membuka modal pilihan lantai (Lantai 1 s.d 4), menggerakkan lantai kabin ke atas/bawah secara halus (*smooth cubic lerp*), dan membawa posisi pemain naik/turun secara realistis.
4. **Hierarchical Voxel Character Rig**:
   * Rangka karakter agen 3D berbasis voxel (proporsi Steve/Alex) dengan sendi pundak, pinggul, kepala, dan badan independen.
   * Animasi prosedural berjalan (*sinusoidal leg & arm swing*), duduk, dan mengetik keyboard di meja kerja.
5. **Real-Time 24-Hour Day/Night Atmospheric Cycle**:
   * Orbit matahari eliptis parametrik yang mensimulasikan waktu 24 jam nyata (atau preset instan: Pagi 07:00, Siang 12:00, Sore 17:30, Malam 22:00).
   * Interpolasi temperatur warna sinar matahari dari jingga fajar ($2200\text{K}$) ke biru langit terik ($5800\text{K}$) hingga cahaya rembulan malam ($12000\text{K}$).
   * Kubah bintang (*star dome*) dengan 1.200 partikel bintang yang menyala otomatis di malam hari.
6. **Sistem Pintu Otomatis (*Proximity Sliding Doors*)**:
   * Pintu kaca geser otomatis di entrance timur The Ring, Caffè Macs, dan Steve Jobs Theater yang membuka saat avatar mendekat ($< 6\text{ meter}$) dan menutup kembali saat menjauh.
7. **Spatial Telemetry HUD**:
   * HUD transparan di sudut kanan bawah yang menampilkan koordinat pemain real-time $(X, Y, Z)$, indikator FPS render, dan mode kamera.

---

## 4. Apa Saja yang Masih Menjadi Kekurangan?

Berdasarkan audit spasial mendalam, berikut adalah kekurangan yang menjadi target perbaikan pada fase berikutnya (*World v2.0*):

1. **Karakter Agen Masih Berbasis Voxel (Bukan Humanoid Realistis)**:
   * Menggunakan gaya blok retro ala Minecraft. Sangat ringan untuk performa browser, tetapi kontras dengan gaya arsitektur Apple Park yang modern dan fotorealistik.
2. **Karakter Menembus Meja (*Mesh Clipping*)**:
   * Belum adanya sistem *Seating Anchor Point* membuat agen duduk tepat di dalam kubus meja (tubuh menembus meja kerja dan monitor) alih-alih duduk rapi di atas kursi.
3. **Gedung Server Tantau Belum Ada Akses Vertikal**:
   * Lantai 2 Datacenter belum memiliki tangga atau shaft lift, sehingga pemain di mode orang pertama tidak bisa naik ke lantai atas secara logis tanpa mengaktifkan mode terbang (*God Mode*).
4. **Interior Gedung Satelit Masih Kosong**:
   * Lantai bawah tanah Steve Jobs Theater belum memiliki panggung pementasan, layar LED keynote, dan kursi melingkar.
   * Gedung Tantau baru memuat kubus server kasar, belum memiliki meja konsol monitor SOC (*Security Operations Center*).
5. **Pencahayaan Matahari Luar Terlalu Silau (*Specular Overexposure*)**:
   * Cahaya matahari menembus kaca lengkung dengan pantulan terlalu keras seperti cermin karena tone mapping linear dan kurangnya tekstur *roughness* mikro pada lantai.
6. **Minim Lampu Plafon Interior**:
   * Di dalam gedung belum terpasang lampu strip LED plafon, sehingga ruangan terlihat gelap gulita saat matahari bergeser ke malam hari.
7. **Perabotan Menghalangi Pintu Lift**:
   * Belum ada zona eksklusi (*Keep-Out Zone*) di depan lift, sehingga beberapa meja kerja sempat ter-generate menabrak jalur keluar-masuk kabin lift.

---

## 5. Detail Teknis: Material, Tekstur, Pencahayaan, Bayangan, & Formula Matematika

Seluruh dunia 3D dibangun di atas fondasi komputasi grafika matematis presisi tinggi menggunakan library Three.js:

### 5.1. Konfigurasi Material Fisik (PBR Materials)
Sistem menggunakan `MeshStandardMaterial` dan `MeshPhysicalMaterial` yang merespons cahaya secara optik nyata:
* **Apple Curved Glass Material**:
  ```typescript
  new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.28,
    roughness: 0.05,
    metalness: 0.1,
    transmission: 0.82,  // Efek tembus pandang kaca fisik
    ior: 1.52,           // Indeks refraksi kaca optik
    thickness: 1.2,      // Ketebalan refraksi kaca
  });
  ```
* **Aerodynamic Canopy Sun Fins**:
  `MeshStandardMaterial` berwarna putih pekat (`#ffffff`) dengan `roughness: 0.22` dan `metalness: 0.05` untuk mereplikasi pelat aluminium komposit anti-silau.
* **Titanium Mullions & Pillars**:
  `MeshStandardMaterial` berwarna abu-abu titanium (`#475569`) dengan `roughness: 0.35` dan `metalness: 0.85`.

### 5.2. Pembuatan Tekstur Prosedural In-Memory (HTML5 Canvas Textures)
Sistem membuat tekstur resolusi tinggi $512 \times 512$ langsung di memori GPU tanpa mengunduh file eksternal:
1. **Tekstur Lantai Kayu Oak (Blonde Oak Wood)**:
   * Base color: `#ebd5b3` (Scandinavian White Oak).
   * Pola serat kayu dihitung dengan fungsi gelombang sinus:
     $$y_{grain}(i) = i + 8 \cdot \sin(0.05 \cdot i)$$
   * Celah antar-papan ditarik setiap interval $64\text{ piksel}$.
   * Diterapkan properti `wrapS = wrapT = RepeatWrapping` dengan frekuensi pengulangan `repeat.set(4, 4)`.
2. **Tekstur Panel Surya Atap (Solar Grid)**:
   * Base color: `#0a1128` (Deep navy photovoltaic silicon).
   * Busbar perak vertikal ditarik setiap $16\text{ piksel}$ dan garis horizontal tipis setiap $32\text{ piksel}$.

### 5.3. Formula Matematika Pembentukan Objek
1. **Lengkungan $360^\circ$ The Grand Ring (Parametric Circle)**:
   Setiap segmen dinding kaca lengkung dibentuk dari koordinat parametrik polar:
   $$X(\theta) = R \cdot \cos(\theta), \quad Z(\theta) = R \cdot \sin(\theta), \quad \theta \in [0, 2\pi]$$
   Geometri dinding kaca menggunakan segmen sudut halus ($\Delta\theta = \frac{2\pi}{128}$ atau 128 segmen radial).
2. **Ketinggian Bertingkat (*Floor Height Offset*)**:
   Ketinggian lantai ke-$fl$ dirumuskan secara linier:
   $$Y_{floor}(fl) = (fl - 1) \times 4.0\text{ meter}$$
3. **Orbit Matahari 24 Jam**:
   Posisi matahari di langit dihitung berdasarkan waktu jam berjalan ($t \in [0, 24]$):
   $$\theta_{sun} = \left( \frac{t - 6}{24} \right) \cdot 2\pi$$
   $$\vec{P}_{sun} = \begin{bmatrix} 380 \cdot \cos(\theta_{sun}) \\ \max(-5, 320 \cdot \sin(\theta_{sun})) \\ 220 \cdot \sin(0.5 \cdot \theta_{sun}) \end{bmatrix}$$

### 5.4. Pengaturan Pencahayaan & Bayangan Halus (PBR Soft Shadows)
* **DirectionalLight (Matahari)**: Intensitas 1.4, memproyeksikan bayangan dari ketinggian langit.
* **Shadow Map**: Resolusi tinggi $2048 \times 2048$ piksel.
* **Shadow Bias**: `bias = -0.0003` dan `normalBias = 0.02` untuk mengeliminasi cacat visual garis hitam bergerigi (*shadow acne*).
* **Penumbra Lembut**: `shadow.radius = 2.5` menggunakan algoritma *PCFSoftShadowMap* pada renderer.
* **HemisphereLight**: Langit atas putih (`#ffffff`), pantulan tanah biru batu tulis gelap (`#1e293b`), intensitas 0.9.

---

## 6. Detail Rinci Mekanik & Fisika di Dalam World Building

Sistem fisika dikelola oleh modul [`OfficePlayerPhysics.ts`](file:///d:/my%20project/VIRTUAL%20TECH%20STARTUP%20MULTI-AGENT%20SYSTEM/frontend/src/components/office/3d/controls/OfficePlayerPhysics.ts) dan [`OfficeCollisionSystem.ts`](file:///d:/my%20project/VIRTUAL%20TECH%20STARTUP%20MULTI-AGENT%20SYSTEM/frontend/src/components/office/3d/controls/OfficeCollisionSystem.ts):

### 6.1. Kinematika Gerak Pemain (Player Locomotion)
* **Kecepatan Jalan (Walk Speed)**: $7.5\text{ m/s}$.
* **Kecepatan Sprint**: $13.0\text{ m/s}$ (diaktifkan dengan menahan tombol `ShiftLeft`).
* **Akselerasi**: $40.0\text{ m/s}^2$ menghasilkan sensasi dorongan gerak yang responsif.
* **Gaya Gesek (Friction)**: $11.0$ untuk penghentian gerak yang tidak licin (*no icy sliding*).
* **Gravitasi & Lompatan**:
  * Kecepatan Awal Lompat: $V_0 = 4.8\text{ m/s}$.
  * Gravitasi Bumi: $g = 15.0\text{ m/s}^2$.
  * Perhitungan vertikal:
    $$V_y(t + \Delta t) = V_y(t) - g \cdot \Delta t$$
    $$Y(t + \Delta t) = Y(t) + V_y \cdot \Delta t$$
  * Saat $Y \le Y_{target\_floor}$, pemain dinyatakan *grounded* ($V_y = 0$).

### 6.2. Efek Imersi Kamera Sinematik
* **Head-Bobbing (Goyangan Kepala)**:
  Saat avatar berjalan, kamera berayun sinusoidal meniru langkah kaki manusia:
  $$\Delta Y_{bob} = \sin(\text{timer}) \times 0.065\text{ m}$$
  $$\Delta X_{bob} = \cos(0.5 \cdot \text{timer}) \times 0.035\text{ m}$$
  Timer bergerak pada frekuensi $12.0\text{ rad/s}$ saat berjalan dan $17.5\text{ rad/s}$ saat sprint.
* **Strafe Camera Banking (Roll Tilt)**:
  Ketika pemain melangkah menyamping (tombol `A` atau `D`), kamera memiringkan sudut kemiringan (*roll*) sebesar $0.025\text{ radian}$ secara halus (*cubic lerp*).
* **Dynamic Sprint FoV Zoom**:
  Kamera Perspective Camera secara dinamis memperlebar sudut pandang (*Field of View*) dari $72^\circ$ (keadaan santai) menjadi $80^\circ$ saat sprint untuk memberikan sensasi akselerasi kecepatan.

### 6.3. Deteksi Tabrakan & Resolusi Melingkar (Collision Detection)
Pemain direpresentasikan sebagai silinder lingkaran vertikal dengan radius $r_{player} = 0.5\text{ meter}$.
1. **Batas Cincin Konsentris The Grand Ring**:
   Pemain di dalam koridor dijaga agar radius posisinya $R = \sqrt{X^2 + Z^2}$ selalu memenuhi:
   $$R_{in} + r_{player} \le R \le R_{out} - r_{player}$$
   $$\iff 98.5\text{m} \le \sqrt{X^2 + Z^2} \le 135.5\text{m}$$
   Jika pemain menyentuh kaca lengkung, vektor posisi diproyeksikan kembali ke batas busur tanpa mematikan momentum gerak tangensial (*sliding resolution*).
2. **Collider Melingkar Statis**:
   * Kolam Refleksi Pusat: $(0, 0)$ radius $24.5\text{m}$.
   * Steve Jobs Theater: $(40, 230)$ radius $25.2\text{m}$.
   * Batang Pohon: Radius $0.6\text{m}$.

### 6.4. Mekanik Lift Kaca (Vertical Travel Physics)
Ketika pemain memilih lantai tujuan $fl_{dest}$ di HUD:
1. Posisi vertikal kabin lift dihitung menggunakan interpolasi kurva kuadrat halus (*smooth quad ease-in-out*):
   $$Y_{lift}(t) = Y_{start} + (Y_{dest} - Y_{start}) \cdot \text{easeInOut}(t)$$
2. Jika pemain berdiri di dalam radius kabin lift ($< 3.2\text{ meter}$ dari poros tengah lift), posisi $Y$ pemain dikunci dan dibawa naik/turun bersama kabin secara absolut, mencegah pemain terjatuh menembus lantai lift.

---

## 7. Relevansi Antara World Building ("/office") dengan "project_description.md"

World building 3D di `/office` bukanlah game terpisah yang berdiri sendiri, melainkan **Antarmuka Spasial (Spatial Cockpit Interface)** yang terikat erat ke sistem inkubasi startup otonom:

```
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI INCUBATION BACKEND                  │
│  State Machine • PR Engine • OWASP Scanner • Event Bus      │
└──────────────────────────────┬──────────────────────────────┘
                               │
            WebSocket: /corporate/ws/office/{project_id}
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             THREE.JS 3D APPLE PARK MEGA-CAMPUS              │
│                                                             │
│  • Event Bus: PR Diterbitkan ──► Agen FE jalan ke Server     │
│  • Stage Gate: Gate 2 Selesai ──► Agen berkumpul di Penthouse│
│  • Token Usage: Pembakaran LLM ──► Kecepatan ketik animasi  │
│  • Oasis Console: Directive ──► Dispatch tugas langsung     │
└─────────────────────────────────────────────────────────────┘
```

1. **Sinkronisasi State Real-Time Dua Arah (Two-Way WebSocket Bridge)**:
   * Setiap mutasi status di backend (misalnya agen `Backend Specialist` mulai menulis kode API database) memancarkan event ke `CorporateEventBus`.
   * Saluran WebSocket `/corporate/ws/office/{project_id}` meneruskan mutasi ini ke mesin kanvas Three.js. Avatar 3D `Backend Specialist` secara otomatis mengubah statusnya dari `WALKING` menjadi `CODING`, memunculkan animasi mengetik di workstation Lantai 1, dan menampilkan balon dialog kode commit aktif di atas kepalanya.
2. **Visualisasi Tahapan Siklus Hidup Startup (Living Milestone Manifestation)**:
   * Saat venture masih di tahap `SPARRING_ROOM`, agen Founder, CoS, dan CTO terlihat berkumpul di meja bundar Executive Penthouse Lantai 4.
   * Saat memasuki tahap `MOCK_PROTOTYPING`, agen PM, UI/UX, dan Frontend aktif bekerja di sayap Silicon Lab Lantai 1 dan Product Suite Lantai 2.
   * Saat masuk ke `PRODUCTION_HARDENING`, agen DevSecOps terlihat berpatroli menuju Tantau Datacenter untuk mengaudit server.
3. **Pusat Komando Founder Terpadu (The Oasis Command Console)**:
   * Konsol obrolan di bagian bawah kanvas 3D terhubung langsung ke router direktif backend (`POST /api/v1/corporate/office/directive`).
   * Founder dapat mengetik perintah langsung:
     * `@fe ubah tema warna dashboard menjadi indigo neon`
     * `@devsecops lakukan audit ulang celah XSS pada form login`
     * `@all berkumpul di auditorium untuk evaluasi sprint rilis`
   * Perintah ini seketika mengubah *scratchpad* agen, menggerakkan avatar mereka ke lokasi tujuan, dan mencatat instruksi ke audit trail venture.

---
*Dokumen ini merupakan spesifikasi arsitektur resmi subsistem spasial 3D per Oktober 2026.*
