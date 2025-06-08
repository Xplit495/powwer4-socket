import logging
import re
import uuid

from flask_socketio import emit

from server import socketio
from server.database import email_exists, username_exists, create_user


@socketio.on('register')
def handle_register(data):
    try:
        validation_result = validate_registration_data(data)
        if not validation_result['valid']:
            emit('register_error', {'message': validation_result['error']})
            return

        email = data['email'].lower().strip()
        username = data['username'].strip()
        password_hash = data['password']

        if email_exists(email):
            emit('register_error', {'message': 'Cet email est déjà utilisé'})
            return

        if username_exists(username):
            emit('register_error', {'message': 'Ce nom d\'utilisateur est déjà pris'})
            return

        player_id = str(uuid.uuid4())

        create_user(player_id, email, password_hash, username)

        emit('register_success', {
            'message': 'Inscription réussie',
            'username': username
        })

        logging.info(f"Nouvel utilisateur inscrit: {username} ({email}) (player_id: {player_id})")

    except Exception as e:
        logging.error(f"Erreur lors de l'inscription: {e}")
        emit('register_error', {'message': 'Erreur serveur, veuillez réessayer'})

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

# Pour faire jolie, car une verification via mail serait plus esthétique, mais ce sera un bonus
def validate_registration_data(data):
    required_fields = ['email', 'username', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'error': f'Le champ {field} est requis'}

    email = data['email'].strip()
    username = data['username'].strip()
    password = data['password']

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Format d\'email invalide'}

    username_pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(username_pattern, username):
        return {'valid': False, 'error': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, _ et -'}

    if len(password) < 10:  # Un hash devrait être plus long
        return {'valid': False, 'error': 'Mot de passe invalide'}

    return {'valid': True, 'error': None}