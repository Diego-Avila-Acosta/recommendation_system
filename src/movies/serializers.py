from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="Movie ID", required=False)
    title = serializers.CharField(max_length=255)
    genres = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True,
        default=list
    )

    def create(self, validated_data):
        return Movie.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.genres = validated_data.get("genres", instance.genres)
        instance.save()

        return instance
