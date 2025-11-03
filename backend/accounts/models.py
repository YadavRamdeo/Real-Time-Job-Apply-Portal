from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

@receiver(post_save, sender=Notification)
def push_notification_ws(sender, instance: 'Notification', created, **kwargs):
    """Push new notifications to the user's WebSocket group."""
    try:
        if not created:
            return
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        group = f"notifications_{instance.user_id}"
        payload = {
            'type': 'notification_message',
            'notification': {
                'id': instance.id,
                'title': instance.title,
                'message': instance.message,
                'is_read': instance.is_read,
                'created_at': instance.created_at.isoformat(),
            }
        }
        async_to_sync(channel_layer.group_send)(group, payload)
    except Exception:
        # Fail silently; notifications are still available via REST polling
        pass
