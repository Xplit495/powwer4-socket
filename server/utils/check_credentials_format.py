import re

def check_credentials_format(data, is_register):
    required_fields = ['email', 'password']
    if is_register:
        required_fields.append('username')

    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'error': f'Le champ {field} est requis'}

    email = data['email'].strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if not re.match(email_pattern, email):
        return {'valid': False, 'error': 'Format d\'email invalide'}

    password = data['password']
    if len(password) < 10:  # Un hash devrait être plus long
        return {'valid': False, 'error': 'Mot de passe invalide'}

    if is_register:
        username = data['username'].strip()
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(username_pattern, username):
            return {'valid': False, 'error': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, _ et -'}

    return {'valid': True, 'error': None}