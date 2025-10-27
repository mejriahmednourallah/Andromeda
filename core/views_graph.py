from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Note, Link
try:
    from notes.models import Note as NotesAppNote
except Exception:
    NotesAppNote = None


@login_required
def universe_graph_page(request):
    return render(request, 'notes/graph.html')


@login_required
def graph_data_api(request):
    user = request.user
    # Ensure core.Note entries exist for notes created in the notes app so orphan
    # (unlinked) notes appear in the Universe Graph. This is a best-effort sync
    # and will create minimal Core Note records for any NotesAppNote missing in core.
    if NotesAppNote is not None:
        for n in NotesAppNote.objects.filter(user=user):
            # try to find by title and owner; create if missing
            Note.objects.get_or_create(owner=user, title=n.title, defaults={'body': getattr(n, 'content', '')})

    notes = Note.objects.filter(owner=user)
    links = Link.objects.filter(src__owner=user, dst__owner=user).select_related('src', 'dst')

    # Ensure notes app has entries for all core notes so they can be opened from the graph
    if NotesAppNote is not None:
        for note in notes:
            # Ensure this core note exists in notes app
            try:
                # Try to get existing note by title
                notes_app_note = NotesAppNote.objects.filter(user=user, title=note.title).first()
                if notes_app_note is None:
                    # Create new note
                    notes_app_note = NotesAppNote.objects.create(
                        user=user,
                        title=note.title,
                        content=note.body or ''
                    )
                else:
                    # Update existing note content if different
                    if notes_app_note.content != (note.body or ''):
                        notes_app_note.content = note.body or ''
                        notes_app_note.save()
            except Exception as e:
                # If there are issues with duplicates, skip this note
                print(f"Warning: Could not sync note '{note.title}': {e}")
                continue

    nodes = []
    for note in notes:
        outgoing = note.outgoing_links.count()
        incoming = note.incoming_links.count()
        # Try to find a matching Note object from the notes app (by title + user)
        notes_app_id = None
        if NotesAppNote is not None:
            try:
                match = NotesAppNote.objects.filter(user=user, title=note.title).first()
                if match is not None:
                    notes_app_id = getattr(match, 'id', None)
            except Exception:
                notes_app_id = None

        nodes.append({
            'id': str(note.id),
            'notes_app_id': notes_app_id,
            'title': note.title,
            'connections': outgoing + incoming,
            'created_at': note.created_at.isoformat()
        })

    edges = []
    for link in links:
        edges.append({'source': str(link.src.id), 'target': str(link.dst.id), 'strength': 1.0})

    return JsonResponse({'nodes': nodes, 'edges': edges, 'stats': {'total_notes': len(nodes), 'total_links': len(edges), 'orphaned_notes': len([n for n in nodes if n['connections'] == 0])}})


@login_required
def note_detail_api(request, note_id):
    try:
        note = Note.objects.get(id=note_id, owner=request.user)
        return JsonResponse({'id': str(note.id), 'title': note.title, 'content': note.body, 'created_at': note.created_at.isoformat(), 'updated_at': note.updated_at.isoformat()})
    except Note.DoesNotExist:
        return JsonResponse({'error': 'Note not found'}, status=404)
