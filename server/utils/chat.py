from flask import request

from server import *


@socketio.on('send_message')
def handle_send_message(data):
    """
    OPTIONNEL : Chat pendant la partie.

    CE QUE CETTE FONCTION DOIT FAIRE :
    1. Valider et nettoyer le message
    2. Identifier la partie du joueur
    3. Broadcaster à l'adversaire
    """
    # TODO: Implémenter si souhaité
    pass