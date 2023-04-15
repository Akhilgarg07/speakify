import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def send_disconnect_message(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_disconnected',
                'user': {
                    'first_name': self.scope["user"].first_name,
                    'username': self.scope["user"].username,
                    'gender': self.scope["user"].userprofile.gender,
                    'country': self.scope["user"].userprofile.country,
                }
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.send_disconnect_message()
        await asyncio.sleep(1)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        
        await self.clear_chat_room()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = await self.get_user_data()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': {
                    'first_name': self.scope["user"].first_name,
                    'username': self.scope["user"].username,
                    'gender': self.scope["user"].userprofile.gender,
                    'country': self.scope["user"].userprofile.country,
                }
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
        }))
    
    async def user_disconnected(self, event):
        user = event['user']

        # Send a disconnect message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'disconnect',
            'user': user,
        }))



    @database_sync_to_async
    def get_user_data(self):
        return {
            'username': self.scope["user"].username,
            'gender': self.scope["user"].userprofile.gender,
            'country': self.scope["user"].userprofile.country,
        }
    
    @database_sync_to_async
    def clear_chat_room(self):
        user_profile = self.scope["user"].userprofile
        user_profile.chat_room = None
        user_profile.save()

