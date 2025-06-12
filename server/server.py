import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO, leave_room

from database import init_database, logout_user_update
from models import MatchmakingQueue, Player, Status

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

clients_dictionary = {}
active_games = {}
queue = MatchmakingQueue()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

socketio = SocketIO(app, async_mode='threading', ping_timeout=10, ping_interval=5)

from handlers.logon_handler import handle_register

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
            # Local import to avoid circular import issues
            from handlers import handle_forfeit
            handle_forfeit(True, socket_id)
            leave_room(player.current_game_id, sid=socket_id)

        logout_user_update(player)

        logging.info(f"[DISCONNECT] {player.username} depuis {player.player_ip} après {str(datetime.now() - player.connected_at)}")
    else:
        logging.info(f"[DISCONNECT] {socket_id} from {request.remote_addr}")

    del clients_dictionary[socket_id]

init_database()

host = os.getenv('SERVER_HOST')
port = int(os.getenv('SERVER_PORT'))

logging.info(f"Server starting on : {host}:{port}")
socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)