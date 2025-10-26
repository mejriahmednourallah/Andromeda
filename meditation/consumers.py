import json
from channels.generic.websocket import AsyncWebsocketConsumer


class FocusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.user is None or self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f'focus_{self.user.id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'timer_tick':
            await self.send(text_data=json.dumps({'type': 'timer_tick', 'elapsed_minutes': data.get('elapsed_minutes')}))

    async def session_update(self, event):
        await self.send(text_data=json.dumps(event))
