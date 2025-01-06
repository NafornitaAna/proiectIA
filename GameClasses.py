import random

class PlayerType:
    NoPlayer = 0
    Computer = 1
    Human = 2

class Move:
    def __init__(self, piece_id, new_x, new_y):
        self.piece_id = piece_id
        self.new_x = new_x
        self.new_y = new_y

class Piece:
    def __init__(self, x, y, piece_id, player, is_king=False):
        self.x = x
        self.y = y
        self.id = piece_id
        self.player = player
        self.is_king = is_king  # Adăugăm un atribut pentru "damă"

    def valid_moves(self, current_board):
        moves = []
        directions = [(-1, -1), (1, -1)] if self.player == PlayerType.Human else [(-1, 1), (1, 1)]
        if self.is_king:  # Dama poate merge în toate direcțiile diagonale
            directions += [(-1, 1), (1, -1)]

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            move = Move(self.id, new_x, new_y)
            if self.is_valid_move(current_board, move):
                moves.append(move)
            # Verifică săritura peste o piesă adversă
            capture_x, capture_y = self.x + 2 * dx, self.y + 2 * dy
            capture_move = Move(self.id, capture_x, capture_y)
            if self.can_capture(current_board, move, capture_move):
                moves.append(capture_move)
        return moves

    def is_valid_move(self, current_board, move):
        # Verifică dacă mișcarea este pe tablă
        if move.new_x < 0 or move.new_x >= current_board.size or move.new_y < 0 or move.new_y >= current_board.size:
            return False
        # Verifică dacă poziția țintă este liberă
        for piece in current_board.pieces:
            if piece.x == move.new_x and piece.y == move.new_y:
                return False
        return True

    def can_capture(self, current_board, move, capture_move):
        if not self.is_valid_move(current_board, capture_move):
            return False
        # Verifică dacă există o piesă adversă în mijloc
        mid_x = (self.x + move.new_x) // 2
        mid_y = (self.y + move.new_y) // 2
        for piece in current_board.pieces:
            if piece.x == mid_x and piece.y == mid_y and piece.player != self.player:
                return True
        return False


class Board:
    def __init__(self, board=None):
        self.size = 8  # Tabla de joc standard de dame
        self.pieces = []
        if board is None:
            self.initialize_pieces()

    def initialize_pieces(self):
        # Piese negre (computer)
        for y in range(3):
            for x in range(self.size):
                if (x + y) % 2 == 1:
                    self.pieces.append(Piece(x, y, len(self.pieces), PlayerType.Computer))
        # Piese albe (uman)
        for y in range(5, 8):
            for x in range(self.size):
                if (x + y) % 2 == 1:
                    self.pieces.append(Piece(x, y, len(self.pieces), PlayerType.Human))

    def make_move(self, move):
        next_board = Board(self)  # Copiere
        piece = next_board.pieces[move.piece_id]
        piece.x = move.new_x
        piece.y = move.new_y

        # Verifică capturarea piesei
        mid_x = (piece.x + move.new_x) // 2
        mid_y = (piece.y + move.new_y) // 2
        next_board.pieces = [
            p for p in next_board.pieces if not (p.x == mid_x and p.y == mid_y and p.player != piece.player)
        ]

        # Verifică promovarea la "damă"
        if piece.player == PlayerType.Human and piece.y == 0:
            piece.is_king = True
        elif piece.player == PlayerType.Computer and piece.y == self.size - 1:
            piece.is_king = True

        return next_board

    def check_finish(self):
        human_pieces = [p for p in self.pieces if p.player == PlayerType.Human]
        computer_pieces = [p for p in self.pieces if p.player == PlayerType.Computer]
        if not human_pieces:
            return True, PlayerType.Computer
        if not computer_pieces:
            return True, PlayerType.Human
        return False, PlayerType.NoPlayer

class Minimax:
    _rand = random.Random()

    @staticmethod
    def find_next_board(current_board):
        best_score = float('-inf')
        best_moves = []

        for piece in current_board.pieces:
            if piece.player == PlayerType.Computer:
                for move in piece.valid_moves(current_board):
                    next_board = current_board.make_move(move)
                    score = next_board.evaluation_function()
                    if score > best_score:
                        best_score = score
                        best_moves = [move]
                    elif score == best_score:
                        best_moves.append(move)

        best_move = Minimax._rand.choice(best_moves) if best_moves else None
        return current_board.make_move(best_move) if best_move else current_board