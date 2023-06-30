import numpy as np
from PIL import Image

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status


from recommend.models import Schedule, DietPlan
from recommend.serializers import (
    RecommenderSerializer,
    ScheduleSerializer,
    DietPlanSerializer,
)
from recommend.utils.predict_type import calculate_body_type

from utils.misc import save_diets_from_excel


class RecommenderAPIView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = RecommenderSerializer(data=request.data)
            if serializer.is_valid():
                uploaded_image = serializer.validated_data["image"]
                pil_image = Image.open(uploaded_image)
                image_array = np.array(pil_image)
                res_img = np.resize(image_array, (640, 640))
                body_type, body_model = calculate_body_type(res_img)

                user = request.user
                if user.body_type:
                    return Response(
                        {"error": "User already has a diet plan!"},
                        status=status.HTTP_208_ALREADY_REPORTED,
                    )

                user.body_type = body_type
                Schedule.objects.create(user=user)
                user.save()

                return Response(
                    {"body_type": body_type, "body_model": body_model},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ScheduleAPIVIew(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()

    def get(self, request):
        try:
            user = request.user
            schedule = self.queryset.get(user=user)
            diet_plan = DietPlan.objects.filter(
                body_type=user.body_type, day=schedule.current_day
            )

            ser = DietPlanSerializer(diet_plan, many=True)

            return Response(
                ser.data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        try:
            user = request.user
            schedule = self.queryset.get(user=user)
            day = schedule.current_day

            if day == 30:
                schedule.delete()
                user.score += 30
                user.save()
                
                return Response(
                    {"message": "Congratz"},
                    status=status.HTTP_200_OK,
                )

            # Add score
            # Add day only if its 8pm or more
            # Delete schedule if day is 30 - done

            ser = self.serializer_class(schedule)

            return Response(
                ser.data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SaveDietPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, req):
        try:
            save_diets_from_excel()

            return Response(
                "Success",
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
