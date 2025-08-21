import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL
class Genre(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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
    movie_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255, db_index=True)
    duration = models.PositiveIntegerField(help_text="Seconds")
    cdn_path = models.URLField()
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    maturity_rating = models.CharField(
        max_length=16, blank=True, help_text="e.g., U, U/A 13+, PG-13, R"
    )
    language = models.CharField(max_length=32, blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    cast = models.JSONField(default=list, blank=True)
    directors = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["release_year"]),
            models.Index(fields=["language"]),
        ]

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

    

