import customtkinter as ctk
from gui.main_window import MainWindow
from network.socket_client import SocketClient

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    socket_client = SocketClient()

    app = MainWindow(socket_client)
    app.run()

if __name__ == "__main__":
    main()