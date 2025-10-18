# HIMATE E-VOTE Backend Documentation

## Arsitektur Backend

Backend dibangun dengan Flask dan Flask-SocketIO untuk komunikasi real-time.

## Database Schema

### Tabel: voters
\`\`\`sql
CREATE TABLE voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nim TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    has_voted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

### Tabel: candidates
\`\`\`sql
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    photo TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

### Tabel: votes
\`\`\`sql
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_nim TEXT NOT NULL,
    candidate_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_nim) REFERENCES voters(nim),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);
\`\`\`

## API Endpoints

### GET /api/candidates
Mendapatkan daftar kandidat aktif.

**Response:**
\`\`\`json
[
  {
    "id": 1,
    "name": "Kandidat 1",
    "description": "Deskripsi",
    "photo": "/static/img/candidate1.png",
    "active": 1
  }
]
\`\`\`

### POST /api/absensi
Registrasi pemilih dan tambahkan ke antrian.

**Request:**
\`\`\`json
{
  "nim": "12345678",
  "name": "Nama Pemilih"
}
\`\`\`

**Response (Success):**
\`\`\`json
{
  "success": true,
  "message": "Absensi berhasil",
  "queue_pos": 1
}
\`\`\`

**Response (Error):**
\`\`\`json
{
  "error": "NIM sudah terdaftar"
}
\`\`\`

### POST /api/vote
Rekam suara pemilih.

**Request:**
\`\`\`json
{
  "nim": "12345678",
  "candidate_id": 1
}
\`\`\`

**Response (Success):**
\`\`\`json
{
  "success": true,
  "message": "Vote berhasil dicatat"
}
\`\`\`

### GET /api/stats
Mendapatkan statistik voting real-time.

**Response:**
\`\`\`json
{
  "candidates": [
    {
      "id": 1,
      "name": "Kandidat 1",
      "vote_count": 5
    }
  ],
  "total_voters": 100,
  "voted_count": 45,
  "turnout_percentage": 45.0
}
\`\`\`

## Socket.IO Events

### Client → Server

#### bilik_ready
Bilik siap menerima pemilih.

\`\`\`javascript
socket.emit('bilik_ready', {
  client_id: 'booth_abc123'
});
\`\`\`

#### bilik_ack
Bilik acknowledge pemilih yang diterima.

\`\`\`javascript
socket.emit('bilik_ack', {
  voter_nim: '12345678'
});
\`\`\`

#### bilik_reset
Reset bilik ke standby setelah voting selesai.

\`\`\`javascript
socket.emit('bilik_reset');
\`\`\`

### Server → Client

#### voter_arrived
Broadcast ketika pemilih baru tiba di antrian.

\`\`\`javascript
socket.on('voter_arrived', (data) => {
  // data: { nim, name, queue_pos }
});
\`\`\`

#### bilik_activate
Aktivasi bilik untuk pemilih tertentu.

\`\`\`javascript
socket.on('bilik_activate', (data) => {
  // data: { voter: { nim, name }, queue_pos }
});
\`\`\`

#### vote_update
Broadcast update hasil voting ke semua client.

\`\`\`javascript
socket.on('vote_update', (stats) => {
  // stats: { candidates, total_voters, voted_count, turnout_percentage }
});
\`\`\`

## Global State Management

### voter_queue
Deque untuk menyimpan pemilih yang menunggu.

\`\`\`python
voter_queue = deque()
\`\`\`

### active_booths
Dictionary untuk tracking bilik yang aktif.

\`\`\`python
active_booths = {
  'socket_id': {
    'client_id': 'booth_abc123',
    'status': 'standby|voting',
    'voter_nim': '12345678'
  }
}
\`\`\`

## Alur Voting

1. **Absensi**: Panitia input NIM + nama → POST /api/absensi
2. **Queue**: Pemilih masuk antrian → emit voter_arrived
3. **Aktivasi**: Server cari bilik kosong → emit bilik_activate
4. **Voting**: Pemilih pilih kandidat → POST /api/vote
5. **Update**: Server broadcast hasil → emit vote_update
6. **Reset**: Bilik reset → emit bilik_reset

## Error Handling

### Duplicate NIM
\`\`\`json
{
  "error": "NIM sudah terdaftar"
}
\`\`\`

### Voter Already Voted
\`\`\`json
{
  "error": "Pemilih sudah melakukan voting"
}
\`\`\`

### Invalid Candidate
\`\`\`json
{
  "error": "Kandidat tidak valid"
}
\`\`\`

## Logging

### log_absensi.txt
\`\`\`
[2024-01-15 10:30:45] ABSEN NIM 12345678 - Nama Pemilih
[2024-01-15 10:31:20] ABSEN NIM 87654321 - Nama Lain
\`\`\`

### log_vote.txt
\`\`\`
[2024-01-15 10:32:10] VOTE NIM 12345678 -> candidate 1 - Kandidat 1
[2024-01-15 10:33:45] VOTE NIM 87654321 -> candidate 2 - Kandidat 2
\`\`\`

## Performance Considerations

- SQLite cocok untuk skala kecil-menengah (hingga 1000 pemilih)
- Socket.IO menggunakan eventlet untuk async handling
- Database connection di-pool per request
- Queue processing menggunakan thread lock untuk thread safety

## Deployment

### Development
\`\`\`bash
python backend/app.py
\`\`\`

### Production
Gunakan production WSGI server seperti Gunicorn:
\`\`\`bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 backend.app:app
\`\`\`

## Security Notes

- Tidak ada authentication - kontrol fisik saja
- NIM harus unik untuk mencegah double voting
- Database lock untuk thread safety
- Logging untuk audit trail
