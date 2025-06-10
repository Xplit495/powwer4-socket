import logging
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "db.sqlite"

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"[URGENT] Erreur de connexion à la DB: {e} - {DB_PATH}")
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

def create_user(player_id, email, password_hash, username):
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
        SELECT player_id, email, password_hash, username,
               total_games_count, win_games_count, lose_games_count, tie_games_count,
               latest_socket_id, latest_player_ip, last_connection_time
        FROM users WHERE email = ?
    """, (email,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'player_id': result['player_id'],
            'email': result['email'],
            'password_hash': result['password_hash'],
            'username': result['username'],
            'total_games_count': result['total_games_count'],
            'win_games_count': result['win_games_count'],
            'lose_games_count': result['lose_games_count'],
            'tie_games_count': result['tie_games_count'],
            'latest_socket_id': result['latest_socket_id'],
            'latest_player_ip': result['latest_player_ip'],
            'last_connection_time': result['last_connection_time']
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
    """
    Met à jour les statistiques du joueur qu'il soit partie de l'application.

    Il faut faire un appel à la base de données pour mettre à jour les stats persistantes.
    """
    # TODO: Implémenter la mise à jour des stats

def update_game_stats(game):
    """
    Ajoute les statistiques d'une partie à la base de données.
    """