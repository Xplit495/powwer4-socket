from dotenv import load_dotenv
from flask import Flask, request
from models import MatchmakingQueue
from models import Player, Status

from server import *

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