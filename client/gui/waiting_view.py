import customtkinter as ctk

class WaitingView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.message = None
        self.progress = None

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.message = ctk.CTkLabel(
            center_frame,
            text="Recherche d'un adversaire...",
            font=("Arial", 24)
        )
        self.message.pack(pady=30)

        self.progress = ctk.CTkProgressBar(center_frame, width=400)
        self.progress.pack(pady=20)
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        cancel_btn = ctk.CTkButton(
            center_frame,
            text="Annuler",
            command=self.cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(pady=20)

    def cancel(self):
        self.controller.socketio.emit('leave_queue')
        self.controller.show_view("menu")

    def show(self):
        self.pack(fill="both", expand=True)
        if self.progress:
            self.progress.start()

    def hide(self):
        if self.progress:
            self.progress.stop()
        self.pack_forget()