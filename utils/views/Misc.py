from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_503_SERVICE_UNAVAILABLE

from time import sleep

class MiscAPIView(APIView):
    
    def get(self, request):
        sleep(2.5)
        return Response(status=HTTP_503_SERVICE_UNAVAILABLE)
    