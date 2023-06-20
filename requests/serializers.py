from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.serializers import EndUserSerializer

from requests.models import Request, Order


class RequestListCreateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Request
        fields = '__all__'

    def create(self, validated_data):
        price = validated_data.get('price')
        estimated_profit = price * 0.25
        validated_data['estimated_profit'] = estimated_profit
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(source='__str__')
    # rider = serializers.CharField(source='rider.username', read_only=True)
    # requestee = serializers.CharField(source='requestee.username', read_only=True)
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='__str__')
    rider = serializers.CharField(source='rider.username', read_only=True)
    requestee = serializers.CharField(
        source='requestee.username', read_only=True)
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
