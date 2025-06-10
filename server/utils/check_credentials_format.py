import re

def check_credentials_format(email, password_hash, username, is_register):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Format d\'email invalide'}

    if len(password_hash) < 10:
        return {'valid': False, 'error': 'Mot de passe invalide'}

    if is_register:
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(username_pattern, username):
            return {'valid': False, 'error': 'Formant de pseudo invalide (a-z, A-Z, 0-9, _, -)'}

    return {'valid': True, 'error': None}