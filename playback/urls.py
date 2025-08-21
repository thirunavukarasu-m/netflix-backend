from django.urls import path
from .views import DeviceRegisterView, MovieListCreateView, PlaybackStartView, PlaybackHeartbeatView, PlaybackStopView, ActiveSessionsView, MovieSearchView, GenreBulkUpsertView
urlpatterns = [
    path('device/', DeviceRegisterView.as_view(), name = 'device'),
    path('movie/', MovieListCreateView.as_view(), name = 'movie'),
    path('playback/start/', PlaybackStartView.as_view(), name = 'playback_start'),
    path('playback/heartbeat/', PlaybackHeartbeatView.as_view(), name='playback-heartbeat'),
    path('playback/stop/', PlaybackStopView.as_view(), name='playback-stop'),
    path('playback/active/', ActiveSessionsView.as_view(), name='playback-active'),
    path("movie/search/", MovieSearchView.as_view(), name="movie-search"),
    path("genre/", GenreBulkUpsertView.as_view(), name="genre"),
]