from django.contrib import admin
from .models import Device, Movie, UserSubscriptionPlan, SubscriptionPlan, WatchSession


admin.site.register(Device)
admin.site.register(Movie)
admin.site.register(UserSubscriptionPlan)
admin.site.register(SubscriptionPlan)
admin.site.register(WatchSession)