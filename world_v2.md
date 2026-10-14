# BLUEPRINT & STRATEGY: 3D WORLD BUILDING V2.0
## Apple Park Sovereign Multi-Agent Mega-Campus Simulator
**Dokumen Resmi Rencana Perbaikan, Level Design, & Peningkatan Realisme Spasial**

---

## 1. Executive Summary: Keputusan Strategis Founder

Sebelum melangkah ke level pengembangan fitur lanjutan (*The Ultimate Spatial AI Operating System*), Founder mengambil keputusan strategis yang tepat: **menghentikan sementara penulisan kode (*code-freeze*) untuk mematangkan rancangan denah (*floor plan*), zonasi arsitektural, dan *positioning* interior secara menyeluruh**.

### Mengapa Langkah Ini Diambil?
1. **Menghindari Pemborosan Waktu (*Zero Trial-and-Error*)**:  
   Memperbaiki koordinat $(X, Y, Z)$ secara langsung di kode tanpa panduan denah selalu berujung pada pergeseran berulang (geser $0.5\text{m}$, uji coba, masih bertabrakan, lalu revisi ulang).
2. **Prinsip "Measure Twice, Cut Once"**:  
   Dengan denah dan aturan tata letak yang matang di atas kertas/dokumen, proses implementasi ke dalam Three.js procedural engine akan berjalan cepat, presisi 1:1, dan bebas regresi.
3. **Fondasi Teknis Sudah Stabil**:  
   Mesin inti WebGL (60 FPS, Web Worker, State Machine, WebSocket event streaming, dan 131/131 backend testing) telah 100% lulus uji. Fokus berikutnya murni pada estetika spasial, arsitektur interior, dan ergonomi visual.

---

## 2. Evaluasi Masalah & Celah World Building Saat Ini (Current State Audit)

Berdasarkan pengamatan menyeluruh pada dunia 3D saat ini, berikut adalah daftar aspek yang memerlukan pembenahan mendasar:

### 2.1. Karakter & Mekanik Spasial
* **Karakter Agen Berbasis Voxel (Bukan Humanoid Realistis):**  
  Desain voxel (proporsi ala Steve/Alex Minecraft) sangat hemat performa, namun bagi pengguna yang mengharapkan karakter fotorealistik bergaya Unreal Engine MetaHuman, gaya ini terasa bergaya retro-blok.
* **Karakter Menembus Meja (*Mesh Clipping*):**  
  Titik koordinat duduk agen belum memiliki sistem *Anchor Point* dan arah hadap (*facing yaw*). Avatar duduk tepat di tengah kubus meja alih-alih di belakang kursi.
* **Perabotan di Area Perlintasan Lift:**  
  Belum ada batasan zona terlarang (*No-Spawn Keep-Out Zone*) di depan pintu lift kaca, sehingga perabotan sempat ter-generate menghalangi akses keluar-masuk lantai.

### 2.2. Arsitektur & Zonasi Gedung
* **Gedung Server Tantau Belum Memiliki Akses Vertikal:**  
  Gedung Tantau SecOps Datacenter belum memiliki shaft lift atau tangga darurat untuk mengakses lantai atas secara masuk akal.
* **Potensi 2 Gedung Satelit Belum Maksimal:**  
  - **Steve Jobs Theater**: Cangkang silinder kaca luar sudah berdiri, namun lantai amfiteater bawah tanah (*Underground Keynote Auditorium*) belum terisi panggung, kursi audiens melingkar, dan layar presentasi.
  - **Tantau SecOps Datacenter**: Masih berupa deretan server monolitik dasar tanpa *War Room Red-Teaming* atau *NOC Security Console*.
* **Banyak Ruangan Terasa Kosong:**  
  Koridor The Grand Ring sepanjang 272 meter memiliki bentang ruang luas yang belum diisi sekat partisi, bilik kerja, tanaman indoor, atau lounge santai.

### 2.3. Pencahayaan & Visual
* **Pantulan Sinar Matahari Berlebihan (*Overexposed Specular Flare*):**  
  `DirectionalLight` luar ruangan terlalu terik dan menembus dinding kaca dengan tone mapping linear biasa, menyebabkan lantai tampak seperti cermin yang menyilaukan mata (*washed out*).
* **Gedung Gelap / Minim Lampu Interior:**  
  Interior ruangan tidak memiliki sumber cahaya lampu plafon (*ceiling LED lights / warm ambient lights*), sehingga ruangan terasa mati dan tidak realistis saat siklus waktu bergeser ke sore atau malam.

---

## 3. Strategi Realisme Tanpa Blender / Unreal Engine 5

Founder **tidak perlu menguasai software 3D modeling rumit** seperti Blender atau Unreal Engine 5. Industri WebGL modern menggunakan pendekatan modular siap pakai:

### A. Tekstur PBR Fisik Gratis (CC0 / Public Domain)
Realisme permukaan dinding, aspal, kayu, dan kaca diselesaikan menggunakan pustaka tekstur PBR gratis dari [Poly Haven](https://polyhaven.com/textures) dan [ambientCG](https://ambientcg.com/):
* **Albedo / Base Color Map**: Tekstur warna asli (parket kayu oak, marmer putih Apple Park, beton arsitektural).
* **Roughness Map**: Mengontrol pantulan kilap agar tidak silau cermin, melainkan memiliki doff alami.
* **Normal Map**: Memberikan ilusi pori-pori dan guratan 3D timbul pada permukaan datar saat terkena sudut cahaya miring.

### B. Pencahayaan Sinematik (100% Kode Three.js)
70% dari sensasi fotorealisme berasal dari kalibrasi pencahayaan:
1. **ACES Filmic Tone Mapping**: Mengaktifkan kurva warna industri film Hollywood (`THREE.ACESFilmicToneMapping`) agar gradasi transisi cahaya terang ke gelap terasa halus, hangat, dan lembut di mata.
2. **Atmospheric Sky Shader**: Menggunakan modul bawaan `three/addons/objects/Sky.js` untuk mensimulasikan hamburan sinar matahari bumi (*Rayleigh & Mie Scattering*) secara akurat tanpa gambar langit datar.
3. **Lampu Plafon Emissive**: Menambahkan lampu strip LED tipis di langit-langit tiap ruangan dengan *PointLight* hangat.

### C. Aset Model Perabotan & Vegetasi Siap Pakai (.GLB / .GLTF)
* Mengunduh model kursi kantor ergonomis, meja kerja, monitor melengkung, sofa, dan pohon rindang dari kreator bebas lisensi (seperti Quaternius, Kenney, atau Poly Haven).
* Model di-load langsung menggunakan `GLTFLoader` dalam hitungan baris kode.

### D. Partikel Atmosfer Dinamis
* Partikel debu melayang (*dust motes*) di bawah sorotan lampu ruangan.
* Kelopak bunga sakura berguguran di taman tengah The Grand Ring.
* Kabut jarak halus (*Exponential Fog*) untuk memberikan kesan megah dan kedalaman koridor kampus.

---

## 4. Panduan & Format Denah yang Diperlukan

Untuk memudahkan pengerjaan teknis, denah yang disusun Founder cukup mengikuti acuan matematis dan format teks terstruktur di bawah ini.

### 4.1. Skala Matematis Kampus
* **Satuan Ukuran**: $1\text{ unit Three.js} = 1\text{ meter dunia nyata}$.
* **Ketinggian Antar-Lantai**: $4.0\text{ meter}$ per tingkat.
  * Lantai 1: $Y = 0.0\text{m} - 4.0\text{m}$ (Ground Floor)
  * Lantai 2: $Y = 4.0\text{m} - 8.0\text{m}$ (Mid Floor)
  * Lantai 3: $Y = 8.0\text{m} - 12.0\text{m}$ (Executive Floor)
  * Lantai 4: $Y = 12.0\text{m} - 16.0\text{m}$ (Founder Penthouse)
* **The Grand Ring**: Radius tengah $\approx 117\text{ meter}$, lebar koridor gedung $\approx 12\text{ meter}$.

### 4.2. Template Deskripsi Denah Ruangan (Format Rekomendasi)

```markdown
### [Nama Gedung] - Lantai [Nomor Lantai]
* **Nama Ruangan**: (Contoh: Silicon Lab Tech Guild)
* **Tema / Suasana**: (Contoh: Minimalis industrial, kaca tempered, pencahayaan cool-white)
* **Akses & Pintu**: (Contoh: Menghadap ke koridor dalam lingkar taman)
* **Tata Letak Workstation**:
  1. Meja [Nama Agen, misal: Frontend Lead]:
     - Posisi: Sisi barat dekat kaca luar.
     - Arah Hadap: Menghadap ke utara (menghadap layar komputer).
     - Kursi: Mundur 0.6 meter dari bibir meja agar tidak nembus.
  2. Meja [Nama Agen, misal: Backend Lead]:
     - Posisi: 2 meter di sebelah timur meja Frontend.
     - Arah Hadap: Menghadap ke utara.
* **Perabotan Penunjang**:
  - Meja rapat berdiri (Standing meeting pod) di tengah.
  - Rak server mini di sudut ruangan.
  - Tanaman hias monstera di samping pintu.
* **Titik Akses Vertikal**: (Khusus gedung bertingkat seperti Tantau: lokasi lift / tangga)
* **Zona Bebas (Keep-Out)**: Area radius 2 meter di depan pintu lift wajib bebas barang.
```

---

## 5. Pipeline Prioritas Pengerjaan (Roadmap Bertahap)

Pengerjaan renovasi 3D akan dijalankan secara bertahap mengikuti standar industri:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE PRODUKSI 3D V2.0                       │
├────────────────────────────────────────────────────────────────────────┤
│ FASE 1: Whiteboxing / Blockout Denah & Zonasi Dinding                  │
│         • Membangun dinding partisi ruangan sesuai denah Founder       │
│         • Menambahkan shaft lift / tangga di Tantau Datacenter         │
│         • Membuka sekat bawah tanah Steve Jobs Theater                 │
│                                  │                                     │
│                                  ▼                                     │
│ FASE 2: Penataan Perabotan & Anchor Mekanik Karakter (Anti-Clipping)   │
│         • Peletakan meja, monitor, dan kursi dengan offset aman        │
│         • Mengunci orientasi duduk agen (agen menghadap monitor)       │
│         • Menetapkan batas zona larangan perabotan di area lift        │
│                                  │                                     │
│                                  ▼                                     │
│ FASE 3: Tata Cahaya Interior & Kalibrasi Sinar Matahari                │
│         • Implementasi ACES Filmic Tone Mapping (anti-glare)           │
│         • Pemasangan lampu strip LED plafon di setiap ruangan          │
│         • Kalibrasi pencahayaan siklus waktu (Pagi, Siang, Sore, Malam)│
│                                  │                                     │
│                                  ▼                                     │
│ FASE 4: Pemasangan Tekstur PBR Fisik                                   │
│         • Tekstur lantai parket kayu, marmer lobby, dan karpet rapat   │
│         • Tekstur beton arsitektural halus & kaca tempered berbayang   │
│                                  │                                     │
│                                  ▼                                     │
│ FASE 5: Vegetasi Realistis & Partikel Atmosfer (Final Polish)          │
│         • Integrasi model pohon GLB rindang di taman lingkar dalam     │
│         • Partikel kelopak sakura & debu melayang (dust motes)         │
│         • Efek kabut atmosferik (Exponential Fog)                      │
└────────────────────────────────────────────────────────────────────────┘
```

---
*Dokumen ini menjadi acuan kerja resmi untuk pengembangan world building v2.0.*
