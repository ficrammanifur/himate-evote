-- Initialize himate_evote database schema

CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nim TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    has_voted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    photo TEXT,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_nim TEXT NOT NULL,
    candidate_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_nim) REFERENCES voters(nim),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- Insert sample candidates
INSERT OR IGNORE INTO candidates (id, name, description, photo) VALUES
(1, 'Kandidat 1', 'Visi dan misi untuk kampus yang lebih baik', '/static/img/candidate1.png'),
(2, 'Kandidat 2', 'Komitmen untuk perubahan positif', '/static/img/candidate2.png'),
(3, 'Kandidat 3', 'Bersama membangun masa depan cerah', '/static/img/candidate3.png');
