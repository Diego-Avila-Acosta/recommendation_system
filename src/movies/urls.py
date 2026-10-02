from django.urls import path
from movies.api import (MovieDetailAPIView, MovieListCreateAPIView,
                        WatchHistoryView, UserPreferencesView, GeneralUploadView)


app_name = "movies"

urlpatterns = [
    path("movies/", MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>", MovieDetailAPIView.as_view(), name="movie-detail"),
    path("user/<int:user_id>", UserPreferencesView.as_view(),
         name="user-preferences"),
    path("user/<int:user_id>/watch-history/",
         WatchHistoryView.as_view(), name="user-watch-history"),
    path("upload/", GeneralUploadView.as_view(), name="file-upload"),
]
