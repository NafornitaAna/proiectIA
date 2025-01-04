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
    def __init__(self, x, y, piece_id, player):
        self.x = x
        self.y = y
        self.id = piece_id
        self.player = player

    def valid_moves(self, current_board):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            move = Move(self.id, new_x, new_y)
            if self.is_valid_move(current_board, move):
                moves.append(move)
        return moves

    def is_valid_move(self, current_board, move):
        if move.new_x < 0 or move.new_x >= current_board.size or move.new_y < 0 or move.new_y >= current_board.size:
            return False
        for piece in current_board.pieces:
            if piece.x == move.new_x and piece.y == move.new_y:
                return False
        return True

class Board:
    def __init__(self, board=None):
        if board is None:
            self.size = 4  # dimensiunea tablei de joc
            self.pieces = []

            for i in range(self.size):
                self.pieces.append(Piece(i, self.size - 1, i, PlayerType.Computer))

            for i in range(self.size):
                self.pieces.append(Piece(i, 0, i + self.size, PlayerType.Human))
        else:
            self.size = board.size
            self.pieces = [Piece(p.x, p.y, p.id, p.player) for p in board.pieces]

    def evaluation_function(self):
        computer_score = sum(self.size - 1 - piece.y for piece in self.pieces if piece.player == PlayerType.Computer)
        human_score = sum(piece.y for piece in self.pieces if piece.player == PlayerType.Human)
        return computer_score - human_score

    def make_move(self, move):
        next_board = Board(self)  # copy
        next_board.pieces[move.piece_id].x = move.new_x
        next_board.pieces[move.piece_id].y = move.new_y
        return next_board

    def check_finish(self):
        finished = False
        winner = PlayerType.NoPlayer

        if len([p for p in self.pieces if p.player == PlayerType.Human and p.y == self.size - 1]) == self.size:
            finished = True
            winner = PlayerType.Human
        elif len([p for p in self.pieces if p.player == PlayerType.Computer and p.y == 0]) == self.size:
            finished = True
            winner = PlayerType.Computer

        return finished, winner

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
