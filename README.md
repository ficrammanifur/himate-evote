# HIMATE E-VOTE

Sistem Pemilihan Elektronik Kampus Universitas Cendekia Abditama

## Deskripsi

HIMATE E-VOTE adalah sistem voting elektronik yang dirancang untuk pemilihan kampus tanpa login. Sistem ini meniru alur TPS (Tempat Pemungutan Suara) nyata dengan:

- **Meja Panitia**: Untuk registrasi/absensi pemilih
- **Bilik Voting**: Untuk proses pemilihan kandidat
- **Real-time Dashboard**: Untuk monitoring hasil voting

## Fitur Utama

- ✓ Absensi pemilih tanpa login
- ✓ FIFO queue system untuk bilik voting
- ✓ Real-time vote updates dengan Socket.IO
- ✓ Dark theme dengan aksen kuning-hijau (#d4d94a)
- ✓ Animasi lightning effects pada hover kandidat
- ✓ Doughnut chart realtime dengan count-up animation
- ✓ Logging otomatis ke file teks
- ✓ Responsive design

## Teknologi

- **Backend**: Flask + Flask-SocketIO
- **Database**: SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Real-time**: Socket.IO
- **Charts**: Chart.js

## Instalasi

### Prasyarat
- Python 3.8+
- pip

### Langkah Instalasi

1. Clone repository atau download project
2. Jalankan setup script:
   \`\`\`bash
   chmod +x setup.sh
   ./setup.sh
   \`\`\`

3. Aktifkan virtual environment:
   \`\`\`bash
   source venv/bin/activate
   \`\`\`

4. Jalankan aplikasi:
   \`\`\`bash
   python backend/app.py
   \`\`\`

5. Akses aplikasi:
   - Panitia: http://localhost:5000/
   - Bilik Voting: http://localhost:5000/voting

## Struktur Folder

\`\`\`
himate_evote/
├── backend/
│   ├── app.py                 # Flask application
│   ├── database/
│   │   ├── evote.db          # SQLite database
│   │   ├── log_absensi.txt   # Attendance log
│   │   └── log_vote.txt      # Vote log
│   ├── static/
│   │   ├── css/style.css     # Styling
│   │   ├── js/
│   │   │   ├── socket.js     # Socket.IO client
│   │   │   ├── main.js       # Panitia page logic
│   │   │   └── voting.js     # Voting booth logic
│   │   └── img/              # Candidate images
│   └── templates/
│       ├── index.html        # Panitia dashboard
│       ├── voting.html       # Voting booth
│       └── thankyou.html     # Thank you page
├── init_db.sql               # Database schema
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── README.md                 # This file
\`\`\`

## Penggunaan

### Panitia (Meja Registrasi)
1. Buka http://localhost:5000/
2. Input NIM dan nama pemilih
3. Klik "Daftar Absensi"
4. Pemilih akan masuk antrian dan bilik akan otomatis aktif

### Bilik Voting
1. Buka http://localhost:5000/voting di laptop bilik
2. Tunggu pemilih tiba (booth akan otomatis aktif)
3. Pemilih memilih satu kandidat
4. Konfirmasi pilihan
5. Halaman terima kasih muncul dengan animasi
6. Bilik kembali ke standby

### Dashboard
- Lihat statistik real-time di halaman panitia
- Chart doughnut menampilkan distribusi suara
- Turnout percentage dengan animasi count-up
- Antrian pemilih yang menunggu

## API Endpoints

- `GET /api/candidates` - Daftar kandidat aktif
- `POST /api/absensi` - Registrasi pemilih
- `POST /api/vote` - Rekam suara
- `GET /api/stats` - Statistik voting

## Socket.IO Events

- `bilik_ready` - Bilik siap menerima pemilih
- `bilik_activate` - Aktivasi bilik untuk pemilih
- `bilik_ack` - Bilik acknowledge pemilih
- `bilik_reset` - Reset bilik ke standby
- `voter_arrived` - Pemilih tiba di antrian
- `vote_update` - Update hasil voting

## Logging

Semua aktivitas dicatat di:
- `backend/database/log_absensi.txt` - Catatan absensi
- `backend/database/log_vote.txt` - Catatan suara

## Customization

### Menambah Kandidat
Edit `init_db.sql` atau gunakan database manager untuk menambah data ke tabel `candidates`.

### Mengubah Warna
Edit `backend/static/css/style.css`:
- `--accent-yellow: #d4d94a` - Warna aksen utama
- `--primary-dark: #000000` - Warna latar
- `--primary-light: #FFFFFF` - Warna teks

### Mengubah Font
Edit `backend/static/css/style.css` untuk mengubah font family.

## Troubleshooting

### Port 5000 sudah digunakan
Edit `backend/app.py` baris terakhir:
\`\`\`python
socketio.run(app, host='0.0.0.0', port=5001, debug=True)
\`\`\`

### Database error
Hapus `backend/database/evote.db` dan jalankan ulang aplikasi.

### Bilik tidak aktif
Pastikan Socket.IO terkoneksi dengan baik. Cek browser console untuk error.

## Lisensi

Universitas Cendekia Abditama - 2024

## Support

Untuk pertanyaan atau masalah, hubungi tim IT kampus.
# himate-evote
