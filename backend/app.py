from flask import Flask, render_template, request, jsonify, session, redirect, send_file
from flask_socketio import SocketIO
from datetime import datetime
import sqlite3
import os
import csv
import io
from collections import deque
import threading
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'himate-evote-secret-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database path
DB_PATH = 'backend/database/evote.db'
LOG_ABSENSI_PATH = 'backend/database/log_absensi.txt'
LOG_VOTE_PATH = 'backend/database/log_vote.txt'

# Global state
voter_queue = deque()
active_booths = {}  # {socket_id: {client_id, status, voter_nim}}
booth_lock = threading.Lock()

# Credentials
SUPERADMIN_USER = '2222104036'
SUPERADMIN_PASS = 'superadmin123'
ADMIN_USER = 'admin123'
ADMIN_PASS = 'admin123'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database if not exists"""
    if not os.path.exists('backend/database'):
        os.makedirs('backend/database')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            photo TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_nim TEXT NOT NULL,
            candidate_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (voter_nim) REFERENCES voters(nim),
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
    ''')
    
    # Insert default candidates if empty
    cursor.execute('SELECT COUNT(*) FROM candidates')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO candidates (name, description, photo, active) VALUES
            ('Kandidat 1', 'Deskripsi Kandidat 1', '/static/img/kandidat1.jpg', 1),
            ('Kandidat 2', 'Deskripsi Kandidat 2', '/static/img/kandidat2.jpg', 1),
            ('Kandidat 3', 'Deskripsi Kandidat 3', '/static/img/kandidat3.jpg', 1)
        ''')
    
    conn.commit()
    conn.close()
    
    # Create log files if not exist
    if not os.path.exists(LOG_ABSENSI_PATH):
        open(LOG_ABSENSI_PATH, 'w').close()
    if not os.path.exists(LOG_VOTE_PATH):
        open(LOG_VOTE_PATH, 'w').close()

def log_absensi(nim, name):
    """Log attendance"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_ABSENSI_PATH, 'a') as f:
        f.write(f'[{timestamp}] ABSEN NIM {nim} - {name}\n')

def log_vote(nim, candidate_id, candidate_name):
    """Log vote"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_VOTE_PATH, 'a') as f:
        f.write(f'[{timestamp}] VOTE NIM {nim} -> candidate {candidate_id} - {candidate_name}\n')

def get_vote_stats():
    """Get current vote statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.id, c.name, c.active, COUNT(v.id) as vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
        ORDER BY c.id
    ''')
    
    candidates = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as total FROM voters')
    total_voters = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as voted FROM voters WHERE has_voted = 1')
    voted_count = cursor.fetchone()['voted']
    
    conn.close()
    
    stats = {
        'candidates': [dict(c) for c in candidates],
        'total_voters': total_voters,
        'voted_count': voted_count,
        'turnout_percentage': round((voted_count / total_voters * 100) if total_voters > 0 else 0, 1)
    }
    
    return stats

def process_voter_queue():
    """Process voter queue and activate booths"""
    with booth_lock:
        if voter_queue and active_booths:
            # Find first available booth
            for socket_id, booth in active_booths.items():
                if booth['status'] == 'standby':
                    voter = voter_queue.popleft()
                    booth['status'] = 'voting'
                    booth['voter_nim'] = voter['nim']
                    
                    # Emit to booth
                    socketio.emit('bilik_activate', {
                        'voter': voter,
                        'queue_pos': len(voter_queue)
                    }, room=socket_id)
                    break

# Routes
@app.route('/')
def index():
    """Panitia page"""
    return render_template('index.html')

@app.route('/voting')
def voting():
    """Voting booth page"""
    return render_template('voting.html')

@app.route('/thankyou')
def thankyou():
    """Thank you page"""
    return render_template('thankyou.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Login for both super admin and regular admin"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Super Admin
        if username == SUPERADMIN_USER and password == SUPERADMIN_PASS:
            session['superadmin'] = True
            session['admin'] = False
            return redirect('/superadmin')
        
        # Regular Admin
        elif username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            session['superadmin'] = False
            return redirect('/admin_monitoring')
        
        return render_template('admin_login.html', error='Kredensial salah!')
    
    if session.get('superadmin'):
        return redirect('/superadmin')
    if session.get('admin'):
        return redirect('/admin_monitoring')
    return render_template('admin_login.html')

@app.route('/admin_monitoring')
def admin_monitoring():
    """Regular admin monitoring page"""
    if not session.get('admin') and not session.get('superadmin'):
        return redirect('/admin')
    return render_template('admin_monitoring.html')

@app.route('/superadmin')
def superadmin():
    """Super Admin dashboard"""
    if not session.get('superadmin'):
        return redirect('/admin')
    return render_template('superadmin.html')

@app.route('/logout')
def logout():
    session.pop('superadmin', None)
    session.pop('admin', None)
    return redirect('/')

# API Endpoints (log access for both admin types)
def is_authorized():
    return session.get('superadmin') or session.get('admin')

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM candidates ORDER BY id')
    candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(candidates)

@app.route('/api/add_candidate', methods=['POST'])
def add_candidate():
    """Add new candidate - super admin only"""
    if not session.get('superadmin'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO candidates (name, description, photo, active) VALUES (?, ?, ?, 1)',
            (data['name'], data.get('description', ''), data['photo'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toggle_candidate', methods=['POST'])
def toggle_candidate():
    """Toggle candidate active status - super admin only"""
    if not session.get('superadmin'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE candidates SET active = ? WHERE id = ?', (int(data['active']), data['id']))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Candidate not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/voters', methods=['GET'])
def get_voters():
    """Get voters list with search - super admin only"""
    if not session.get('superadmin'):
        return jsonify({'error': 'Unauthorized'}), 401
    search = request.args.get('search', '')
    conn = get_db()
    cursor = conn.cursor()
    if search:
        cursor.execute('''
            SELECT * FROM voters 
            WHERE nim LIKE ? OR name LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute('SELECT * FROM voters ORDER BY created_at DESC')
    voters = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(voters)

@app.route('/api/absensi', methods=['POST'])
def absensi():
    """Register voter attendance"""
    data = request.json
    nim = data.get('nim', '').strip()
    name = data.get('name', '').strip()
    
    if not nim or not name:
        return jsonify({'error': 'NIM dan nama harus diisi'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if voter already exists
        cursor.execute('SELECT id, has_voted FROM voters WHERE nim = ?', (nim,))
        existing = cursor.fetchone()
        
        if existing:
            if existing['has_voted']:
                conn.close()
                return jsonify({'error': 'Pemilih sudah melakukan voting'}), 400
            # Already registered, just add to queue
            voter = {'nim': nim, 'name': name}
        else:
            # Register new voter
            cursor.execute(
                'INSERT INTO voters (nim, name) VALUES (?, ?)',
                (nim, name)
            )
            conn.commit()
            voter = {'nim': nim, 'name': name}
        
        conn.close()
        
        # Log attendance
        log_absensi(nim, name)
        
        # Add to queue
        voter_queue.append(voter)
        queue_pos = len(voter_queue)
        
        # Broadcast voter arrived
        socketio.emit('voter_arrived', {
            'nim': nim,
            'name': name,
            'queue_pos': queue_pos
        }, broadcast=True)
        
        # Try to process queue
        process_voter_queue()
        
        return jsonify({
            'success': True,
            'message': 'Absensi berhasil',
            'queue_pos': queue_pos
        })
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'NIM sudah terdaftar'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vote', methods=['POST'])
def vote():
    """Record a vote"""
    data = request.json
    nim = data.get('nim', '').strip()
    candidate_id = data.get('candidate_id')
    
    if not nim or not candidate_id:
        return jsonify({'error': 'Data tidak lengkap'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check voter exists and hasn't voted
        cursor.execute('SELECT id, has_voted FROM voters WHERE nim = ?', (nim,))
        voter = cursor.fetchone()
        
        if not voter:
            conn.close()
            return jsonify({'error': 'Pemilih tidak terdaftar'}), 400
        
        if voter['has_voted']:
            conn.close()
            return jsonify({'error': 'Pemilih sudah melakukan voting'}), 400
        
        # Check candidate exists
        cursor.execute('SELECT name FROM candidates WHERE id = ? AND active = 1', (candidate_id,))
        candidate = cursor.fetchone()
        
        if not candidate:
            conn.close()
            return jsonify({'error': 'Kandidat tidak valid'}), 400
        
        # Record vote
        cursor.execute(
            'INSERT INTO votes (voter_nim, candidate_id) VALUES (?, ?)',
            (nim, candidate_id)
        )
        
        # Update voter status
        cursor.execute('UPDATE voters SET has_voted = 1 WHERE nim = ?', (nim,))
        
        conn.commit()
        conn.close()
        
        # Log vote
        log_vote(nim, candidate_id, candidate['name'])
        
        # Broadcast vote update
        stats = get_vote_stats()
        socketio.emit('vote_update', stats, broadcast=True)
        
        return jsonify({
            'success': True,
            'message': 'Vote berhasil dicatat'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get current voting statistics"""
    return jsonify(get_vote_stats())

@app.route('/api/logs/<log_type>')
def get_logs(log_type):
    """Get log file content - for both admin types"""
    if not is_authorized():
        return jsonify({'error': 'Unauthorized'}), 401
    log_path = LOG_ABSENSI_PATH if log_type == 'absensi' else LOG_VOTE_PATH
    try:
        with open(log_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return str(e), 500

@app.route('/api/export/csv')
def export_csv():
    """Export stats to CSV - super admin only"""
    if not session.get('superadmin'):
        return jsonify({'error': 'Unauthorized'}), 401
    stats = get_vote_stats()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Kandidat', 'Suara', 'Persentase'])
    
    # Data
    for cand in stats['candidates']:
        percentage = round((cand['vote_count'] / stats['voted_count'] * 100) if stats['voted_count'] > 0 else 0, 1)
        writer.writerow([cand['name'], cand['vote_count'], f"{percentage}%"])
    
    writer.writerow([])  # Empty row
    writer.writerow(['Total Pemilih', stats['total_voters']])
    writer.writerow(['Suara Masuk', stats['voted_count']])
    writer.writerow(['Turnout', f"{stats['turnout_percentage']}%"])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'hasil_voting_{datetime.now().strftime("%Y-%m-%d")}.csv'
    )

@app.route('/api/export/pdf')
def export_pdf():
    """Export stats to PDF - super admin only"""
    if not session.get('superadmin'):
        return jsonify({'error': 'Unauthorized'}), 401
    stats = get_vote_stats()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("Hasil Voting HIMATE E-VOTE", styles['Title'])
    story.append(title)
    
    # Stats summary
    data = [['Statistik Umum']]
    data.append(['Total Pemilih', stats['total_voters']])
    data.append(['Suara Masuk', stats['voted_count']])
    data.append(['Turnout (%)', f"{stats['turnout_percentage']}%"])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    # Candidates votes
    story.append(Paragraph("Distribusi Suara", styles['Heading2']))
    vote_data = [['Kandidat', 'Suara', 'Persentase']]
    for cand in stats['candidates']:
        percentage = round((cand['vote_count'] / stats['voted_count'] * 100) if stats['voted_count'] > 0 else 0, 1)
        vote_data.append([cand['name'], cand['vote_count'], f"{percentage}%"])
    
    vote_table = Table(vote_data)
    vote_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(vote_table)
    
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hasil_voting_{datetime.now().strftime("%Y-%m-%d")}.pdf'
    )

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')

@socketio.on('bilik_ready')
def handle_bilik_ready(data):
    """Register booth as ready"""
    client_id = data.get('client_id', request.sid)
    
    with booth_lock:
        active_booths[request.sid] = {
            'client_id': client_id,
            'status': 'standby',
            'voter_nim': None
        }
    
    print(f'Booth ready: {client_id}')
    
    # Try to process queue
    process_voter_queue()

@socketio.on('bilik_ack')
def handle_bilik_ack(data):
    """Booth acknowledges voter activation"""
    voter_nim = data.get('voter_nim')
    print(f'Booth acknowledged voter: {voter_nim}')

@socketio.on('bilik_reset')
def handle_bilik_reset():
    """Reset booth to standby"""
    with booth_lock:
        if request.sid in active_booths:
            active_booths[request.sid]['status'] = 'standby'
            active_booths[request.sid]['voter_nim'] = None
    
    # Try to process queue
    process_voter_queue()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    with booth_lock:
        if request.sid in active_booths:
            del active_booths[request.sid]
    
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)