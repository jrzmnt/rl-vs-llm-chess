import chess
import random

class SimpleLLM:
    def generate_move(self, board):
        legal_moves = list(board.legal_moves)
        
        # Simple priorities
        capture_moves = [move for move in legal_moves if board.is_capture(move)]
        check_moves = [move for move in legal_moves if board.gives_check(move)]
        center_moves = [move for move in legal_moves if chess.square_rank(move.to_square) in [3,4] and chess.square_file(move.to_square) in [3,4]]
        
        # LLM "thoughts"
        thoughts = []
        if check_moves:
            thoughts.append("I can give a check. This is a good move.")
        if capture_moves:
            thoughts.append("There are pieces I can capture. This might be advantageous.")
        if center_moves:
            thoughts.append("Controlling the center of the board is important.")
        
        # Move selection
        if check_moves and random.random() < 0.7:
            chosen_move = random.choice(check_moves)
            thoughts.append("I decided to give a check.")
        elif capture_moves and random.random() < 0.6:
            chosen_move = random.choice(capture_moves)
            thoughts.append("I'm going to capture a piece.")
        elif center_moves and random.random() < 0.5:
            chosen_move = random.choice(center_moves)
            thoughts.append("I'll move to the center.")
        else:
            chosen_move = random.choice(legal_moves)
            thoughts.append("I'll make a random move.")
        
        return chosen_move, "\n".join(thoughts)

class LLMAgent:
    def __init__(self):
        self.move_cache = {}
        self.llm = SimpleLLM()

    def get_action(self, state, timeout=1):
        if state in self.move_cache:
            return self.move_cache[state]

        board = chess.Board(state)
        chosen_move, thoughts = self.llm.generate_move(board)

        move_uci = chosen_move.uci()
        self.move_cache[state] = move_uci
        
        print(f"LLM thoughts:\n{thoughts}")
        return move_uci
