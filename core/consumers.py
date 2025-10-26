import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GraphConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f'graph_{self.user.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({'type': 'pong', 'message': 'graph active'}))

    async def graph_update(self, event):
        await self.send(text_data=json.dumps({'type': 'graph_update', 'action': event.get('action', 'refresh'), 'note_id': event.get('note_id')}))
