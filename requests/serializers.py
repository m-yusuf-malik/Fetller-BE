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


# Serializer for lisitng all the available orders for a specifc user
class OrderListSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(source='__str__')
    status = serializers.IntegerField()

    # rider = serializers.CharField(source='rider.username', read_only=True)
    requestee = serializers.CharField(
        source='requestee.username', read_only=True)
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)
    title = serializers.CharField(source='request.title', read_only=True)
    image = serializers.CharField(source='request.image', read_only=True)

    class Meta:
        model = Order
        exclude = ('updated_at', 'request', 'rider')


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class OrderRequestSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Request
        fields = ('title', 'description', 'address', 'city', 'phone_number',
                  'country', 'price', 'estimated_profit', 'user', 'image')


class OrderDetailSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField()
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d', read_only=True)
    request = OrderRequestSerializer()

    class Meta:
        model = Order
        fields = ('status', 'score', 'created_at', 'request')
