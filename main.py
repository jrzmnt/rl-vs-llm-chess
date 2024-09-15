from chess_environment.chess_env import ChessEnvironment
from llm_player.llm_agent import LLMAgent
from rl_player.rl_agent import RLAgent
from chess_gui import ChessGUI
import pygame
import time
import chess
import threading
from queue import Queue
import random
import os
from stable_baselines3 import PPO  # Adicione esta linha

def get_llm_move(llm_player, board, result_queue):
	llm_action = llm_player.get_action(board.fen())
	result_queue.put(llm_action)

def main():
	# Initialize Pygame and create GUI
	pygame.init()
	gui = ChessGUI()

	# Show start screen and get player colors and seed
	white_player, seed_input = gui.show_start_screen()
	if white_player is None:
		print("Game cancelled")
		return

	# Set the random seed
	if seed_input and seed_input.isdigit():
		random_seed = int(seed_input)
	else:
		random_seed = random.randint(1, 1000000)
	random.seed(random_seed)
	print(f"Random seed: {random_seed}")

	rl_color = "White" if white_player == "RL" else "Black"
	llm_color = "White" if white_player == "LLM" else "Black"

	# Recreate GUI with color information
	gui = ChessGUI(rl_color=rl_color, llm_color=llm_color)

	env = ChessEnvironment()
	llm_player = LLMAgent()
	rl_player = RLAgent(env)

	# Train or load RL agent
	model_path = "rl_model.zip"
	if os.path.exists(model_path):
		print("Loading pre-trained RL model...")
		rl_player.model = PPO.load(model_path, env=rl_player.env)
	else:
		print("Training RL agent...")
		gui.update(chess.Board(), "Training RL agent...", "Waiting for RL agent...", [], 0)
		pygame.display.flip()
		rl_player.train(total_timesteps=50000, checkpoint_freq=10000)
		print("RL agent training complete.")

	board = chess.Board()
	done = False
	move_list = []
	start_time = time.time()

	gui.update(board, "RL agent ready", "LLM agent ready", move_list, 0)
	pygame.display.flip()
	time.sleep(2)  # Pause to show the "ready" message

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or gui.check_quit(event):
				running = False
				break

		if not running:
			break

		if not done:
			current_player = "White" if board.turn == chess.WHITE else "Black"
			is_rl_turn = (current_player == "White" and white_player == "RL") or (current_player == "Black" and white_player == "LLM")

			if is_rl_turn:
				# RL player's turn
				print("RL player's turn")
				rl_action = rl_player.get_action(board)
				rl_info = f"Thinking...\nChosen move: {rl_action}"
				move_list.append(f"RL: {rl_action}")
				gui.set_last_move(rl_action)
				gui.update(board, rl_info, "Waiting for RL move...", move_list, time.time() - start_time)
				pygame.display.flip()
				time.sleep(1)  # Add delay for visualization
				
				move = chess.Move.from_uci(rl_action)
				board.push(move)
				gui.update(board, rl_info, "RL moved", move_list, time.time() - start_time)
				pygame.display.flip()
				time.sleep(1)  # Add delay for visualization
			else:
				# LLM player's turn
				print("LLM player's turn")
				llm_info = "Thinking..."
				gui.update(board, "Waiting for LLM move...", llm_info, move_list, time.time() - start_time)
				pygame.display.flip()

				llm_action = llm_player.get_action(board.fen())

				llm_info = f"Chosen move: {llm_action}"
				move_list.append(f"LLM: {llm_action}")
				gui.set_last_move(llm_action)
				gui.update(board, "LLM moved", llm_info, move_list, time.time() - start_time)
				pygame.display.flip()
				
				move = chess.Move.from_uci(llm_action)
				board.push(move)
				gui.update(board, "LLM moved", llm_info, move_list, time.time() - start_time)
				pygame.display.flip()
				time.sleep(1)  # Add delay for visualization

			if board.is_game_over():
				print(f"Game over after {current_player}'s move")
				done = True

		if done:
			result = board.result()
			winner = "White" if result == "1-0" else "Black" if result == "0-1" else "Draw"
			end_message = f"Game over: {winner} wins!" if winner != "Draw" else "Game over: It's a draw!"
			gui.update(board, end_message, end_message, move_list, time.time() - start_time)
			pygame.display.flip()

			# Wait for user to quit
			waiting = True
			while waiting:
				for event in pygame.event.get():
					if event.type == pygame.QUIT or gui.check_quit(event):
						waiting = False
						running = False

	print("Game finished!")
	pygame.quit()

if __name__ == "__main__":
	main()
