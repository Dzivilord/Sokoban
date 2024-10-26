import os
import pygame
from pygame.constants import KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN
from time import sleep

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban-Group14!")
icon = pygame.image.load('Image/logo.png')
pygame.display.set_icon(icon)

# Colors
WHITE, BLACK, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 255, 0)

# Load images
images = {
    'player': pygame.image.load('Image/player.png'),
    'wall': pygame.image.load('Image/wall.png'),
    'stone': pygame.image.load('Image/rock.png'),
    'checkPoint': pygame.image.load('Image/check_point.png'),
    'space': pygame.image.load('Image/space.png'),
    'arrowLeft': pygame.image.load('Image/left_arrow.png'),
    'arrowRight': pygame.image.load('Image/right_arrow.png'),
    'background': pygame.image.load('Image/screen.png')
}

# Map files and settings
map_directory = "Map"
map_file_paths = [os.path.join(map_directory, f) for f in os.listdir(map_directory) if f.endswith('.txt')]

# Initialize global variables
selected_level = 0  # Default level
font = pygame.font.SysFont(None, 40)

# Position variables
player_x, player_y = 0, 0  
check_point_list, rocks_point_list = [], []

def read_map(file_path):
    """Load map data from a file and return as a 2D list."""
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()[1:]]

def render_map(board):
    """Render the map and interface elements on the screen."""
    screen.blit(images['background'], (0, 0))  # Background
    indent = (640 - len(board[0]) * 32) / 2.0  # Calculate indent for centering
    
    # Draw each tile in the board
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            pos = (j * 32 + indent, i * 32 + 200)
            screen.blit(images['space'], pos)
            if cell == '#':
                screen.blit(images['wall'], pos)
            elif cell == '$':
                screen.blit(images['stone'], pos)
            elif cell == '.':
                screen.blit(images['checkPoint'], pos)
            elif cell == '@':
                screen.blit(images['player'], pos)
    
    # Draw interface elements
    draw_interface()

def draw_interface():
    """Draw level text, buttons, and other UI elements."""
    level_text = font.render(f"Level {selected_level + 1}", True, YELLOW)
    screen.blit(level_text, level_text.get_rect(center=(320, 510)))
    
    # Draw arrow buttons
    draw_button(images['arrowLeft'], 90, 480)
    draw_button(images['arrowRight'], 480, 480)

def draw_button(image, x, y):
    """Draw an interactive button on the screen."""
    is_hovered = pygame.Rect(x, y, image.get_width(), image.get_height()).collidepoint(pygame.mouse.get_pos())
    image.set_alpha(200 if is_hovered else 255)
    screen.blit(image, (x, y))
    return is_hovered

def find_positions(board, item):
    """Find positions of specified items in the map."""
    return [(i, j) for i, row in enumerate(board) for j, cell in enumerate(row) if cell == item]

def change_level(direction):
    """Change level based on direction and reset board."""
    global selected_level, board, player_x, player_y, check_point_list, rocks_point_list
    selected_level = (selected_level + direction) % len(map_file_paths)
    board = read_map(map_file_paths[selected_level])
    check_point_list, rocks_point_list = find_positions(board, '.'), find_positions(board, '$')
    player_x, player_y = find_positions(board, '@')[0]

def move_player(board, direction):
    """Move the player in the specified direction, handling stone movement and checking win condition."""
    global player_x, player_y
    dx, dy = {'LEFT': (0, -1), 'RIGHT': (0, 1), 'UP': (-1, 0), 'DOWN': (1, 0)}[direction]
    new_x, new_y = player_x + dx, player_y + dy

    if board[new_x][new_y] in ' .':  # Move player
        board[player_x][player_y], board[new_x][new_y] = ' ', '@'
        player_x, player_y = new_x, new_y
    elif board[new_x][new_y] == '$':  # Push stone if possible
        stone_new_x, stone_new_y = new_x + dx, new_y + dy
        if board[stone_new_x][stone_new_y] in ' .':
            board[stone_new_x][stone_new_y], board[new_x][new_y] = '$', '@'
            board[player_x][player_y] = ' '
            player_x, player_y = new_x, new_y
    check_for_completion(board)

def check_for_completion(board):
    """Check if all checkpoints are filled by stones to trigger a win."""
    if all(board[x][y] == '$' for x, y in check_point_list):
        print("Level Complete!")

# Main loop
def main():
    global board
    board = read_map(map_file_paths[selected_level])
    change_level(0)  # Load initial level

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    move_player(board, "LEFT")
                elif event.key == K_RIGHT:
                    move_player(board, "RIGHT")
                elif event.key == K_UP:
                    move_player(board, "UP")
                elif event.key == K_DOWN:
                    move_player(board, "DOWN")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if draw_button(images['arrowLeft'], 90, 480):
                        change_level(-1)
                    elif draw_button(images['arrowRight'], 480, 480):
                        change_level(1)

        # Render the updated map
        render_map(board)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
