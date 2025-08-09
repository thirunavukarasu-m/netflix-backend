from django.urls import path
from .views import PingView, HelloWorldView
urlpatterns = [
    path('', PingView.as_view(), name='ping'),
    path('hello/', HelloWorldView.as_view(), name='hello')
]