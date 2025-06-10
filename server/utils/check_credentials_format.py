import re

def check_credentials_format(email, password, username, is_register):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Format d\'email invalide'}

    if len(password) < 8:
        return {'valid': False, 'error': 'Le mot de passe doit contenir au moins 8 caractères'}

    if is_register:
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(username_pattern, username):
            return {'valid': False, 'error': 'Format de pseudo invalide (a-z, A-Z, 0-9, _, -)'}

    return {'valid': True, 'error': None}