# tutoring/webrtc_handler.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WebRTCConsumer(AsyncWebsocketConsumer):
    """
    Handles WebRTC signaling (offers, answers, ICE candidates) via WebSockets.
    This allows peers (students & tutors) to discover and connect to each other.
    """

    async def connect(self):
        # Each tutoring room will have a room_name passed in URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"tutoring_{self.room_name}"

        # Join the group (so everyone in the same room gets messages)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive signaling data from a WebSocket client (browser) and 
        broadcast it to others in the same room.
        """
        data = json.loads(text_data)

        # Example data = { "type": "offer", "sdp": "...", "sender": "user1" }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signal_message",
                "message": data
            }
        )

    async def signal_message(self, event):
        """
        Called when group_send broadcasts a message.
        This forwards the signaling message to the WebSocket.
        """
        await self.send(text_data=json.dumps(event["message"]))
