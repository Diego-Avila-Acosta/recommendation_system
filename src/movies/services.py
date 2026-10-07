from typing import IO, Dict, Any
from collections import defaultdict
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from movies.models import Movie, UserMoviePreferences
from movies.serializers import PreferencesSerializer
import csv
import datetime
import json


def add_preference(user_id: int, new_preference: Dict[str, Any]) -> None:
    with transaction.atomic():
        user = get_object_or_404(get_user_model(), id=user_id)
        (user_preferences, created) = UserMoviePreferences.objects.select_for_update(
        ).get_or_create(user_id=user.id, defaults={"preferences": {}})

        current_preferences = defaultdict(list, user_preferences.preferences)

        for key, value in new_preference.items():
            if value not in current_preferences[key]:
                current_preferences[key].append(value)

        user_preferences.preferences = dict(current_preferences)
        user_preferences.save()


def add_watch_history(user_id: int, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)

    movie_info = {
        "title": movie.title,
        "genre": movie.genres,
        "year": movie.release_year,
    }

    try:
        with transaction.atomic():
            user_preferences, created = UserMoviePreferences.objects.get_or_create(
                user_id=user_id, defaults={"watch_history": [movie_info]})
    except IntegrityError:
        user_preferences = UserMoviePreferences.objects.get(user_id=user_id)
        created = False

    if not created:
        current_watch_history = user_preferences.watch_history
        current_watch_history.append(movie_info)
        user_preferences.watch_history = current_watch_history
        user_preferences.save()


def user_preferences(user_id: int):
    user_preferences = get_object_or_404(UserMoviePreferences, user_id=user_id)
    serializer = PreferencesSerializer(user_preferences.preferences)

    return serializer.data


def user_watch_history(user_id: int):
    user_preferences = get_object_or_404(UserMoviePreferences, user_id=user_id)
    return {"watch_history": user_preferences.watch_history}


def parse_csv(file: IO[Any]) -> int:
    movie_processed = 0
    reader = csv.DictReader(file)

    for row in reader:
        create_or_update_movie(**row)
        movie_processed += 1

    return movie_processed


def parse_json(file: IO[Any]) -> int:
    movies_processed = 0
    data = json.load(file)

    for item in data:
        create_or_update_movie(**item)
        movies_processed += 1

    return movies_processed


class FileProcessor:
    def process(self, file_name: str, file_type: str) -> int:
        if default_storage.exists(file_name):
            with default_storage.open(file_name, "r") as file:
                if file_type == "text/csv":
                    movies_proccessed = parse_csv(file)
                elif file_type == "application/json":
                    movies_proccessed = parse_json(file)
                else:
                    raise ValidationError("Invalid file type")

                return movies_proccessed
        else:
            raise ValidationError("File does not exist in storage.")


def create_or_update_movie(
    title: str,
    genres: list,
    country: str | None = None,
    extra_data: dict[Any, Any] | None = None,
    release_year: int | None = None
):
    try:
        current_year = datetime.datetime.now().year
        if release_year is not None and (release_year < 1888 or release_year > current_year):
            raise ValidationError(
                "The release year must be between 1888 and the current year")

        movie, created = Movie.objects.update_or_create(
            title=title,
            defaults={
                "genres": genres,
                "country": country,
                "extra_data": extra_data,
                "release_year": release_year,
            }
        )
        return movie, created
    except Exception as e:
        raise ValidationError(
            f"Failed to create or update the movie: {str(e)}")
