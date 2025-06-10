import logging
import os
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / "db.sqlite"
schema_path = Path(__file__).resolve().parent / "schema.sql"

def init_database():
    if os.path.exists(db_path):
        logging.info("Database already exist !")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
    logging.warning("Fichier et tables de la base de données créée avec succès.")
