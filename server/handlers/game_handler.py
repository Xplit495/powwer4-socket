from flask import request
from flask_socketio import emit
import logging

from server import socketio, active_games, connected_clients


@socketio.on('play_move')
def handle_play_move(data):
    socket_id = request.sid
    column = data.get('column')

    logging.info(f"[GAME] Coup joué par {socket_id}: colonne {column}")

    player = connected_clients[socket_id]
    game_id = player.current_game_id

    if not game_id or game_id not in active_games:
        emit('move_error', {'message': 'Aucune partie en cours'})
        return

    game = active_games[game_id]

    result = game.play_move(player, column)

    if not result['success']:
        emit('move_error', {'message': result['error']})
        logging.warning(f"[GAME] Coup invalide de {player.username}: {result['error']}")
        return

    move_data = {
        'player': player.username,
        'player_number': game.players.index(player) + 1,
        'column': column,
        'row': result['row'],
        'next_player': None if game.is_finished else game.players[game.current_player_index].username
    }

    emit('move_played', move_data, to=game_id)

    logging.info(f"[GAME] {player.username} joue en ({result['row']}, {column}) dans la partie {game_id}")

    if game.is_finished:
        if game.winner:
            winner_player = game.players[game.winner - 1]  # winner est 1-based
            loser_player = game.players[2 - game.winner]   # L'autre joueur

            game_over_data = {
                'game_over': True,
                'winner': winner_player.username,
                'winner_player_number': game.winner,
                'reason': 'victory'
            }

            logging.info(f"[GAME] Victoire de {winner_player.username} dans la partie {game_id}")
        else:
            # Match nul
            game_over_data = {
                'game_over': True,
                'winner': None,
                'reason': 'draw'
            }

            logging.info(f"[GAME] Match nul dans la partie {game_id}")

        emit('game_over', game_over_data, to=game_id)

        # Nettoyer la partie
        clean_game(game, game_id)

@socketio.on('forfeit')
def handle_forfeit():
    socket_id = request.sid

    logging.info(f"[GAME] Forfait demandé par {socket_id}")

    # 1. Identifier la partie en cours
    player = connected_clients[socket_id]
    game_id = player.current_game_id

    if not game_id or game_id not in active_games:
        emit('forfeit_error', {'message': 'Aucune partie en cours'})
        return

    game = active_games[game_id]

    # 2. Déclarer l'adversaire vainqueur
    opponent_socket_id = game.get_opponent_socket_id(socket_id)
    opponent_player = connected_clients[opponent_socket_id]

    # Marquer la partie comme terminée avec l'adversaire comme gagnant
    game.is_finished = True
    game.winner = game.players.index(opponent_player) + 1

    # 5. Notifier les deux joueurs
    forfeit_data = {
        'game_over': True,
        'winner': opponent_player.username,
        'winner_player_number': game.winner,
        'reason': 'forfeit',
        'message': f"{player.username} a abandonné la partie"
    }

    emit('game_over', forfeit_data, room=game_id)

    logging.info(f"[GAME] {player.username} abandonne contre {opponent_player.username} dans la partie {game_id}")

    # 3-4. Mettre à jour les stats et nettoyer
    clean_game(game, game_id)

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

        logging.info(f"[GAME FINISH] {player.username} - {result} - Partie {game_id}")

    del active_games[game_id]
