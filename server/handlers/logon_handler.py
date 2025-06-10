import logging
import uuid
from datetime import datetime

from flask import request
from flask_socketio import emit

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
    password_hash = data['password']
    username = data['username'].strip()

    validation_result = check_credentials_format(email, password_hash, username, True)
    if not validation_result['valid']:
        emit('register_error', {'message': validation_result['error']})
        return

    if email_exists(email):
        emit('register_error', {'message': 'Cet email est déjà utilisé'})
        return

    if username_exists(username):
        emit('register_error', {'message': 'Ce nom d\'utilisateur est déjà pris'})
        return

    player_id = str(uuid.uuid4())

    add_user_in_database(player_id, email, password_hash, username)

    emit('register_success', {'message': 'Inscription réussie ! Veuillez vous connecter.'})
    logging.info(f"New registered user : {username} ({email}) (player_id: {player_id})")

@socketio.on('login')
def handle_login(data):
    email = data['email'].lower().strip()
    password_hash = data['password']

    validation_result = check_credentials_format(email, password_hash, None, False)
    if not validation_result['valid']:
        emit('login_error', {'message': validation_result['error']})
        return

    user = get_user_by_email(email)

    if not user:
        emit('login_error', {'message': 'Email ou mot de passe incorrect'})
        return

    if user['password_hash'] != password_hash:
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

    emit('login_success', {'message': 'Connexion réussie, bienvenue !'})
    logging.info(f"User connected : {user['username']} ({email}) - Socket: {socket_id}")

@socketio.on('logout')
def handle_logout():
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    logout_user_update(player)

    del clients_dictionary[socket_id]

    emit('logout_success', {'message': 'Déconnexion réussie'})
    logging.info(f"User disconnected: {player.username} ({socket_id})")