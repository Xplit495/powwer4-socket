import socketio
import threading
from client.config import SERVER_URL

class SocketClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.callbacks = {}
        self.setup_events()

    def setup_events(self):
        @self.sio.on('connect')
        def on_connect():
            self.trigger_callback('connect')

        @self.sio.on('disconnect')
        def on_disconnect():
            self.trigger_callback('disconnect')

        events = [
            'online', 'login_success', 'login_error',
            'register_success', 'register_error',
            'queue_joined', 'queue_left', 'game_found',
            'move_played', 'move_error', 'your_turn',
            'game_over', 'logout_success'
        ]

        for event in events:
            self.sio.on(event)(lambda data, e=event: self.trigger_callback(e, data))

    def set_callbacks(self, callbacks):
        self.callbacks = callbacks

    def trigger_callback(self, event, data=None):
        if event in self.callbacks:
            self.callbacks[event](data) if data else self.callbacks[event]()

    def connect(self):
        def connect_thread():
            try:
                self.sio.connect(SERVER_URL)
                self.sio.wait()
            except Exception as e:
                print(f"Erreur de connexion: {e}")

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()

    def login(self, email, password):
        self.sio.emit('login', {'email': email, 'password': password})

    def register(self, email, username, password):
        self.sio.emit('register', {
            'email': email,
            'username': username,
            'password': password
        })

    def logout(self):
        self.sio.emit('logout')

    def join_queue(self):
        self.sio.emit('join_queue')

    def leave_queue(self):
        self.sio.emit('leave_queue')

    def play_move(self, column):
        self.sio.emit('play_move', {'column': column})

    def forfeit(self):
        self.sio.emit('forfeit')