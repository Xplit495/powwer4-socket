import customtkinter as ctk

from socket_to_gui import SocketToGui

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = SocketToGui()
app.run()