# HIMATE E-VOTE Setup Guide

Panduan lengkap untuk setup dan menjalankan sistem HIMATE E-VOTE.

## Prasyarat

- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- Terminal/Command Prompt
- Browser modern (Chrome, Firefox, Safari, Edge)

## Instalasi Cepat

### 1. Persiapan Folder

\`\`\`bash
# Buka terminal di folder project
cd himate_evote
\`\`\`

### 2. Jalankan Setup Script

**Linux/Mac:**
\`\`\`bash
chmod +x setup.sh
./setup.sh
\`\`\`

**Windows:**
\`\`\`bash
# Buka Command Prompt atau PowerShell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
mkdir backend\database
mkdir backend\static\img
type nul > backend\database\log_absensi.txt
type nul > backend\database\log_vote.txt
\`\`\`

### 3. Jalankan Aplikasi

\`\`\`bash
# Pastikan virtual environment aktif
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

# Jalankan Flask app
python backend/app.py
\`\`\`

Aplikasi akan berjalan di `http://localhost:5000`

## Akses Aplikasi

### Panitia Dashboard
- URL: http://localhost:5000/
- Fungsi: Registrasi pemilih, monitoring hasil voting
- Akses: Dari laptop meja panitia

### Voting Booth
- URL: http://localhost:5000/voting
- Fungsi: Interface voting untuk pemilih
- Akses: Dari laptop bilik voting (3-4 unit)

### Thank You Page
- URL: http://localhost:5000/thankyou
- Fungsi: Konfirmasi setelah voting
- Akses: Otomatis setelah pemilih memilih

## Konfigurasi

### Mengubah Port

Edit `backend/app.py` baris terakhir:

\`\`\`python
if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # Ubah port di sini
\`\`\`

### Menambah Kandidat

1. Buka `init_db.sql`
2. Tambahkan baris di bagian INSERT candidates:

\`\`\`sql
INSERT OR IGNORE INTO candidates (id, name, description, photo) VALUES
(1, 'Kandidat 1', 'Deskripsi', '/static/img/candidate1.png'),
(2, 'Kandidat 2', 'Deskripsi', '/static/img/candidate2.png'),
(3, 'Kandidat 3', 'Deskripsi', '/static/img/candidate3.png'),
(4, 'Kandidat 4', 'Deskripsi', '/static/img/candidate4.png');  # Tambah di sini
\`\`\`

3. Hapus database lama dan jalankan ulang:

\`\`\`bash
rm backend/database/evote.db
python backend/app.py
\`\`\`

### Mengganti Foto Kandidat

1. Siapkan foto kandidat (format: PNG, JPG)
2. Letakkan di `backend/static/img/`
3. Nama file: `candidate1.png`, `candidate2.png`, dst.
4. Update database jika perlu

### Mengubah Warna Tema

Edit `backend/static/css/style.css`:

\`\`\`css
:root {
  --primary-dark: #000000;      /* Warna latar */
  --primary-light: #FFFFFF;     /* Warna teks */
  --accent-yellow: #d4d94a;     /* Warna aksen */
  --accent-glow: rgba(212, 217, 74, 0.45);  /* Glow effect */
}
\`\`\`

## Troubleshooting

### Error: "Port 5000 already in use"

**Solusi:**
- Ubah port di `backend/app.py`
- Atau tutup aplikasi lain yang menggunakan port 5000

### Error: "ModuleNotFoundError: No module named 'flask'"

**Solusi:**
\`\`\`bash
# Pastikan virtual environment aktif
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

# Install ulang dependencies
pip install -r requirements.txt
\`\`\`

### Error: "No such table: voters"

**Solusi:**
\`\`\`bash
# Hapus database lama
rm backend/database/evote.db

# Jalankan ulang aplikasi
python backend/app.py
\`\`\`

### Bilik tidak menerima pemilih

**Solusi:**
1. Cek browser console (F12) untuk error
2. Pastikan Socket.IO terkoneksi (lihat di Network tab)
3. Refresh halaman bilik
4. Restart aplikasi

### Chart tidak update

**Solusi:**
1. Cek koneksi Socket.IO
2. Buka browser console untuk error
3. Refresh halaman panitia

## Testing

### Test Absensi

1. Buka http://localhost:5000/
2. Input NIM: `12345678`
3. Input Nama: `Test User`
4. Klik "Daftar Absensi"
5. Lihat di antrian

### Test Voting

1. Buka http://localhost:5000/voting di tab baru
2. Klik "Daftar Absensi" di tab pertama
3. Bilik akan otomatis aktif
4. Pilih kandidat
5. Konfirmasi
6. Lihat halaman terima kasih

### Test Real-time Update

1. Buka 2 tab: panitia dan voting
2. Lakukan voting di tab voting
3. Lihat chart update di tab panitia secara real-time

## Backup Data

### Backup Database

\`\`\`bash
cp backend/database/evote.db backup/evote_backup.db
\`\`\`

### Backup Logs

\`\`\`bash
cp backend/database/log_absensi.txt backup/log_absensi_backup.txt
cp backend/database/log_vote.txt backup/log_vote_backup.txt
\`\`\`

## Maintenance

### Membersihkan Database

\`\`\`bash
# Hapus semua data voting tapi keep voters
sqlite3 backend/database/evote.db "DELETE FROM votes;"

# Atau reset semua
rm backend/database/evote.db
python backend/app.py
\`\`\`

### Melihat Log

\`\`\`bash
# Lihat log absensi
cat backend/database/log_absensi.txt

# Lihat log voting
cat backend/database/log_vote.txt
\`\`\`

## Performance Tips

1. **Untuk banyak pemilih**: Gunakan production server (Gunicorn)
2. **Untuk banyak bilik**: Tingkatkan worker count
3. **Untuk stabilitas**: Monitor memory usage
4. **Untuk kecepatan**: Gunakan SSD untuk database

## Deployment ke Server

### Menggunakan Gunicorn

\`\`\`bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 backend.app:app
\`\`\`

### Menggunakan Nginx (Reverse Proxy)

\`\`\`nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
\`\`\`

## Support

Untuk bantuan lebih lanjut, hubungi tim IT atau lihat dokumentasi di README.md
