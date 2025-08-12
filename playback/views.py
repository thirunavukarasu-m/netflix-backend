import uuid, time
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Device, Movie, WatchSession, UserSubscriptionPlan
from .serializers import DeviceSerializer, MovieSerializer, WatchSessionSerializer
import logging

logger = logging.getLogger(__name__)
SESSION_INACTIVITY_TIMEOUT = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 120)

class DeviceRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user)
        devices_qs = Device.objects.filter(user=user)
        devices_serializer = DeviceSerializer(devices_qs, many = True)
        return Response(devices_serializer.data, status= status.HTTP_200_OK)

    def post(self, request):
        payload = request.data.copy()
        serializer = DeviceSerializer(data = payload)
        if serializer.is_valid():
            device, created = Device.objects.get_or_create(
                user = request.user,
                device_id = serializer.validated_data['device_id'],
                defaults= {
                    'name' : serializer.validated_data.get('name', ''),
                    'device_type' : serializer.validated_data.get('device_type', 'other')
                }
            )

            if not created:
                updated = False
                if serializer.validated_data.get('name') and device.name != serializer.validated_data.get('name'):
                    device.name = serializer.validated_data.get('name')
                    updated = True
                if serializer.validated_data.get('device_type') and device.device_type != serializer.validated_data.get('device_type'):
                    device.device_type = serializer.validated_data.get('device_type')
                    updated = True
                if updated:
                    device.save()
                
            return Response({
                'device_id': device.device_id,
                'created': created
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
class MovieListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        movie_qs = Movie.objects.filter(is_active = True)
        movie_serialzer = MovieSerializer(movie_qs, many = True)
        return Response(movie_serialzer.data)

    def post(self, request):
        serializer = MovieSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


class PlaybackStartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """
            Body: {
                device_id : ...,
                movie_id : ...,
                steal : false
            }
        """
        user = request.user
        device_id = request.data.get('device_id')
        movie_id = request.data.get('movie_id')
        steal = bool(request.data.get('steal', False))

        if not device_id or not movie_id:
            return Response({'error': "Please provide valid device_id and movie_id"}, status=status.HTTP_400_BAD_REQUEST)

        device = get_object_or_404(Device, user = user, device_id = device_id)
        movie = get_object_or_404(Movie, movie_id = movie_id, is_active = True)
        try:
            sub = UserSubscriptionPlan.objects.get(user = user)
        except UserSubscriptionPlan.DoesNotExist:
            return Response({'error': "User does not have a subscription."}, status=status.HTTP_403_FORBIDDEN)

        ws = WatchSession.objects.filter(user=user, status='active', device = device, movie = movie).exists()
        if ws:
            return Response({"error": "Already a session is active on this device"}, status= status.HTTP_409_CONFLICT)
        limit = sub.plan.max_simultaneous_streams
        stale_cutoff = timezone.now() - timezone.timedelta(seconds=SESSION_INACTIVITY_TIMEOUT)
        WatchSession.objects.filter(user=user, status='active', last_heartbeat__lt = stale_cutoff).update(status = 'expired')
        active_count = WatchSession.objects.filter(user=user, status = 'active').count()

        if active_count >= limit:
            if not steal:
                active_sessions = WatchSession.objects.filter(user=user, status='active').values('id', 'device__device_id','movie__title', 'created_at', 'last_heartbeat')
                return Response({'error': "Limit reached!", "limit": limit, 'active_count': active_count, 'sessions': active_sessions}, status=status.HTTP_409_CONFLICT)
            else:
                oldest = WatchSession.objects.filter(user=user, status='active').order_by('last_heartbeat').first()
                if oldest:
                    oldest.status = 'ended'
                    oldest.save()

        
        ws = WatchSession.objects.create(user = user, movie = movie, device = device)
        logger.debug("start called user=%s device=%s", user.id, device_id)
        return Response({
            "watch_session_id": ws.id,
            "movie_title": movie.title,
            "movie_cdn" : movie.cdn_path
        }, status= status.HTTP_201_CREATED)

class PlaybackHeartbeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ws_id = request.data.get('watch_session_id')
        if not ws_id:
            return Response({
                "error": "Watch session id is required."
            }, status= status.HTTP_400_BAD_REQUEST)
        ws = get_object_or_404(WatchSession, id = ws_id, user = request.user)
        if ws.status != 'active':
            return Response({
                "error": "Session is not active."
            }, status= status.HTTP_403_FORBIDDEN)
        ws.touch()
        return Response({
            'message' : "Session touched",
            'last_heartbeat' : ws.last_heartbeat
        }, status= status.HTTP_200_OK)

class PlaybackStopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ws_id = request.data.get('watch_session_id')
        if not ws_id:
            return Response({
                'error': "Watch session id is required."
            }, status= status.HTTP_400_BAD_REQUEST)
        ws = get_object_or_404(WatchSession, id = ws_id, user = request.user)
        ws.end()
        return Response({
            "message": "Session terminated."
        }, status= status.HTTP_200_OK)
    

class ActiveSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ws = WatchSession.objects.filter(user = request.user, status = 'active').select_related('device','movie')
        print(ws)
        serializer = WatchSessionSerializer(ws, many = True)
        return Response(serializer.data)
