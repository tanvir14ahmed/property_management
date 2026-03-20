import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.apartment_pk = self.scope["url_route"]["kwargs"]["apartment_pk"]
        self.room_group_name = f"chat_{self.apartment_pk}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user has access to this apartment
        if await self.check_user_access():
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message")
        
        if message_text:
            # We save the message via the view (AJAX/HTMX) and broadcast from there
            # OR we can save here. The user asked for HTMX form submission.
            # So we will broadcast from the view after saving.
            pass

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_user_access(self):
        from properties.models import Apartment, ApartmentOccupancy
        try:
            apartment = Apartment.objects.get(pk=self.apartment_pk, is_active=True)
            if apartment.building.owner == self.user:
                return True
            return ApartmentOccupancy.objects.filter(
                apartment=apartment, tenant=self.user, is_active=True
            ).exists()
        except Apartment.DoesNotExist:
            return False
