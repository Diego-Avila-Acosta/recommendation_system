from typing import Dict, Any
from collections import defaultdict
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from movies.models import Movie, UserMoviePreferences
from movies.serializers import PreferencesSerializer


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
