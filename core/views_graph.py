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

    nodes = []
    for note in notes:
        outgoing = note.outgoing_links.count()
        incoming = note.incoming_links.count()
        nodes.append({'id': str(note.id), 'title': note.title, 'connections': outgoing + incoming, 'created_at': note.created_at.isoformat()})

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
