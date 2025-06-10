import logging

from flask import request
from flask_socketio import emit

from server import socketio, active_games, clients_dictionary


@socketio.on('play_move')
def handle_play_move(data):
    socket_id = request.sid
    player = clients_dictionary[socket_id]

    game_id = player.current_game_id
    game = active_games[game_id]

    column = data['column']
    row = game.board.get_lowest_empty_row(column)

    if game.players[game.current_player_index] != player:
        emit('move_error', {'message': 'Ce n\'est pas votre tour de jouer.'})
        return

    if game.board.is_column_full(column):
        emit('move_error', {'message': 'La colonne est pleine.'})
        return

    game.play_move(row, column)

    emit('move_played', {'grid': game.board.grid}, to=game_id)

    if game.player_win(row, column, game.current_player_index + 1):
        game.winner = game.current_player_index + 1
        game.is_finished = True
    elif game.board.is_board_full():
        game.is_finished = True
    else:
        game.current_player_index = 1 - game.current_player_index
        emit('your_turn', {'your_turn': True}, to=game.get_opponent_socket_id(socket_id))
        emit('your_turn', {'your_turn': False}, to=socket_id)

    if game.is_finished:
        if game.winner:
            winner_username = game.players[game.winner - 1].username
            game_over_data = {'winner': winner_username,'reason': 'victory'}

            logging.info(f"Victory of : {winner_username} in the party : {game_id}")
        else:
            game_over_data = {'winner': None, 'reason': 'draw'}

            logging.info(f"Tie game in : {game_id}")

        emit('game_over', game_over_data, to=game_id)

        clean_game(game, game_id)

@socketio.on('forfeit')
def handle_forfeit(due_to_disconnection=False, socket_id=None):
    """
    The following if/else is to determine special cases where the player forfeits due to disconnection,
    so he can transmit his socket_id to the function, so the socket_id is sent via handle_disconnect()
    function from 'disconnect' event in server.py. So the function exceptionally has arguments with default values bc
    the function can be called directly from the client so it's easier to handle the case here instead of send the parameters via the client.
    """
    if due_to_disconnection:
        socket_id = socket_id
    else:
        socket_id = request.sid
    player = clients_dictionary[socket_id]

    game_id = player.current_game_id
    game = active_games[game_id]

    opponent_socket_id = game.get_opponent_socket_id(socket_id)
    opponent_player = clients_dictionary[opponent_socket_id]

    game.is_finished = True
    game.winner = game.players.index(opponent_player) + 1 # For more human-readable the index is incremented by 1 (p1 = 1, p2 = 2)

    emit('game_over', {'winner': opponent_player.username, 'message': f"{player.username} a déclaré forfait."}, to=game_id)
    logging.info(f"{player.username} forfeit against {opponent_player.username} in the party : {game_id}")

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

    logging.info(f"Game finished : {game_id}")

    del active_games[game_id]