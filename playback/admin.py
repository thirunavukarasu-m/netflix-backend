from django.contrib import admin
from .models import Device, Movie, UserSubscriptionPlan, SubscriptionPlan, WatchSession, Genre


admin.site.register(Device)
admin.site.register(UserSubscriptionPlan)
admin.site.register(SubscriptionPlan)
admin.site.register(WatchSession)
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "language", "is_active")
    list_filter = ("is_active", "release_year", "language", "genres")
    search_fields = ("title", "description")
    filter_horizontal = ("genres",)