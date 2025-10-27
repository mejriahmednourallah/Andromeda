// Basic notes-list frontend: loads notes, search, create shortcut, open note
document.addEventListener('DOMContentLoaded', function () {
  const notesList = document.getElementById('notesList');
  const searchInput = document.getElementById('searchInput');
  const createNoteBtn = document.getElementById('createNoteBtn');
  const emptyCreateBtn = document.getElementById('emptyCreateBtn');

  let debounceTimer = null;

  function fetchNotes(query=''){
    const url = '/notes/api/notes/?search=' + encodeURIComponent(query);
    return fetch(url, { credentials: 'same-origin' })
      .then(r=>r.json())
      .then(data=>{
        renderNotes(data.notes || []);
        return data.notes || [];
      });
  }

  const emptyState = document.getElementById('emptyState');
  const noteView = document.getElementById('noteView');

  function renderNotes(notes){
    notesList.innerHTML = '';
    if(notes.length === 0){
      notesList.innerHTML = '<p class="muted-text">No notes yet</p>';
      return;
    }
    notes.forEach(n=>{
      const el = document.createElement('div');
      el.className = 'note-item';
      el.dataset.noteId = n.id;
      el.innerHTML = `
        <div class="note-item-content">
          <strong>${escapeHtml(n.title)}</strong>
          <div class="muted-text">${escapeHtml(n.content_preview)}</div>
        </div>
        <button class="note-delete-btn" data-note-id="${n.id}" title="Delete note" type="button">
          <i class="fas fa-trash"></i>
        </button>
      `;
      el.addEventListener('click', (e)=>{ 
        // Only trigger if not clicking the delete button
        if (!e.target.closest('.note-delete-btn')) {
          e.preventDefault(); 
          e.stopPropagation(); 
          showNoteDetail(n.id, el); 
        }
      });
      // Remove any hrefs that might cause navigation (defensive)
      el.querySelectorAll('a').forEach(a=>{ a.removeAttribute('href'); a.addEventListener('click', (ev)=>{ ev.preventDefault(); ev.stopPropagation(); }); });
      notesList.appendChild(el);
    });
  }

  // Prevent anchor clicks inside the notes list from causing a navigation
  notesList.addEventListener('click', function(e){
    const a = e.target.closest && e.target.closest('a');
    if(a && a.getAttribute && a.getAttribute('href') && a.getAttribute('href').startsWith('/notes/')){
      e.preventDefault();
      e.stopPropagation();
      const m = a.getAttribute('href').match(/\/notes\/(\d+)\/?.*/);
      if(m && m[1]){
        const el = document.querySelector('#notesList .note-item[data-note-id="' + m[1] + '"]');
        showNoteDetail(m[1], el);
      }
    }
  });

  // Fetch and show a note inline in the main area (no page navigation)
  async function showNoteDetail(noteId, clickedEl){
    try{
      const res = await fetch('/notes/api/notes/' + noteId + '/', { credentials: 'same-origin' });
      if(!res.ok) throw new Error('Failed to load note');
      const data = await res.json();
      const note = data.note;
      renderNoteView(note);  // Show read-only detail; user can click KEEP WRITING to open full editor
      // mark active in list
      document.querySelectorAll('#notesList .note-item').forEach(el=>el.classList.remove('active'));
      if(clickedEl) clickedEl.classList.add('active');
    }catch(err){
      console.error(err);
      alert('Could not load note. See console.');
    }
  }

  function renderNoteView(note){
    if(!noteView || !emptyState) return;
    emptyState.style.display = 'none';
    noteView.style.display = 'block';
    noteView.setAttribute('aria-hidden','false');
    const tagsHtml = (note.tags || []).map(t=>`<span class="tag">${escapeHtml(t)}</span>`).join(' ');
    const backlinksHtml = (note.backlinks || []).length ? `<ul>${note.backlinks.map(b=>`<li><a href="#" data-id="${b.id}" class="bl-link">${escapeHtml(b.title)}</a></li>`).join('')}</ul>` : '<p class="muted-text">No backlinks yet.</p>';
    const contentHtml = escapeHtml(note.content || '').replace(/\n/g,'<br>');
    noteView.innerHTML = `
      <div class="note-detail card">
        <div class="note-detail-header">
          <h2 class="note-title">${escapeHtml(note.title || 'Untitled')}</h2>
          <div class="note-actions">
            <button id="editNoteBtn" class="btn-primary">KEEP WRITING</button>
            <button id="backToListBtn" class="btn-secondary">BACK</button>
          </div>
        </div>
        <div class="note-meta muted-text">Created: ${escapeHtml(note.created_at)} &nbsp; Updated: ${escapeHtml(note.updated_at)}</div>
        <div class="note-tags">${tagsHtml}</div>
        <div class="note-content">${contentHtml}</div>
        <aside class="note-backlinks"><h3>Backlinks</h3>${backlinksHtml}</aside>
      </div>
    `;

    // Attach handlers
  const editBtn = document.getElementById('editNoteBtn');
  if(editBtn) editBtn.addEventListener('click', ()=>{ window.location.href = '/notes/' + note.id + '/edit/'; });
    const backBtn = document.getElementById('backToListBtn');
    if(backBtn) backBtn.addEventListener('click', ()=>{ noteView.style.display='none'; emptyState.style.display='block'; document.querySelectorAll('#notesList .note-item').forEach(el=>el.classList.remove('active')); });
    // backlinks links navigate to inline view
    document.querySelectorAll('.bl-link').forEach(a=>{
      a.addEventListener('click', (e)=>{ e.preventDefault(); const id = a.dataset.id; const el = document.querySelector('#notesList .note-item[data-note-id="' + id + '"]'); showNoteDetail(id, el); });
    });
  }

  // Render a minimal inline editor inside noteView (title, tags, pin, content)
  function renderInlineEditor(note){
    if(!noteView) return;
    emptyState.style.display = 'none';
    noteView.style.display = 'block';
    noteView.setAttribute('aria-hidden','false');
    const tagsValue = (note.tags || []).join(', ');
    // Keep an immutable copy of the note so Cancel can restore the original view
    const originalNote = JSON.parse(JSON.stringify(note));
    noteView.innerHTML = `
      <div class="note-edit-inline card">
        <div class="editor-toolbar">
          <div class="toolbar-left">
            <button id="inlineEditBtn" class="btn-primary">EDIT</button>
            <button id="inlineCancelBtn" class="btn-secondary">CANCEL</button>
            <span id="inlineAutoSaveStatus" class="autosave-status"></span>
          </div>
        </div>
        <div class="editor-content">
          <input type="text" id="inlineNoteTitle" class="note-title-input" value="${escapeHtml(note.title || '')}">
          <div class="editor-meta">
            <input type="text" id="inlineNoteTags" class="note-tags-input" value="${escapeHtml(tagsValue)}">
            <label class="pin-checkbox"><input type="checkbox" id="inlineIsPinned" ${note.is_pinned ? 'checked' : ''}><span>PIN NOTE</span></label>
          </div>
          <textarea id="inlineNoteContent" class="note-content-editor" placeholder="Start writing...">${escapeHtml(note.content || '')}</textarea>
        </div>
      </div>
    `;

    const inlineSaveBtn = document.getElementById('inlineSaveBtn');
    const inlineSaveDraftBtn = document.getElementById('inlineSaveDraftBtn');
    const inlineTitle = document.getElementById('inlineNoteTitle');
    const inlineTags = document.getElementById('inlineNoteTags');
    const inlinePinned = document.getElementById('inlineIsPinned');
    const inlineContent = document.getElementById('inlineNoteContent');
    const inlineStatus = document.getElementById('inlineAutoSaveStatus');

    let inlineTimer = null;
    inlineContent.addEventListener('input', ()=>{
      clearTimeout(inlineTimer);
      inlineTimer = setTimeout(()=>{ inlineAutoSave(note.id); }, 1500);
    });

    // Edit button navigates to the full edit page for this note
    const inlineEditBtn = document.getElementById('inlineEditBtn');
    if(inlineEditBtn){
      inlineEditBtn.addEventListener('click', ()=>{
        // Navigate to the edit page handled by Django: /notes/<id>/edit/
        window.location.href = '/notes/' + note.id + '/edit/';
      });
    }

    // Cancel button: discard changes and restore the read-only note view
    const inlineCancelBtn = document.getElementById('inlineCancelBtn');
    if(inlineCancelBtn){
      inlineCancelBtn.addEventListener('click', ()=>{
        // Render the original note detail without saving
        renderNoteView(originalNote);
      });
    }

    async function inlineAutoSave(id){
      try{
        const csrftoken = getCookie('csrftoken');
        await fetch('/notes/api/notes/' + id + '/autosave/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
          body: JSON.stringify({ title: inlineTitle.value, content: inlineContent.value })
        });
        inlineStatus.textContent = 'Saved';
        setTimeout(()=>inlineStatus.textContent='',1500);
      }catch(err){ console.error(err); }
    }
  }

  function escapeHtml(s){ return (s||'').replace(/[&<>\"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  searchInput.addEventListener('input', function(){
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(()=>{ fetchNotes(searchInput.value.trim()); }, 200);
  });

  // Redirect to the 'create note' page instead of creating via API
  function createNewNote(){
    // Prefer a URL provided by the template (data-create-url) so the path is
    // generated by Django's {% url %} and remains correct across deployments.
    const fromCreateBtn = createNoteBtn && createNoteBtn.dataset && createNoteBtn.dataset.createUrl;
    const fromEmptyBtn = emptyCreateBtn && emptyCreateBtn.dataset && emptyCreateBtn.dataset.createUrl;
    const createUrl = fromCreateBtn || fromEmptyBtn || '/notes/create/';
    window.location = createUrl;
  }

  // Helper to read CSRF token cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Bind create actions
  createNoteBtn.addEventListener('click', function(){ createNewNote(); });
  if(emptyCreateBtn){ emptyCreateBtn.addEventListener('click', function(){ createNewNote(); }); }

  // Delete functionality
  let noteToDelete = null;
  const deleteModal = document.getElementById('deleteModal');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

  // Handle delete button clicks
  notesList.addEventListener('click', function(e){
    const deleteBtn = e.target.closest('.note-delete-btn');
    if(deleteBtn){
      e.stopPropagation();
      const noteId = deleteBtn.dataset.noteId;
      noteToDelete = noteId;
      deleteModal.style.display = 'flex';
      deleteModal.setAttribute('aria-hidden', 'false');
    }
  });

  // Handle delete confirmation
  if(confirmDeleteBtn){
    confirmDeleteBtn.addEventListener('click', async function(){
      if(noteToDelete){
        try{
          const csrftoken = getCookie('csrftoken');
          const res = await fetch('/notes/api/notes/' + noteToDelete + '/delete/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
              'X-CSRFToken': csrftoken
            }
          });
          if(res.ok){
            // Refresh the notes list
            fetchNotes();
            // Hide the note view if it was showing the deleted note
            if(noteView.style.display !== 'none'){
              noteView.style.display = 'none';
              emptyState.style.display = 'block';
            }
          }else{
            alert('Failed to delete note');
          }
        }catch(err){
          console.error('Delete error:', err);
          alert('Failed to delete note');
        }
      }
      deleteModal.style.display = 'none';
      deleteModal.setAttribute('aria-hidden', 'true');
      noteToDelete = null;
    });
  }

  // Handle delete cancellation
  if(cancelDeleteBtn){
    cancelDeleteBtn.addEventListener('click', function(){
      deleteModal.style.display = 'none';
      deleteModal.setAttribute('aria-hidden', 'true');
      noteToDelete = null;
    });
  }

  // Close modal on escape key
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && deleteModal.style.display === 'flex'){
      deleteModal.style.display = 'none';
      deleteModal.setAttribute('aria-hidden', 'true');
      noteToDelete = null;
    }
  });

  // Keyboard shortcut: Ctrl+N to create
  document.addEventListener('keydown', function(e){
    if((e.ctrlKey || e.metaKey) && e.key === 'n'){
      e.preventDefault();
      createNewNote();
    }
  });

  // Initial load
  fetchNotes().then(()=>{
    // If URL includes ?open=<id>, open that note in the inline view (useful when navigating from graph)
    try{
      const params = new URLSearchParams(window.location.search);
      const openId = params.get('open');
      if(openId){
        // Try to find the element in the list and trigger show
        const el = document.querySelector('#notesList .note-item[data-note-id="' + openId + '"]');
        if(el){
          // Simulate click
          el.click();
        } else {
          // If not yet rendered (or not in list due to paging), directly call showNoteDetail
          showNoteDetail(openId, null);
        }
      }
    }catch(e){ console.warn('open param handling failed', e); }
  });
});
