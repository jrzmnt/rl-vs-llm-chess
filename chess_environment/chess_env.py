import chess
import gym
import numpy as np

class ChessEnvironment(gym.Env):
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.action_space = gym.spaces.Discrete(64 * 64)  # Simplificado: origem e destino
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(8, 8, 12), dtype=np.float32)

    def reset(self):
        self.board.reset()
        return self.get_state()

    def step(self, action):
        move = self.action_to_uci(action)
        if move in self.board.legal_moves:
            self.board.push(move)
        else:
            return self.get_state(), -1, True, {}  # Movimento ilegal

        reward = 0
        done = self.board.is_game_over()

        if done:
            result = self.board.result()
            if result == "1-0":
                reward = 1
            elif result == "0-1":
                reward = -1

        return self.get_state(), reward, done, {}

    def get_state(self):
        state = np.zeros((8, 8, 12), dtype=np.float32)
        for i in range(64):
            piece = self.board.piece_at(i)
            if piece:
                color = int(piece.color)
                piece_type = piece.piece_type - 1
                state[i // 8, i % 8, piece_type + 6 * color] = 1
        return state

    def action_to_uci(self, action):
        from_square = action // 64
        to_square = action % 64
        return chess.Move(from_square, to_square)

    def render(self):
        print(self.board)
