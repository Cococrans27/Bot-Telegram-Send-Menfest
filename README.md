# BotMenfest Telegram

Bot Telegram untuk mengirim pesan anonim ke grup/channel dengan sistem koin dan daily limit.

---

## Fitur

- Kirim pesan anonim ke grup/channel (menfess)
- Sistem koin: 1 pesan = 1 koin
- Daily limit: Setiap user hanya bisa mengirim 2 pesan per hari (reset jam 01:00 WIB)
- Admin bisa topup koin user
- Statistik penggunaan untuk admin
- Dukungan avatar acak (opsional, jika folder `avatars` tersedia)

---

## Instalasi & Persiapan

### 1. **Clone repository**
```bash
git clone <repo-anda>
cd <repo-anda>
```

### 2. **Buat dan aktifkan virtual environment (opsional tapi disarankan)**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# atau
source venv/bin/activate  # Linux/Mac
```

### 3. **Install dependensi**
```bash
pip install -r requirements.txt
```

### 4. **Siapkan file konfigurasi**
- Edit `botmenfest.py` dan ganti `BOT_TOKEN`, `TARGET_CHAT_ID`, dan `ADMIN_IDS` sesuai kebutuhan Anda.
- (Opsional) Buat folder `avatars` dan isi dengan gambar `.jpg` atau `.png` jika ingin fitur avatar acak.

---

## requirements.txt

```
python-telegram-bot>=20.0
pytz
```

---

## Cara Menjalankan

```bash
python botmenfest.py
```
atau jika menggunakan Python 3.11:
```bash
py -3.11 botmenfest.py
```

---

## Struktur File

- `botmenfest.py` — Source code utama bot
- `requirements.txt` — Daftar dependensi Python
- `user_data.json` — Database user (otomatis dibuat)
- `avatars/` — (Opsional) Folder gambar avatar acak

---

## Perintah Bot

- `/start` — Mulai bot & daftar user baru
- `/saldo` — Cek sisa koin & daily limit
- `/topup <id_user> <jumlah>` — (Admin) Tambah koin user
- `/statistik` — (Admin) Statistik pengguna & pesan
- `/report` — Info pelaporan user

---

## Catatan

- Minimal Python 3.10 (rekomendasi Python 3.11)
- Untuk deploy di server, pastikan semua dependensi sudah terinstall dan token/channel ID sudah benar.
- Jika ingin reset daily benar-benar otomatis tanpa interaksi user, gunakan scheduler eksternal atau fitur JobQueue.

---

## Lisensi

Bebas digunakan dan dikembangkan kembali sesuai kebutuhan.
