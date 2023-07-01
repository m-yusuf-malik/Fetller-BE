from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status

from account.renderers import UserRenderer

from account.models import EndUser
from requests.models import Request, Order
from requests.serializers import (
    RequestListCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderUpdateSerializer,
)


class RequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RequestListCreateSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def filter_with_params(self, request, requests):
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        country = request.query_params.get("country")
        city = request.query_params.get("city")

        if search:
            requests = requests.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        if ordering:
            requests = requests.order_by(ordering)
        if city:
            requests = requests.filter(city=city)
        if country:
            requests = requests.filter(country=country)

        return requests

    def get(self, request):
        try:
            requests = self.get_queryset()
            requests = requests.filter(is_ordered=False)
            requests = self.filter_with_params(request, requests)

            if not requests:
                return response.Response(
                    "No requests found.", status=status.HTTP_204_NO_CONTENT
                )

            ser = self.serializer_class(requests, many=True)

            return response.Response(ser.data, status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(
                data={
                    "error": ser.errors,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


# get() -> get_queryset() -> get_object()
class RequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    lookup_url_kwarg = "request_id"
    serializer_class = RequestListCreateSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    queryset = Request.objects.all()


class OrderView(
    generics.ListCreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView
):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "req_id"
    lookup_field = "request"

    def get_queryset(self):
        req_id = self.kwargs["req_id"]
        order = Order.objects.filter(request__id=req_id)
        return order

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderListSerializer
        elif self.request.method == "POST":
            return OrderSerializer
        elif self.request.method == "PATCH":
            return OrderUpdateSerializer

    def post(self, req, req_id):
        try:
            request = Request.objects.get(id=req_id)
            request.is_ordered = True

            rider = req.user

            if rider == request.user:
                return response.Response(
                    data={"error": "You cannot take order of your own request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = {
                "rider": rider.id,
                "request": request.id,
                "requestee": request.user.id,
                "score": int(request.estimated_profit * 0.25),
            }

            ser = self.serializer_class(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            request.save()
            rider.is_rider=True
            rider.save()

            return response.Response(
                data={
                    "Message": "Order created successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        except Request.DoesNotExist:
            return response.Response(
                data={"error": "Invalid request ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except EndUser.DoesNotExist:
            return response.Response(
                data={"error": "Invalid rider username."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return response.Response(
                data={"error": ser.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
