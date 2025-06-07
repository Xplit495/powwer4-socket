import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO, emit

from handlers import forfeit_due_to_disconnection
from models import MatchmakingQueue
from models import Player, Status
from server.database.init_db import init_database

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

socketio = SocketIO(
    app,
    async_mode='threading',
    ping_timeout=10,
    ping_interval=5,
    max_http_buffer_size=1000000
)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

connected_clients = {}
active_games = {}
queue = MatchmakingQueue()

@socketio.on('connect')
def handle_connect():
    socket_id = request.sid

    connected_clients[socket_id] = Player(socket_id, request.remote_addr, datetime.now(), False)

    logger.info(f"[CONNECT] {socket_id} from {request.remote_addr}")

    emit('connected', {
        'status': 'connected',
        'message': 'Connexion avec le serveur établie'
    })

@socketio.on('disconnect')
def handle_disconnect():
    socket_id = request.sid

    if socket_id not in connected_clients:
        logger.warning(f"[DISCONNECT] Socket inconnu: {socket_id}")
        return

    player = connected_clients[socket_id]

    connection_duration = str(datetime.now() - player.connected_at).split('.')[0]
    logger.info(f"[DISCONNECT] {player.username} ({socket_id}) depuis {player.player_ip} après {connection_duration}")

    if player.status == Status.WAITING :
        queue.remove_player(socket_id)
        
    if player.status == Status.IN_GAME:
        forfeit_due_to_disconnection(socket_id, player)

    del connected_clients[socket_id]

def broadcast_to_game(game_id, event_name, data, exclude_sid=None):
    """
    Envoie un message à tous les joueurs d'une partie.

    PARAMÈTRES :
    - game_id : identifiant de la partie
    - event_name : nom de l'événement Socket.IO
    - data : données à envoyer
    - exclude_sid : socket_id à exclure (optionnel)
    """
    # TODO: Implémenter le broadcast
    pass

@socketio.on('get_server_stats')
def handle_get_server_stats():
    """
    OPTIONNEL : Pour monitoring.

    Retourne :
    - Nombre de joueurs connectés
    - Nombre de parties en cours
    - Joueurs dans la queue
    - Uptime du serveur
    """
    # TODO: Implémenter si nécessaire
    pass

if __name__ == '__main__':
    host = os.getenv('SERVER_HOST')
    port = int(os.getenv('SERVER_PORT'))
    debug = os.getenv('DEBUG') == 'True'

    logger.info(f"Démarrage du serveur sur {host}:{port}")

    init_database()

    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )