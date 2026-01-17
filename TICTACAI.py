"""
ULTIMATE TIC-TAC-TOE AI
Advanced Minimax Algorithm Implementation
No External Dependencies Required
"""

import math
import random
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict

class UltimateTicTacToeAI:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 3x3 board
        self.current_winner = None
        self.ai_player = 'X'
        self.human_player = 'O'
        self.difficulty = 'unbeatable'  # 'easy', 'medium', 'hard', 'unbeatable'
        self.ai_wins = 0
        self.human_wins = 0
        self.ties = 0
        self.game_history = []
        self.game_id = 1
        self.save_file = 'tictactoe_stats.json'
        self.thinking_depth = 0
        self.nodes_explored = 0
        self.load_statistics()
        
        # ANSI color codes for cross-platform terminal colors
        self.colors = {
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'WHITE': '\033[97m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
            'RESET': '\033[0m'
        }
    
    def color_text(self, text: str, color: str) -> str:
        """Color text using ANSI codes."""
        return f"{self.colors.get(color, '')}{text}{self.colors['RESET']}"
    
    def clear_screen(self):
        """Clear terminal screen cross-platform."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_statistics(self):
        """Load game statistics from file."""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.ai_wins = data.get('ai_wins', 0)
                    self.human_wins = data.get('human_wins', 0)
                    self.ties = data.get('ties', 0)
                    self.game_history = data.get('game_history', [])
                    self.game_id = data.get('next_game_id', 1)
        except Exception as e:
            # If file is corrupted, start fresh
            pass
    
    def save_statistics(self):
        """Save game statistics to file."""
        data = {
            'ai_wins': self.ai_wins,
            'human_wins': self.human_wins,
            'ties': self.ties,
            'game_history': self.game_history[-20:],  # Keep last 20 games
            'next_game_id': self.game_id + 1,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def print_board_nums(self):
        """Show board with position numbers."""
        print(self.color_text("\nBoard Positions Reference:", 'CYAN'))
        print(self.color_text(" 0 │ 1 │ 2 ", 'YELLOW'))
        print(self.color_text("───┼───┼───", 'YELLOW'))
        print(self.color_text(" 3 │ 4 │ 5 ", 'YELLOW'))
        print(self.color_text("───┼───┼───", 'YELLOW'))
        print(self.color_text(" 6 │ 7 │ 8 ", 'YELLOW'))
    
    def print_board(self):
        """Print the current game board with colors."""
        print(self.color_text("\nCurrent Game Board:", 'CYAN'))
        print()
        
        for row in range(3):
            print("   ", end="")
            for col in range(3):
                idx = row * 3 + col
                symbol = self.board[idx]
                
                # Color the symbols
                if symbol == 'X':
                    print(self.color_text(f" {symbol} ", 'RED'), end="")
                elif symbol == 'O':
                    print(self.color_text(f" {symbol} ", 'GREEN'), end="")
                else:
                    print(self.color_text(f" {idx} ", 'YELLOW'), end="")
                
                if col != 2:
                    print("│", end="")
            
            print()
            if row != 2:
                print("   " + "───┼───┼───")
        
        print()
    
    def available_moves(self) -> List[int]:
        """Get list of available moves."""
        return [i for i, spot in enumerate(self.board) if spot == ' ']
    
    def empty_squares(self) -> bool:
        """Check if there are empty squares."""
        return ' ' in self.board
    
    def num_empty_squares(self) -> int:
        """Count number of empty squares."""
        return self.board.count(' ')
    
    def make_move(self, square: int, letter: str) -> bool:
        """Make a move on the board."""
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.check_winner(square, letter):
                self.current_winner = letter
            return True
        return False
    
    def check_winner(self, square: int, letter: str) -> bool:
        """Check if the current move wins the game."""
        # Check row
        row_ind = square // 3
        row = self.board[row_ind*3:(row_ind+1)*3]
        if all([spot == letter for spot in row]):
            return True
        
        # Check column
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        
        # Check diagonals
        if square % 2 == 0:  # Diagonals only on even squares (0, 2, 4, 6, 8)
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([spot == letter for spot in diagonal2]):
                return True
        
        return False
    
    def check_winner_any(self, letter: str) -> bool:
        """Check if a specific letter has won."""
        # Check rows
        for row in range(3):
            if all(self.board[row*3 + col] == letter for col in range(3)):
                return True
        
        # Check columns
        for col in range(3):
            if all(self.board[row*3 + col] == letter for row in range(3)):
                return True
        
        # Check diagonals
        if all(self.board[i] == letter for i in [0, 4, 8]):
            return True
        if all(self.board[i] == letter for i in [2, 4, 6]):
            return True
        
        return False
    
    def minimax(self, depth: int, is_maximizing: bool, alpha: float = -math.inf, 
                beta: float = math.inf, use_alpha_beta: bool = True) -> Tuple[int, int]:
        """
        Minimax algorithm with Alpha-Beta pruning.
        Returns (score, best_move)
        """
        self.nodes_explored += 1
        
        # Terminal states
        if self.check_winner_any('X'):
            return 10 - depth, -1
        if self.check_winner_any('O'):
            return -10 + depth, -1
        if not self.empty_squares():
            return 0, -1
        
        if is_maximizing:
            best_score = -math.inf
            best_move = -1
            for move in self.available_moves():
                self.board[move] = 'X'
                score, _ = self.minimax(depth + 1, False, alpha, beta, use_alpha_beta)
                self.board[move] = ' '
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                if use_alpha_beta:
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break  # Beta cutoff
            
            return best_score, best_move
        else:
            best_score = math.inf
            best_move = -1
            for move in self.available_moves():
                self.board[move] = 'O'
                score, _ = self.minimax(depth + 1, True, alpha, beta, use_alpha_beta)
                self.board[move] = ' '
                
                if score < best_score:
                    best_score = score
                    best_move = move
                
                if use_alpha_beta:
                    beta = min(beta, score)
                    if beta <= alpha:
                        break  # Alpha cutoff
            
            return best_score, best_move
    
    def get_ai_move_easy(self) -> int:
        """AI makes a random move (easy difficulty)."""
        available = self.available_moves()
        
        # Occasionally make a good move
        if random.random() < 0.3:
            # Try to win if possible
            for move in available:
                self.board[move] = 'X'
                if self.check_winner(move, 'X'):
                    self.board[move] = ' '
                    return move
                self.board[move] = ' '
            
            # Try to block human win
            for move in available:
                self.board[move] = 'O'
                if self.check_winner(move, 'O'):
                    self.board[move] = ' '
                    return move
                self.board[move] = ' '
        
        return random.choice(available)
    
    def get_ai_move_medium(self) -> int:
        """AI with moderate intelligence."""
        available = self.available_moves()
        
        # 1. Try to win
        for move in available:
            self.board[move] = 'X'
            if self.check_winner(move, 'X'):
                self.board[move] = ' '
                return move
            self.board[move] = ' '
        
        # 2. Block human win
        for move in available:
            self.board[move] = 'O'
            if self.check_winner(move, 'O'):
                self.board[move] = ' '
                return move
            self.board[move] = ' '
        
        # 3. Take center if available
        if 4 in available:
            return 4
        
        # 4. Take corners
        corners = [0, 2, 6, 8]
        available_corners = [corner for corner in corners if corner in available]
        if available_corners:
            return random.choice(available_corners)
        
        # 5. Take edges
        edges = [1, 3, 5, 7]
        available_edges = [edge for edge in edges if edge in available]
        if available_edges:
            return random.choice(available_edges)
        
        return random.choice(available)
    
    def get_ai_move_hard(self) -> int:
        """AI with hard difficulty using minimax with limited depth."""
        # Use minimax with depth limit
        available = self.available_moves()
        
        # If first move, take center or corner
        if len(available) >= 8:
            if 4 in available:
                return 4
            else:
                return random.choice([0, 2, 6, 8])
        
        # Use minimax with limited depth for faster play
        _, move = self.minimax(0, True, use_alpha_beta=True)
        return move
    
    def get_ai_move_unbeatable(self) -> int:
        """Unbeatable AI using full minimax with alpha-beta pruning."""
        self.nodes_explored = 0
        start_time = time.time()
        
        _, move = self.minimax(0, True, use_alpha_beta=True)
        
        end_time = time.time()
        thinking_time = end_time - start_time
        
        # Show AI thinking stats
        print(self.color_text("\n🤖 AI Thinking Stats:", 'CYAN'))
        print(self.color_text(f"   • Nodes explored: {self.nodes_explored:,}", 'YELLOW'))
        print(self.color_text(f"   • Thinking time: {thinking_time:.3f} seconds", 'YELLOW'))
        print(self.color_text(f"   • Moves evaluated: {len(self.available_moves())}", 'YELLOW'))
        
        return move
    
    def get_ai_move(self) -> int:
        """Get AI move based on current difficulty."""
        if self.difficulty == 'easy':
            return self.get_ai_move_easy()
        elif self.difficulty == 'medium':
            return self.get_ai_move_medium()
        elif self.difficulty == 'hard':
            return self.get_ai_move_hard()
        else:  # unbeatable
            return self.get_ai_move_unbeatable()
    
    def analyze_position(self):
        """Analyze current board position."""
        print(self.color_text("\n📊 Position Analysis:", 'MAGENTA'))
        
        # Check winning chances
        available = self.available_moves()
        
        # Can AI win in next move?
        for move in available:
            self.board[move] = 'X'
            if self.check_winner(move, 'X'):
                self.board[move] = ' '
                print(self.color_text("   • AI can win next move!", 'GREEN'))
                return
            self.board[move] = ' '
        
        # Can human win in next move?
        for move in available:
            self.board[move] = 'O'
            if self.check_winner(move, 'O'):
                self.board[move] = ' '
                print(self.color_text("   • Human can win next move!", 'RED'))
                return
            self.board[move] = ' '
        
        # Evaluate board score
        score = self.evaluate_board()
        if score > 5:
            print(self.color_text(f"   • AI has strong position (score: {score})", 'GREEN'))
        elif score < -5:
            print(self.color_text(f"   • Human has strong position (score: {score})", 'RED'))
        else:
            print(self.color_text(f"   • Position is balanced (score: {score})", 'YELLOW'))
        
        # Strategic advice
        if 4 in available:  # Center available
            print(self.color_text("   • Center control is available (key position!)", 'CYAN'))
        
        corners = [corner for corner in [0, 2, 6, 8] if corner in available]
        if len(corners) >= 2:
            print(self.color_text("   • Multiple corners available (good strategic positions)", 'CYAN'))
    
    def evaluate_board(self) -> int:
        """Evaluate the board state."""
        # Check for win/lose
        if self.check_winner_any('X'):
            return 100
        if self.check_winner_any('O'):
            return -100
        
        # Heuristic evaluation
        score = 0
        
        # Evaluate rows, columns, and diagonals
        lines = [
            # Rows
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            # Columns
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            # Diagonals
            [0, 4, 8], [2, 4, 6]
        ]
        
        for line in lines:
            values = [self.board[i] for i in line]
            x_count = values.count('X')
            o_count = values.count('O')
            empty_count = values.count(' ')
            
            # Award points for potential wins
            if x_count == 2 and empty_count == 1:
                score += 10
            elif o_count == 2 and empty_count == 1:
                score -= 10
            elif x_count == 1 and empty_count == 2:
                score += 1
            elif o_count == 1 and empty_count == 2:
                score -= 1
        
        # Center control bonus
        if self.board[4] == 'X':
            score += 3
        elif self.board[4] == 'O':
            score -= 3
        
        # Corner control bonus
        corners = [0, 2, 6, 8]
        for corner in corners:
            if self.board[corner] == 'X':
                score += 2
            elif self.board[corner] == 'O':
                score -= 2
        
        return score
    
    def show_game_tips(self):
        """Display strategic tips for the game."""
        print(self.color_text("\n💡 Tic-Tac-Toe Strategy Tips:", 'MAGENTA'))
        tips = [
            "1. Take the center (position 4) if available",
            "2. Corners (0, 2, 6, 8) are stronger than edges",
            "3. Create forks (threats in two directions)",
            "4. Block opponent's potential winning lines",
            "5. Watch for opponent's forcing moves"
        ]
        for tip in tips:
            print(self.color_text(f"   {tip}", 'YELLOW'))
    
    def play_turn(self, player: str) -> bool:
        """Handle a single turn."""
        self.clear_screen()
        
        # Show header
        print(self.color_text("=" * 60, 'CYAN'))
        print(self.color_text("🤖 ULTIMATE TIC-TAC-TOE AI".center(60), 'GREEN'))
        print(self.color_text("=" * 60, 'CYAN'))
        
        # Show game info
        print(self.color_text(f"\nGame #{self.game_id} | Difficulty: {self.difficulty.upper()}", 'YELLOW'))
        print(self.color_text(f"Score: AI {self.ai_wins} - {self.human_wins} You | Ties: {self.ties}", 'CYAN'))
        
        self.print_board_nums()
        self.print_board()
        
        if player == self.human_player:
            # Human turn
            print(self.color_text(f"\n🧑 Your turn ({player})", 'GREEN'))
            print(self.color_text("Enter position (0-8) or 'q' to quit, 'h' for help:", 'YELLOW'))
            
            while True:
                move = input("> ").strip().lower()
                
                if move == 'q':
                    return False
                elif move == 'h':
                    self.show_game_tips()
                    self.analyze_position()
                    continue
                elif move == 'a':
                    self.analyze_position()
                    continue
                elif move == 'd':
                    self.change_difficulty()
                    continue
                elif move == 's':
                    self.show_statistics()
                    continue
                
                try:
                    move = int(move)
                    if move < 0 or move > 8:
                        print(self.color_text("Please enter a number between 0 and 8", 'RED'))
                        continue
                    
                    if self.board[move] != ' ':
                        print(self.color_text("That position is already taken!", 'RED'))
                        continue
                    
                    self.make_move(move, player)
                    return True
                    
                except ValueError:
                    print(self.color_text("Please enter a valid number or command", 'RED'))
        
        else:
            # AI turn
            print(self.color_text(f"\n🤖 AI's turn ({player})", 'RED'))
            print(self.color_text("AI is thinking...", 'YELLOW'))
            
            # Show thinking animation
            for _ in range(3):
                time.sleep(0.3)
                print(".", end="", flush=True)
            print()
            
            move = self.get_ai_move()
            self.make_move(move, player)
            
            print(self.color_text(f"AI plays at position {move}", 'RED'))
            time.sleep(1)
            return True
    
    def change_difficulty(self):
        """Change game difficulty."""
        print(self.color_text("\n🎯 Select Difficulty Level:", 'MAGENTA'))
        print(self.color_text("1. Easy (Random moves)", 'YELLOW'))
        print(self.color_text("2. Medium (Basic strategy)", 'YELLOW'))
        print(self.color_text("3. Hard (Advanced strategy)", 'YELLOW'))
        print(self.color_text("4. Unbeatable (Perfect play)", 'YELLOW'))
        
        while True:
            choice = input("Enter choice (1-4): ").strip()
            if choice == '1':
                self.difficulty = 'easy'
                break
            elif choice == '2':
                self.difficulty = 'medium'
                break
            elif choice == '3':
                self.difficulty = 'hard'
                break
            elif choice == '4':
                self.difficulty = 'unbeatable'
                break
            else:
                print(self.color_text("Invalid choice!", 'RED'))
        
        print(self.color_text(f"Difficulty set to {self.difficulty.upper()}!", 'GREEN'))
        time.sleep(1)
    
    def show_statistics(self):
        """Display game statistics."""
        self.clear_screen()
        
        print(self.color_text("=" * 60, 'CYAN'))
        print(self.color_text("📊 GAME STATISTICS".center(60), 'GREEN'))
        print(self.color_text("=" * 60, 'CYAN'))
        
        total_games = self.ai_wins + self.human_wins + self.ties
        
        if total_games > 0:
            ai_percent = (self.ai_wins / total_games) * 100
            human_percent = (self.human_wins / total_games) * 100
            tie_percent = (self.ties / total_games) * 100
        else:
            ai_percent = human_percent = tie_percent = 0
        
        print(self.color_text(f"\nTotal Games Played: {total_games}", 'YELLOW'))
        print(self.color_text("\nWin/Loss Record:", 'CYAN'))
        print(self.color_text(f"  AI Wins: {self.ai_wins} ({ai_percent:.1f}%)", 'RED'))
        print(self.color_text(f"  Your Wins: {self.human_wins} ({human_percent:.1f}%)", 'GREEN'))
        print(self.color_text(f"  Ties: {self.ties} ({tie_percent:.1f}%)", 'YELLOW'))
        
        if total_games > 0:
            print(self.color_text("\nRecent Games History:", 'MAGENTA'))
            for game in self.game_history[-5:]:
                winner = game.get('winner', 'Tie')
                if winner == 'X':
                    print(self.color_text(f"  Game {game['id']}: AI won in {game['moves']} moves", 'RED'))
                elif winner == 'O':
                    print(self.color_text(f"  Game {game['id']}: You won in {game['moves']} moves", 'GREEN'))
                else:
                    print(self.color_text(f"  Game {game['id']}: Tie", 'YELLOW'))
        
        print(self.color_text("\nCurrent Difficulty: ", 'CYAN') + 
              self.color_text(self.difficulty.upper(), 'YELLOW'))
        
        input("\nPress Enter to continue...")
    
    def record_game(self, moves: int, winner: str):
        """Record game results."""
        game_data = {
            'id': self.game_id,
            'date': datetime.now().isoformat(),
            'difficulty': self.difficulty,
            'moves': moves,
            'winner': winner,
            'board': self.board.copy()
        }
        self.game_history.append(game_data)
        
        if winner == 'X':
            self.ai_wins += 1
        elif winner == 'O':
            self.human_wins += 1
        else:
            self.ties += 1
        
        self.save_statistics()
    
    def show_winner_animation(self, winner: str):
        """Show winning animation."""
        self.clear_screen()
        
        if winner == 'X':
            color = 'RED'
            message = "🤖 AI WINS!"
        elif winner == 'O':
            color = 'GREEN'
            message = "🎉 YOU WIN!"
        else:
            color = 'YELLOW'
            message = "🤝 IT'S A TIE!"
        
        print(self.color_text("=" * 60, color))
        print(self.color_text(message.center(60), color))
        print(self.color_text("=" * 60, color))
        
        # Animated board
        for _ in range(3):
            self.print_board()
            time.sleep(0.5)
            print("\n" * 2)
    
    def show_game_over_screen(self, winner: str, moves: int):
        """Display game over screen."""
        self.clear_screen()
        
        print(self.color_text("=" * 60, 'CYAN'))
        
        if winner == 'X':
            print(self.color_text("💀 GAME OVER - AI WINS!".center(60), 'RED'))
            print(self.color_text("The AI's perfect strategy prevails!".center(60), 'YELLOW'))
        elif winner == 'O':
            print(self.color_text("🎉 VICTORY - YOU WIN!".center(60), 'GREEN'))
            print(self.color_text("Congratulations! You beat the AI!".center(60), 'YELLOW'))
        else:
            print(self.color_text("🤝 DRAW GAME".center(60), 'YELLOW'))
            print(self.color_text("Excellent defense on both sides!".center(60), 'YELLOW'))
        
        print(self.color_text("=" * 60, 'CYAN'))
        
        self.print_board()
        
        print(self.color_text(f"\n📈 Game Stats:", 'MAGENTA'))
        print(self.color_text(f"   • Total moves: {moves}", 'YELLOW'))
        print(self.color_text(f"   • Difficulty: {self.difficulty.upper()}", 'YELLOW'))
        print(self.color_text(f"   • Game ID: #{self.game_id}", 'YELLOW'))
        
        print(self.color_text("\nOptions:", 'CYAN'))
        print(self.color_text("  1. Play Again", 'YELLOW'))
        print(self.color_text("  2. Change Difficulty", 'YELLOW'))
        print(self.color_text("  3. View Statistics", 'YELLOW'))
        print(self.color_text("  4. Exit", 'YELLOW'))
        
        while True:
            choice = input("\nSelect option (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            print(self.color_text("Invalid choice!", 'RED'))
    
    def reset_game(self):
        """Reset the game board."""
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
        self.game_id += 1
    
    def run(self):
        """Main game loop."""
        self.clear_screen()
        
        # Show welcome screen
        print(self.color_text("=" * 60, 'CYAN'))
        print(self.color_text("🤖 ULTIMATE TIC-TAC-TOE AI".center(60), 'GREEN'))
        print(self.color_text("Powered by Minimax Algorithm with Alpha-Beta Pruning".center(60), 'YELLOW'))
        print(self.color_text("=" * 60, 'CYAN'))
        
        print(self.color_text("\nWelcome to the Ultimate Tic-Tac-Toe Challenge!", 'MAGENTA'))
        print(self.color_text("\nYou are playing as 'O' against the AI 'X'", 'YELLOW'))
        
        # Difficulty selection
        self.change_difficulty()
        
        while True:
            self.reset_game()
            moves = 0
            
            # Choose who goes first
            print(self.color_text("\nWho goes first?", 'MAGENTA'))
            print(self.color_text("1. You (Human)", 'YELLOW'))
            print(self.color_text("2. AI", 'YELLOW'))
            
            while True:
                choice = input("Enter choice (1-2): ").strip()
                if choice == '1':
                    current_player = self.human_player
                    break
                elif choice == '2':
                    current_player = self.ai_player
                    break
                else:
                    print(self.color_text("Invalid choice!", 'RED'))
            
            # Game loop
            while self.empty_squares() and not self.current_winner:
                if not self.play_turn(current_player):
                    print(self.color_text("\nThanks for playing!", 'YELLOW'))
                    self.save_statistics()
                    return
                
                moves += 1
                
                # Switch player
                current_player = self.human_player if current_player == self.ai_player else self.ai_player
            
            # Game over
            winner = self.current_winner
            
            # Show winner animation
            self.show_winner_animation(winner)
            
            # Record game
            self.record_game(moves, winner if winner else 'tie')
            
            # Show game over screen and get next action
            choice = self.show_game_over_screen(winner, moves)
            
            if choice == '1':
                continue  # Play again
            elif choice == '2':
                self.change_difficulty()
                continue
            elif choice == '3':
                self.show_statistics()
                continue
            else:  # Exit
                break
        
        print(self.color_text("\nThanks for playing! Final statistics saved.", 'YELLOW'))
        self.save_statistics()
        print(self.color_text("\nGoodbye! 👋\n", 'CYAN'))


def main():
    """Main entry point."""
    # Check if running in VS Code or terminal that supports colors
    try:
        game = UltimateTicTacToeAI()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please make sure you're running Python 3.6 or higher.")


if __name__ == "__main__":
    main()