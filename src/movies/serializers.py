from typing import Any
from rest_framework import serializers
from .models import Movie
from django.core.exceptions import ObjectDoesNotExist
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


class PreferencesDetailSerializer(serializers.Serializer):
    genre = serializers.CharField(
        max_length=100, allow_blank=True, required=False)
    director = serializers.CharField(
        max_length=100, allow_blank=True, required=False)
    actor = serializers.CharField(
        max_length=100, allow_blank=True, required=False)
    year = serializers.IntegerField(
        min_value=1900, max_value=2099, required=False, allow_null=False)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if all(value in [None, ""] for value in data.values()):
            raise serializers.ValidationError(
                "At least one preference must be provided"
            )
        return data


class AddPreferenceSerializer(serializers.Serializer):
    new_preferences = PreferencesDetailSerializer()


class AddToWatchHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, value: int) -> int:
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid movie ID. No such movie exists.")
        return value


class PreferencesSerializer(serializers.Serializer):
    genre = serializers.ListField(
        child=serializers.CharField(), required=False)
    director = serializers.ListField(
        child=serializers.CharField(), required=False)
    actor = serializers.ListField(
        child=serializers.CharField(), required=False)
    year = serializers.ListField(child=serializers.CharField(), required=False)


class WatchHistorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    year = serializers.IntegerField()
    genre = serializers.CharField(max_length=255)


class GeneralFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if value.size > 10485760:  # 10MB limit
            raise serializers.ValidationError(
                "The file size exceeds the limit of 10MB.")

        allowed_types = ["text/csv", "application/json", "application/xml"]

        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Unsuporrted file type")

        return value
