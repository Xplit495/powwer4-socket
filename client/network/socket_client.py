import socketio
import threading

SERVER_URL = "http://localhost:5000"

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

        @self.sio.on('online')
        def on_online(data):
            self.trigger_callback('online', data)

        @self.sio.on('login_success')
        def on_login_success(data):
            self.trigger_callback('login_success', data)

        @self.sio.on('login_error')
        def on_login_error(data):
            self.trigger_callback('login_error', data)

        @self.sio.on('register_success')
        def on_register_success(data):
            self.trigger_callback('register_success', data)

        @self.sio.on('register_error')
        def on_register_error(data):
            self.trigger_callback('register_error', data)

        @self.sio.on('logout_success')
        def on_logout_success(data):
            self.trigger_callback('logout_success', data)

        @self.sio.on('queue_joined')
        def on_queue_joined(data):
            self.trigger_callback('queue_joined', data)

        @self.sio.on('queue_left')
        def on_queue_left(data):
            self.trigger_callback('queue_left', data)

        @self.sio.on('game_found')
        def on_game_found(data):
            self.trigger_callback('game_found', data)

        @self.sio.on('move_played')
        def on_move_played(data):
            self.trigger_callback('move_played', data)

        @self.sio.on('move_error')
        def on_move_error(data):
            self.trigger_callback('move_error', data)

        @self.sio.on('your_turn')
        def on_your_turn(data):
            self.trigger_callback('your_turn', data)

        @self.sio.on('game_over')
        def on_game_over(data):
            self.trigger_callback('game_over', data)

        @self.sio.on('forfeit')
        def on_forfeit(data):
            self.trigger_callback('forfeit', data)





    # Set callbacks for events
    def set_callbacks(self, callbacks):
        self.callbacks = callbacks

    def trigger_callback(self, event, data=None):
        if event in self.callbacks:
            if data is not None:
                self.callbacks[event](data)
            else:
                self.callbacks[event]()

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
        self.sio.emit('login', {
            'email': email,
            'password': password
        })

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