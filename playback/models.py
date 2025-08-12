import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=80)
    max_simultaneous_streams = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.max_simultaneous_streams})"

class UserSubscriptionPlan(models.Model):
    user = models.OneToOneField(User, related_name='subscription', on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    start_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} --> {self.plan}'

class Movie(models.Model):
    movie_id = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(default=0)
    cdn_path = models.CharField(max_length=1024, help_text = 'Path on CDN or signed URL template')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

DEVICE_TYPES = (
    ('mobile','mobile'),
    ('tablet','tablet'),
    ('tv','tv'),
    ('browser','browser'),
    ('other','other'),
)


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, default='other')
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'device_id')

    def __str__(self):
        return f"{self.user} - {self.device_id}"
    

SESSION_STATUS = (
    ('active','active'),
    ('ended','ended'),
    ('expired','expired'),
)

class WatchSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_sessions')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='watch_sessions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_sessions')
    started_at = models.DateTimeField(default=timezone.now)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default="active")
    created_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['user','status']),
            models.Index(fields=['last_heartbeat']),
        ]
    
    def touch(self):
        self.last_heartbeat = timezone.now
        self.save(update_fields=['last_heartbeat'])
    
    def end(self):
        self.status = 'ended'
        self.save(update_fields=['status'])

    

