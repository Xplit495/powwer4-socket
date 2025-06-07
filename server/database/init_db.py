import sqlite3
import os

def init_database():
    if os.path.exists('db.sqlite'):
        print("La base de données existe déjà. Aucune action n'est nécessaire.")
        return

    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    with open('schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    conn.commit()
    print("Fichier et tables de la base de données créée avec succès.")

    conn.close()