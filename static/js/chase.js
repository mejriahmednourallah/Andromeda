// Simple chase widget: a small circle that gently chases the cursor across the site
(function(){
    let widget = document.getElementById('chase-widget');
    if (!widget) {
        widget = document.createElement('div');
        widget.id = 'chase-widget';
        widget.innerHTML = '<span class="label">Me</span>';
        document.body.appendChild(widget);
    }

    // Position fixed in top left corner under nav bar
    const navHeight = 80; // approximate nav height
    const margin = 20; // margin from edges

    function positionWidget() {
        widget.style.position = 'fixed';
        widget.style.left = margin + 'px';
        widget.style.top = navHeight + margin + 'px';
        widget.style.zIndex = '1000';
    }

    // No mouse following needed
    function animate() {
        // Just ensure position is correct
        positionWidget();
        requestAnimationFrame(animate);
    }

    // Start only after DOM loaded
    function readPomodoroFromStorage() {
        try {
            const stored = JSON.parse(localStorage.getItem('andromeda_pomodoro'));
            if (stored && stored.enabled) return stored;
        } catch (e) {}
        // also check window variable if set
        if (window.__ANDROMEDA_POMODORO && window.__ANDROMEDA_POMODORO.enabled) return window.__ANDROMEDA_POMODORO;
        return null;
    }

    function isChaseVisible() {
        return localStorage.getItem('andromeda_chase_visible') !== 'false'; // default true
    }

    function formatTimeSeconds(s) {
        const minutes = Math.floor(s / 60);
        const seconds = Math.max(0, s % 60);
        return `${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`;
    }

    // Build widget HTML structure (collapsed view + details panel)
    widget.classList.add('collapsed');
    widget.innerHTML = `
        <div class="collapsed-view">
            <div class="timer" id="chase-timer">--:--</div>
        </div>
        <div class="details" id="chase-details">
            <div class="title">Pomodoro</div>
            <div class="state" id="chase-state">Idle</div>
            <div class="chase-actions">
                <button id="chase-pause">Pause</button>
                <button id="chase-resume" class="secondary">Resume</button>
                <button id="chase-skip" class="secondary">Skip</button>
                <button id="chase-open" class="secondary">Open Focus</button>
            </div>
        </div>
    `;

    let collapseTimer = null;

    function setCollapsed(v) {
        if (v) { widget.classList.remove('open'); widget.classList.add('collapsed'); }
        else { widget.classList.remove('collapsed'); widget.classList.add('open'); }
    }

    function scheduleCollapse() {
        if (collapseTimer) clearTimeout(collapseTimer);
        collapseTimer = setTimeout(() => setCollapsed(true), 900);
    }

    function cancelCollapse() { if (collapseTimer) { clearTimeout(collapseTimer); collapseTimer = null; } }

    function updateLabel() {
        if (!isChaseVisible()) {
            widget.style.display = 'none';
            return;
        }
        const state = readPomodoroFromStorage();
        const timerEl = document.getElementById('chase-timer');
        const stateEl = document.getElementById('chase-state');
        if (!timerEl) return;
        if (state && state.enabled) {
            widget.style.display = 'flex';
            if (state.state === 'work' || state.state === 'break') {
                // compute remaining from expectedEnd if present
                if (state.expectedEnd) {
                    state.timerRemaining = Math.max(0, Math.round((state.expectedEnd - Date.now()) / 1000));
                }
                if (state.timerRemaining <= 0) {
                    // timer finished
                    timerEl.textContent = '';
                    stateEl.textContent = 'Idle';
                    return;
                }
                timerEl.textContent = formatTimeSeconds(state.timerRemaining);
                stateEl.textContent = state.state === 'work' ? 'Work' : 'Break';
            } else {
                // pomodoro enabled but idle
                timerEl.textContent = '';
                stateEl.textContent = 'Ready';
            }
        } else {
            // no active pomodoro; hide widget entirely
            timerEl.textContent = '';
            stateEl.textContent = 'Idle';
            widget.style.display = 'none';
        }
    }

    // click toggles open/close
    widget.addEventListener('click', function(e) {
        // if clicking a button inside details, let button handlers run
        const btn = e.target.closest('button');
        if (btn) return;
        const isOpen = widget.classList.contains('open');
        setCollapsed(isOpen);
    });

    // collapse on mouseleave
    widget.addEventListener('mouseleave', function() { scheduleCollapse(); });
    widget.addEventListener('mouseenter', function() { cancelCollapse(); });

    // action buttons: write an action to localStorage so focus page (if open) processes it
    function sendAction(action) {
        try { localStorage.setItem('andromeda_pomodoro_action', JSON.stringify({ action: action, ts: Date.now() })); } catch (e) { console.error(e); }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // attach handlers (use event delegation-safe query)
        document.getElementById('chase-pause')?.addEventListener('click', function(e){ e.stopPropagation(); sendAction('pause'); this.textContent = 'Sent'; setTimeout(()=>this.textContent='Pause',800); });
        document.getElementById('chase-resume')?.addEventListener('click', function(e){ e.stopPropagation(); sendAction('resume'); this.textContent = 'Sent'; setTimeout(()=>this.textContent='Resume',800); });
        document.getElementById('chase-skip')?.addEventListener('click', function(e){ e.stopPropagation(); sendAction('complete'); this.textContent = 'Sent'; setTimeout(()=>this.textContent='Skip',800); });
        document.getElementById('chase-open')?.addEventListener('click', function(e){ e.stopPropagation(); window.location.href = '/focus/'; });
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { positionWidget(); requestAnimationFrame(animate); setInterval(updateLabel, 800); });
    } else {
        positionWidget();
        requestAnimationFrame(animate);
        setInterval(updateLabel, 800);
    }

    // Listen for visibility changes from focus page
    window.addEventListener('storage', function(e) {
        if (e.key === 'andromeda_chase_action') {
            try {
                const action = JSON.parse(e.newValue);
                if (action.action === 'visibility_change') {
                    updateLabel(); // re-check visibility
                }
                localStorage.removeItem('andromeda_chase_action');
            } catch (err) {}
        }
    });
})();
