from rest_framework import serializers

class RecommenderSerializer(serializers.Serializer):
    image = serializers.ImageField()
