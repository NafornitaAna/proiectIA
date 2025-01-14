import math
import random
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
        capture_moves = []
        regular_moves = []
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for dx, dy in directions:
            new_x = self.x + 2 * dx
            new_y = self.y + 2 * dy
            mid_x = self.x + dx
            mid_y = self.y + dy
            move = Move(self.id, new_x, new_y)
            if self.is_valid_move(current_board, move) and current_board.get_piece_at(mid_x, mid_y, PlayerType.Human):
                capture_moves.append(move)

            new_x = self.x + dx
            new_y = self.y + dy
            move = Move(self.id, new_x, new_y)
            if self.is_valid_move(current_board, move):
                regular_moves.append(move)

        return capture_moves if capture_moves else regular_moves

    def is_valid_move(self, current_board, move):
        if move.new_x < 0 or move.new_x >= 8 or move.new_y < 0 or move.new_y >= 8:
            return False
        if current_board.get_piece_at(move.new_x, move.new_y, PlayerType.Computer) or \
                current_board.get_piece_at(move.new_x, move.new_y, PlayerType.Human):
            return False

        dx = move.new_x - self.x
        dy = move.new_y - self.y

        if abs(dx) == 1 and abs(dy) == 1:
            return True

        if abs(dx) == 2 and abs(dy) == 2:
            mid_x = (self.x + move.new_x) // 2
            mid_y = (self.y + move.new_y) // 2
            mid_piece = current_board.get_piece_at(mid_x, mid_y,
                                                   PlayerType.Human if self.player == PlayerType.Computer else PlayerType.Computer)
            if mid_piece:
                return True

        return False


class Board:
    def __init__(self):
        self.pieces = []
        self._initialize_pieces()

    def evaluation_function(self):
        computer_score = sum(7 - piece.y for piece in self.pieces if piece.player == PlayerType.Computer)
        human_score = sum(piece.y for piece in self.pieces if piece.player == PlayerType.Human)

        computer_pieces_count = sum(1 for piece in self.pieces if piece.player == PlayerType.Computer)
        human_pieces_count = sum(1 for piece in self.pieces if piece.player == PlayerType.Human)

        initial_pieces_count = 12
        captured_by_computer = initial_pieces_count - human_pieces_count
        captured_by_human = initial_pieces_count - computer_pieces_count

        computer_score += captured_by_computer * 20
        human_score += captured_by_human * 20

        return computer_score - human_score

    def _initialize_pieces(self):
        computer_positions = [(1, 0), (3, 0), (5, 0), (7, 0), (0, 1), (2, 1), (4, 1), (6, 1), (1, 2), (3, 2), (5, 2),
                              (7, 2)]
        human_positions = [(0, 5), (2, 5), (4, 5), (6, 5), (1, 6), (3, 6), (5, 6), (7, 6), (0, 7), (2, 7), (4, 7),
                           (6, 7)]

        for i, (x, y) in enumerate(computer_positions):
            self.pieces.append(Piece(x, y, i, PlayerType.Computer))
        for i, (x, y) in enumerate(human_positions, len(computer_positions)):
            self.pieces.append(Piece(x, y, i, PlayerType.Human))

    def get_piece_at(self, x, y, player_type):
        for piece in self.pieces:
            if piece.x == x and piece.y == y and piece.player == player_type:
                return piece
        return None

    def copy(self):
        new_board = Board()
        new_board.pieces = [Piece(piece.x, piece.y, piece.id, piece.player) for piece in self.pieces]
        return new_board

    def get_all_valid_moves(self, player):
        all_moves = []
        for piece in self.pieces:
            if piece.player == player:
                all_moves.extend(piece.valid_moves(self))
        return all_moves

    def make_move(self, move):
        for piece in self.pieces:
            if piece.id == move.piece_id:
                dx = move.new_x - piece.x
                dy = move.new_y - piece.y
                if abs(dx) == 2 and abs(dy) == 2:
                    mid_x = (piece.x + move.new_x) // 2
                    mid_y = (piece.y + move.new_y) // 2
                    mid_piece = self.get_piece_at(mid_x, mid_y,
                                                  PlayerType.Human if piece.player == PlayerType.Computer else PlayerType.Computer)
                    if mid_piece:
                        self.pieces.remove(mid_piece)
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
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.wins = {}
        self.plays = {}
        self.max_simulations = 10

    def uct_select(self, node):
        log_parent_visits = math.log(self.plays[node])
        best_score = -float('inf')
        best_child = None

        for child in node.children:
            if child not in self.plays or self.plays[child] == 0:
                return child
            score = (self.wins[child] / self.plays[child]) + math.sqrt(2 * log_parent_visits / self.plays[child])
            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def simulate(self, node):
        board = node.board.copy()
        player = node.player

        while not board.check_finish()[0]:
            moves = board.get_all_valid_moves(player)
            if not moves:
                break

            capture_moves = [move for move in moves if abs(move.new_x - move.new_y) == 2]
            if capture_moves:
                move = random.choice(capture_moves)
            else:
                move = random.choice(moves)

            board.make_move(move)
            player = PlayerType.Computer if player == PlayerType.Human else PlayerType.Human

        return board.check_finish()[1]

    def backpropagate(self, path, winner):
        for node in path:
            if node not in self.plays:
                self.plays[node] = 0
                self.wins[node] = 0
            self.plays[node] += 1
            if node.player == winner:
                self.wins[node] += 1

    def run(self):
        root = Node(self.board, self.player)
        self.plays[root] = 0
        self.wins[root] = 0

        for _ in range(self.max_simulations):
            node = root
            path = [node]

            while node.children:
                node = self.uct_select(node)
                path.append(node)

            if not node.children and not node.board.check_finish()[0]:
                node.expand()
                for child in node.children:
                    self.plays[child] = 0
                    self.wins[child] = 0
                if node.children:
                    node = random.choice(node.children)
                    path.append(node)

            winner = self.simulate(node)

            self.backpropagate(path, winner)

        if not root.children:
            return None

        return max(root.children, key=lambda n: self.plays[n]).move

    def simulate_move(self, board, move):
        new_board = board.copy()
        new_board.make_move(move)
        return new_board

    def find_next_board(self, board):
        self.board = board
        best_move = self.run()
        if best_move is None:
            return board
        new_board = board.copy()
        new_board.make_move(best_move)
        return new_board


class Node:
    def __init__(self, board, player, move=None):
        self.board = board
        self.player = player
        self.move = move
        self.children = []

    def expand(self):
        moves = self.board.get_all_valid_moves(self.player)
        for move in moves:
            new_board = self.board.copy()
            new_board.make_move(move)
            child_node = Node(new_board, PlayerType.Computer if self.player == PlayerType.Human else PlayerType.Human,
                              move)
            self.children.append(child_node)
