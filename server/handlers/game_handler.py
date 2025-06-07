from flask import request

from server import *


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

def forfeit_due_to_disconnection(socket_id, player):
    game_id = player.current_game_id
    game = active_games[game_id]
    opponent_socket_id = game.get_opponent_socket_id(socket_id)

    emit('forfeit', {'message': f"{player.username} a abandonné la partie."}, to=opponent_socket_id)

    opponent_player = connected_clients[opponent_socket_id]
    game.is_finished = True
    game.winner = game.players.index(opponent_player) + 1

    clean_game(game, game_id)

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

        logger.info(f"[GAME FINISH] {player.username} - {result} - Partie {game_id}")

    del active_games[game_id]
