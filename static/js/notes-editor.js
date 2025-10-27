// Notes editor: autosave, simple formatting shortcuts, link suggestions
document.addEventListener('DOMContentLoaded', function () {
  let noteId = document.getElementById('noteId') && document.getElementById('noteId').value;
  const titleEl = document.getElementById('noteTitle');
  const contentEl = document.getElementById('noteContent');
  const saveBtn = document.getElementById('saveBtn');
  const autoSaveStatus = document.getElementById('autoSaveStatus');

  let autosaveTimer = null;

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

  // Create note via API (used when on /notes/create/)
  async function createNote(){
    const csrftoken = getCookie('csrftoken');
    const res = await fetch('/notes/api/notes/create/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ title: titleEl.value || 'Untitled Note', content: contentEl.value || '' })
    });
    const data = await res.json();
    if(data && data.success && data.note_id){
      // Update local noteId and hidden input
      noteId = String(data.note_id);
      const noteIdInput = document.getElementById('noteId');
      if(noteIdInput) noteIdInput.value = noteId;
      // Update URL to the edit page without reloading
      const newUrl = '/notes/' + noteId + '/edit/';
      window.history.replaceState({}, '', newUrl);
      return noteId;
    } else {
      console.error('Failed to create note', data);
      throw new Error('Failed to create note');
    }
  }

  function saveDraft(){
    // If no noteId yet, create the note first
    if(!noteId){
      createNote().then(()=>{
        // After creation, call autosave endpoint to persist current content (server already has content)
        const csrftoken = getCookie('csrftoken');
        fetch('/notes/api/notes/' + noteId + '/autosave/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
          body: JSON.stringify({ title: titleEl.value, content: contentEl.value })
        }).then(r=>r.json()).then(data=>{
          autoSaveStatus.textContent = 'Saved';
          setTimeout(()=>autoSaveStatus.textContent = '', 1500);
        });
      }).catch(err=>{
        console.error(err);
      });
      return;
    }
    const csrftoken = getCookie('csrftoken');
    fetch('/notes/api/notes/' + noteId + '/autosave/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
      body: JSON.stringify({ title: titleEl.value, content: contentEl.value })
    }).then(r=>r.json()).then(data=>{
      autoSaveStatus.textContent = 'Saved';
      setTimeout(()=>autoSaveStatus.textContent = '', 1500);
    });
  }

  contentEl && contentEl.addEventListener('input', function(){
    document.getElementById('wordCount') && (document.getElementById('wordCount').textContent = contentEl.value.trim().split(/\s+/).filter(Boolean).length);
    document.getElementById('charCount') && (document.getElementById('charCount').textContent = contentEl.value.length);
    clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(saveDraft, 1500);
  });

  // Keyboard shortcuts for basic formatting
  document.addEventListener('keydown', function(e){
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b'){
      e.preventDefault(); wrapSelection('**','**');
    }
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i'){
      e.preventDefault(); wrapSelection('*','*');
    }
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k'){
      e.preventDefault(); insertAtCaret('[text](url)');
    }
  });

  function wrapSelection(before, after){
    const s = contentEl.selectionStart, e = contentEl.selectionEnd;
    const v = contentEl.value;
    contentEl.value = v.slice(0,s) + before + v.slice(s,e) + after + v.slice(e);
    contentEl.selectionStart = s + before.length;
    contentEl.selectionEnd = e + before.length;
    contentEl.focus();
  }

  function insertAtCaret(text){
    const s = contentEl.selectionStart, e = contentEl.selectionEnd;
    const v = contentEl.value;
    contentEl.value = v.slice(0,s) + text + v.slice(e);
    contentEl.selectionStart = contentEl.selectionEnd = s + text.length;
    contentEl.focus();
  }

  // Save button (full save)
  saveBtn && saveBtn.addEventListener('click', function(){
    const csrftoken = getCookie('csrftoken');
    // If there's no noteId yet, create the note then navigate to edit endpoint
    if(!noteId){
      createNote().then(()=>{
        // After creation, perform an update to ensure latest content is saved
        fetch('/notes/api/notes/' + noteId + '/update/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
          body: JSON.stringify({ title: titleEl.value, content: contentEl.value })
        }).then(r=>r.json()).then(data=>{ autoSaveStatus.textContent = 'Saved'; setTimeout(()=>autoSaveStatus.textContent = '',1500); });
      }).catch(err=>{ console.error(err); alert('Could not save note. See console.'); });
      return;
    }
    fetch('/notes/api/notes/' + noteId + '/update/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
      body: JSON.stringify({ title: titleEl.value, content: contentEl.value })
    }).then(r=>r.json()).then(data=>{ autoSaveStatus.textContent = 'Saved'; setTimeout(()=>autoSaveStatus.textContent = '',1500); });
  });
});
