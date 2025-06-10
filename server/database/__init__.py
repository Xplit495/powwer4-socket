from .db_manager import (
    email_exists, username_exists, add_user_in_database,
    get_user_by_email, login_user_update, logout_user_update,
    logout_user_update
)
from .init_db import init_database, db_path