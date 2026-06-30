<div align="center">

<img src="assets/icon.png" width="120" alt="PetDesk icon" />

# PetDesk 🐾

**Pet virtual pixel-art yang hidup di desktop Windows kamu.**
Jalan-jalan sendiri di layar, bisa di-drag, punya 60+ gerakan, dan bisa diajak
ngobrol lewat LLM (OpenAI-compatible) maupun bot Telegram.

*A cute pixel-art desktop companion for Windows — pure Python + Tkinter, no extra packages.*

</div>

---

https://github.com/user-attachments/assets/93038da8-795c-4fa5-b354-7f44ba75dfa4

## ✨ Fitur

- 🐾 **Pet pixel-art** transparan, selalu di atas window lain, di-generate acak (bentuk, telinga, warna).
- 🎬 **60+ gerakan** otomatis: jalan, lari, loncat, tidur, makan, main bola/musik, skateboard,
  layangan, payung, kejar kupu-kupu, menari, zoomies, dan banyak lagi — semua bergaya pixel senada.
- 🫨 **Squash & stretch** (prinsip animasi): memanjang saat melompat, memipih saat mendarat.
- 🪂 **Parasut**: drag pet ke atas layar lalu lepaskan — ia membuka parasut & melayang turun.
- 💬 **Ngobrol via LLM** (OpenAI-compatible: LM Studio, Ollama, llama.cpp, dll). Jawaban tampil
  sebagai **running text** di atas pet.
- 📡 **Jembatan Telegram** (opsional): pet jadi "otak" bot Telegram-mu dan auto-membalas chat.
- ⚙️ **Pengaturan** lewat klik-kanan: ukuran, jeda antar aktivitas, koneksi LLM, Telegram.

> 100% offline-friendly. Tanpa `pip install` — Tkinter sudah bawaan Python.

---

## 🚀 Mulai cepat

**Butuh:** Windows + [Python 3](https://www.python.org/downloads/) (centang *"Add Python to PATH"* saat instal).
Cek dengan: `python --version`.

1. Unduh / clone repo ini.
2. **Klik dua kali `Jalankan_Pet.bat`**.
3. Pet muncul di pojok bawah layar dan mulai beraktivitas. 🎉

> Mau ikon yang cakep di Desktop? Klik dua kali **`Buat_Pintasan.bat`** — ia membuat shortcut
> **PetDesk** di Desktop lengkap dengan ikonnya. (File `.bat` sendiri memang tidak bisa berikon,
> jadi pakai shortcut ini.)

---

## 🎮 Cara berinteraksi

| Aksi | Hasil |
|------|-------|
| **Drag** (tahan klik kiri, geser) | memindahkan pet; dilepas dari **tinggi** → buka **parasut** 🪂, dari dekat lantai → jatuh biasa |
| **Klik dua kali** | membuka jendela **Ngobrol** (chat LLM) |
| **Klik kanan** | menu lengkap (di bawah) |

**Menu klik-kanan:**
💬 Ngobrol · 📏 Ukuran pet · 🎬 Aksi acak · 🎲 Ganti tampilan · 💤 Tidurkan ·
➕ Tambah pet · ⚙ Pengaturan… · 📡 Telegram on/off · 🗑 Hapus · 🚪 Keluar

---

## ⚙️ Pengaturan

Klik kanan → **⚙ Pengaturan…**:

- **Ukuran pet** — slider (juga ada preset di menu: Kecil/Sedang/Besar/Jumbo).
- **Jeda antar aktivitas** — Singkat / Medium / Lama.
- **Koneksi LLM** & **Telegram** — lihat di bawah.

Semua tersimpan otomatis di `pet_config.json` (lihat catatan privasi).

### 💬 Hubungkan ke LLM (OpenAI-compatible)
1. Jalankan server LLM-mu (mis. **LM Studio** di `http://localhost:1234/v1`, atau
   **Ollama** di `http://localhost:11434/v1`).
2. Pengaturan → isi **Base URL**, **Model**, **API Key** (kosong kalau lokal) → **Tes LLM** → **Simpan**.
3. Klik dua kali pet untuk ngobrol. (Kalau Base URL gagal, otomatis dicoba ulang dengan `/v1`.)

### 📡 Hubungkan ke bot Telegram (opsional)
Pet bisa menjadi otak bot Telegram-mu: tiap pesan ke bot dibalas pakai LLM, dan tampil sebagai
running text di desktop.
1. Buat bot di **@BotFather**, salin **bot token**.
2. Pengaturan → bagian **Jembatan Telegram** → isi token → **Tes Telegram** → centang **Aktifkan** → simpan.
3. Kirim pesan ke bot-mu dari Telegram.

> ⚠️ **Warning "Telegram polling conflict" (HTTP 409)?** Artinya ada pihak lain yang juga menarik
> update bot yang sama (agent lama, atau aplikasi dibuka dua kali, atau webhook). Aplikasi sudah
> menangani ini (hapus webhook otomatis, anti dobel-instance, pulih sendiri). Kalau masih muncul,
> pastikan tidak ada program lain yang memakai bot token yang sama.

---

## 🔒 Privasi (penting untuk yang fork/clone)

Semua data pribadimu — **bot token Telegram, API key, base URL** — disimpan di **`pet_config.json`**,
dan file itu **sudah masuk `.gitignore`** sehingga **tidak ikut ter-upload ke GitHub**.

- Jangan commit `pet_config.json`.
- Untuk berbagi format, gunakan **`pet_config.example.json`** (berisi placeholder, tanpa rahasia).
- Cara teraman: jangan edit file manual — cukup isi semuanya lewat menu **⚙ Pengaturan**.

---

## 🧩 Menambah gerakan baru

Sistemnya data-driven. Buka `desktop_pet.py`:

1. (Opsional) tambah sprite item di dict **`_PROPS`** (digambar `karakter → warna`; outline gelap
   ditambahkan otomatis).
2. Tambah satu baris di **`_SPECS`**:
   ```python
   ("main_skuter", "board", "under", "glide", "tuck", "Ngacir~"),
   #  nama        prop      place    motion   pose    teks
   ```
   - `prop`: nama sprite di `_PROPS`, atau `None` untuk gerak tanpa item.
   - `place`: `front_feet` / `above` / `high` / `float_up` / `flit` / `bounce`.
   - `motion`: `still` / `sway` / `glide` / `roll` / `chase` / `hop` / `spin` / `dance` /
     `pace` / `shiver` / `moonwalk` / `wander` / `zoomies`.
   - `pose`: `idle` / `walk` / `tuck`.

---

## 📁 Struktur

```
PetDesk/
├─ desktop_pet.py          # aplikasi utama (Tkinter): perilaku, menu, chat, Telegram
├─ pet_art.py              # generator + renderer pixel-art (squash & stretch)
├─ Jalankan_Pet.bat        # jalankan pet (klik dua kali)
├─ Buat_Pintasan.bat       # buat shortcut Desktop berikon
├─ pet_config.example.json # contoh setelan (salin -> pet_config.json)
├─ assets/icon.png|.ico    # ikon aplikasi
├─ .gitignore              # mengecualikan pet_config.json (data pribadi)
└─ LICENSE                 # MIT
```

---

## 📜 Lisensi

[MIT](LICENSE) — bebas dipakai, diubah, dan dibagikan. Dibuat untuk seru-seruan. 🐾
