from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class PingView(APIView):
    def get(self, request):
        print("Ping received.")
        return Response({"message":"Pong"}, status=status.HTTP_200_OK)

class HelloWorldView(APIView):
    def get(self, request):
        print("Hello World!")
        return Response({'message': "Hello World!"}, status=status.HTTP_200_OK)