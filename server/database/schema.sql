CREATE TABLE IF NOT EXISTS users (
    player_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,

    total_games_count INTEGER DEFAULT 0,
    win_games_count INTEGER DEFAULT 0,
    lose_games_count INTEGER DEFAULT 0,
    tie_games_count INTEGER DEFAULT 0,

    latest_socket_id TEXT,
    latest_player_ip TEXT,
    last_connection_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS game_history (
    game_id TEXT PRIMARY KEY,

    player_id_1 TEXT NOT NULL,
    player_username_1 TEXT NOT NULL,

    player_id_2 TEXT NOT NULL,
    player_username_2 TEXT NOT NULL,

    winner INTEGER NOT NULL,

    game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);