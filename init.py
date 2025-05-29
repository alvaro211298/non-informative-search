import pygame
import random
import sys
from copy import deepcopy
import math

# Initialize PyGame
pygame.init()

# Window configuration
WIDTH = 600
HEIGHT = 650
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle with IDS")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 100, 200)  # For the spinning wheel
FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 25)  # For "Analyzing..." text

# Goal state
GOAL_STATE = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8]
]


def generate_random_state():
    """Generate a random solvable initial state"""
    state = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    random.shuffle(state)
    # Check if solvable (even number of inversions)
    inversions = 0
    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                inversions += 1
    
    # If odd number of inversions, swap two non-zero tiles to make it solvable
    if inversions % 2 != 0:
        found_swap = False
        for i_s in range(8):
            for j_s in range(i_s + 1, 9):
                if state[i_s] != 0 and state[j_s] != 0:
                    state[i_s], state[j_s] = state[j_s], state[i_s]
                    found_swap = True
                    break
            if found_swap:
                break
        if not found_swap:  # Fallback in case no two non-zero elements are found (unlikely for 8-puzzle)
            state[0], state[1] = state[1], state[0]
            
    return [state[i:i+3] for i in range(0, 9, 3)]


def find_empty(board):
    """Find position of empty tile (0)"""
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return (i, j)
    return None


def generate_moves(board):
    """Generate all valid moves"""
    moves = []
    i, j = find_empty(board)
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
        ni, nj = i + di, j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_board = deepcopy(board)
            new_board[i][j], new_board[ni][nj] = new_board[ni][nj], new_board[i][j]
            moves.append(new_board)
    return moves


def depth_limited_search(board, limit, path):
    """Depth-Limited Search (DFS with limit)"""
    if board == GOAL_STATE:
        return path
    if len(path) >= limit:
        return None
    for move in generate_moves(board):
        # Avoid cycles by checking if the state is already in the current path
        if move not in path:
            result = depth_limited_search(move, limit, path + [move])
            if result is not None:
                return result
    return None


def solve_puzzle(board):
    """Iterative Deepening Search (IDS)"""
    limit = 0
    while True:
        solution = depth_limited_search(board, limit, [board])
        if solution is not None:
            return solution
        limit += 1


def draw_board(board, solving_in_progress, current_step=0, solution=None):
    """Draw the puzzle board and animation"""
    WINDOW.fill(WHITE)
    pygame.draw.rect(WINDOW, GRAY, (50, 100, 500, 500))  # Main puzzle area
    
    for i in range(3):
        for j in range(3):
            if board[i][j] != 0:
                pygame.draw.rect(WINDOW, BLUE, (50 + j * 166, 100 + i * 166, 166, 166))
                number = FONT.render(str(board[i][j]), True, WHITE)
                # Center the number in the tile
                text_rect = number.get_rect(center=(50 + j * 166 + 166 // 2, 100 + i * 166 + 166 // 2))
                WINDOW.blit(number, text_rect)

    # Solve button (left top)
    pygame.draw.rect(WINDOW, BLACK, (50, 30, 200, 50))
    solve_text = FONT.render("Solve", True, WHITE)
    solve_text_rect = solve_text.get_rect(center=(50 + 100, 30 + 25))
    WINDOW.blit(solve_text, solve_text_rect)

    # Restart Board button (right top)
    pygame.draw.rect(WINDOW, BLACK, (350, 30, 200, 50))
    restart_text = FONT.render("Restart Board", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=(350 + 100, 30 + 25))
    WINDOW.blit(restart_text, restart_text_rect)

    # Analyzing animation (spinning wheel and text)
    if solving_in_progress:
        # Adjusted position for the spinning wheel and text
        center_x, center_y = WIDTH // 2, 80  # Moved up from 70 to 80 (adjust as needed)
        radius = 15
        thickness = 3
        start_angle = math.radians(pygame.time.get_ticks() * 0.3)  # Rotate slowly
        end_angle = start_angle + math.radians(270)  # Draw 3/4 of a circle

        # Draw the base circle (optional, can be grayed out for effect)
        pygame.draw.circle(WINDOW, GRAY, (center_x, center_y), radius, thickness)
        # Draw the spinning arc
        pygame.draw.arc(WINDOW, DARK_BLUE, 
                       (center_x - radius, center_y - radius, radius * 2, radius * 2),
                       start_angle, end_angle, thickness)

        # Draw "Analyzing..." text
        analyzing_text = SMALL_FONT.render("Analyzing...", True, BLACK)
        text_rect = analyzing_text.get_rect(center=(center_x, center_y + radius + 15))  # Below the wheel
        WINDOW.blit(analyzing_text, text_rect)

    # Step counter (displayed when a solution is being animated or when it's complete)
    if solution is not None:
        # len(solution) is the number of states including the initial one.
        # So, the number of steps is len(solution) - 1.
        step_text = FONT.render(f"Steps: {current_step}/{len(solution) - 1}", True, BLACK)
        WINDOW.blit(step_text, (200, 600))  # Position at the bottom


def puzzle_game():
    """Main game function"""
    board = generate_random_state()
    solution = None
    current_step = 0
    solving_in_progress = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not solving_in_progress:
                # Allow manual moves only when not solving
                i, j = find_empty(board)
                if event.key == pygame.K_UP and i < 2:
                    board[i][j], board[i+1][j] = board[i+1][j], board[i][j]
                elif event.key == pygame.K_DOWN and i > 0:
                    board[i][j], board[i-1][j] = board[i-1][j], board[i][j]
                elif event.key == pygame.K_LEFT and j < 2:
                    board[i][j], board[i][j+1] = board[i][j+1], board[i][j]
                elif event.key == pygame.K_RIGHT and j > 0:
                    board[i][j], board[i][j-1] = board[i][j-1], board[i][j]
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Check for "Solve" button click
                if 50 <= x <= 250 and 30 <= y <= 80:
                    if not solving_in_progress:  # Only allow solving if not already in progress
                        solving_in_progress = True
                        # Update the display immediately to show "Analyzing..." before solving
                        draw_board(board, solving_in_progress)
                        pygame.display.update()

                        # Perform the actual solving (this can take a moment)
                        solution = solve_puzzle(board)
                        current_step = 0  # Reset step counter for animation
                        
                        if solution:
                            board = deepcopy(solution[0])  # Show the initial state of the solution
                        
                        solving_in_progress = False  # Solving is done, whether solution found or not

                # Check for "Restart Board" button click
                elif 350 <= x <= 550 and 30 <= y <= 80:
                    board = generate_random_state()
                    solution = None  # Clear any ongoing solution
                    current_step = 0
                    solving_in_progress = False  # Reset solving state

        # Display the board and animation
        draw_board(board, solving_in_progress, current_step, solution)

        # Animate solution steps if a solution exists and we are not currently analyzing
        if solution is not None and not solving_in_progress:
            if current_step < len(solution):
                board = deepcopy(solution[current_step])  # Update the board to the current step of the solution
                pygame.display.update()  # Update to show the new board state
                pygame.time.delay(500)   # Delay for visualization
                current_step += 1
            else:
                # Solution animation complete, ensure current_step reflects total steps for display
                # We show total steps as len(solution) - 1, and current_step reaches len(solution)
                # So to display the final state and total steps, we set current_step to len(solution)-1
                # if current_step was len(solution) already (meaning animation finished).
                if current_step == len(solution):  # If animation just finished
                    current_step = len(solution) - 1  # Adjust to show the final count
                
                # Make sure the final step count is shown
                draw_board(board, solving_in_progress, current_step, solution)
                pygame.display.update()  # Final update to ensure step count is correct
                # No "Solved!" message, just keeps the final step count visible

        pygame.display.update()  # This must be called at the end of each loop iteration for Pygame to render


# This ensures puzzle_game() is called only when the script is executed directly
if __name__ == "__main__":
    puzzle_game()