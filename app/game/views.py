from django.conf import settings
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET

from .forms import MoveForm
from .models import Game, PLAYER_1, PLAYER_2


def notify_game_event(game_id, session_key):
    """Send a notification via PostgreSQL."""
    cursor = connection.cursor()
    cursor.execute(f"NOTIFY game_changes, '{game_id}:{session_key}'")


@require_GET
def index(request):
    """
    Check the session for an associated game, and show the state.
    If no game is associated, join an available game.
    If no game is available, make a new one.
    """
    game = None
    player = None

    # First, find if session already has a game.
    game_id = request.session.get('game_id')
    if game_id:
        try:
            game = Game.objects.get(id=game_id)
            player = request.session.get('player')
        except Game.DoesNotExist:
            # This "should" never happen.
            game = None

    if not game:
        # Session didn't already have a game, so find a game waiting for a match, or create a new one.
        match_making_game = Game.objects.filter(state=Game.STATE_MATCH_MAKING).first()
        if match_making_game:
            # Update the game with update() to handle the race condition of 2 clients finding the same
            # matchmaking game at the same time. Only 1 will be able to update it.
            games_updated = Game.objects.filter(id=match_making_game.id).update(state=Game.STATE_IN_PROGRESS)
            if games_updated > 0:
                # We successfully joined the game and updated the status.
                match_making_game.refresh_from_db()
                game = match_making_game
                player = PLAYER_2  # We joined the game so we're player 2.
                notify_game_event(game.id, request.session.session_key)

        if not game:
            # No game was waiting for a match, or we failed to change a game to in progress,
            # so create a new game.
            game = Game.objects.create()
            player = PLAYER_1  # We created the game so we're player 1.

        request.session['game_id'] = game.id  # Serialize the ID, not the game itself.
        request.session['player'] = player

    context = {
        'game': game,
        'player': player,
        'websocket_url': settings.WEBSOCKET_URL,
        'board_url': reverse('game:board'),
    }
    return render(request, "game/index.html", context)


@require_POST
def move(request):
    """Perform the move."""
    try:
        game = Game.objects.get(id=request.session.get('game_id'))
        player = request.session.get('player')
    except Game.DoesNotExist:
        # This is unrecoverable.
        return redirect('game:index')

    form = MoveForm(game, player, request.POST)
    error_message = None
    if form.is_valid():
        # It would be more elegant to handle this with signals, but since we need to include the session ID it must
        # be done here.
        notify_game_event(game.id, request.session.session_key)
    else:
        # Django supports multiple error messages but in our case there will only ever be one.
        error_message = form.non_field_errors()[0]

    context = {
        'game': game,
        'player': player,
        'error_message': error_message,
    }
    template = 'game/complete.html' if game.is_complete() else 'game/in_progress.html'
    return render(request, template, context)


@require_GET
def board(request):
    """Return just the board content."""
    try:
        game = Game.objects.get(id=request.session.get('game_id'))
        player = request.session.get('player')
    except Game.DoesNotExist:
        # This is unrecoverable.
        return HttpResponse(status=204)

    context = {
        'game': game,
        'player': player,
    }
    template = 'game/complete.html' if game.is_complete() else 'game/in_progress.html'
    return render(request, template, context)

@require_POST
def reset(request):
    """Clear the session so user can start/join a new game."""
    request.session.pop('game_id')
    request.session.pop('player')
    return redirect('game:index')


@require_GET
def game(request):
    """Return the game ID associated with the session, if any."""
    return JsonResponse({
        "id": request.session.get('game_id'),
    })
