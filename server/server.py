import logging
import random
import time
import uuid
from datetime import datetime

import bcrypt
from flask import Flask, request
from flask_socketio import SocketIO, leave_room, emit, disconnect, join_room

from database import *
from models import MatchmakingQueue, Player, Status, Game
from utils import check_credentials_format

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

clients_dictionary = {}
active_games = {}
queue = MatchmakingQueue()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AWap9DTrxJXzkdV486KzG44CMOMByo3W' # Not very clean, but it's not in a production server.
socketio = SocketIO(app, async_mode='threading', ping_timeout=10, ping_interval=5)

@socketio.on('connect')
def handle_connect():
    socket_id = request.sid
    clients_dictionary[socket_id] = Player(socket_id, request.environ.get('REMOTE_ADDR', 'unknown'), False)

    logging.info(f"[CONNECT] {socket_id} from {request.remote_addr}")

@socketio.on('disconnect')
def handle_disconnect():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    if player.authenticated:
        if player.status == Status.IN_QUEUE :
            queue.remove_player(socket_id)

        elif player.status == Status.IN_GAME:
            handle_forfeit(True, socket_id)
            leave_room(player.current_game_id, sid=socket_id)

        logout_user_update(player)

        logging.info(f"[DISCONNECT] {player.username} depuis {player.player_ip} après {str(datetime.now() - player.connected_at)}")
    else:
        logging.info(f"[DISCONNECT] {socket_id} from {request.remote_addr}")

    del clients_dictionary[socket_id]

@socketio.on('register')
def handle_register(data):
    email = data['email'].lower().strip()
    password = data['password']
    username = data['username'].strip()

    validation_result = check_credentials_format(email, password, username, True)
    if not validation_result['valid']:
        emit('register_error', {'message': validation_result['error']})
        return

    if email_exists(email):
        emit('register_error', {'message': 'Cet email est déjà utilisé'})
        return

    if username_exists(username):
        emit('register_error', {'message': 'Ce nom d\'utilisateur est déjà pris'})
        return

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_hash = password_hash.decode('utf-8')

    player_id = str(uuid.uuid4())

    add_user_in_database(player_id, email, password_hash, username)

    emit('register_success')
    logging.info(f"New registered user : {username} ({email}) (player_id: {player_id})")

@socketio.on('login')
def handle_login(data):
    email = data['email'].lower().strip()
    password = data['password']

    validation_result = check_credentials_format(email, password, None, False)
    if not validation_result['valid']:
        emit('login_error', {'message': validation_result['error']})
        return

    user = get_user_by_email(email)

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')): # Check if user exists and password matches
        emit('login_error', {'message': 'Email ou mot de passe incorrect'})
        return

    socket_id = request.sid
    connection_time = datetime.now()
    login_user_update(user['player_id'], socket_id, request.environ.get('REMOTE_ADDR', 'unknown'), connection_time)

    player = clients_dictionary[socket_id]
    player.authenticated = True
    player.player_id = user['player_id']
    player.username = user['username']
    player.total_games_count = user['total_games_count']
    player.win_games_count = user['win_games_count']
    player.lose_games_count = user['lose_games_count']
    player.tie_games_count = user['tie_games_count']
    player.connected_at = connection_time
    player.status = Status.CONNECTED

    emit('login_success', {'player_username': player.username})
    logging.info(f"User connected : {user['username']} ({email}) - Socket: {socket_id}")

@socketio.on('logout')
def handle_logout():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    logout_user_update(player)

    emit('logout_success')
    logging.info(f"User disconnected: {player.username} ({socket_id})")

    disconnect()

@socketio.on('join_queue')
def handle_join_queue():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    queue.add_player(socket_id)
    player.join_queue()

    emit('queue_joined', {'size': queue.size()})
    logging.info(f"{player.username} join the queue")

    check_matchmaking()

@socketio.on('leave_queue')
def handle_leave_queue():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    queue.remove_player(socket_id)
    player.leave_queue()

    emit('queue_left')
    logging.info(f"{player.username} leave the queue")

@socketio.on('play_move')
def handle_play_move(data):
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    game_id = player.current_game_id
    game = active_games[game_id]

    column = data['column']
    row = game.board.get_lowest_empty_row(column)

    if game.players[game.current_player_index] != player:
        emit('move_error', {'message': 'Ce n\'est pas votre tour de jouer.'})
        return

    if game.board.is_column_full(column):
        emit('move_error', {'message': 'La colonne est pleine.'})
        return

    game.play_move(row, column)

    emit('move_played', {'grid': game.board.grid}, to=game_id)

    if game.player_win(row, column, game.current_player_index + 1):
        game.winner = game.current_player_index + 1
        game.is_finished = True
    elif game.board.is_board_full():
        game.is_finished = True
    else:
        game.current_player_index = 1 - game.current_player_index
        emit('your_turn', {'your_turn': True}, to=game.get_opponent_socket_id(socket_id))
        emit('your_turn', {'your_turn': False}, to=socket_id)

    if game.is_finished:
        if game.winner:
            winner_username = game.players[game.winner - 1].username
            game_over_data = {'winner': winner_username,'reason': 'victory'}

            logging.info(f"Victory of : {winner_username} in the party : {game_id}")
        else:
            game_over_data = {'winner': None, 'reason': 'draw'}

            logging.info(f"Tie game in : {game_id}")

        emit('game_over', game_over_data, to=game_id)

        clean_game(game, game_id)

@socketio.on('forfeit')
def handle_forfeit(due_to_disconnection=False, socket_id=None):
    """
    The following if/else is to determine special cases where the player forfeits due to disconnection,
    so he can transmit his socket_id to the function, so the socket_id is sent via handle_disconnect()
    function from 'disconnect' event in server.py. So the function exceptionally has arguments with default values bc
    the function can be called directly from the client so it's easier to handle the case here instead of send the parameters via the client.
    """
    if not due_to_disconnection:
        socket_id = request.sid
    player = clients_dictionary[socket_id]

    game_id = player.current_game_id
    game = active_games[game_id]

    opponent_socket_id = game.get_opponent_socket_id(socket_id)
    opponent_player = clients_dictionary[opponent_socket_id]

    game.is_finished = True
    game.winner = game.players.index(opponent_player) + 1 # For more human-readable the index is incremented by 1 (p1 = 1, p2 = 2)

    emit('game_over', {'winner': opponent_player.username, 'player_who_forfeit': player.username ,'reason': "forfeit"}, to=game_id)
    logging.info(f"{player.username} forfeit against {opponent_player.username} in the party : {game_id}")

    clean_game(game, game_id)

def check_matchmaking():
    if queue.size() >= 2:
        time.sleep(1)
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

def clean_game(game, game_id):
    tie = game.is_finished and game.winner is None

    for player in game.players:
        if tie:
            result = "tie"
        else:
            player_number = game.players.index(player) + 1
            is_winner = (player_number == game.winner)
            if is_winner:
                result = "win"
            else:
                result = "lose"

        player.end_game(result)

    logging.info(f"Game finished : {game_id}")
    update_game_history(game)

    del active_games[game_id]

init_database()

host = '0.0.0.0'
port = 5000

logging.info(f"Server starting on : {host}:{port}")
socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)