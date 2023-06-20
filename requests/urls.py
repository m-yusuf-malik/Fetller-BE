from django.urls import path

from requests.views import RequestListCreateView, RequestRetrieveUpdateDestroyView, OrderView

urlpatterns = [
    path('requests', RequestListCreateView.as_view()),
    path('requests/<int:request_id>', RequestRetrieveUpdateDestroyView.as_view()),
    
    path('requests/<int:req_id>/order', OrderView.as_view()),
]
