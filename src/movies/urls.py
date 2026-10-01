from django.urls import path
from movies.api import MovieDetailAPIView, MovieListCreateAPIView


app_name = "movies"

urlpatterns = [
    path("movies/", MovieListCreateAPIView.as_view(), name="movie-list"),
    path("movies/<int:pk>", MovieDetailAPIView.as_view(), name="movie-detail")
]
