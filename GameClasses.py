from enum import Enum


class PlayerType(Enum):
    Human = 1
    Computer = 2
    NoPlayer = 3


class Piece:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player


class Board:
    def __init__(self):
        self.pieces = [
            Piece(x, y, PlayerType.Computer)
            for x, y in [(1, 0), (3, 0), (5, 0), (7, 0), (0, 1), (2, 1), (4, 1), (6, 1), (1, 2), (3, 2), (5, 2), (7, 2)]
        ] + [
            Piece(x, y, PlayerType.Human)
            for x, y in [(0, 5), (2, 5), (4, 5), (6, 5), (1, 6), (3, 6), (5, 6), (7, 6), (0, 7), (2, 7), (4, 7), (6, 7)]
        ]

    def get_piece_at(self, x, y, player_type):
        for piece in self.pieces:
            if piece.x == x and piece.y == y and piece.player == player_type:
                return piece
        return None

    def is_valid_move(self, start_x, start_y, target_x, target_y):
        if abs(target_x - start_x) == 1 and abs(target_y - start_y) == 1:
            if not self.get_piece_at(target_x, target_y, PlayerType.Human) and not self.get_piece_at(target_x, target_y, PlayerType.Computer):
                return True
        return False

    def move_piece(self, start_x, start_y, target_x, target_y):
        piece = self.get_piece_at(start_x, start_y, PlayerType.Human)
        if piece:
            piece.x = target_x
            piece.y = target_y

    def check_finish(self):
        if all(piece.player != PlayerType.Human for piece in self.pieces):
            return True, PlayerType.Computer
        if all(piece.player != PlayerType.Computer for piece in self.pieces):
            return True, PlayerType.Human
        return False, None


class Move:
    def __init__(self, start, end_x, end_y):
        self.start = start
        self.end_x = end_x
        self.end_y = end_y


class Minimax:
    @staticmethod
    def find_next_board(board):
        # Simulare simplă: doar întoarce aceeași tablă
        return board
