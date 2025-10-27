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

  // AI convert button: convert markdown to plain text via AI and retype into editor
  const aiBtn = document.getElementById('aiConvertBtn');
  async function aiConvertToPlain(){
    if(!contentEl) return;
    aiBtn.disabled = true;
    const originalLabel = aiBtn.title;
    aiBtn.title = 'Converting...';

    try{
      // ensure the note exists
      if(!noteId){
        await createNote();
      }

      const csrftoken = getCookie('csrftoken');
      const res = await fetch('/notes/api/notes/' + noteId + '/convert/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
        body: JSON.stringify({ mode: 'to_plain', save: false })
      });
      const data = await res.json();
      if(!data || !data.converted){
        throw new Error(data && data.error ? data.error : 'Conversion failed');
      }

      const converted = data.converted;
      // If very long text, replace directly; otherwise animate typing for UX
      const MAX_ANIMATE = 3000;
      contentEl.focus();
      if(converted.length > MAX_ANIMATE){
        contentEl.value = converted;
      } else {
        contentEl.value = '';
        let i = 0;
        const speed = 2; // ms per character (fast)
        await new Promise((resolve)=>{
          const iv = setInterval(()=>{
            contentEl.value += converted.charAt(i);
            i++;
            // maintain caret at end
            contentEl.selectionStart = contentEl.selectionEnd = contentEl.value.length;
            if(i >= converted.length){ clearInterval(iv); resolve(); }
          }, speed);
        });
      }

      // trigger autosave (saveDraft defined above)
      if(typeof saveDraft === 'function'){
        saveDraft();
      }

    }catch(err){
      console.error('AI convert error', err);
      alert('AI conversion failed: ' + (err.message || 'unknown'));
    } finally {
      aiBtn.disabled = false;
      aiBtn.title = originalLabel;
    }
  }

  aiBtn && aiBtn.addEventListener('click', function(){
    if(!confirm('Convert this note from Markdown to plain text using AI? The editor will be updated and autosaved.')) return;
    aiConvertToPlain();
  });

  // AI convert plain text -> markdown
  const aiToMdBtn = document.getElementById('aiToMdBtn');
  async function aiConvertToMarkdown(){
    if(!contentEl) return;
    aiToMdBtn.disabled = true;
    const originalLabel = aiToMdBtn.title;
    aiToMdBtn.title = 'Converting...';
    try{
      if(!noteId){ await createNote(); }
      const csrftoken = getCookie('csrftoken');
      const res = await fetch('/notes/api/notes/' + noteId + '/convert/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
        body: JSON.stringify({ mode: 'to_markdown', save: false })
      });
      const data = await res.json();
      if(!data || !data.converted){ throw new Error(data && data.error ? data.error : 'Conversion failed'); }
      const converted = data.converted;
      // For markdown results we usually want it directly in the editor
      contentEl.value = converted;
      // autosave
      if(typeof saveDraft === 'function'){ saveDraft(); }
    }catch(err){
      console.error('AI to MD error', err);
      alert('AI conversion to Markdown failed: ' + (err.message || 'unknown'));
    } finally {
      aiToMdBtn.disabled = false;
      aiToMdBtn.title = originalLabel;
    }
  }
  aiToMdBtn && aiToMdBtn.addEventListener('click', function(){
    if(!confirm('Convert this note from plain text to Markdown using AI? The editor will be updated and autosaved.')) return;
    aiConvertToMarkdown();
  });

  // PDF Download button
  const previewBtn = document.getElementById('previewMdBtn');
  const previewPane = document.getElementById('previewPane');
  const previewContent = document.getElementById('previewContent');
  let markedLoaded = false;

  function loadMarked(){
    return new Promise((resolve, reject)=>{
      if(window.marked){ markedLoaded = true; return resolve(); }
      const s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
      s.onload = function(){ markedLoaded = true; resolve(); };
      s.onerror = function(){ reject(new Error('Failed to load markdown renderer')); };
      document.head.appendChild(s);
    });
  }

  async function downloadPDF(){
    try{
      // Load marked
      await loadMarked();

      // Load html2pdf if needed
      if(!window.html2pdf){
        await new Promise((res, rej)=>{
          const s = document.createElement('script');
          s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
          s.onload = res;
          s.onerror = ()=>rej(new Error('Failed to load html2pdf'));
          document.head.appendChild(s);
        });
      }

      let md = contentEl ? contentEl.value : '';
      const title = titleEl ? titleEl.value || 'Untitled Note' : 'Untitled Note';

      // Convert wiki-links [[Title]] into plain text
      md = md.replace(/\[\[([^\]]+)\]\]/g, function(_, inner){
        const linkTitle = inner.trim();
        return linkTitle;
      });

      // Render markdown to HTML
      const html = window.marked ? window.marked.parse(md) : ('<pre>' + md.replace(/</g,'&lt;') + '</pre>');

      // Create a temporary element for PDF generation
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = `
        <div style="font-family: 'Courier New', monospace; padding: 40px; max-width: 800px; margin: 0 auto;">
          <h1 style="color: #2C2C2C; border-bottom: 2px solid #000000; padding-bottom: 10px; margin-bottom: 30px;">${title.replace(/</g,'&lt;')}</h1>
          <div style="line-height: 1.6; color: #2C2C2C;">${html}</div>
        </div>
      `;

      // PDF options
      const options = {
        margin: 1,
        filename: `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
      };

      // Generate and download PDF
      await window.html2pdf().set(options).from(tempDiv).save();

    }catch(err){
      console.error('PDF generation error', err);
      alert('Could not generate PDF. Please try again.');
    }
  }

  previewBtn && previewBtn.addEventListener('click', function(){ downloadPDF(); });

  // small helpers for escaping attributes/values used when building wiki-link anchors
  function escapeHtmlAttr(s){ return (s||'').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function escapeHtml(s){ return (s||'').replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
});
