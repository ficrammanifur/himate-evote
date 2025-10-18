// Admin JavaScript for login and superadmin dashboard
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    
    if (currentPath === '/admin_login') {
        // Handle login form
        const form = document.getElementById('adminLoginForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                // Client-side validation (basic)
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                if (!username || !password) {
                    e.preventDefault();
                    alert('Username dan password harus diisi!');
                    return;
                }
            });
        }
    } else if (currentPath === '/superadmin') {
        // Superadmin dashboard logic
        loadStats();
        loadCandidates();
        loadLog('absensi'); // Default log

        // Add candidate form
        const addForm = document.getElementById('addCandidateForm');
        if (addForm) {
            addForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(addForm);
                const data = Object.fromEntries(formData);

                try {
                    const response = await fetch('/api/add_candidate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert('Kandidat berhasil ditambahkan!');
                        addForm.reset();
                        loadCandidates();
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        }

        // Real-time updates via Socket.IO
        const socket = io();
        socket.on('vote_update', function(stats) {
            updateStats(stats);
            updateChart(stats);
        });

        // Section switching
        const sections = document.querySelectorAll('.admin-section');
        sections.forEach(section => {
            if (section.classList.contains('active')) {
                showSection(section.id);
            }
        });
    }
});

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active'); // Assuming clicked from nav

    // Load data if needed
    if (sectionId === 'dashboard') {
        loadStats();
    } else if (sectionId === 'candidates') {
        loadCandidates();
    } else if (sectionId === 'logs') {
        loadLog('absensi'); // Default
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        updateStats(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStats(stats) {
    document.getElementById('totalVoters').textContent = stats.total_voters;
    document.getElementById('totalVotes').textContent = stats.voted_count;
    document.getElementById('turnout').textContent = stats.turnout_percentage + '%';
    document.getElementById('activeBooths').textContent = Object.keys(active_booths || {}).length; // From global, but fetch if needed
}

let voteChart;
function updateChart(stats) {
    const ctx = document.getElementById('voteChart');
    if (!ctx) return;

    const labels = stats.candidates.map(c => c.name);
    const data = stats.candidates.map(c => c.vote_count);

    if (voteChart) {
        voteChart.destroy();
    }

    voteChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#d4d94a', '#51cf66', '#ff6b6b', '#4dabf7']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

async function loadCandidates() {
    try {
        const response = await fetch('/api/candidates');
        const candidates = await response.json();
        const tbody = document.getElementById('candidatesTable');
        tbody.innerHTML = '';

        candidates.forEach(cand => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${cand.id}</td>
                <td>${cand.name}</td>
                <td>${cand.description || ''}</td>
                <td><img src="${cand.photo}" alt="${cand.name}" style="width: 50px; height: 50px;"></td>
                <td>${cand.active ? 'Aktif' : 'Nonaktif'}</td>
                <td>
                    <button class="action-btn ${cand.active ? 'btn-deactivate' : 'btn-activate'}" onclick="toggleCandidate(${cand.id}, ${cand.active ? 0 : 1})">
                        ${cand.active ? 'Nonaktifkan' : 'Aktifkan'}
                    </button>
                </td>
            `;
        });
    } catch (error) {
        console.error('Error loading candidates:', error);
    }
}

async function toggleCandidate(id, active) {
    try {
        const response = await fetch('/api/toggle_candidate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, active })
        });
        const result = await response.json();
        if (result.success) {
            loadCandidates();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function loadLog(type) {
    try {
        const response = await fetch(`/api/logs/${type}`);
        const log = await response.text();
        document.getElementById('logContent').textContent = log;
        
        // Update tab active
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
    } catch (error) {
        console.error('Error loading log:', error);
        document.getElementById('logContent').textContent = 'Error loading log.';
    }
}

// Tambahan untuk admin_monitoring.html
if (window.location.pathname === '/admin_monitoring') {
    let voteChart;

    async function loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            updateStats(stats);
            updateChart(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    function updateStats(stats) {
        document.getElementById('totalVoters').textContent = stats.total_voters || 0;
        document.getElementById('totalVotes').textContent = stats.voted_count || 0;
        document.getElementById('turnout').textContent = stats.turnout_percentage + '%';
        document.getElementById('activeBooths').textContent = 0; // Simplified, or fetch if needed
    }

    function updateChart(stats) {
        const ctx = document.getElementById('voteChart');
        if (!ctx) return;

        const labels = stats.candidates.map(c => c.name);
        const data = stats.candidates.map(c => c.vote_count);

        if (voteChart) {
            voteChart.destroy();
        }

        voteChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#d4d94a', '#51cf66', '#ff6b6b', '#4dabf7']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    // Log function (reuse from superadmin)
    let currentLogType = 'absensi';
    async function loadLog(type) {
        currentLogType = type;
        try {
            const response = await fetch(`/api/logs/${type}`);
            const log = await response.text();
            document.getElementById('logContent').textContent = log;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick="loadLog('${type}')"]`).classList.add('active');
        } catch (error) {
            console.error('Error loading log:', error);
        }
    }
}