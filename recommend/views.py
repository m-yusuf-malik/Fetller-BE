import numpy as np
from PIL import Image

from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status


from recommend.serializers import RecommenderSerializer
from recommend.utils.predict_type import calculate_body_type

class RecommenderAPIView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        try:
            serializer = RecommenderSerializer(data=request.data)
            if serializer.is_valid():
                uploaded_image = serializer.validated_data['image']
                pil_image = Image.open(uploaded_image)
                image_array = np.array(pil_image)
                body_type, body_model = calculate_body_type(image_array)
                
                return Response({'body_type': body_type, 'body_model':body_model}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({
                'error':str(e), 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
