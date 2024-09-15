import chess
import random

class LLMAgent:
    def __init__(self):
        self.move_cache = {}

    def get_action(self, state, timeout=1):
        if state in self.move_cache:
            return self.move_cache[state]

        board = chess.Board(state)
        legal_moves = list(board.legal_moves)

        # Simple heuristics
        capture_moves = [move for move in legal_moves if board.is_capture(move)]
        check_moves = [move for move in legal_moves if board.gives_check(move)]
        
        if check_moves:
            chosen_move = random.choice(check_moves)
        elif capture_moves:
            chosen_move = random.choice(capture_moves)
        else:
            chosen_move = random.choice(legal_moves)

        move_uci = chosen_move.uci()
        self.move_cache[state] = move_uci
        return move_uci
