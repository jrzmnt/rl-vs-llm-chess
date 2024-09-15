import chess
import pygame


class ChessGUI:
    def __init__(self, width=1200, height=800, rl_color=None, llm_color=None):
        pygame.init()
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess: RL vs LLM")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 36)

        self.board_size = min(height, width // 3) - 80
        self.square_size = self.board_size // 8
        self.board_pos = (
            (width - self.board_size) // 2,
            (height - self.board_size) // 2,
        )

        self.rl_surface = pygame.Surface((width // 3, height))
        self.llm_surface = pygame.Surface((width // 3, height))

        self.piece_images = self._load_piece_images()
        self.small_piece_images = self._load_piece_images(size=self.square_size // 2)
        self.last_move = None

        # Colors
        self.bg_color = (240, 240, 240)
        self.text_color = (50, 50, 50)
        self.highlight_color = (255, 255, 0, 128)
        self.light_square = (234, 235, 200)
        self.dark_square = (119, 154, 88)
        self.border_color = (100, 100, 100)

        self.quit_button = pygame.Rect(self.width - 110, 10, 100, 40)

        self.rl_color = rl_color
        self.llm_color = llm_color

        self.input_box = pygame.Rect(self.width // 2 - 100, 500, 200, 32)
        self.input_text = ''
        self.input_active = False

        self.piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9}
        self.white_pieces = {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0}
        self.black_pieces = {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0}
        self.white_captures = 0
        self.black_captures = 0

    def _load_piece_images(self, size=None):
        if size is None:
            size = self.square_size
        pieces = ['p', 'n', 'b', 'r', 'q', 'k']
        colors = ['b', 'w']
        images = {}
        for color in colors:
            for piece in pieces:
                filename = f"{color}{piece}.png"
                img = pygame.image.load(f"chess_pieces/{filename}")
                images[f"{color}{piece}"] = pygame.transform.scale(img, (size, size))
        return images

    def update(self, board, rl_info, llm_info, move_list, game_time):
        self.screen.fill(self.bg_color)
        
        # Draw chess board
        self._draw_board(board)
        
        # Update captured pieces count
        self.white_pieces, self.black_pieces = self._update_captured_pieces(board)
        
        # Draw RL info
        self.rl_surface.fill(self.bg_color)
        self._draw_agent_info(self.rl_surface, f"RL Agent ({self.rl_color})", rl_info, move_list)
        self._draw_captured_pieces_info(self.rl_surface, self.rl_color)
        self.screen.blit(self.rl_surface, (0, 0))
        
        # Draw LLM info
        self.llm_surface.fill(self.bg_color)
        self._draw_agent_info(self.llm_surface, f"LLM Agent ({self.llm_color})", llm_info, move_list)
        self._draw_captured_pieces_info(self.llm_surface, self.llm_color)
        self._draw_text(self.llm_surface, f"Game time: {game_time:.1f}s", (10, self.height - 100), self.text_color)
        self.screen.blit(self.llm_surface, (self.width * 2 // 3, 0))

        # Draw borders
        pygame.draw.line(self.screen, self.border_color, (self.width // 3, 0), (self.width // 3, self.height), 2)
        pygame.draw.line(self.screen, self.border_color, (self.width * 2 // 3, 0), (self.width * 2 // 3, self.height), 2)

        # Draw Quit button
        pygame.draw.rect(self.screen, (200, 50, 50), self.quit_button)
        quit_text = self.font.render("Quit", True, (255, 255, 255))
        self.screen.blit(quit_text, (self.quit_button.centerx - quit_text.get_width() // 2, self.quit_button.centery - quit_text.get_height() // 2))

    def _draw_board(self, board):
        # Draw border around the board
        pygame.draw.rect(self.screen, self.border_color, (
            self.board_pos[0] - 2, self.board_pos[1] - 2,
            self.board_size + 4, self.board_size + 4
        ), 2)

        for row in range(8):
            for col in range(8):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                x = self.board_pos[0] + col * self.square_size
                y = self.board_pos[1] + row * self.square_size
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))

                # Highlight last move
                if self.last_move:
                    from_square = chess.parse_square(self.last_move[:2])
                    to_square = chess.parse_square(self.last_move[2:4])
                    if (7-row, col) in [(from_square // 8, from_square % 8), (to_square // 8, to_square % 8)]:
                        pygame.draw.rect(self.screen, self.highlight_color, (x, y, self.square_size, self.square_size))

                piece = board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_image = self.piece_images[f"{'w' if piece.color else 'b'}{piece.symbol().lower()}"]
                    self.screen.blit(piece_image, (x, y))

        # Draw coordinates
        for i in range(8):
            # Files (A-H)
            text = self.small_font.render(chess.FILE_NAMES[i], True, self.text_color)
            x = self.board_pos[0] + i * self.square_size + self.square_size // 2 - text.get_width() // 2
            self.screen.blit(text, (x, self.board_pos[1] + self.board_size + 5))

            # Ranks (1-8)
            text = self.small_font.render(str(8 - i), True, self.text_color)
            y = self.board_pos[1] + i * self.square_size + self.square_size // 2 - text.get_height() // 2
            self.screen.blit(text, (self.board_pos[0] - 20, y))

    def _draw_agent_info(self, surface, agent_name, info, move_list):
        pygame.draw.rect(surface, (220, 220, 220), (10, 10, self.width // 3 - 20, 50), border_radius=10)
        self._draw_text(surface, agent_name, (20, 20), self.text_color, font=self.large_font)
        
        pygame.draw.rect(surface, (255, 255, 255), (10, 70, self.width // 3 - 20, 100), border_radius=10)
        self._draw_text(surface, info, (20, 80), self.text_color, max_width=self.width // 3 - 40)
        
        if move_list:
            pygame.draw.rect(surface, (255, 255, 255), (10, 180, self.width // 3 - 20, self.height - 280), border_radius=10)
            self._draw_text(surface, "Move history:", (20, 190), self.text_color)
            start_index = max(0, len(move_list) - 15)  # Start from the last 15 moves or from the beginning if less than 15
            for i, move in enumerate(move_list[start_index:]):
                move_number = start_index + i + 1
                text = self.small_font.render(f"{move_number}. {move}", True, self.text_color)
                surface.blit(text, (30, 220 + i * 25))

    def _draw_text(self, surface, text, pos, color, font=None, max_width=None):
        if font is None:
            font = self.font
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            if max_width and test_surface.get_width() > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (pos[0], pos[1] + i * 30))

    def set_last_move(self, move):
        self.last_move = move

    def show_start_screen(self):
        self.screen.fill(self.bg_color)
        title = self.large_font.render("Chess: RL vs LLM", True, self.text_color)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        subtitle = self.font.render("Choose who plays as White", True, self.text_color)
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 200))

        rl_white_button = pygame.Rect(self.width // 2 - 150, 300, 300, 50)
        llm_white_button = pygame.Rect(self.width // 2 - 150, 370, 300, 50)

        pygame.draw.rect(self.screen, (200, 200, 200), rl_white_button, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), llm_white_button, border_radius=10)

        rl_text = self.font.render("RL plays as White", True, self.text_color)
        llm_text = self.font.render("LLM plays as White", True, self.text_color)

        self.screen.blit(rl_text, (rl_white_button.centerx - rl_text.get_width() // 2, rl_white_button.centery - rl_text.get_height() // 2))
        self.screen.blit(llm_text, (llm_white_button.centerx - llm_text.get_width() // 2, llm_white_button.centery - llm_text.get_height() // 2))

        seed_text = self.font.render("Enter seed (optional):", True, self.text_color)
        self.screen.blit(seed_text, (self.width // 2 - seed_text.get_width() // 2, 450))

        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
        input_surface = self.font.render(self.input_text, True, self.text_color)
        self.screen.blit(input_surface, (self.input_box.x + 5, self.input_box.y + 5))

        # Add creator information
        creator_text = self.small_font.render("Created by Juarez Monteiro", True, self.text_color)
        github_text = self.small_font.render("GitHub: @jrzmnt", True, self.text_color)
        self.screen.blit(creator_text, (10, self.height - 40))
        self.screen.blit(github_text, (10, self.height - 20))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rl_white_button.collidepoint(event.pos):
                        return "RL", self.input_text
                    elif llm_white_button.collidepoint(event.pos):
                        return "LLM", self.input_text
                    elif self.input_box.collidepoint(event.pos):
                        self.input_active = True
                    else:
                        self.input_active = False
                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode
                        # Re-render the input box
                        pygame.draw.rect(self.screen, self.bg_color, self.input_box)
                        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
                        input_surface = self.font.render(self.input_text, True, self.text_color)
                        self.screen.blit(input_surface, (self.input_box.x + 5, self.input_box.y + 5))
                        pygame.display.flip()

        return None, None

    def check_quit(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.quit_button.collidepoint(event.pos):
                return True
        return False

    def _update_captured_pieces(self, board):
        white_pieces = {'p': 8, 'n': 2, 'b': 2, 'r': 2, 'q': 1}
        black_pieces = {'p': 8, 'n': 2, 'b': 2, 'r': 2, 'q': 1}

        for piece_type in chess.PIECE_TYPES:
            if piece_type != chess.KING:
                symbol = chess.piece_symbol(piece_type)
                white_pieces[symbol] -= len(board.pieces(piece_type, chess.WHITE))
                black_pieces[symbol] -= len(board.pieces(piece_type, chess.BLACK))

        self.white_captures = sum(black_pieces.values())
        self.black_captures = sum(white_pieces.values())

        return white_pieces, black_pieces

    def _draw_captured_pieces_info(self, surface, color):
        captured = self.white_captures if color == 'White' else self.black_captures
        opponent_pieces = self.black_captures if color == 'White' else self.white_captures

        text = f"Captured pieces: {captured}"
        text_surface = self.font.render(text, True, self.text_color)
        surface.blit(text_surface, (10, self.height - 70))

        # Add information about opponent's captured pieces
        piece_symbols = {'p': '♙', 'n': '♘', 'b': '♗', 'r': '♖', 'q': '♕'}
        opponent_color = 'Black' if color == 'White' else 'White'
        opponent_pieces_text = f"{opponent_color} pieces captured: "
        for piece, count in (self.white_pieces if color == 'Black' else self.black_pieces).items():
            if count > 0:
                opponent_pieces_text += f"{piece_symbols[piece]}:{count} "

        opponent_text_surface = self.small_font.render(opponent_pieces_text, True, self.text_color)
        surface.blit(opponent_text_surface, (10, self.height - 40))