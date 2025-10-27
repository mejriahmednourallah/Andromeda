// Simple chase widget: a small circle that gently chases the cursor across the site
(function(){
    let widget = document.getElementById('chase-widget');
    if (!widget) {
        widget = document.createElement('div');
        widget.id = 'chase-widget';
        widget.innerHTML = '<span class="label">Me</span>';
        document.body.appendChild(widget);
    }

    // Anchor close to the right edge; widget chases cursor vertically but stays on right
    let targetY = window.innerHeight / 2;
    let y = targetY;
    const anchorRight = 48; // px from right edge
    const ease = 0.16; // lower = more lag

    function onMove(e) {
        // only track vertical movement; horizontal anchor remains at right edge
        targetY = e.clientY;
    }

    function animate() {
        const dy = targetY - y;
        y += dy * ease;
        // compute anchored x
        const x = window.innerWidth - anchorRight;
        widget.style.left = x + 'px';
        widget.style.top = y + 'px';
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
        const state = readPomodoroFromStorage();
        const timerEl = document.getElementById('chase-timer');
        const stateEl = document.getElementById('chase-state');
        if (!timerEl) return;
        if (state && state.enabled && (state.state === 'work' || state.state === 'break')) {
            // compute remaining from expectedEnd if present
            if (state.expectedEnd) {
                state.timerRemaining = Math.max(0, Math.round((state.expectedEnd - Date.now()) / 1000));
            }
            if (state.timerRemaining <= 0) {
                // hide widget when timer finished and no active state
                timerEl.textContent = '';
                stateEl.textContent = 'Idle';
                widget.style.display = 'none';
                return;
            }
            widget.style.display = 'flex';
            timerEl.textContent = formatTimeSeconds(state.timerRemaining);
            stateEl.textContent = state.state === 'work' ? 'Work' : 'Break';
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
        document.addEventListener('DOMContentLoaded', () => { document.addEventListener('mousemove', onMove); requestAnimationFrame(animate); setInterval(updateLabel, 800); });
    } else {
        document.addEventListener('mousemove', onMove);
        requestAnimationFrame(animate);
        setInterval(updateLabel, 800);
    }
})();
