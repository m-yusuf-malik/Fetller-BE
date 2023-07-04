from rest_framework import serializers

from recommend.models import Schedule, DietPlan


class RecommenderSerializer(serializers.Serializer):
    image = serializers.ImageField()


class ScheduleSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Schedule
        fields = ("current_day", "critical_day", "created_at", "updated_at")


class DietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = ("day", "time", "meal")


class DietPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = ("meal", "time", "day",)


class CombinedDietPlansSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    Breakfast = serializers.CharField()
    Lunch = serializers.CharField()  
    Dinner = serializers.CharField()