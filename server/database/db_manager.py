import logging
import sqlite3

from .init_db import db_path


def get_db_connection():
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.critical(f"Erreur de connexion à la DB: {e} - {db_path}")
        raise

def email_exists(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,)) # Sert à retourner 1 si l'email existe, on se fiche de la valeur retournée, on veut juste savoir si l'email existe ou pas
    is_email = cursor.fetchone()

    conn.close()
    return is_email is not None

def username_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE username = ? LIMIT 1", (username,)) # Sert à retourner 1 si le nom d'utilisateur existe, on se fiche de la valeur retournée, on veut juste savoir si le nom d'utilisateur existe ou pas
    is_username = cursor.fetchone()

    conn.close()
    return is_username is not None

def add_user_in_database(player_id, email, password_hash, username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            player_id, email, password_hash, username,
            total_games_count, win_games_count, lose_games_count, tie_games_count
        ) VALUES (?, ?, ?, ?, 0, 0, 0, 0)
    """, (player_id, email, password_hash, username))

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT player_id, password_hash, username, total_games_count, 
        win_games_count, lose_games_count, tie_games_count
        FROM users WHERE email = ?
    """, (email,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'player_id': result['player_id'],
            'password_hash': result['password_hash'],
            'username': result['username'],
            'total_games_count': result['total_games_count'],
            'win_games_count': result['win_games_count'],
            'lose_games_count': result['lose_games_count'],
            'tie_games_count': result['tie_games_count'],
        }
    return None

def login_user_update(player_id, socket_id, player_ip, last_connection_time):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users 
        SET latest_socket_id = ?, 
            latest_player_ip = ?, 
            last_connection_time = ?
        WHERE player_id = ?
    """, (socket_id, player_ip, last_connection_time, player_id))

    conn.commit()
    conn.close()

def logout_user_update(player):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users 
        SET total_games_count = ?,
            win_games_count = ?,
            lose_games_count = ?,
            tie_games_count = ?
        WHERE player_id = ?
    """, (player.total_games_count, player.win_games_count,
          player.lose_games_count, player.tie_games_count,
          player.player_id))

    conn.commit()
    conn.close()

def update_game_history(game):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO game_history (
            game_id, player_id_1, player_username_1, player_id_2, player_username_2, winner, game_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,(game.game_id, game.players[0].player_id, game.players[0].username, game.players[1].player_id,
        game.players[1].username, game.winner, game.game_date))

    conn.commit()
    conn.close()