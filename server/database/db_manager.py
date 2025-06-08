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