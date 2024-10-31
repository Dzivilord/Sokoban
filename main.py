import os
import pygame
from pygame.constants import KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN
from time import sleep
import threading
from BFS import bfs
from DFS import dfs
from UCS import ucs
from AStar import astar


# Initialize pygame
pygame.init()
pygame.font.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 901, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban-Group14!")
icon = pygame.image.load('image/logo.png')
pygame.display.set_icon(icon)

# Colors
WHITE, BLACK, BLUE, YELLOW,CYAN = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 255, 0),(0, 255, 255)

# Load images
images = {
    'player': pygame.image.load('image/player.png'),
    'wall': pygame.image.load('image/wall.png'),
    'stone': pygame.image.load('image/rock.png'),
    'checkPoint': pygame.image.load('image/check_point.png'),
    'space': pygame.image.load('image/space.png'),
    'arrowLeft': pygame.image.load('image/left_arrow.png'),
    'arrowRight': pygame.image.load('image/right_arrow.png'),
    'background': pygame.image.load('image/background.png'),
    'BFSButton':pygame.image.load('image/BFS.png'),
    'DFSButton':pygame.image.load('image/DFS.png'),
    'UCSButton':pygame.image.load('image/UCS.png'),
    'AStarButton':pygame.image.load('image/AStar.png'),
    'ResetButton':pygame.image.load('image/reset.png'),
    'StopButton':pygame.image.load('image/stop.png')
    
}

# Map files and settings
map_directory = "input"
map_file_paths = [os.path.join(map_directory, f) for f in os.listdir(map_directory) if f.endswith('.txt')]

# Initialize global variables
selected_level = 0  # Default levels
step_count = 0
font = pygame.font.SysFont(None, 30)
instruct_step=""

# Position variables
player_x, player_y = 0, 0  
check_point_list, stones_point_list = [], []

stones_weights=[]
total_weights_pushed=0



def read_map(file_path):
    global stones_weights
    """Load map data from a file and return as a 2D list along with stone weights."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Hàng đầu tiên chứa khối lượng các viên đá
        stones_weights = list(map(int, lines[0].strip().split()))  # Lấy các giá trị khối lượng và chuyển thành số nguyên
        # Các hàng sau chứa bản đồ
        return [list(line.strip()) for line in lines[1:]]
        
stones_weights_dict={}
MOVE_SPEED = 4
def render_map(board):
    """Render the map and interface elements on the screen."""
    screen.blit(images['background'], (0, 0))  # Background
    indent = (600 - len(board[0]) * 32) / 2.0  # Calculate indent for centering
    
    # Draw each tile in the board
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            pos = (j * 32 + indent, i * 32 + 130)
            screen.blit(images['space'], pos)
            if cell == '#':
                screen.blit(images['wall'], pos)
            elif cell == '.':
                screen.blit(images['checkPoint'], pos)
            elif cell == '$' or cell=="*":
                screen.blit(images['stone'], pos)
                stone_position = (i, j)  # Position of the stone
                if stone_position in stones_weights_dict:
                    weight = stones_weights_dict[stone_position]
                    weight_text = font.render(str(weight), True, CYAN)  # Render weight text
                    weight_rect = weight_text.get_rect(center=(pos[0] + 16, pos[1] + 12))  # Position the text above the stone
                    screen.blit(weight_text, weight_rect)  # Draw the weight text

            elif cell == '@' or cell== '+' :
                screen.blit(images['player'], pos)


    # Draw interface elements
    draw_interface()

def draw_interface():
    """Draw level text, buttons, and other UI elements."""
    level_text = font.render(f"Level {selected_level + 1}", True, BLACK)
    screen.blit(level_text, level_text.get_rect(center=(320, 80)))
    
    step_text = font.render(f"Steps: {step_count}", True, BLACK)
    step_text_rect = step_text.get_rect(center=(740, 160))
    screen.blit(step_text, step_text_rect)
    
    for i in range(0, len(instruct_step), 25):
        chunk = instruct_step[i:i + 25]
        text_area = pygame.Rect(130, 430 + 20 * (i // 25), 350, 30)  # Thay đổi y dựa trên chunk
        text_surface = pygame.Surface((text_area.width, text_area.height), pygame.SRCALPHA)
        # Render văn bản
        solution_text = font.render(f"{chunk}", True, YELLOW)
        text_surface.blit(solution_text, (0, 0))  # Vẽ văn bản lên text_surface
        screen.blit(text_surface, text_area.topleft)  # Vẽ text_surface lên màn hình
        
    weights_text = font.render(f"Total weights:{total_weights_pushed}", True, BLACK)
    weights_text_rect = weights_text.get_rect(center=(740, 200))
    screen.blit(weights_text, weights_text_rect)
    # Draw arrow buttons
    draw_button(images['arrowLeft'], 140, 45)
    draw_button(images['arrowRight'], 400, 45)
    draw_button(images['BFSButton'],600,215)
    draw_button(images['DFSButton'],730,215)
    draw_button(images['UCSButton'],600,320)
    draw_button(images["AStarButton"],730,320)
    draw_button(images['ResetButton'],600,5)
    draw_button(images['StopButton'],720,5)

def draw_button(image, x, y):
    """Draw an interactive button on the screen."""
    is_hovered = pygame.Rect(x, y, image.get_width(), image.get_height()).collidepoint(pygame.mouse.get_pos())
    image.set_alpha(200 if is_hovered else 255)
    screen.blit(image, (x, y))
    return is_hovered

def find_positions(board, item):
    """Find positions of specified items in the map."""
    return [(i, j) for i, row in enumerate(board) for j, cell in enumerate(row) if cell in item]

def change_level(direction):
    """Change level based on direction and reset board."""
   
    global selected_level, board, player_x, player_y, check_point_list, stones_point_list,step_count,stones_weights,total_weights_pushed,stones_weights_dict

    
    selected_level = (selected_level + direction) % len(map_file_paths)
    
    stones_weights=[]
    board = read_map(map_file_paths[selected_level])
    check_point_list, stones_point_list = find_positions(board, ('.','+','*')), find_positions(board, ('$','*'))
    player_x, player_y = find_positions(board, ('@','+'))[0]
    step_count = 0
    total_weights_pushed=0
    stones_weights_dict={}
    
    for index, stones in enumerate(stones_point_list):
        stones_weights_dict[stones] = stones_weights[index]
    
    #print(stones_weights_dict)

def move_player(board, direction):
    """Move the player in the specified direction, handling stone movement and checking win condition."""
    global player_x, player_y, step_count, stones_weights_dict, stones_point_list, total_weights_pushed

    dx, dy = {'LEFT': (0, -1), 'RIGHT': (0, 1), 'UP': (-1, 0), 'DOWN': (1, 0)}[direction]
    new_x, new_y = player_x + dx, player_y + dy

    # Nếu vị trí mới là khoảng trống hoặc điểm kiểm tra
    if board[new_x][new_y] in ' .':
        # Di chuyển người chơi
        board[player_x][player_y], board[new_x][new_y] = ' ', '@'
        player_x, player_y = new_x, new_y
        step_count += 1

    # Nếu vị trí mới có viên đá
    elif board[new_x][new_y] == '$' or board[new_x][new_y] == '*':
        stone_new_x, stone_new_y = new_x + dx, new_y + dy  # Vị trí mới cho viên đá

        # Kiểm tra xem viên đá có thể được đẩy không
        if board[stone_new_x][stone_new_y] in ' .':
            # Xác định vị trí của viên đá trước khi đẩy
            old_stone_position = (new_x, new_y)  # Vị trí cũ của viên đá
            new_stone_position = (stone_new_x, stone_new_y)  # Vị trí mới của viên đá

            # Lấy khối lượng của viên đá
            weight = stones_weights_dict.get(old_stone_position)

            # Đẩy viên đá
            board[stone_new_x][stone_new_y], board[new_x][new_y] = '$', '@'
            board[player_x][player_y] = ' '

            if board[stone_new_x][stone_new_y] in check_point_list:
                board[stone_new_x][stone_new_y] = '*'
            elif board[new_x][new_y] in check_point_list:
                board[new_x][new_y] = '+'
            # Cập nhật vị trí người chơi
            player_x, player_y = new_x, new_y
            step_count += 1
            #print(old_stone_position)

            # Cập nhật từ điển với vị trí mới
            #print (stones_weights_dict)
            if old_stone_position in stones_weights_dict:
                # Gán khối lượng vào vị trí mới
                stones_weights_dict[new_stone_position] = weight

                del stones_weights_dict[old_stone_position]  # Xóa vị trí cũ của viên đá

                # Cập nhật tổng khối lượng đã đẩy
                total_weights_pushed += weight
                #print(f"Updated weight for stone at {new_stone_position}: {weight}")
                #print(f"Total weight pushed: {total_weights_pushed}")
    for point in check_point_list:
        if board[point[0]][point[1]] != '@' and board[point[0]][point[1]] != "$" and board[point[0]][point[1]] != "+"and board[point[0]][point[1]] != "*":
            board[point[0]][point[1]] = "."

    # Kiểm tra xem trò chơi đã hoàn thành chưa
    check_completion(board)
    

def check_completion(board):
    """Check if all checkpoints are filled by stones to trigger a win."""
    if all(board[x][y] == '$' for x, y in check_point_list):
        print("Level Complete!")

stop_moving = False
def stop_move():
    global stop_moving
    stop_moving = True
    move_thread.daemon
    

    
def moveOnInstruct(steps):
    steps=str(steps).lower()
    #print(steps)
    for step in steps:
        if stop_moving:  # Kiểm tra nếu yêu cầu dừng
            break
        if step=='l':
            move_player(board,"LEFT")
        elif step=='r':
            move_player(board,"RIGHT")
        elif step=='u':
            move_player(board,"UP")
        elif step=='d':
            move_player(board,"DOWN")

 
        sleep(0.5)
def start_move_on_instruct(steps):
    global stop_moving
    global move_thread
    stop_moving = False  
    move_thread = threading.Thread(target=moveOnInstruct, args=(steps,))
    move_thread.start()
# Main loop

def main():
    global board,instruct_step
    #board = read_map(map_file_paths[selected_level])
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
                    if draw_button(images['arrowLeft'], 140, 45):
                        change_level(-1)
                    elif draw_button(images['arrowRight'], 400, 45):
                        change_level(1)
                    elif draw_button(images["BFSButton"], 600, 215):
                        change_level(0)
                        
                        instruct_step=bfs(map_file_paths[selected_level])
                        instruct_step=instruct_step[:100] + "..." if len(instruct_step) > 100 else instruct_step
                        start_move_on_instruct(instruct_step)
                        
                    elif draw_button(images["DFSButton"], 730, 215):
                        change_level(0)
                        
                        instruct_step=dfs(map_file_paths[selected_level])
                        instruct_step=instruct_step[:100] + "..." if len(instruct_step) > 100 else instruct_step
                        start_move_on_instruct(instruct_step) 
                                         
                    elif draw_button(images['UCSButton'], 600, 320):
                        change_level(0)
                        instruct_step=ucs(map_file_paths[selected_level])
                        instruct_step=instruct_step[:100] + "..." if len(instruct_step) > 100 else instruct_step
                        start_move_on_instruct(instruct_step)

                    elif draw_button(images['AStarButton'], 730, 320):
                        change_level(0)
                        instruct_step=astar(map_file_paths[selected_level])
                        instruct_step=instruct_step[:100] + "..." if len(instruct_step) > 100 else instruct_step
                        start_move_on_instruct(instruct_step)
                        
                    elif draw_button(images['ResetButton'], 600, 5):
                        change_level(0)
                    elif draw_button(images['StopButton'],720,5):
                        stop_move()
                                          
        # Render the updated map
        render_map(board)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
