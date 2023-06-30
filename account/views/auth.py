from rest_framework import (
    views,
    response,
    status,
)

from rest_framework_simplejwt.views import TokenObtainPairView

from account.serializers import RegisterSerializer, TokenSerializer
from account.models import EndUser
from account.renderers import UserRenderer


class LoginView(TokenObtainPairView):
    renderer_classes = [UserRenderer]
    serializer_class = TokenSerializer


class RegisterView(views.APIView):
    renderer_classes = [UserRenderer]
    model = EndUser
    serializer_class = RegisterSerializer

    def post(self, request):
        try:
            data = request.data
            ser = self.serializer_class(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()

            return response.Response(
                data={
                    "Message": "Account created successfully!",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return response.Response(
                data={
                    "error": ser.errors,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
