import tkinter as tk
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
            messagebox.showerror("Error", "Cannot load table.jpg")
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
        square_size = 50  # Tabla este 400x400 pixeli, deci 50x50 pe pătrățel
        piece_radius = square_size // 2 - 5  # Dimensiunea piesei

        # Pozițiile pieselor
        black_pieces = [
            (1, 0), (3, 0), (5, 0), (7, 0),
            (0, 1), (2, 1), (4, 1), (6, 1),
            (1, 2), (3, 2), (5, 2), (7, 2),
        ]
        white_pieces = [
            (0, 5), (2, 5), (4, 5), (6, 5),
            (1, 6), (3, 6), (5, 6), (7, 6),
            (0, 7), (2, 7), (4, 7), (6, 7),
        ]

        # Desenează piesele negre
        for x, y in black_pieces:
            x_center = square_size * x + square_size // 2
            y_center = square_size * y + square_size // 2
            self.buffer_draw.ellipse(
                [
                    x_center - piece_radius,  # Stânga
                    y_center - piece_radius,  # Sus
                    x_center + piece_radius,  # Dreapta
                    y_center + piece_radius,  # Jos
                ],
                fill=(0, 0, 0),  # Culoare neagră
            )

        # Desenează piesele albe
        for x, y in white_pieces:
            x_center = square_size * x + square_size // 2
            y_center = square_size * y + square_size // 2
            self.buffer_draw.ellipse(
                [
                    x_center - piece_radius,  # Stânga
                    y_center - piece_radius,  # Sus
                    x_center + piece_radius,  # Dreapta
                    y_center + piece_radius,  # Jos
                ],
                fill=(255, 255, 255),  # Culoare albă
            )

        # Convertește buffer-ul într-un PhotoImage pentru afișare rapidă
        self.tk_buffer = ImageTk.PhotoImage(self.buffer)

        # Desenează buffer-ul pe canvas într-o singură operațiune
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_buffer)

    def on_canvas_click(self, event):
        if self.current_player != PlayerType.Human:
            return

        mouse_x = event.x // 125
        mouse_y = 3 - (event.y // 125)

        if self.selected_piece is None:
            # Selectează o piesă
            for p in self.board.pieces:
                if p.player == PlayerType.Human and p.x == mouse_x and p.y == mouse_y:
                    self.selected_piece = p.id
                    self.draw_board()
                    return
        else:
            # Mută piesa selectată
            selected_piece = self.board.pieces[self.selected_piece]
            move = Move(self.selected_piece, mouse_x, mouse_y)

            if selected_piece.is_valid_move(self.board, move):
                self.selected_piece = None
                new_board = self.board.make_move(move)
                self.board = new_board
                self.draw_board()

                self.current_player = PlayerType.Computer
                self.check_finish()
                
                if self.current_player == PlayerType.Computer:
                    self.computer_move()

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
                messagebox.showinfo("Game Over", "Calculatorul a castigat!")
            elif winner == PlayerType.Human:
                messagebox.showinfo("Game Over", "Ai castigat!")
            self.current_player = PlayerType.NoPlayer

    def new_game(self):
        self.board = Board()
        self.current_player = PlayerType.Computer
        self.computer_move()

    def exit_game(self):
        self.root.quit()

    def show_about(self):
        about_text = (
            "Algoritmul minimax\r\n" 
            "Inteligenta artificiala, Laboratorul 7\r\n" 
            "(c)2024 Florin Leon\r\n" 
            "http://florinleon.byethost24.com/lab_ia.html"
        )
        messagebox.showinfo("Despre jocul Dame simple", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCheckersApp(root)
    root.mainloop()
