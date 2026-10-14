---
trigger: always_on
---

# Rule: Code Quality & Modularity Standards

- **SRP & File Limit**: Maksimal 150–200 baris kode per file. Jika melebihi batas, WAJIB pecah menjadi modul terpisah (Single Responsibility Principle).
- **Type Hints**: WAJIB menyertakan type hints lengkap pada semua parameter dan return value fungsi/method Python.
- **Docstring**: Gunakan Google-style docstring ringkas untuk setiap class dan fungsi utama.
- **Logging**: Gunakan logger terkonfigurasi (`loguru` / logger internal). DILARANG KERAS menggunakan `print()`.
- **I/O Exception Handling**: WAJIB menggunakan `try-except` spesifik pada seluruh operasi I/O, network call, file I/O, dan data parsing. DILARANG menggunakan bare `except:`.
- **Code Hygiene**: WAJIB membersihkan dead code, komentar yang tidak relevan, dan unused imports sebelum tugas dianggap selesai.