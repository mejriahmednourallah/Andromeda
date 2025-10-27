// Focus Timer JavaScript - WebSocket + API Integration

let timerInterval = null;
let elapsedSeconds = 0;
let isPaused = false;
let currentSessionId = null;
let ws = null;

// Pomodoro state
let pomodoro = {
    enabled: false,
    workMinutes: 25,
    shortBreak: 5,
    longBreak: 15,
    cyclesBeforeLongBreak: 4,
    currentCycle: 0,
    state: 'idle', // 'idle' | 'work' | 'break'
    timerRemaining: 0
};

// expose initial global state for other pages (chase widget)
window.__ANDROMEDA_POMODORO = {
    enabled: false,
    state: pomodoro.state,
    timerRemaining: pomodoro.timerRemaining
};

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
    try {
        const response = await fetch('/focus/api/categories/');
        if (!response.ok) {
            console.error('Failed loading categories', response.status);
            return;
        }
        const data = await response.json();
        const select = document.getElementById('categorySelect');
        // remove previous non-placeholder options
        select.querySelectorAll('option:not([value=""])').forEach(o => o.remove());
        if (!data.categories || data.categories.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No categories yet';
            opt.disabled = true;
            select.appendChild(opt);
            return;
        }
        data.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            select.appendChild(option);
        });
    } catch (err) {
        console.error('Error loading categories', err);
    }
}

function formatTimeSeconds(s) {
    const minutes = Math.floor(s / 60);
    const seconds = Math.max(0, s % 60);
    return `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
}

function updateTimerDisplay() {
    // If pomodoro running in countdown mode use timerRemaining, else show elapsedSeconds
    if (pomodoro.enabled && (pomodoro.state === 'work' || pomodoro.state === 'break')) {
        const minutes = Math.floor(pomodoro.timerRemaining / 60);
        const seconds = pomodoro.timerRemaining % 60;
        document.getElementById('timerDisplay').textContent = `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
    } else {
        const minutes = Math.floor(elapsedSeconds / 60);
        const seconds = elapsedSeconds % 60;
        document.getElementById('timerDisplay').textContent = `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
    }
}

function setPomodoroStatus(text) {
    const el = document.getElementById('pomStatus');
    if (el) el.textContent = text;
}

function clearExistingInterval() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

async function startPomodoro() {
    // read settings from inputs
    pomodoro.workMinutes = parseInt(document.getElementById('pomWorkMinutes').value || 25, 10);
    pomodoro.shortBreak = parseInt(document.getElementById('pomShortBreak').value || 5, 10);
    pomodoro.longBreak = parseInt(document.getElementById('pomLongBreak').value || 15, 10);
    pomodoro.cyclesBeforeLongBreak = parseInt(document.getElementById('pomCycles').value || 4, 10);
    pomodoro.enabled = true;
    pomodoro.currentCycle = 0;
    // persist enabled
    window.__ANDROMEDA_POMODORO.enabled = true;
    localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
    await startWorkInterval();
}

async function startWorkInterval() {
    const categoryId = document.getElementById('categorySelect').value;
    if (!categoryId) { alert('Please select a category first!'); pomodoro.enabled = false; setPomodoroStatus('Pomodoro aborted: no category'); return; }
    setPomodoroStatus(`Work — Cycle ${pomodoro.currentCycle + 1} of ${pomodoro.cyclesBeforeLongBreak}`);
    // start server session for the work interval
    try {
        const response = await fetch('/focus/api/sessions/start/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ category_id: categoryId }) });
        const data = await response.json();
        currentSessionId = data.session_id;
    } catch (err) {
        console.error('Failed to start session for pomodoro', err);
        pomodoro.enabled = false; setPomodoroStatus('Pomodoro error: cannot start session');
        return;
    }

    pomodoro.state = 'work';
    // compute expected end timestamp so other pages can compute remaining even if this tab is backgrounded
    const expectedEnd = Date.now() + pomodoro.workMinutes * 60 * 1000;
    pomodoro.timerRemaining = Math.round((expectedEnd - Date.now()) / 1000);
    // update global state
    window.__ANDROMEDA_POMODORO.state = pomodoro.state;
    window.__ANDROMEDA_POMODORO.expectedEnd = expectedEnd;
    window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
    localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
    clearExistingInterval();
    timerInterval = setInterval(async () => {
        if (isPaused) return;
        // compute remaining from expectedEnd to survive throttling/background
        pomodoro.timerRemaining = Math.max(0, Math.round((window.__ANDROMEDA_POMODORO.expectedEnd - Date.now()) / 1000));
        // update global state each tick
        window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
        window.__ANDROMEDA_POMODORO.state = pomodoro.state;
        localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
        updateTimerDisplay();
        if (pomodoro.timerRemaining <= 0) {
            // end work interval
            clearExistingInterval();
            try {
                await fetch(`/focus/api/sessions/${currentSessionId}/complete/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ notes: '' }) });
            } catch (err) { console.error('Failed to complete session', err); }
            pomodoro.currentCycle += 1;
            loadStats(); loadSessions('today');
            // Decide break
            if (pomodoro.currentCycle >= pomodoro.cyclesBeforeLongBreak) {
                // long break
                await startBreakInterval(pomodoro.longBreak, true);
                pomodoro.currentCycle = 0; // reset cycles
            } else {
                await startBreakInterval(pomodoro.shortBreak, false);
            }
            // After break, automatically start next work if still enabled
            if (pomodoro.enabled) {
                await startWorkInterval();
            }
        }
    }, 1000);

    // update UI controls
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'inline-block';
    document.getElementById('completeBtn').style.display = 'inline-block';
    document.getElementById('categorySelect').disabled = true;
}

async function startBreakInterval(minutes, isLong) {
    if (minutes <= 0) return; // skip if zero
    pomodoro.state = 'break';
    setPomodoroStatus((isLong ? 'Long' : 'Short') + ` break — ${minutes} min`);
    // set expected end timestamp for break as well
    const expectedEnd = Date.now() + minutes * 60 * 1000;
    pomodoro.timerRemaining = Math.round((expectedEnd - Date.now()) / 1000);
    // update global state
    window.__ANDROMEDA_POMODORO.state = pomodoro.state;
    window.__ANDROMEDA_POMODORO.expectedEnd = expectedEnd;
    window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
    localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
    clearExistingInterval();
    return new Promise(resolve => {
        timerInterval = setInterval(() => {
            if (isPaused) return;
            pomodoro.timerRemaining = Math.max(0, Math.round((window.__ANDROMEDA_POMODORO.expectedEnd - Date.now()) / 1000));
            window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
            localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
            updateTimerDisplay();
            if (pomodoro.timerRemaining <= 0) {
                clearExistingInterval();
                resolve();
            }
        }, 1000);
    });
}

document.getElementById('startBtn')?.addEventListener('click', async function() {
    const pomToggle = document.getElementById('pomodoroToggle');
    const pomEnabled = pomToggle && pomToggle.checked;
    if (pomEnabled) {
        // Start pomodoro flow
        await startPomodoro();
        return;
    }
    // regular session
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
    // If in pomodoro work interval, pause server session as well
    if (pomodoro.enabled && pomodoro.state === 'work' && currentSessionId) {
        try { await fetch(`/focus/api/sessions/${currentSessionId}/pause/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } }); } catch(e){console.error(e);}    
    }
    document.getElementById('pauseBtn').style.display = 'none';
    document.getElementById('resumeBtn').style.display = 'inline-block';
});

document.getElementById('resumeBtn')?.addEventListener('click', async function() {
    isPaused = false;
    if (pomodoro.enabled && pomodoro.state === 'work' && currentSessionId) {
        try { await fetch(`/focus/api/sessions/${currentSessionId}/resume/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } }); } catch(e){console.error(e);}    
    }
    document.getElementById('resumeBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'inline-block';
});

document.getElementById('completeBtn')?.addEventListener('click', function() {
    clearExistingInterval();
    // If pomodoro running, stop the flow
    if (pomodoro.enabled) {
        pomodoro.enabled = false;
        pomodoro.state = 'idle';
        setPomodoroStatus('Pomodoro stopped');
        document.getElementById('categorySelect').disabled = false;
    }
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

document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
    loadCategories();
    loadStats();
    loadSessions('today');
    updateTimerDisplay();

    const pomToggle = document.getElementById('pomodoroToggle');
    if (pomToggle) {
        pomToggle.addEventListener('change', function(e) {
            pomodoro.enabled = e.target.checked;
            setPomodoroStatus(pomodoro.enabled ? 'Pomodoro ready' : 'Pomodoro disabled');
        });
    }

    const chaseToggle = document.getElementById('chaseWidgetToggle');
    if (chaseToggle) {
        // load initial state
        const chaseVisible = localStorage.getItem('andromeda_chase_visible') !== 'false'; // default true
        chaseToggle.checked = chaseVisible;
        // save on change
        chaseToggle.addEventListener('change', function(e) {
            localStorage.setItem('andromeda_chase_visible', e.target.checked);
            // notify chase widget to update
            localStorage.setItem('andromeda_chase_action', JSON.stringify({ action: 'visibility_change', visible: e.target.checked, ts: Date.now() }));
        });
    }
});

// Handle actions from the chase widget via localStorage communication
function handlePomodoroActionObj(obj) {
    if (!obj || !obj.action) return;
    const action = obj.action;
    console.log('Received external pomodoro action', action);
    (async () => {
        try {
            if (action === 'pause') {
                if (currentSessionId) {
                    await fetch(`/focus/api/sessions/${currentSessionId}/pause/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
                    isPaused = true;
                    document.getElementById('pauseBtn').style.display = 'none';
                    document.getElementById('resumeBtn').style.display = 'inline-block';
                }
            } else if (action === 'resume') {
                if (currentSessionId) {
                    await fetch(`/focus/api/sessions/${currentSessionId}/resume/`, { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
                    isPaused = false;
                    document.getElementById('resumeBtn').style.display = 'none';
                    document.getElementById('pauseBtn').style.display = 'inline-block';
                }
            } else if (action === 'complete') {
                if (currentSessionId) {
                    await fetch(`/focus/api/sessions/${currentSessionId}/complete/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }, body: JSON.stringify({ notes: '' }) });
                    resetTimer(); document.getElementById('reflectionModal').style.display = 'none'; loadStats(); loadSessions('today');
                }
            }
        } catch (err) { console.error('Error handling external action', err); }
    })();
}

// Listen for storage events from other tabs (chase widget places actions here)
window.addEventListener('storage', function(e) {
    if (e.key === 'andromeda_pomodoro_action') {
        try { const obj = JSON.parse(e.newValue); handlePomodoroActionObj(obj); localStorage.removeItem('andromeda_pomodoro_action'); } catch (err) {}
    }
});

// Also process any pending action present on load (in case it was set before focus tab opened)
try {
    const pending = JSON.parse(localStorage.getItem('andromeda_pomodoro_action'));
    if (pending) { handlePomodoroActionObj(pending); localStorage.removeItem('andromeda_pomodoro_action'); }
} catch (e) {}

// handle presets and bind preset selector
document.addEventListener('DOMContentLoaded', function() {
    const preset = document.getElementById('pomPreset');
    const work = document.getElementById('pomWorkMinutes');
    const shortB = document.getElementById('pomShortBreak');
    const longB = document.getElementById('pomLongBreak');
    const cycles = document.getElementById('pomCycles');
    function applyPreset(p) {
        if (!p) return;
        if (p === 'classic') { work.value = 25; shortB.value = 5; longB.value = 15; cycles.value = 4; }
        else if (p === 'short') { work.value = 15; shortB.value = 3; longB.value = 10; cycles.value = 4; }
        else if (p === 'long') { work.value = 50; shortB.value = 10; longB.value = 30; cycles.value = 3; }
        // custom leaves inputs as-is
    }
    if (preset) {
        preset.addEventListener('change', function(e) {
            applyPreset(e.target.value);
            // if custom selected, focus work input
            if (e.target.value === 'custom') work.focus();
        });
        // initialize
        applyPreset(preset.value);
    }

    // load persisted pomodoro state if any
    try {
        const stored = JSON.parse(localStorage.getItem('andromeda_pomodoro'));
        if (stored && stored.enabled) {
            window.__ANDROMEDA_POMODORO = stored;
            pomodoro = { ...pomodoro, ...stored }; // sync local pomodoro object
            // reflect enabled toggle if present
            const t = document.getElementById('pomodoroToggle');
            if (t) { t.checked = true; pomodoro.enabled = true; setPomodoroStatus('Pomodoro resumed'); }
            // if there's an active timer, restart the interval
            if (stored.state && (stored.state === 'work' || stored.state === 'break') && stored.expectedEnd) {
                const now = Date.now();
                if (now < stored.expectedEnd) {
                    // timer still active, restart interval
                    pomodoro.state = stored.state;
                    pomodoro.timerRemaining = Math.max(0, Math.round((stored.expectedEnd - now) / 1000));
                    window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
                    clearExistingInterval();
                    timerInterval = setInterval(async () => {
                        if (isPaused) return;
                        pomodoro.timerRemaining = Math.max(0, Math.round((window.__ANDROMEDA_POMODORO.expectedEnd - Date.now()) / 1000));
                        window.__ANDROMEDA_POMODORO.timerRemaining = pomodoro.timerRemaining;
                        window.__ANDROMEDA_POMODORO.state = pomodoro.state;
                        localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
                        updateTimerDisplay();
                        if (pomodoro.timerRemaining <= 0) {
                            // timer finished while page was away, handle completion
                            clearExistingInterval();
                            if (pomodoro.state === 'work') {
                                await handleWorkComplete();
                            } else {
                                await handleBreakComplete();
                            }
                        }
                    }, 1000);
                    updateTimerDisplay();
                    // Update UI to show active session controls
                    document.getElementById('startBtn').style.display = 'none';
                    document.getElementById('pauseBtn').style.display = 'inline-block';
                    document.getElementById('completeBtn').style.display = 'inline-block';
                    document.getElementById('categorySelect').disabled = true;
                } else {
                    // timer expired while away, reset to idle
                    pomodoro.state = 'idle';
                    pomodoro.timerRemaining = 0;
                    window.__ANDROMEDA_POMODORO.state = 'idle';
                    window.__ANDROMEDA_POMODORO.timerRemaining = 0;
                    localStorage.setItem('andromeda_pomodoro', JSON.stringify(window.__ANDROMEDA_POMODORO));
                    setPomodoroStatus('Timer completed while away');
                    updateTimerDisplay();
                }
            }
        }
    } catch (e) { /* ignore parse errors */ }
});
