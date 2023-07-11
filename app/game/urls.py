from django.urls import path

from . import views

app_name = "game"
urlpatterns = [
    path("", views.index, name="index"),
    path("move/", views.move, name="move"),
    path("board/", views.board, name="board"),
    path("reset/", views.reset, name="reset"),
    path("_game/", views.game, name="game"),  # _ in name indicates private usage- for Sanic only.
]
