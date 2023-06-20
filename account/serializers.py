from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import EndUser, Batch


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token


class BatchCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Batch
        fields = '__all__'


class RegisterSerializer(ModelSerializer):
    batch = serializers.CharField(source='batch.batch_name', read_only=True)

    class Meta:
        model = EndUser
        fields = (
            'username',
            'email',
            'password',
            'phone',
            'country',
            'batch'
        )

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        # Create the User instance
        user = super().create(validated_data)
        print(user)
        batch_data = {
            'batch_name': 1,
            'user': user.pk,
        }

        batch_serializer = BatchCreateUpdateSerializer(data=batch_data)
        batch_serializer.is_valid(raise_exception=True)
        batch_serializer.save()

        print(batch_serializer.data)

        return user


class EndUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(max_length=50, write_only=True)
    batch = serializers.CharField(source='batch.__str__')

    class Meta:
        model = EndUser
        fields = ['username', 'email', 'name',
                  'phone', 'country', 'city', 'batch']

    # def validate_password(self, value):
    #     self.instance.set_password(value)
    #     return self.instance.password


class BatchRetrieveSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='__str__', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Batch
        fields = '__all__'
