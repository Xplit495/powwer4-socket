import logging
import uuid
from datetime import datetime

from flask import request
from flask_socketio import emit

from server import socketio, connected_clients
from server.database import email_exists, username_exists, create_user, get_user_by_email, login_user_update
from server.utils import check_credentials_format


@socketio.on('register')
def handle_register(data):
    try:
        validation_result = check_credentials_format(data, True)
        if not validation_result['valid']:
            emit('register_error', {'message': validation_result['error']})
            return

        email = data['email'].lower().strip()
        username = data['username'].strip()
        password_hash = data['password']

        if email_exists(email):
            emit('register_error', {'message': 'Cet email est déjà utilisé'})
            return

        if username_exists(username):
            emit('register_error', {'message': 'Ce nom d\'utilisateur est déjà pris'})
            return

        player_id = str(uuid.uuid4())

        create_user(player_id, email, password_hash, username)

        emit('register_success', {
            'message': 'Inscription réussie',
            'username': username
        })

        logging.info(f"Nouvel utilisateur inscrit: {username} ({email}) (player_id: {player_id})")

    except Exception as e:
        logging.error(f"Erreur lors de l'inscription: {e}")
        emit('register_error', {'message': 'Erreur serveur, veuillez réessayer'})

@socketio.on('login')
def handle_login(data):
    try:
        validation_result = check_credentials_format(data, False)
        if not validation_result['valid']:
            emit('login_error', {'message': validation_result['error']})
            return

        email = data['email'].lower().strip()
        password_hash = data['password']

        user = get_user_by_email(email)
        if not user:
            emit('login_error', {'message': 'Email ou mot de passe incorrect'})
            return

        if user['password_hash'] != password_hash:
            emit('login_error', {'message': 'Email ou mot de passe incorrect'})
            return

        socket_id = request.sid
        player_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        last_connection_time = datetime.now()

        login_user_update(user['player_id'], socket_id, player_ip, last_connection_time)

        logging.info(f"Informations de connexion / token mis à jour pour l'utilisateur: {user['player_id']}")

        player = connected_clients[socket_id]
        player.authenticated = True
        player.player_id = user['player_id']
        player.username = user['username']
        player.total_games_count = user['total_games_count']
        player.win_games_count = user['win_games_count']
        player.lose_games_count = user['lose_games_count']
        player.tie_games_count = user['tie_games_count']
        player.connected_at = datetime.now()

        emit('login_success', {
            'message': 'Connexion réussie',
        })

        logging.info(f"Utilisateur connecté: {user['username']} ({email}) - Socket: {socket_id}")

    except Exception as e:
        logging.error(f"Erreur lors de la connexion: {e}")
        emit('login_error', {'message': 'Erreur serveur, veuillez réessayer'})