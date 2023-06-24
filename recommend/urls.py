from django.urls import path

from recommend.views import RecommenderAPIView

urlpatterns = [
    path('recommend', RecommenderAPIView.as_view(), name='recommend'),
    
]
