import chess
import random
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

class SimpleLLM:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2-large")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2-large")
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def clean_move(self, move_string):
        match = re.search(r'\b[a-h][1-8][a-h][1-8][qrbn]?\b', move_string.lower())
        return match.group(0) if match else ""

    def fallback_move(self, board):
        legal_moves = list(board.legal_moves)
        captures = [move for move in legal_moves if board.is_capture(move)]
        checks = [move for move in legal_moves if board.gives_check(move)]
        if checks:
            return random.choice(checks)
        elif captures:
            return random.choice(captures)
        else:
            return random.choice(legal_moves)

    def generate_move(self, board, max_attempts=5):
        legal_moves = list(board.legal_moves)
        
        for attempt in range(max_attempts):
            prompt = f"Chess FEN: {board.fen()}\n"
            prompt += f"Legal moves: {' '.join([move.uci() for move in legal_moves])}\n"
            prompt += "Choose the best move from the legal moves. Respond with only the UCI notation of the chosen move (e.g., e2e4):"
            
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            attention_mask = input_ids.ne(self.tokenizer.pad_token_id).float()

            outputs = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=5,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            suggested_move = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            suggested_move = self.clean_move(suggested_move)

            if suggested_move:
                try:
                    move = chess.Move.from_uci(suggested_move)
                    if move in legal_moves:
                        return move, f"Valid move {suggested_move} generated on attempt {attempt + 1}."
                except ValueError:
                    pass
        
        chosen_move = self.fallback_move(board)
        thoughts = f"Failed to generate a valid move after {max_attempts} attempts. Using fallback strategy."
        return chosen_move, thoughts

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
