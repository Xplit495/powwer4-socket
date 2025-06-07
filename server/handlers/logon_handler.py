from dotenv import load_dotenv
from flask import Flask, request
from models import MatchmakingQueue
from models import Player, Status

from server import *


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