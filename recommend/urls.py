from django.urls import path

from recommend.views import RecommenderAPIView, SaveDietPlanView, ScheduleAPIVIew

urlpatterns = [
    path("recommend", RecommenderAPIView.as_view(), name="recommend"),
    path("diet-plan", ScheduleAPIVIew.as_view(), name="diet_plan"),
    path("save-diets", SaveDietPlanView.as_view()),
]
