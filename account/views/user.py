from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics

from account.serializers import EndUserSerializer, BatchRetrieveSerializer, BatchCreateUpdateSerializer
from account.models import EndUser, Batch
from account.renderers import UserRenderer


class UserRetrieveView(generics.RetrieveUpdateAPIView):
    lookup_field = 'username'
    renderer_classes = [UserRenderer]
    queryset = EndUser.objects.all()
    serializer_class = EndUserSerializer
    permission_classes = [IsAuthenticated]


class BatchView(generics.RetrieveUpdateAPIView):
    serializer_class = BatchCreateUpdateSerializer
    queryset = Batch.objects.all()
    lookup_url_kwarg = 'username'
    lookup_field = 'user__username'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BatchRetrieveSerializer
        elif self.request.method == 'PATCH':
            return self.serializer_class
