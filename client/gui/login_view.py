import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.register_error = None
        self.reg_password = None
        self.reg_username = None
        self.reg_email = None
        self.login_error = None
        self.login_password = None
        self.login_email = None

        title = ctk.CTkLabel(self, text="Puissance 4 Online", font=("Arial", 36, "bold"))
        title.pack(pady=40)

        self.tabview = ctk.CTkTabview(self, width=400, height=350)
        self.tabview.pack(pady=20)

        self.setup_login_tab()
        self.setup_register_tab()

    def setup_login_tab(self):
        tab = self.tabview.add("Connexion")

        self.login_email = ctk.CTkEntry(tab, placeholder_text="Email", width=300)
        self.login_email.pack(pady=15)

        self.login_password = ctk.CTkEntry(tab, placeholder_text="Mot de passe", show="*", width=300)
        self.login_password.pack(pady=15)

        login_btn = ctk.CTkButton(
            tab,
            text="Se connecter",
            command=self.login,
            width=300,
            height=40
        )
        login_btn.pack(pady=20)

        self.login_error = ctk.CTkLabel(tab, text="", text_color="red")
        self.login_error.pack()

    def setup_register_tab(self):
        tab = self.tabview.add("Inscription")

        self.reg_email = ctk.CTkEntry(tab, placeholder_text="Email", width=300)
        self.reg_email.pack(pady=10)

        self.reg_username = ctk.CTkEntry(tab, placeholder_text="Pseudo", width=300)
        self.reg_username.pack(pady=10)

        self.reg_password = ctk.CTkEntry(tab, placeholder_text="Mot de passe", show="*", width=300)
        self.reg_password.pack(pady=10)

        register_btn = ctk.CTkButton(
            tab,
            text="S'inscrire",
            command=self.register,
            width=300,
            height=40
        )
        register_btn.pack(pady=20)

        self.register_error = ctk.CTkLabel(tab, text="", text_color="red")
        self.register_error.pack()

    def login(self):
        email = self.login_email.get()
        password = self.login_password.get()

        if email and password:
            self.controller.socket_client.login(email, password)

    def register(self):
        email = self.reg_email.get()
        username = self.reg_username.get()
        password = self.reg_password.get()

        if email and username and password:
            self.controller.socket_client.register(email, username, password)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()