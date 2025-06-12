import customtkinter as ctk

class MenuView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.welcome_label = None

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.welcome_label = ctk.CTkLabel(
            center_frame,
            text="Bienvenue !",
            font=("Arial", 32, "bold")
        )
        self.welcome_label.pack(pady=40)

        play_btn = ctk.CTkButton(
            center_frame,
            text="JOUER",
            command=self.play,
            width=250,
            height=60,
            font=("Arial", 20, "bold"),
            corner_radius=30
        )
        play_btn.pack(pady=20)

        logout_btn = ctk.CTkButton(
            center_frame,
            text="Se déconnecter",
            command=self.logout,
            width=250,
            height=50,
            fg_color="red",
            hover_color="darkred",
            corner_radius=25
        )
        logout_btn.pack(pady=10)

    def play(self):
        self.controller.socket_client.join_queue()

    def logout(self):
        self.controller.socket_client.logout()

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()