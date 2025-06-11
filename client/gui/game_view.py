import customtkinter as ctk

PLAYER1_COLOR = "#FF0000"
PLAYER2_COLOR = "#FFAF00"
EMPTY_COLOR = "gray20"
HOVER_COLOR = "gray30"
CELL_SIZE = 70
CELL_PADDING = 3
MSG_YOUR_TURN = "À votre tour"
MSG_OPPONENT_TURN = "Tour de l'adversaire"

BOARD_ROWS = 6
BOARD_COLS = 7

class GameView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.board_buttons = []
        self.current_player = None
        self.is_my_turn = False

        self.setup_ui()

    def setup_ui(self):
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=20)

        self.opponent_label = ctk.CTkLabel(self.info_frame, font=("Arial", 18))
        self.opponent_label.pack(side="left", padx=20)

        self.status_label = ctk.CTkLabel(self.info_frame, font=("Arial", 16))
        self.status_label.pack(side="left", padx=20)

        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.pack(pady=20)

        for row in range(BOARD_ROWS):
            row_buttons = []
            for col in range(BOARD_COLS):
                btn = ctk.CTkButton(
                    self.board_frame,
                    text="",
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    fg_color=EMPTY_COLOR,
                    hover_color=HOVER_COLOR,
                    command=lambda c=col: self.play_move(c)
                )
                btn.grid(row=row, column=col, padx=CELL_PADDING, pady=CELL_PADDING)
                row_buttons.append(btn)
            self.board_buttons.append(row_buttons)

        forfeit_btn = ctk.CTkButton(
            self,
            text="Abandonner",
            command=self.forfeit,
            fg_color="red",
            hover_color="darkred"
        )
        forfeit_btn.pack(pady=10)

    def setup_game(self, data):
        self.opponent_label.configure(text=f"Adversaire: {data['opponent_username']}")
        self.current_player = data['player_number']
        self.is_my_turn = data['your_turn']
        self.update_status()
        self.clear_board()

    def play_move(self, column):
        if self.is_my_turn:
            self.controller.socket_client.play_move(column)

    def update_board(self, grid):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                cell = grid[row][col]
                if cell == 1:
                    color = PLAYER1_COLOR
                elif cell == 2:
                    color = PLAYER2_COLOR
                else:
                    color = EMPTY_COLOR
                self.board_buttons[row][col].configure(fg_color=color)

    def update_status(self):
        if self.is_my_turn:
            self.status_label.configure(text=MSG_YOUR_TURN, text_color="green")
        else:
            self.status_label.configure(text=MSG_OPPONENT_TURN, text_color="orange")

    def forfeit(self):
        self.controller.socket_client.forfeit()

    def clear_board(self):
        for row in self.board_buttons:
            for btn in row:
                btn.configure(fg_color=EMPTY_COLOR)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()