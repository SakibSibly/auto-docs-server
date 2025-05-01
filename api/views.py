from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class V1ApiGreet(APIView):
    def get(self, request):
        """
        Handle GET requests to the /api/v1/info/ endpoint.
        """
        return Response({"message": "Hello, World from API version 1!"}, status=status.HTTP_200_OK)