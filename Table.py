﻿import tkinter as tk
from tkinter import messagebox
from GameClasses import Board, Move, Minimax, PlayerType
from PIL import Image, ImageTk, ImageDraw

class SimpleCheckersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Checkers")

        # Configurare meniuri
        menu_bar = tk.Menu(self.root)
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.exit_game)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

        # Canvas pentru tablă
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()

        # Încărcare imagine tablă
        try:
            self.board_image = Image.open("tabla.jpg")
            self.board_photo = ImageTk.PhotoImage(self.board_image)
        except:
            messagebox.showerror("Error", "Cannot load tabla.jpg")
            self.root.quit()

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Inițializare buffer offscreen (imaginea de fundal)
        self.buffer = Image.new("RGB", (400, 400))
        self.buffer_draw = ImageDraw.Draw(self.buffer)

        self.board = Board()
        self.current_player = PlayerType.Human
        self.selected_piece = None

        self.draw_board()

    def draw_board(self):
        # Curățare buffer offscreen
        self.buffer.paste(self.board_image, (0, 0))

        # Dimensiunea pătrățelelor
        square_size = 50
        piece_radius = square_size // 2 - 5

        # Desenează tabla
        for piece in self.board.pieces:
            x_center = square_size * piece.x + square_size // 2
            y_center = square_size * piece.y + square_size // 2
            color = (255, 0, 0) if (piece.x, piece.y) == self.selected_piece else (0, 0, 0) if piece.player == PlayerType.Computer else (255, 255, 255)
            self.buffer_draw.ellipse(
                [
                    x_center - piece_radius,
                    y_center - piece_radius,
                    x_center + piece_radius,
                    y_center + piece_radius,
                ],
                fill=color,
            )

        # Convertește buffer-ul într-un PhotoImage pentru afișare rapidă
        self.tk_buffer = ImageTk.PhotoImage(self.buffer)

        # Desenează buffer-ul pe canvas într-o singură operațiune
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_buffer)

    def on_canvas_click(self, event):
        square_size = 50
        clicked_x = event.x // square_size
        clicked_y = event.y // square_size

        if self.selected_piece is None:
            # Selectează piesa
            if self.board.get_piece_at(clicked_x, clicked_y, PlayerType.Human):
                self.selected_piece = (clicked_x, clicked_y)
                self.draw_board()
        else:
            # Mută piesa selectată
            selected_x, selected_y = self.selected_piece
            if self.board.is_valid_move(selected_x, selected_y, clicked_x, clicked_y):
                self.board.move_piece(selected_x, selected_y, clicked_x, clicked_y)
                self.selected_piece = None
                self.draw_board()

                self.current_player = PlayerType.Computer
                self.check_finish()
                if self.current_player == PlayerType.Computer:
                    self.computer_move()
            else:
                # Deselectează piesa dacă mutarea nu este validă
                self.selected_piece = None
                self.draw_board()

    def computer_move(self):
        next_board = Minimax.find_next_board(self.board)
        self.board = next_board
        self.draw_board()
        self.current_player = PlayerType.Human
        self.check_finish()

    def check_finish(self):
        finished, winner = self.board.check_finish()
        if finished:
            if winner == PlayerType.Computer:
                messagebox.showinfo("Game Over", "Calculatorul a câștigat!")
            elif winner == PlayerType.Human:
                messagebox.showinfo("Game Over", "Ai câștigat!")
            self.current_player = PlayerType.NoPlayer

    def new_game(self):
        self.board = Board()
        self.current_player = PlayerType.Computer
        self.computer_move()

    def exit_game(self):
        self.root.quit()

    def show_about(self):
        about_text = "Joc de dame realizat în Python"
        messagebox.showinfo("Despre jocul Dame", about_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCheckersApp(root)
    root.mainloop()
