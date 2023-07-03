import numpy as np
from PIL import Image

from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status

from account.models import Batch

from recommend.models import Schedule, DietPlan
from recommend.serializers import (
    RecommenderSerializer,
    ScheduleSerializer,
    DietPlanSerializer,
    DietPlansSerializer,
)
from recommend.utils.predict_type import calculate_body_type

from utils.misc import save_diets_from_excel


class RecommenderAPIView(APIView):
    # parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            user = request.user
            if user.body_type:
                return Response(
                    {"error": "User already has a diet plan!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RecommenderSerializer(data=request.data)
            if serializer.is_valid():
                uploaded_image = serializer.validated_data["image"]
                pil_image = Image.open(uploaded_image).convert(
                    "RGB"
                )  # Convert to RGB format
                image_array = np.array(pil_image)
                data = calculate_body_type(image_array)

                if "error" in data.keys():
                    return Response(
                        {"error": data.get("error")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # if "error" in data.keys():
                #     return Response(
                #         {"error": data.get("error")},
                #         status=status.HTTP_400_BAD_REQUEST,
                #     )

                body_type, body_model = data
                # print({"body_type": body_type, "body_model": body_model})

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


# for showing and updating current diet-plan
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

            cur_time = timezone.localtime(timezone.now())

            schedule.critical_day = (cur_time - schedule.updated_at).days
            schedule.save()

            ser = DietPlanSerializer(diet_plan, many=True)
            sch = self.serializer_class(schedule)

            # should be not
            # if not (cur_time.hour >= 10 and cur_time.hour <= 21):
            #     return Response(
            #         {"error": "Wait untill 10 A.M."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            return Response(
                {"diet": ser.data, "schedule": sch.data},
                status=status.HTTP_200_OK,
            )

        except Schedule.DoesNotExist:
            return Response(
                data={"error": "No schedule exits."},
                status=status.HTTP_400_BAD_REQUEST,
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

            cur_time = timezone.localtime(timezone.now())
            schedule.critical_day = (cur_time - schedule.updated_at).days
            schedule.save()

            if schedule.critical_day >= 5:
                schedule.delete()
                user.score -= 50

                batch = Batch.objects.get(user=user)
                batch.batch_name = user.score % 100
                batch.save()

                user.body_type = None
                user.save()

                return Response(
                    {
                        "error": "More than 5 days not taking the diet. Failed to complete the diet."
                    },
                    status=status.HTTP_205_RESET_CONTENT,
                )

            # Delete schedule if day is 30 - done
            if day == 30:
                schedule.delete()
                user.score += 30

                batch = Batch.objects.get(user=user)
                batch.batch_name = user.score % 100
                batch.save()

                user.body_type = None
                user.save()

                return Response(
                    {"message": "Completed whole diet."},
                    status=status.HTTP_204_NO_CONTENT,
                )

            # Add day only if its 8pm or more - done
            if cur_time.hour >= 10 and cur_time.hour <= 21:
                return Response(
                    {"error": "Take the whole diet before completing it."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Add score - done
            user.score += 5

            batch = Batch.objects.get(user=user)
            batch.batch_name = int(user.score / 100)

            schedule.current_day += 1
            schedule.updated_at = cur_time

            batch.save()
            schedule.save()
            user.save()

            ser = self.serializer_class(schedule)

            return Response(
                ser.data,
                status=status.HTTP_200_OK,
            )

        except Schedule.DoesNotExist:
            return Response(
                data={"error": "No schedule exits."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DietPlansAPIView(generics.ListAPIView):
    serializer_class = DietPlansSerializer
    queryset = DietPlan.objects.all()

    def get(self, request):
        try:
            NUM_OF_ROWS = 3

            user = request.user
            schedule = Schedule.objects.get(user=user)
            diet_plan = DietPlan.objects.filter(
                body_type=user.body_type,
                day__gte=schedule.current_day,
                time__in=["Lunch", "Breakfast", "Dinner"],
            )[: 3 * NUM_OF_ROWS]

            ser = DietPlansSerializer(diet_plan, many=True)

            return Response(
                ser.data,
                status=status.HTTP_200_OK,
            )

        except Schedule.DoesNotExist:
            return Response(
                data={"error": "No schedule exits."},
                status=status.HTTP_400_BAD_REQUEST,
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
