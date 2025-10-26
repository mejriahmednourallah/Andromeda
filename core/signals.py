from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Note, Link
from .utils import parse_note_links
try:
    from channels.layers import get_channel_layer
except Exception:
    get_channel_layer = None
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Note)
def update_note_links(sender, instance, created, **kwargs):
    if hasattr(instance, '_skip_link_parsing'):
        return
    parse_note_links(instance)
    # Broadcast update if channel layer available
    if get_channel_layer is None:
        return
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    room_group_name = f'graph_{instance.owner.id}'
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {'type': 'graph_update', 'action': 'refresh', 'note_id': str(instance.id)}
    )
