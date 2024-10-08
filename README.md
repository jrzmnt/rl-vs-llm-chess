# Chess: RL vs LLM

This project implements a chess game where a Reinforcement Learning (RL) agent plays against a Large Language Model (LLM). The game is visualized using a Pygame-based graphical user interface.

<p align="center">
  <img src="rl-vs-llm.gif" alt="Chess game between an RL and LLM models" width="35%">
</p>

## Features

- RL agent trained using Proximal Policy Optimization (PPO) from Stable Baselines3
- LLM agent based on a simplified version of DistilGPT2
- Interactive chess board with move highlighting
- Real-time display of game information, including captured pieces and move history
- Customizable random seed for reproducibility

## Requirements

- Python 3.7+
- PyTorch
- Stable Baselines3
- Pygame
- python-chess
- transformers (Hugging Face)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/jrzmnt/chess-rl-vs-llm.git
   cd chess-rl-vs-llm
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script to start the game:

```
python src\main.py
```

## How It Works

1. The RL agent is trained using PPO on the custom chess environment defined in `chess_environment/chess_env.py`.
2. The LLM agent in `llm_player/llm_agent.py` generates moves based on the current board state using a simplified version of DistilGPT2.
3. The game alternates between the two agents, with each move being visualized on the chess board using the Pygame GUI implemented in `chess_gui.py`.
4. The `main.py` script orchestrates the game flow, including initialization, turn management, and game termination conditions.
5. The game continues until checkmate, stalemate, or the maximum number of moves is reached.

## Customization

- Adjust the RL training parameters in `rl_player/rl_agent.py`
- Modify the LLM prompt or model in `llm_player/llm_agent.py`
- Customize the GUI appearance in `chess_gui.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [Stable Baselines3](https://github.com/DLR-RM/stable-baselines3) for the RL implementation
- [Hugging Face Transformers](https://github.com/huggingface/transformers) for the LLM implementation
- [python-chess](https://github.com/niklasf/python-chess) for the chess logic
- [Pygame](https://www.pygame.org/) for the graphical interface

## Citation

If you use this project in your research or wish to refer to our related work on games and artificial intelligence, please use the following BibTeX entry:

```bibtex
@article{monteiro2018beating,
  title={Beating bomberman with artificial intelligence},
  author={Monteiro, Juarez and Granada, Roger Leitzke and Pinto, Rafael and Barros, Rodrigo Coelho},
  journal={Anais do XV Encontro Nacional de Intelig{\^e}ncia Artificial e Computacional (ENIAC 2018), 2018, Brasil.},
  year={2018}
}
```

## Author

Created by Juarez Monteiro

LinkedIn: [@juarez-monteiro](https://www.linkedin.com/in/juarez-monteiro/)

GitHub: [@jrzmnt](https://github.com/jrzmnt)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
