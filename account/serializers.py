from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import EndUser, Batch


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username
        token["is_rider"] = user.is_rider
        token["name"] = user.name
        token["destination_country"] = user.destination_country

        return token


class BatchCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"


class RegisterSerializer(ModelSerializer):
    batch = serializers.CharField(source="batch.batch_name", read_only=True)

    class Meta:
        model = EndUser
        fields = ("username", "email", "password", "phone", "country", "batch")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        batch_data = {
            "batch_name": 0,
            "user": user.pk,
        }

        batch_serializer = BatchCreateUpdateSerializer(data=batch_data)
        batch_serializer.is_valid(raise_exception=True)
        batch_serializer.save()

        return user


class EndUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(max_length=50, write_only=True)
    batch = serializers.CharField(source="batch.__str__")

    class Meta:
        model = EndUser
        fields = [
            "username",
            "email",
            "name",
            "phone",
            "country",
            "city",
            "score",
            "batch",
            "destination_country",
        ]

    # def validate_password(self, value):
    #     self.instance.set_password(value)
    #     return self.instance.password


class BatchRetrieveSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source="__str__", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Batch
        fields = "__all__"
