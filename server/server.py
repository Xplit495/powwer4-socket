import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO, emit

from models import Player, Status
from models import MatchmakingQueue

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

def forfeit_due_to_disconnection(socket_id, player):
    game_id = player.current_game_id
    game = active_games[game_id]
    opponent_socket_id = game.get_opponent_socket_id(socket_id)

    emit('forfeit', {'message': f"{player.username} a abandonné la partie."}, to=opponent_socket_id)

    opponent_player = connected_clients[opponent_socket_id]
    game.is_finished = True
    game.winner = game.players.index(opponent_player) + 1

    clean_game(game, game_id)

@socketio.on('register')
def handle_register(data):
    """
    Le client s'identifie avec ses informations.

    DONNÉES REÇUES : {
        'username': str,      # Pseudo du joueur
        'client_version': str # Version du client (pour compatibilité)
    }

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Valider le format des données reçues
    2. Vérifier que le username est valide (longueur, caractères...)
    3. Vérifier que le socket_id n'est pas déjà enregistré
    4. Créer un objet Player avec les infos
    5. Stocker dans registered_players
    6. Répondre au client avec succès ou erreur

    RÉPONSES POSSIBLES :
    - emit('register_success', {'username': ..., 'player_id': ...})
    - emit('register_error', {'message': 'Username already taken'})
    """
    logger.info(f"Tentative d'enregistrement: {data}")

    # TODO: Implémenter la validation et l'enregistrement
    pass

@socketio.on('login')
def handle_login(data):
    """
    OPTIONNEL : Si vous avez un système de comptes persistants.

    DONNÉES REÇUES : {
        'email': str,
        'password': str
    }

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Vérifier les credentials dans la base de données
    2. Créer une session pour le joueur
    3. Charger les stats du joueur
    4. Répondre avec un token ou les infos du joueur
    """
    # TODO: Implémenter si nécessaire
    pass

@socketio.on('join_queue')
def handle_join_queue():
    """
    Le joueur veut jouer et rejoint la file d'attente.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Vérifier que le joueur est bien enregistré
    2. Vérifier qu'il n'est pas déjà dans la queue
    3. Vérifier qu'il n'est pas déjà en partie
    4. L'ajouter à waiting_queue
    5. Lui envoyer sa position dans la queue
    6. Déclencher la vérification de matchmaking

    RÉPONSES :
    - emit('queue_joined', {'position': int, 'players_waiting': int})
    - emit('queue_error', {'message': 'Already in queue'})
    """
    socket_id = request.sid
    logger.info(f"Joueur {socket_id} rejoint la queue")

    # TODO: Implémenter la logique de queue
    pass

@socketio.on('leave_queue')
def handle_leave_queue():
    """
    Le joueur quitte la file d'attente.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Vérifier que le joueur est dans la queue
    2. Le retirer de waiting_queue
    3. Confirmer au client

    RÉPONSE :
    - emit('queue_left', {'message': 'You left the queue'})
    """
    # TODO: Implémenter
    pass

def check_matchmaking():
    """
    Fonction utilitaire pour créer des matchs.
    Appelée après chaque join_queue.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Vérifier s'il y a au moins 2 joueurs dans waiting_queue
    2. Prendre les 2 premiers (FIFO) ou faire du skill-based matching
    3. Créer une nouvelle partie (Game)
    4. Créer une room Socket.IO pour cette partie
    5. Notifier les deux joueurs
    6. Retirer les joueurs de la queue
    """
    # TODO: Implémenter la création de matchs
    pass


@socketio.on('play_move')
def handle_play_move(data):
    """
    Un joueur joue un coup.

    DONNÉES REÇUES : {
        'column': int  # Colonne choisie (0-6)
    }

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Identifier le joueur et sa partie en cours
    2. Vérifier que c'est bien son tour
    3. Valider le coup (colonne valide, pas pleine)
    4. Appliquer le coup sur le Board
    5. Vérifier s'il y a victoire ou match nul
    6. Broadcaster le coup à tous les joueurs de la partie
    7. Passer au tour suivant ou terminer la partie

    BROADCASTS (à tous dans la room) :
    - emit('move_played', {...}, room=game_id)
    - emit('game_over', {...}, room=game_id)
    """
    socket_id = request.sid
    logger.info(f"Coup joué par {socket_id}: {data}")

    # TODO: Implémenter la logique de jeu
    pass

@socketio.on('forfeit')
def handle_forfeit():
    """
    Un joueur abandonne la partie.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Identifier la partie en cours
    2. Déclarer l'adversaire vainqueur
    3. Mettre à jour les stats
    4. Nettoyer la partie
    5. Notifier les deux joueurs
    """
    # TODO: Implémenter l'abandon
    pass

@socketio.on('request_game_state')
def handle_request_game_state():
    """
    Le client demande l'état actuel de sa partie.
    Utile après une reconnexion.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Identifier la partie du joueur
    2. Envoyer l'état complet du plateau
    3. Indiquer à qui c'est le tour
    """
    # TODO: Implémenter la synchronisation
    pass

@socketio.on('send_message')
def handle_send_message(data):
    """
    OPTIONNEL : Chat pendant la partie.

    DONNÉES REÇUES : {
        'message': str
    }

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Valider et nettoyer le message
    2. Identifier la partie du joueur
    3. Broadcaster à l'adversaire
    """
    # TODO: Implémenter si souhaité
    pass

def get_player_by_socket(socket_id):
    """
    Récupère un joueur par son socket_id.
    Retourne None si non trouvé.
    """
    # TODO: Implémenter
    pass

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

        logger.info(f"[GAME OVER] {player.username} - {result} - Partie {game_id}")

    del active_games[game_id]

def update_player_stats(player):
    """
    Met à jour les statistiques du joueur après une partie.

    Il faut faire un appel à la base de données pour mettre à jour les stats persistantes.
    """
    # TODO: Implémenter la mise à jour des stats

def validate_username(username):
    """
    Valide un nom d'utilisateur.

    RÈGLES :
    - 3-20 caractères
    - Alphanumériques + underscore
    - Pas de mots interdits

    Retourne (bool, error_message)
    """
    # TODO: Implémenter la validation
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

    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )