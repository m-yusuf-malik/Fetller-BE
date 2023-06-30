from rest_framework import serializers

from recommend.models import Schedule, DietPlan


class RecommenderSerializer(serializers.Serializer):
    image = serializers.ImageField()


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class DietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = "__all__"
