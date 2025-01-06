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

        # Pozițiile pieselor negre și albe
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
            fill_color = (255, 255, 255)  # Culoare albă

            # Dacă piesa este selectată, schimbă culoarea la roșu
            if self.selected_piece and (x, y) == self.selected_piece:
                fill_color = (255, 0, 0)  # Roșu

            self.buffer_draw.ellipse(
                [
                    x_center - piece_radius,  # Stânga
                    y_center - piece_radius,  # Sus
                    x_center + piece_radius,  # Dreapta
                    y_center + piece_radius,  # Jos
                ],
                fill=fill_color,  # Culoare piesă
            )

        # Convertește buffer-ul într-un PhotoImage pentru afișare rapidă
        self.tk_buffer = ImageTk.PhotoImage(self.buffer)

        # Desenează buffer-ul pe canvas într-o singură operațiune
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_buffer)

    def highlight_piece_and_moves(self, piece):
        square_size = 50
        piece_radius = square_size // 2 - 5

        # Evidențiem piesa selectată
        x_center = piece.x * square_size + square_size // 2
        y_center = piece.y * square_size + square_size // 2
        self.buffer_draw.ellipse(
            [
                x_center - piece_radius,
                y_center - piece_radius,
                x_center + piece_radius,
                y_center + piece_radius
            ],
            outline=(255, 0, 0),  # Bordură roșie
            width=3
        )

        # Evidențiem mutările posibile
        for move in piece.valid_moves(self.board):
            x_highlight = move.new_x * square_size
            y_highlight = move.new_y * square_size
            self.buffer_draw.rectangle(
                [x_highlight, y_highlight, x_highlight + square_size, y_highlight + square_size],
                outline=(0, 255, 0),  # Bordură verde
                width=2
            )

        # Actualizăm canvasul
        self.tk_buffer = ImageTk.PhotoImage(self.buffer)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_buffer)


    def on_canvas_click(self, event):
        if self.current_player != PlayerType.Human:
            return

        # Calculăm coordonatele mouse-ului pe tablă
        square_size = 50
        mouse_x = event.x // square_size
        mouse_y = event.y // square_size

        # Verificăm dacă este selectată o piesă
        if self.selected_piece is None:
            # Caută o piesă umană în acea poziție
            for piece in self.board.pieces:
                if piece.player == PlayerType.Human and piece.x == mouse_x and piece.y == mouse_y:
                    self.selected_piece = piece.id
                    self.draw_board()
                    self.highlight_piece_and_moves(piece)
                    return
        else:
            # Mutăm piesa selectată
            selected_piece = self.board.pieces[self.selected_piece]
            move = Move(self.selected_piece, mouse_x, mouse_y)

            # Verificăm dacă mișcarea este validă
            valid_moves = selected_piece.valid_moves(self.board)
            if any(m.new_x == move.new_x and m.new_y == move.new_y for m in valid_moves):
                self.board = self.board.make_move(move)
                self.selected_piece = None
                self.draw_board()
                self.current_player = PlayerType.Computer
                self.check_finish()

                if self.current_player == PlayerType.Computer:
                    self.computer_move()
            else:
                # Deselectăm piesa dacă mutarea este invalidă
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
        about_text = ("Joc de dame")
        messagebox.showinfo("Despre jocul Dame", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCheckersApp(root)
    root.mainloop()
