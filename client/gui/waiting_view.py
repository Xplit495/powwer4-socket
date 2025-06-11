import customtkinter as ctk
from client.utils.constants import MSG_WAITING

class WaitingView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.message = ctk.CTkLabel(
            center_frame,
            text=MSG_WAITING,
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
        self.controller.socket_client.leave_queue()
        self.controller.show_view("menu")

    def show(self):
        self.pack(fill="both", expand=True)
        self.progress.start()

    def hide(self):
        self.progress.stop()
        self.pack_forget()