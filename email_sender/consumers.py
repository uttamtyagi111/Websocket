import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EmailStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"email_status_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        print(f"WebSocket connected for user: {self.user_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"WebSocket disconnected for user: {self.user_id}")

    async def receive(self, text_data):
        pass

    async def send_status_update(self, event):
        status = event["status"]
        email = event["email"]
        timestamp = event["timestamp"]

        await self.send(
            text_data=json.dumps(
                {"email": email, "status": status, "timestamp": timestamp}
            )
        )
