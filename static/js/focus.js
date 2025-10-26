// Focus Timer JavaScript - WebSocket + API Integration

let timerInterval = null;
let elapsedSeconds = 0;
let isPaused = false;
let currentSessionId = null;
let ws = null;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/focus/`);
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'session_update') {
            loadStats();
            loadSessions('today');
        }
    };
    ws.onerror = function(error) { console.error('WebSocket error:', error); };
}

async function loadCategories() {
    const response = await fetch('/focus/api/categories/');
    const data = await response.json();
    const select = document.getElementById('categorySelect');
    data.categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = cat.name;
        select.appendChild(option);
    });
}

function updateTimerDisplay() {
    const minutes = Math.floor(elapsedSeconds / 60);
    const seconds = elapsedSeconds % 60;
    document.getElementById('timerDisplay').textContent = `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
}

document.getElementById('startBtn')?.addEventListener('click', async function() {
    const categoryId = document.getElementById('categorySelect').value;
    if (!categoryId) { alert('Please select a category first!'); return; }
    const response = await fetch('/focus/api/sessions/start/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ category_id: categoryId }) });
    const data = await response.json();
    currentSessionId = data.session_id;
    elapsedSeconds = 0;
    timerInterval = setInterval(() => { if (!isPaused) { elapsedSeconds++; updateTimerDisplay(); } }, 1000);
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'inline-block';
    document.getElementById('completeBtn').style.display = 'inline-block';
    document.getElementById('categorySelect').disabled = true;
});

document.getElementById('pauseBtn')?.addEventListener('click', async function() {
    isPaused = true;
    await fetch(`/focus/api/sessions/${currentSessionId}/pause/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
    document.getElementById('pauseBtn').style.display = 'none';
    document.getElementById('resumeBtn').style.display = 'inline-block';
});

document.getElementById('resumeBtn')?.addEventListener('click', async function() {
    isPaused = false;
    await fetch(`/focus/api/sessions/${currentSessionId}/resume/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
    document.getElementById('resumeBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'inline-block';
});

document.getElementById('completeBtn')?.addEventListener('click', function() {
    clearInterval(timerInterval);
    document.getElementById('reflectionModal').style.display = 'flex';
});

document.getElementById('saveReflection')?.addEventListener('click', async function() {
    const notes = document.getElementById('reflectionNotes').value;
    await fetch(`/focus/api/sessions/${currentSessionId}/complete/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ notes: notes }) });
    resetTimer();
    document.getElementById('reflectionModal').style.display = 'none';
    document.getElementById('reflectionNotes').value = '';
    loadStats(); loadSessions('today');
});

document.getElementById('skipReflection')?.addEventListener('click', async function() {
    await fetch(`/focus/api/sessions/${currentSessionId}/complete/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ notes: '' }) });
    resetTimer(); document.getElementById('reflectionModal').style.display = 'none'; loadStats(); loadSessions('today');
});

function resetTimer() {
    elapsedSeconds = 0; isPaused = false; currentSessionId = null; updateTimerDisplay();
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('pauseBtn').style.display = 'none';
    document.getElementById('resumeBtn').style.display = 'none';
    document.getElementById('completeBtn').style.display = 'none';
    document.getElementById('categorySelect').disabled = false;
}

async function loadStats() {
    const response = await fetch('/focus/api/stats/');
    const data = await response.json();
    document.getElementById('todayMinutes').textContent = data.today_minutes;
    document.getElementById('todaySessions').textContent = data.today_sessions;
    document.getElementById('favoriteCategory').textContent = data.favorite_category;
}

async function loadSessions(filter = 'today') {
    const response = await fetch(`/focus/api/sessions/?filter=${filter}`);
    const data = await response.json();
    const container = document.getElementById('sessionHistory');
    container.innerHTML = '';
    if (data.sessions.length === 0) { container.innerHTML = '<p style="text-align:center;color:#666;padding:40px;">No sessions yet. Start your first focus session!</p>'; return; }
    data.sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = 'session-item';
        const startTime = new Date(session.start_time);
        const timeStr = startTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        div.innerHTML = ` <div> <div class="session-category">${session.category__name || 'Uncategorized'}</div> <div class="session-time">${timeStr}</div> </div> <div class="session-duration">${session.duration} min</div>`;
        container.appendChild(div);
    });
}

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        loadSessions(this.dataset.filter);
    });
});

function getCookie(name) { let cookieValue = null; if (document.cookie && document.cookie !== '') { const cookies = document.cookie.split(';'); for (let i = 0; i < cookies.length; i++) { const cookie = cookies[i].trim(); if (cookie.substring(0, name.length + 1) === (name + '=')) { cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); break; } } } return cookieValue; }

document.addEventListener('DOMContentLoaded', function() { initWebSocket(); loadCategories(); loadStats(); loadSessions('today'); });
