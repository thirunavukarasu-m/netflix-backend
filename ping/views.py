from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class PingView(APIView):
    def get(self, request):
        print("Ping received.")
        return Response({"message":"Pong"}, status=status.HTTP_200_OK)