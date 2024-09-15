import os
import random
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import torch
import numpy as np

class RLAgent:
    def __init__(self, env):
        self.env = DummyVecEnv([lambda: env])
        self.model_path = "rl_model.zip"
        self.checkpoint_path = "rl_model_checkpoint.zip"
        self.model = None

    def train(self, total_timesteps=50000, checkpoint_freq=10000):
        if os.path.exists(self.model_path):
            print("Loading pre-trained model...")
            self.model = PPO.load(self.model_path, env=self.env)
        else:
            print("Training new model...")
            self.model = PPO("MlpPolicy", self.env, verbose=1, 
                             device='cuda' if torch.cuda.is_available() else 'cpu',
                             learning_rate=1e-4,
                             n_steps=1024,
                             batch_size=64,
                             n_epochs=4,
                             gamma=0.99,
                             gae_lambda=0.95,
                             clip_range=0.2)
        
        for i in range(0, total_timesteps, checkpoint_freq):
            self.model.learn(total_timesteps=checkpoint_freq)
            self.model.save(self.checkpoint_path)
            print(f"Checkpoint saved at {i+checkpoint_freq} steps")

        self.model.save(self.model_path)
        print(f"Final model saved to {self.model_path}")

    def get_action(self, board):
        state = self.board_to_state(board)
        action, _ = self.model.predict(state, deterministic=True)
        return self.action_to_move(action, board)

    def board_to_state(self, board):
        # Converte o tabuleiro para o formato esperado pelo modelo (8, 8, 12)
        state = np.zeros((8, 8, 12), dtype=np.float32)
        piece_map = board.piece_map()
        for square, piece in piece_map.items():
            rank, file = divmod(square, 8)
            piece_type = piece.piece_type - 1
            color = int(piece.color)
            state[rank, file, piece_type + 6*color] = 1
        return state.reshape(1, 8, 8, 12)  # Adicione uma dimensão extra para batch

    def action_to_move(self, action, board):
        # Converte a ação do modelo para um movimento válido no tabuleiro
        legal_moves = list(board.legal_moves)
        if action < len(legal_moves):
            return legal_moves[action].uci()
        else:
            return random.choice(legal_moves).uci()
