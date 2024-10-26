import os
import pygame
from pygame.constants import KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN
from time import sleep

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((800, 640))
pygame.display.set_caption("Sokoban-Group14!")
icon = pygame.image.load('Image/logo.png')
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Load images
player = pygame.image.load('Image/player.png')
wall = pygame.image.load('Image/wall.png')
stone = pygame.image.load('Image/rock.png')
checkPoint = pygame.image.load('Image/check_point.png')
space = pygame.image.load('Image/space.png')
arrowLeft = pygame.image.load('Image/left_arrow.png')
arrowRight = pygame.image.load('Image/right_arrow.png')
initBackground = pygame.image.load('Image/screen.png')

# Map directory and files
map_directory = "Map"
map_file_paths = [os.path.join(map_directory, f) for f in os.listdir(map_directory) if f.endswith('.txt')]

def readMapFromFile(file_path):
    board=[]
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the first line
        board = [list(line.rstrip()) for line in lines]
    return board

# Function to render the map
def renderMap(board):
    width = len(board[0])
    height = len(board)
    indent = (640 - width * 32) / 2.0  
    
    for i in range(height):
        for j in range(width):
            screen.blit(space, (j * 32 + indent, i * 32 + 200))
            if board[i][j] == '#':
                screen.blit(wall, (j * 32 + indent, i * 32 + 200))
            elif board[i][j] == '$':
                screen.blit(stone, (j * 32 + indent, i * 32 + 200))
            elif board[i][j] == '.':
                screen.blit(checkPoint, (j * 32 + indent, i * 32 + 200))
            elif board[i][j] == '@':
                screen.blit(player, (j * 32 + indent, i * 32 + 200))

# Global variables
running = True
selected_level = 0  # Default level
font = pygame.font.SysFont(None, 40)

# Player position
player_x, player_y = 0, 0  # Initialize player position to (0, 0)

# Function to find the player's position in the map

check_point_list=[]
def find_checkpoint_position(board):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == '.':
                result=(i,j)
                check_point_list.append(result)  # Return the player's position
rocks_point_list=[]               
def find_rocks_position(board):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == '$':
                result=(i,j)
                rocks_point_list.append(result) 
                
                         
def find_player_position(board):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == '@':
                return i, j  # Return the player's position

# Function to change the level
def change_level(direction):
    global selected_level
    selected_level = (selected_level + direction) % len(map_file_paths)
    board = readMapFromFile(map_file_paths[selected_level])
    setUP()
    print(selected_level)
    
    check_point_list.clear()
    rocks_point_list.clear()
    player_x, player_y = find_player_position(board)  
    find_checkpoint_position(board)
    find_rocks_position(board)
    #print(check_point_list)
    #print(rocks_point_list)
    

# Function to move the player
def move_player(board, direction):
    global player_x, player_y
    new_x, new_y = player_x, player_y

    # Calculate new player position based on direction
    if direction == "LEFT":
        new_y -= 1
    elif direction == "RIGHT":
        new_y += 1
    elif direction == "UP":
        new_x -= 1
    elif direction == "DOWN":
        new_x += 1

    # Check if the new position is valid (empty space or checkpoint)
    if board[new_x][new_y] == ' ' or board[new_x][new_y] == '.':
        # Move the player
        board[player_x][player_y] = ' '  # Empty the old position
        board[new_x][new_y] = '@'  # Set the new position
        player_x, player_y = new_x, new_y  # Update player position
    # If there's a stone, attempt to move it as well
    elif board[new_x][new_y] == '$':
        # Check if the stone can be pushed
        stone_new_x, stone_new_y = new_x + (new_x - player_x), new_y + (new_y - player_y)
        if board[stone_new_x][stone_new_y] == ' ' or board[stone_new_x][stone_new_y] == '.':
            # Move the stone
            board[stone_new_x][stone_new_y] = '$'
            board[new_x][new_y] = '@'
            board[player_x][player_y] = ' '  # Empty the old player position
            player_x, player_y = new_x, new_y  # Update player position
    for point in check_point_list:
        if board[point[0]][point[1]]==" ":
            board[point[0]][point[1]]="."
    check_win(board)
def check_win(board):
    for point in check_point_list:
        if board[point[0]][point[1]] !="$":
            print("Not yet")
            return
    
    print("Nice")
            
# Function to draw arrow buttons
def draw_arrow_button(image, x, y, width, height):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hovered = x < mouse_x < x + width and y < mouse_y < y + height  

    if is_hovered:
        image.set_alpha(200)  
    else:
        image.set_alpha(255)

    screen.blit(image, (x, y))
    return is_hovered  

# Function to set up the display
def setUP():
    screen.blit(initBackground, (0, 0))
     # Read map for the selected level


    renderMap(board)

    level_text = font.render(f"Level {selected_level + 1}", True, YELLOW)
    text_rect = level_text.get_rect(center=(320, 510))

    rect_x, rect_y, rect_width, rect_height = 200, 470, 240, 80
    pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_width, rect_height))

    button_left_hover = draw_arrow_button(arrowLeft, 90, 480, 100, 50)
    button_right_hover = draw_arrow_button(arrowRight, 480, 480, 100, 50)

    screen.blit(level_text, text_rect)

def moveByInstruct(path):
    global board  # Đảm bảo sử dụng biến board toàn cục
    path = str(path).lower()
    for step in path:
        if step == "l":
            move_player(board, "LEFT")
        elif step == "r":
            move_player(board, "RIGHT")
        elif step == "d":
            move_player(board, "DOWN")
        elif step == "u":
            move_player(board, "UP")
        
        # Cập nhật màn hình sau mỗi bước di chuyển
        renderMap(board)
        pygame.display.flip()
        sleep(0.5)  # Tùy chỉnh thời gian nghỉ giữa các bước nếu cần

#cho push cmn nó lên main đi chia branch ra làm gì

# Main loop
if __name__ == "__main__":
    # Load map and set player position
    screen.fill(WHITE)
    board = readMapFromFile(map_file_paths[selected_level])
    setUP()
    player_x, player_y = find_player_position(board)  # Find the player's starting position on the board
    find_checkpoint_position(board)
    print (check_point_list)  
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle level change with mouse clicks on arrow buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if 90 < mouse_x < 190 and 480 < mouse_y < 530:  # Left arrow button
                        screen.fill(WHITE)

                        change_level(-1)  # Decrease level
                        board = readMapFromFile(map_file_paths[selected_level])
                        player_x, player_y = find_player_position(board)
                        
                    elif 480 < mouse_x < 530 and 480 < mouse_y < 530:  # Right arrow button
                        screen.fill(WHITE)
                        change_level(1)  # Increase level
                        board = readMapFromFile(map_file_paths[selected_level])
                        player_x, player_y = find_player_position(board)
                        
                        

            # Handle player movement with keyboard inputs
            if event.type == pygame.KEYDOWN:
                if event.key == K_LEFT:
                    move_player(board, "LEFT")
                    moveByInstruct("luRurrDrdLLLuRRRRRRRurD")

                elif event.key == K_RIGHT:
                    move_player(board, "RIGHT")
                elif event.key == K_UP:
                    move_player(board, "UP")

                elif event.key == K_DOWN:
                    move_player(board, "DOWN")
                 

        # Render the updated map and display it

        renderMap(board)
        pygame.display.flip()

    pygame.quit()
