import numpy as np
import heapq
"""Tải các câu đố và định nghĩa quy tắc của trò chơi Sokoban"""


def transferToGameState(layout):
    """Chuyển đổi bố cục của câu đố ban đầu thành trạng thái trò chơi"""
    layout = [x.replace('\n','') for x in layout]  # Loại bỏ ký tự xuống dòng
    layout = [','.join(layout[i]) for i in range(len(layout))]  # Gộp các dòng
    layout = [x.split(',') for x in layout]  # Tách các phần tử
    maxColsNum = max([len(x) for x in layout])  # Tìm số cột tối đa
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ': layout[irow][icol] = 0   # không gian trống
            elif layout[irow][icol] == '#': layout[irow][icol] = 1 # tường
            elif layout[irow][icol] == '@': layout[irow][icol] = 2 # người chơi
            elif layout[irow][icol] == '$': layout[irow][icol] = 3 # hộp
            elif layout[irow][icol] == '.': layout[irow][icol] = 4 # mục tiêu
            elif layout[irow][icol] == '*': layout[irow][icol] = 5 # hộp trên mục tiêu
            elif layout[irow][icol] == '+': layout[irow][icol] = 6 # người chơi trên mục tiêu
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([0 for _ in range(maxColsNum-colsNum)])  # Thêm khoảng trắng vào cột thiếu
    return np.array(layout)  # Trả về mảng NumPy

def PosOfPlayer(gameState):
    """Trả về vị trí của người chơi"""
    # Tìm vị trí của người chơi (2) hoặc người chơi trên mục tiêu (6)
    player_positions = np.argwhere((gameState == 2) | (gameState == 6))
    # Lấy vị trí đầu tiên (nếu có nhiều vị trí)
    player_position = player_positions[0]
    # Trả về vị trí dưới dạng tuple, ví dụ: (2, 2)
    return tuple(map(int, player_position))

def PosOfStones(gameState, weights):
    """Trả về vị trí của các hộp cùng với trọng số tương ứng"""
    # Tìm vị trí của các hộp (3) hoặc hộp trên mục tiêu (5)
    Stone_positions = [tuple(map(int, pos)) for pos in np.argwhere((gameState == 3) | (gameState == 5))]
    # Chuyển đổi từng vị trí từ np.int64 sang int và kết hợp với trọng số
    Stone_with_weights = []
    for index, pos in enumerate(Stone_positions):
        # Lấy trọng số tương ứng từ weights
        weight = weights[index] if index < len(weights) else 1  # Gán 1 nếu không đủ trọng số
        Stone_with_weights.append((tuple(map(int, pos)), weight))  # Thêm vị trí và trọng số vào danh sách

    # Chuyển đổi danh sách thành tuple
    return tuple(Stone_with_weights)

def PosOfWalls(gameState):
    """Trả về vị trí của các tường"""
    # Tìm vị trí của các tường (mã là 1)
    wall_positions = np.argwhere(gameState == 1)
    # Chuyển đổi từng vị trí thành tuple và trả về danh sách các vị trí
    return tuple(map(tuple, wall_positions))

def PosOfGoals(gameState):
    """Trả về vị trí của các mục tiêu"""
    # Tìm vị trí của các mục tiêu (4), hộp trên mục tiêu (5), và người chơi trên mục tiêu (6)
    goal_positions = np.argwhere((gameState == 4) | (gameState == 5) | (gameState == 6))
    # Chuyển đổi từng vị trí thành tuple và trả về danh sách các vị trí
    return tuple(map(tuple, goal_positions))

def isEndState(posStone):
    """Kiểm tra xem tất cả các hộp có nằm trên mục tiêu hay không (tức là đã thắng trò chơi)"""
    return sorted(posStone) == sorted(posGoals)  # So sánh vị trí của hộp với mục tiêu

def isLegalAction(action, posPlayer, posStone):
    """Kiểm tra xem hành động đã cho có hợp lệ hay không"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # nếu di chuyển là đẩy
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]  # Tính toán vị trí mới của hộp
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]  # Tính toán vị trí mới của người chơi
    return (x1, y1) not in posStone + posWalls  # Kiểm tra xem vị trí mới có nằm trong hộp hoặc tường không


def legalActions(posPlayer, posStone):
    """Trả về tất cả các hành động hợp lệ cho người chơi trong trạng thái trò chơi hiện tại"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'], [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]  # Tất cả các hành động có thể
    legalActions = []  # Danh sách chứa các hành động hợp lệ

    for dx, dy, move, push in allActions:
        new_pos = (posPlayer[0] + dx, posPlayer[1] + dy)  # Vị trí mới của người chơi
        if new_pos in posStone:
            # Nếu người chơi đẩy hộp
            action = (dx, dy, push)
        else:
            # Nếu người chơi chỉ di chuyển bình thường
            action = (dx, dy, move)
        # Kiểm tra xem hành động có hợp lệ hay không
        if isLegalAction(action, posPlayer, posStone):
            legalActions.append(action)  # Thêm hành động hợp lệ vào danh sách
    return tuple(legalActions)  # Ví dụ: ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posStone, action):
    """Trả về trạng thái trò chơi cập nhật sau khi thực hiện một hành động"""
    xPlayer, yPlayer = posPlayer  # Vị trí trước đó của người chơi
    newPosPlayer = (xPlayer + action[0], yPlayer + action[1])  # Vị trí hiện tại của người chơi
    posStone = list(posStone)  # Chuyển đổi tuple hộp thành danh sách để dễ dàng thao tác

    if action[-1].isupper():  # Nếu hành động là đẩy
        # Tính toán vị trí hộp mới
        newPosStone = (xPlayer + 2 * action[0], yPlayer + 2 * action[1])
        # Cập nhật vị trí hộp
        for i in range(len(posStone)):
            if posStone[i] == newPosPlayer:
                posStone[i] = newPosStone  # Cập nhật vị trí mới của hộp

    return newPosPlayer, tuple(posStone)  # Trả về vị trí mới của người chơi và danh sách hộp

def isFailed(posStone):
    """Kiểm tra xem trạng thái có thể thất bại hay không, sau đó cắt tỉa tìm kiếm"""
    # Các mẫu quay và lật
    rotatePattern = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [2, 5, 8, 1, 4, 7, 0, 3, 6],
        [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
        [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1]
    ]

    flipPattern = [
        [2, 1, 0, 5, 4, 3, 8, 7, 6],
        [0, 3, 6, 1, 4, 7, 2, 5, 8],
        [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
        [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1]
    ]

    allPatterns = rotatePattern + flipPattern

    for Stone in posStone:
        if Stone not in posGoals:  # Nếu hộp không nằm trên mục tiêu
            # Tạo danh sách các vị trí xung quanh hộp
            board = [(Stone[0] - 1, Stone[1] - 1), (Stone[0] - 1, Stone[1]), (Stone[0] - 1, Stone[1] + 1),
                     (Stone[0], Stone[1] - 1), (Stone[0], Stone[1]), (Stone[0], Stone[1] + 1),
                     (Stone[0] + 1, Stone[1] - 1), (Stone[0] + 1, Stone[1]), (Stone[0] + 1, Stone[1] + 1)]

            for pattern in allPatterns:
                newBoard = [board[i] for i in pattern]

                # Kiểm tra các điều kiện thất bại
                if ((newBoard[1] in posWalls and newBoard[5] in posWalls) |
                   (newBoard[1] in posStone and newBoard[2] in posWalls and newBoard[5] in posWalls) |
                   (newBoard[1] in posStone and newBoard[2] in posWalls and newBoard[5] in posStone) |
                   (newBoard[1] in posStone and newBoard[2] in posStone and newBoard[5] in posStone) |
                   (newBoard[1] in posStone and newBoard[6] in posStone and
                    newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls)):
                    return True
    return False

class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0

def cost(action, currentStonePos, newStonePos):
    """A cost function that computes the total cost based on actions"""
    # nếu action viết hoa thì + thêm weight
    # nếu không thì là 1
    if action[-1].islower():
        return 1
    else:
        positions = [item[0] for item in currentStonePos]
        for index in range(len(positions)):
            if positions[index] != newStonePos[index]:
                return index # trả về index của hộp bị đẩy
        return 1 + currentStonePos[index][1]  # Trả về weight của hộp bị đẩy

def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    # Tách phần số và ma trận
    weights = list(map(int, lines[0].strip().split()))  # Dòng đầu tiên là số
    layout = [line.rstrip(' ') for line in lines[1:]]  # Các dòng còn lại là ma trận
    return weights, layout


gameState=""
posWalls=""
posGoals=""
def Setup(path):
    global gameState, posWalls, posGoals,weights,layout
    weights, layout = parse_file(path)
    gameState = transferToGameState(layout)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)


