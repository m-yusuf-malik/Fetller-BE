from django.db.models import Q
from django.core.mail import send_mail

# from django.conf.settings import EMAIL_HOST_USER

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
    OrderDetailSerializer,
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
            user = request.user
            requests = requests.filter(is_ordered=False).exclude(user=user)
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

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderListSerializer
        elif self.request.method == "POST":
            return OrderSerializer

    def get(self, request):
        try:
            user = request.user
            orders = self.queryset.filter(rider=user)
            ser = OrderListSerializer(orders, many=True)

            return response.Response(ser.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return response.Response(
                data={"error": "No order found."},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return response.Response(
                data={
                    "error": ser.errors,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, req):
        try:
            req_id = req.data.get("request_id")
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

            ser = OrderSerializer(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            request.save()
            rider.is_rider = True
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
                data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderUpdateDestroyView(
    generics.UpdateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView
):
    serializer_class = OrderUpdateSerializer
    queryset = Order.objects.all()
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    # lookup_url_kwarg = "req_id"
    lookup_field = "id"

    # def get_queryset(self):
    #     req_id = self.kwargs["req_id"]
    #     order = Order.objects.filter(request__id=req_id)
    #     return order
    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderDetailSerializer
        else:
            return OrderUpdateSerializer

    def destroy(self, req, id):
        try:
            order = self.get_queryset().get(id=id)
            user = req.user
            request = Request.objects.get(id=order.request.id)

            user.score += order.score

            message = f"Congratulation, {user.username}, you have completed your order."
            send_mail(
                "Order Status",
                message,
                "fettlerplus@gmail.com",
                [user.email],
                fail_silently=True,
            )            
            
            message = f"Congratulation, {request.user.username}, your order have been completed by {user.username}."
            send_mail(
                "Order Status",
                message,
                "fettlerplus@gmail.com",
                [request.user.email],
                fail_silently=True,
            )

            user.save()
            order.delete()
            request.delete()

            return response.Response(status=status.HTTP_204_NO_CONTENT)

        except Request.DoesNotExist:
            return response.Response(
                data={"error": "No request exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Order.DoesNotExist:
            return response.Response(
                data={"error": "No order exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return response.Response(
                data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, req, id):
        try:
            order_status = req.data.get("status")

            order = self.get_queryset().get(id=id)
            rider = req.user
            request = Request.objects.get(id=order.request.id)

            order.status = order_status
            order.save()

            message = f"{rider.username} has updated the status of your {request.title}'s request order."
            send_mail(
                "Order Status",
                message,
                "fettlerplus@gmail.com",
                [request.user.email],
                fail_silently=True,
            )

            return response.Response(status=status.HTTP_200_OK)

        except Exception as e:
            return response.Response(
                data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
