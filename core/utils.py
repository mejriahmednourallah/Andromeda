import re
from .models import Note, Link


def parse_note_links(note):
    pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, note.body or '')
    created_links = []
    # Remove old outgoing links from this note
    Link.objects.filter(src=note).delete()
    for title in matches:
        try:
            target = Note.objects.filter(title__iexact=title.strip(), owner=note.owner).first()
            if not target or target.id == note.id:
                continue
            link, created = Link.objects.get_or_create(src=note, dst=target)
            if created:
                created_links.append(link)
        except Note.DoesNotExist:
            continue
    return created_links


def rebuild_all_links(user):
    total_links = 0
    for note in Note.objects.filter(owner=user):
        links = parse_note_links(note)
        total_links += len(links)
    return total_links
