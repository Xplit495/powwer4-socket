import logging
import uuid
from datetime import datetime

import bcrypt
from flask import request
from flask_socketio import emit, disconnect

from server import socketio, clients_dictionary
from server.database import (
    email_exists, username_exists, add_user_in_database,
    get_user_by_email, login_user_update, logout_user_update
)
from server.models import Status
from server.utils import check_credentials_format


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