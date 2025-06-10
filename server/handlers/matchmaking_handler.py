import logging
import random
import uuid

from flask import request
from flask_socketio import emit, join_room

from server import socketio, clients_dictionary, active_games, queue
from server.models import Game


@socketio.on('join_queue')
def handle_join_queue():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    queue.add_player(socket_id)
    player.join_queue()

    emit('queue_joined', {'message': 'Vous avez rejoint la queue'})
    logging.info(f"{player.username} join the queue")

    check_matchmaking()

@socketio.on('leave_queue')
def handle_leave_queue():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    queue.remove_player(socket_id)
    player.leave_queue()

    emit('queue_left', {'message': 'Vous avez quitté la queue'})
    logging.info(f"{player.username} leave the queue")

def check_matchmaking():
    if queue.size() >= 2:
        game_id = str(uuid.uuid4())

        player1_socket_id, player2_socket_id = queue.find_match()
        player1 = clients_dictionary[player1_socket_id]
        player2 = clients_dictionary[player2_socket_id]

        current_player_index = random.randint(0, 1)
        active_games[game_id] = Game(game_id, player1, player2, current_player_index)

        player1.start_game(game_id)
        player2.start_game(game_id)

        join_room(game_id, sid=player1_socket_id)
        join_room(game_id, sid=player2_socket_id)

        emit('game_found', {'opponent_username': player2.username, 'your_turn': current_player_index == 0,'player_number': 1}, to=player1_socket_id)
        emit('game_found', {'opponent_username': player1.username, 'your_turn': current_player_index == 1,'player_number': 2}, to=player2_socket_id)
        logging.info(f"Match created: {game_id} - {player1.username} vs {player2.username}")