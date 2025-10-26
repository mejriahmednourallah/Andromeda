// Universe Graph JavaScript - Cytoscape.js + WebSocket
let cy = null; let ws = null; let currentNoteId = null;

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/graph/`);
    ws.onmessage = function(event) { const data = JSON.parse(event.data); if (data.type === 'graph_update') { loadGraphData(); } };
    ws.onerror = function(error) { console.error('WebSocket error:', error); };
}

function initCytoscape() {
    cy = cytoscape({
        container: document.getElementById('graphCanvas'),
        style: [
            { selector: 'node', style: {
                'background-color': '#000000',
                'border-width': 0,
                'label': 'data(title)',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'text-margin-y': 6,
                'color': '#000000',
                'font-size': '11px',
                'font-weight': '600',
                'font-family': 'ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace',
                'width': 'data(size)',
                'height': 'data(size)',
                'text-wrap': 'ellipsis',
                'text-max-width': 140
            } },
            { selector: 'node:hover', style: {
                'border-width': 0,
                'label': 'data(title)',
                'font-size': '12px',
                'z-index': 9999
            } },
            { selector: 'node:selected', style: {
                'border-width': 0,
                'label': 'data(title)',
                'font-size': '12px',
                'z-index': 9999
            } },
            { selector: 'edge', style: {
                'width': 1,
                'line-color': '#E6E6E6',
                'curve-style': 'bezier',
                'opacity': 0.6,
                'source-arrow-shape': 'none',
                'target-arrow-shape': 'none'
            } },
            { selector: 'edge.highlight', style: { 'line-color': '#FF8C42', 'opacity': 0.95, 'width': 2 } }
        ],
        layout: { name: 'cose', animate: true, randomize: false, idealEdgeLength: 80, nodeOverlap: 12, gravity: 0.1 },
        wheelSensitivity: 0.2,
        zoomingEnabled: true,
        panningEnabled: true
    });

    // Interaction handlers
    cy.on('tap', 'node', function(evt) { const node = evt.target; openNotePanel(node.id()); });
    cy.on('dbltap', 'node', function(evt) { const node = evt.target; window.location.href = `/notes/${node.id()}/`; });

    // Hover / neighbor highlight
    cy.on('mouseover', 'node', function(evt) {
        const node = evt.target;
        cy.elements().addClass('dimmed');
        node.removeClass('dimmed');
        const neighborhood = node.closedNeighborhood();
        neighborhood.removeClass('dimmed');
        neighborhood.connectedEdges().addClass('highlight');
    });
    cy.on('mouseout', 'node', function(evt) {
        cy.elements().removeClass('dimmed');
        cy.edges().removeClass('highlight');
    });

    // allow drag + zoom fit on load
    cy.on('layoutstop', () => { cy.fit(50); });
}

const dimmedStyle = document.createElement('style'); dimmedStyle.textContent = `.dimmed { opacity: 0.2 !important; }`; document.head.appendChild(dimmedStyle);

async function loadGraphData() {
    try {
        document.getElementById('loadingOverlay').style.display = 'flex';
        const response = await fetch('/graph/api/graph/');
        const data = await response.json();
        document.getElementById('totalNotes').textContent = data.stats.total_notes;
        document.getElementById('totalLinks').textContent = data.stats.total_links;
        document.getElementById('orphanedNotes').textContent = data.stats.orphaned_notes;
        if (data.nodes.length === 0) {
            document.getElementById('loadingOverlay').style.display = 'none';
            document.getElementById('emptyState').style.display = 'flex';
            return;
        }
        document.getElementById('emptyState').style.display = 'none';
        if (cy) { cy.elements().remove(); }

        // Prepare nodes with sizes for white-background black-dot look
        const maxConn = Math.max(1, ...data.nodes.map(n => n.connections));
        const nodes = data.nodes.map(n => {
            const size = Math.max(12, Math.min(56, 12 + Math.round((n.connections / maxConn) * 44)));
            return { data: { id: n.id, title: n.title, connections: n.connections, created_at: n.created_at, size: size } };
        });
        const edges = data.edges.map(e => ({ data: { id: `${e.source}-${e.target}`, source: e.source, target: e.target, strength: e.strength } }));
        cy.add(nodes); cy.add(edges);
        cy.layout({ name: 'cose', animate: true, randomize: false, idealEdgeLength: 80 }).run();
        setTimeout(() => { document.getElementById('loadingOverlay').style.display = 'none'; }, 800);
    } catch (error) { console.error('Error loading graph:', error); document.getElementById('loadingOverlay').innerHTML = `<i class="fas fa-exclamation-triangle fa-3x" style="color:#FF8C42;"></i><p style="color:#FF8C42;">Failed to load graph. Please refresh.</p>`; }
}

async function openNotePanel(noteId) {
    currentNoteId = noteId;
    try {
        const response = await fetch(`/graph/api/notes/${noteId}/`);
        const note = await response.json();
        document.getElementById('notePanelTitle').textContent = note.title;
        const created = new Date(note.created_at); const updated = new Date(note.updated_at);
        document.getElementById('noteCreated').textContent = `Created: ${created.toLocaleDateString()}`;
        document.getElementById('noteUpdated').textContent = `Updated: ${updated.toLocaleDateString()}`;
        const preview = note.content.substring(0,300) + (note.content.length>300? '...' : '');
        document.getElementById('noteContent').textContent = preview;
        document.getElementById('openNoteBtn').href = `/notes/${noteId}/`;
        document.getElementById('editNoteBtn').href = `/notes/${noteId}/edit/`;
        const panel = document.getElementById('notePanel'); panel.style.display = 'flex'; setTimeout(() => panel.classList.add('active'), 10);
    } catch (error) { console.error('Error loading note:', error); alert('Failed to load note details'); }
}

function closeNotePanel() { const panel = document.getElementById('notePanel'); panel.classList.remove('active'); setTimeout(() => panel.style.display = 'none', 300); currentNoteId = null; if (cy) cy.nodes().unselect(); }
document.getElementById('closePanelBtn')?.addEventListener('click', closeNotePanel);
document.addEventListener('keydown', function(e) { if (e.key === 'Escape' && currentNoteId) closeNotePanel(); });

document.addEventListener('DOMContentLoaded', function() { initCytoscape(); initWebSocket(); loadGraphData(); });
let resizeTimeout; window.addEventListener('resize', function() { clearTimeout(resizeTimeout); resizeTimeout = setTimeout(() => { if (cy) { cy.resize(); cy.fit(); } }, 250); });
