import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract token from query string
        query_string = self.scope.get('query_string', b'').decode()
        token = None
        
        if 'token=' in query_string:
            token = query_string.split('token=')[1].split('&')[0]
        
        if not token:
            await self.close()
            return
        
        # Authenticate user
        self.user = await self.get_user_from_token(token)
        if not self.user:
            await self.close()
            return
        
        # Add user to their personal notification group
        self.group_name = f'notifications_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send any unread notifications on connect
        await self.send_unread_notifications()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
            elif message_type == 'get_unread':
                await self.send_unread_notifications()
        except json.JSONDecodeError:
            pass
    
    async def notification_message(self, event):
        """Handle notification messages from group"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """Get user from auth token"""
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id, 
                user=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    async def send_unread_notifications(self):
        """Send all unread notifications to client"""
        notifications = await self.get_unread_notifications()
        
        for notification in notifications:
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                }
            }))
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """Get unread notifications for user"""
        return list(
            Notification.objects.filter(
                user=self.user, 
                is_read=False
            ).order_by('-created_at')[:10]
        )


# Utility function to send notification to user's WebSocket group
async def send_notification_to_user(user_id, notification_data):
    """Send notification to specific user via WebSocket"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    group_name = f'notifications_{user_id}'
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )