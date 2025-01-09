from enum import Enum

class PlayerType(Enum):
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
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            move = Move(self.id, new_x, new_y)
            if self.is_valid_move(current_board, move):
                moves.append(move)
        return moves

    def is_valid_move(self, current_board, move):
        if move.new_x < 0 or move.new_x >= 8 or move.new_y < 0 or move.new_y >= 8:
            return False
        if move.new_x != self.x+1 and move.new_x!=self.x-1:
            return False
        if move.new_y != self.y+1 and move.new_y!=self.y-1:
            return False
        if current_board.get_piece_at(move.new_x, move.new_y, PlayerType.Computer) or \
           current_board.get_piece_at(move.new_x, move.new_y, PlayerType.Human):
            return False
        return True

class Board:
    def __init__(self):
        self.pieces = []
        self._initialize_pieces()

    def evaluation_function(board):
        computer_score = sum(7 - piece.y for piece in board.pieces if piece.player == PlayerType.Computer)
        human_score = sum(piece.y for piece in board.pieces if piece.player == PlayerType.Human)
        return computer_score - human_score

    def _initialize_pieces(self):
        computer_positions = [(1, 0), (3, 0), (5, 0), (7, 0), (0, 1), (2, 1), (4, 1), (6, 1), (1, 2), (3, 2), (5, 2), (7, 2)]
        human_positions = [(0, 5), (2, 5), (4, 5), (6, 5), (1, 6), (3, 6), (5, 6), (7, 6), (0, 7), (2, 7), (4, 7), (6, 7)]

        for i, (x, y) in enumerate(computer_positions):
            self.pieces.append(Piece(x, y, i, PlayerType.Computer))
        for i, (x, y) in enumerate(human_positions, len(computer_positions)):
            self.pieces.append(Piece(x, y, i, PlayerType.Human))

    def get_piece_at(self, x, y, player_type):
        return next((piece for piece in self.pieces if piece.x == x and piece.y == y and piece.player == player_type), None)

    def make_move(self, move):
        for piece in self.pieces:
            if piece.id == move.piece_id:
                piece.x = move.new_x
                piece.y = move.new_y
                break

    def check_finish(self):
        human_pieces = any(piece.player == PlayerType.Human for piece in self.pieces)
        computer_pieces = any(piece.player == PlayerType.Computer for piece in self.pieces)

        if not human_pieces:
            return True, PlayerType.Computer
        if not computer_pieces:
            return True, PlayerType.Human
        return False, PlayerType.NoPlayer

class MonteCarlo:
    @staticmethod
    def simulate_move(board, move):
        next_board = Board()
        next_board.pieces = [Piece(p.x, p.y, p.id, p.player) for p in board.pieces]
        next_board.make_move(move)
        return next_board

    @staticmethod
    def find_next_board(current_board):
        all_moves = []
        for piece in current_board.pieces:
            if piece.player == PlayerType.Computer:
                all_moves.extend(piece.valid_moves(current_board))

        if not all_moves:
            return current_board

        move_scores = {}
        for move in all_moves:
            win_count = 0
            total_simulations = 10  # Number of simulations per move

            for _ in range(total_simulations):
                next_board = MonteCarlo.simulate_move(current_board, move)
                score = next_board.evaluation_function()
                win_count += 1 if score > 0 else 0

            move_scores[move] = win_count / total_simulations

        best_move = max(move_scores, key=move_scores.get)
        current_board.make_move(best_move)
        return current_board

