import re
from .models import Note, NoteLink

# Optional sync to core graph models (keeps universe graph in sync with notes app)
try:
    from core.models import Note as CoreNote, Link as CoreLink
except Exception:
    CoreNote = None
    CoreLink = None


LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


def parse_note_links(note):
    """Parse the note content for [[Other Note]] links and update NoteLink entries.

    This looks for [[Note Title]] patterns, tries to find a Note with that title
    belonging to the same user, and creates NoteLink records between source and
    target. It removes links that are no longer present.
    """
    if not hasattr(note, 'content'):
        return

    matches = LINK_PATTERN.findall(note.content or '')
    target_titles = set([m.strip() for m in matches if m.strip()])

    # Current outgoing targets (by title)
    existing_targets = set(note.outgoing_links.values_list('target_note__title', flat=True))

    # Add new links (create NoteLink and mirror to core graph when possible)
    for title in target_titles - existing_targets:
        target = Note.objects.filter(user=note.user, title=title).first()
        if not target:
            # Target doesn't exist (could be a future note); skip for now
            continue

        NoteLink.objects.get_or_create(source_note=note, target_note=target)

        # Mirror into core graph (best-effort)
        if CoreNote and CoreLink:
            try:
                src_core, _ = CoreNote.objects.get_or_create(owner=note.user, title=note.title, defaults={'body': note.content})
                dst_core, _ = CoreNote.objects.get_or_create(owner=target.user, title=target.title, defaults={'body': target.content})
                CoreLink.objects.get_or_create(src=src_core, dst=dst_core)
            except Exception:
                # Non-fatal: don't block note saving for graph sync failures
                pass

    # Remove links that were deleted from content (and mirror removals)
    for title in existing_targets - target_titles:
        target = Note.objects.filter(user=note.user, title=title).first()
        if not target:
            continue

        NoteLink.objects.filter(source_note=note, target_note=target).delete()

        if CoreNote and CoreLink:
            try:
                src_core = CoreNote.objects.filter(owner=note.user, title=note.title).first()
                dst_core = CoreNote.objects.filter(owner=target.user, title=target.title).first()
                if src_core and dst_core:
                    CoreLink.objects.filter(src=src_core, dst=dst_core).delete()
            except Exception:
                pass
