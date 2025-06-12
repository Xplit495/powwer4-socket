import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.tabview = None
        self.login_email = None
        self.login_password = None
        self.login_error = None
        self.reg_email = None
        self.reg_username = None
        self.reg_password = None
        self.register_error = None

        title = ctk.CTkLabel(self, text="Puissance 4 Online", font=("Arial", 36, "bold"))
        title.pack(pady=40)

        self.tabview = ctk.CTkTabview(self, width=400, height=350)
        self.tabview.pack(pady=20)

        self.setup_login_tab()
        self.setup_register_tab()

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
            command=self.handle_register,
            width=300,
            height=40
        )
        register_btn.pack(pady=20)

        self.register_error = ctk.CTkLabel(tab, text="", text_color="red")
        self.register_error.pack()

    def setup_login_tab(self):
        tab = self.tabview.add("Connexion")

        self.login_email = ctk.CTkEntry(tab, placeholder_text="Email", width=300)
        self.login_email.pack(pady=15)

        self.login_password = ctk.CTkEntry(tab, placeholder_text="Mot de passe", show="*", width=300)
        self.login_password.pack(pady=15)

        login_btn = ctk.CTkButton(
            tab,
            text="Se connecter",
            command=self.handle_login,
            width=300,
            height=40
        )
        login_btn.pack(pady=20)

        self.login_error = ctk.CTkLabel(tab, text="", text_color="red")
        self.login_error.pack()

    def handle_register(self):
        email = self.reg_email.get()
        password = self.reg_password.get()
        username = self.reg_username.get()

        if email and password and username:
            self.register_error.configure(text="")
            self.controller.socketio.emit('register', {'email': email, 'password': password, 'username': username})
        else:
            self.register_error.configure(text="Veuillez remplir tous les champs")

    def handle_login(self):
        email = self.login_email.get()
        password = self.login_password.get()

        if email and password:
            self.login_error.configure(text="")
            self.controller.socketio.emit('login', {'email': email, 'password': password})
        else:
            self.login_error.configure(text="Veuillez remplir tous les champs")

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()