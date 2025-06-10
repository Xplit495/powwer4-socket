import logging
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import emit, join_room

from server import socketio, clients_dictionary, active_games
from server.models import Game


@socketio.on('join_queue')
def handle_join_queue():
    socket_id = request.sid
    logging.info(f"[MATCHMAKING] Joueur {socket_id} tente de rejoindre la queue")

    player = clients_dictionary[socket_id]

    active_games.add_player(socket_id)
    player.join_queue()

    position = active_games.get_position(socket_id)
    players_waiting = active_games.size()

    emit('queue_joined', {
        'position': position,
        'players_waiting': players_waiting
    })

    logging.info(f"[MATCHMAKING] {player.username} rejoint la queue (position: {position})")

    check_matchmaking()

@socketio.on('leave_queue')
def handle_leave_queue():
    socket_id = request.sid
    logging.info(f"[MATCHMAKING] Joueur {socket_id} tente de quitter la queue")

    player = clients_dictionary[socket_id]

    active_games.remove_player(socket_id)
    player.leave_queue()

    emit('queue_left', {'message': 'You left the queue'})

    logging.info(f"[MATCHMAKING] {player.username} a quitté la queue")

def check_matchmaking():
    if active_games.size() < 2:
        logging.info(f"[MATCHMAKING] Pas assez de joueurs en queue: {active_games.size()}")
        return

    match = active_games.find_match()

    player1_socket_id, player2_socket_id = match

    player1 = clients_dictionary[player1_socket_id]
    player2 = clients_dictionary[player2_socket_id]

    game = Game(player1, player2)
    game_id = game.game_id

    active_games[game_id] = game

    player1.start_game(game_id)
    player2.start_game(game_id)

    join_room(game_id, sid=player1_socket_id)
    join_room(game_id, sid=player2_socket_id)

    emit('game_found', {
        'game_id': game_id,
        'opponent': {
            'username': player2.username,
            'total_games': player2.total_games_count,
            'wins': player2.win_games_count
        },
        'your_turn': True,
        'player_number': 1
    }, to=player1_socket_id)

    emit('game_found', {
        'game_id': game_id,
        'opponent': {
            'username': player1.username,
            'total_games': player1.total_games_count,
            'wins': player1.win_games_count
        },
        'your_turn': False,
        'player_number': 2
    }, to=player2_socket_id)

    logging.info(f"[MATCHMAKING] Match créé: {game_id} - {player1.username} vs {player2.username}")

@socketio.on('queue_status')
def handle_queue_status():
    socket_id = request.sid

    player = clients_dictionary[socket_id]

    position = active_games.get_position(socket_id)

    waiting_duration = datetime.now() - player.joined_queue_at
    waiting_time = str(waiting_duration).split('.')[0]

    emit('queue_status', {
        'in_queue': True,
        'position': position,
        'players_waiting': active_games.size(),
        'waiting_time': waiting_time
    })