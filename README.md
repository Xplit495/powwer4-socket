# 🎮 Connect 4 Online

A real-time multiplayer Connect 4 game with modern GUI and automatic matchmaking system.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![Socket.IO](https://img.shields.io/badge/socket.io-4.0+-yellow.svg)

## 📋 Description

**Connect 4 Online** is a desktop application that allows you to play the classic Connect 4 game online against other players. The project uses a robust client-server architecture with WebSocket communication to ensure a smooth real-time gaming experience.

### ✨ Key Features

- 🔐 **Secure Authentication**: Sign up/login with bcrypt hashing
- 🎯 **Automatic Matchmaking**: FIFO queue to quickly find an opponent
- ⚡ **Real-time**: Instant bidirectional communication via Socket.IO
- 📊 **Statistics**: Win/loss tracking (stored in database)
- 🎨 **Modern Interface**: Intuitive GUI with CustomTkinter
- 🔌 **Disconnection Handling**: Automatic forfeit and reconnection

## 🛠️ Technologies Used

### Backend
- **Python 3.8+**
- **Flask** + **Flask-SocketIO**
- **SQLite3** (database)
- **bcrypt** (security)
- **eventlet** (async server)

### Frontend
- **Python 3.8+**
- **CustomTkinter** (graphical interface)
- **python-socketio[client]**
- **threading**

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Xplit495/power4-socket
cd power4-socket
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Launch the Game

1. **Start the server** (terminal 1)
```bash
python server/server.py
```

2. **Launch the client** (terminal 2)
```bash
python client/client.py
```

To play with two players, simply launch two client instances!

## 📁 Project Structure

```
power4-socket/
├── client/                 # Client application
│   ├── client.py          # Entry point
│   ├── socket_to_gui.py   # Socket/GUI handler
│   └── gui/               # Interface views
├── server/                # Game server
│   ├── server.py         # Flask-SocketIO server
│   ├── database/         # SQLite database management
│   └── models/           # Business classes (Game, Player, Board)
├── requirements.txt      # Dependencies
└── README.md
```

## 🎮 How to Play

1. **Sign up/Login**: Create an account or log in
2. **Main Menu**: Click "PLAY" to join the queue
3. **Matchmaking**: Wait for an opponent to be found (automatic)
4. **Game**: Click on a column to play, align 4 pieces to win!

### Game Rules
- Players take turns placing a piece of their color
- Pieces fall by gravity in the chosen column
- First to align 4 pieces (horizontal, vertical, or diagonal) wins
- If the grid is full without a winner, it's a tie

## 🔧 Advanced Configuration

The server listens by default on all interfaces (`0.0.0.0:5000`).

To modify the server URL on the client side, edit the `SERVER_URL` variable in `client/socket_to_gui.py`:
```python
SERVER_URL = "http://your-server:5000"
```

## 📊 Technical Features

- **MVC Architecture** with clear separation of concerns
- **Security**: Server-side validation, hashed passwords
- **Performance**: O(1) win detection algorithm
- **Stability**: Robust disconnection/reconnection handling

## 🚧 Future Improvements

- [ ] Live chat between players
- [ ] Statistics visualization in the interface
- [ ] Spectator mode
- [ ] ELO ranking system
- [ ] AI mode
- [ ] Customizable themes

## 👤 Author

Solo project completed as part of a school assignment (OOP).

- **Duration**: 1 month
- **Development hours**: ~80 hours
- **First experience** with Socket.IO and CustomTkinter


⭐ **Feel free to star this project if you found it useful!**