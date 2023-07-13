from django.urls import path

from requests.views import RequestListCreateView, RequestRetrieveUpdateDestroyView, OrderView, OrderUpdateDestroyView

urlpatterns = [
    path('requests', RequestListCreateView.as_view()),
    path('requests/<int:request_id>', RequestRetrieveUpdateDestroyView.as_view()),

    path('orders', OrderView.as_view()),
    path('orders/<int:id>', OrderUpdateDestroyView.as_view()),
]
