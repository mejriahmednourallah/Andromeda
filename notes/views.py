from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
import json
from .models import Note, Tag, NoteLink
from .utils import parse_note_links


# ============================================
# PAGE VIEWS
# ============================================


@login_required
def note_list(request):
    """Main notes list page - Obsidian-style sidebar"""
    return render(request, 'notes/note_list.html')


@login_required
def note_detail(request, note_id):
    """View single note"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    backlinks = note.get_backlinks()
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'backlinks': backlinks
    })


@login_required
def note_create(request):
    """Create new note page"""
    return render(request, 'notes/note_edit.html')


@login_required
def note_edit(request, note_id):
    """Edit existing note page"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    return render(request, 'notes/note_edit.html', {'note': note})


# ============================================
# API ENDPOINTS
# ============================================


@login_required
def api_notes_list(request):
    """
    GET /api/notes/
    Query params: ?search=query&tag=tagname&archived=true&pinned=true
    """
    notes = Note.objects.filter(user=request.user, is_deleted=False)

    # Filters
    search = request.GET.get('search', '')
    if search:
        notes = notes.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    tag = request.GET.get('tag', '')
    if tag:
        notes = notes.filter(tags__name=tag)

    archived = request.GET.get('archived', 'false') == 'true'
    notes = notes.filter(is_archived=archived)

    pinned = request.GET.get('pinned', '')
    if pinned == 'true':
        notes = notes.filter(is_pinned=True)

    # Prepare response
    data = []
    for note in notes:
        data.append({
            'id': note.id,
            'title': note.title,
            'slug': note.slug,
            'content_preview': note.content[:150] + '...' if len(note.content) > 150 else note.content,
            'word_count': note.get_word_count(),
            'tags': [tag.name for tag in note.tags.all()],
            'is_pinned': note.is_pinned,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
        })

    return JsonResponse({'notes': data})


@login_required
@require_http_methods(["POST"])
def api_note_create(request):
    """POST /api/notes/create/"""
    data = json.loads(request.body)

    note = Note.objects.create(
        user=request.user,
        title=data.get('title', 'Untitled Note'),
        content=data.get('content', ''),
        is_pinned=data.get('is_pinned', False)
    )

    # Add tags
    tag_names = data.get('tags', [])
    for tag_name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
        note.tags.add(tag)

    # Parse links
    parse_note_links(note)

    return JsonResponse({
        'success': True,
        'note_id': note.id,
        'message': 'Note created successfully'
    })


@login_required
@require_http_methods(["POST"])
def api_note_update(request, note_id):
    """POST /api/notes/{id}/update/"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    data = json.loads(request.body)

    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.is_pinned = data.get('is_pinned', note.is_pinned)
    note.save()

    # Update tags
    if 'tags' in data:
        note.tags.clear()
        for tag_name in data['tags']:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            note.tags.add(tag)

    # Re-parse links
    parse_note_links(note)

    return JsonResponse({
        'success': True,
        'message': 'Note updated successfully'
    })


@login_required
@require_http_methods(["POST"])
def api_note_delete(request, note_id):
    """POST /api/notes/{id}/delete/ - Soft delete"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)

    note.is_deleted = True
    note.deleted_at = timezone.now()
    note.save()

    return JsonResponse({
        'success': True,
        'message': 'Note moved to trash'
    })


@login_required
@require_http_methods(["POST"])
def api_note_restore(request, note_id):
    """POST /api/notes/{id}/restore/"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=True)

    note.is_deleted = False
    note.deleted_at = None
    note.save()

    return JsonResponse({
        'success': True,
        'message': 'Note restored'
    })


@login_required
@require_http_methods(["POST"])
def api_note_pin(request, note_id):
    """POST /api/notes/{id}/pin/"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    note.is_pinned = not note.is_pinned
    note.save()

    return JsonResponse({
        'success': True,
        'is_pinned': note.is_pinned
    })


@login_required
@require_http_methods(["POST"])
def api_note_archive(request, note_id):
    """POST /api/notes/{id}/archive/"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    note.is_archived = not note.is_archived
    note.save()

    return JsonResponse({
        'success': True,
        'is_archived': note.is_archived
    })


@login_required
def api_tags_list(request):
    """GET /api/tags/"""
    tags = Tag.objects.annotate(note_count=Count('notes')).order_by('name')

    data = [{
        'name': tag.name,
        'color': tag.color,
        'count': tag.note_count
    } for tag in tags]

    return JsonResponse({'tags': data})


@login_required
def api_note_autosave(request, note_id):
    """POST /api/notes/{id}/autosave/ - Auto-save draft"""
    note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
    data = json.loads(request.body)

    note.content = data.get('content', note.content)
    note.title = data.get('title', note.title)
    note._skip_link_parsing = True  # Skip auto-parsing on autosave
    note.save()

    return JsonResponse({
        'success': True,
        'saved_at': timezone.now().isoformat()
    })


@login_required
def api_note_detail(request, note_id):
    """GET /api/notes/{id}/ - Return full note data as JSON"""
    try:
        note = get_object_or_404(Note, id=note_id, user=request.user, is_deleted=False)
        # Build backlinks safely: query NoteLink and select_related the source Note so
        # we always get Note objects for source_note (avoids unexpected attribute errors).
        backlink_links = NoteLink.objects.filter(target_note=note).select_related('source_note')
        backlinks_list = []
        for l in backlink_links:
            src = getattr(l, 'source_note', None)
            if src is None:
                continue
            # Ensure we don't raise if title is missing for some unexpected object
            title = getattr(src, 'title', None) or ''
            backlinks_list.append({'id': getattr(src, 'id', None), 'title': title})

        data = {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'tags': [t.name for t in note.tags.all()],
            'is_pinned': note.is_pinned,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'backlinks': backlinks_list
        }
        return JsonResponse({'note': data})
    except Exception as e:
        import traceback
        print("Error in api_note_detail:", str(e))
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
