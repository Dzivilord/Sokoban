import sys
import collections
import numpy as np
import time
import psutil
import os
import heapq
import re
import math
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

def PosOfBoxes(gameState, weights):
    """Trả về vị trí của các hộp cùng với trọng số tương ứng"""
    # Tìm vị trí của các hộp (3) hoặc hộp trên mục tiêu (5)
    box_positions = [tuple(map(int, pos)) for pos in np.argwhere((gameState == 3) | (gameState == 5))]
    # Chuyển đổi từng vị trí từ np.int64 sang int và kết hợp với trọng số
    box_with_weights = []
    for index, pos in enumerate(box_positions):
        # Lấy trọng số tương ứng từ weights
        weight = weights[index] if index < len(weights) else 1  # Gán 1 nếu không đủ trọng số
        box_with_weights.append((tuple(map(int, pos)), weight))  # Thêm vị trí và trọng số vào danh sách

    # Chuyển đổi danh sách thành tuple
    return tuple(box_with_weights)

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

def isEndState(posBox):
    """Kiểm tra xem tất cả các hộp có nằm trên mục tiêu hay không (tức là đã thắng trò chơi)"""
    return sorted(posBox) == sorted(posGoals)  # So sánh vị trí của hộp với mục tiêu

def isLegalAction(action, posPlayer, posBox):
    """Kiểm tra xem hành động đã cho có hợp lệ hay không"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # nếu di chuyển là đẩy
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]  # Tính toán vị trí mới của hộp
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]  # Tính toán vị trí mới của người chơi
    return (x1, y1) not in posBox + posWalls  # Kiểm tra xem vị trí mới có nằm trong hộp hoặc tường không


def legalActions(posPlayer, posBox):
    """Trả về tất cả các hành động hợp lệ cho người chơi trong trạng thái trò chơi hiện tại"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'], [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]  # Tất cả các hành động có thể
    legalActions = []  # Danh sách chứa các hành động hợp lệ

    for dx, dy, move, push in allActions:
        new_pos = (posPlayer[0] + dx, posPlayer[1] + dy)  # Vị trí mới của người chơi
        if new_pos in posBox:
            # Nếu người chơi đẩy hộp
            action = (dx, dy, push)
        else:
            # Nếu người chơi chỉ di chuyển bình thường
            action = (dx, dy, move)
        # Kiểm tra xem hành động có hợp lệ hay không
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)  # Thêm hành động hợp lệ vào danh sách
    return tuple(legalActions)  # Ví dụ: ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posBox, action):
    """Trả về trạng thái trò chơi cập nhật sau khi thực hiện một hành động"""
    xPlayer, yPlayer = posPlayer  # Vị trí trước đó của người chơi
    newPosPlayer = (xPlayer + action[0], yPlayer + action[1])  # Vị trí hiện tại của người chơi
    posBox = list(posBox)  # Chuyển đổi tuple hộp thành danh sách để dễ dàng thao tác

    if action[-1].isupper():  # Nếu hành động là đẩy
        # Tính toán vị trí hộp mới
        newPosBox = (xPlayer + 2 * action[0], yPlayer + 2 * action[1])
        # Cập nhật vị trí hộp
        for i in range(len(posBox)):
            if posBox[i] == newPosPlayer:
                posBox[i] = newPosBox  # Cập nhật vị trí mới của hộp

    return newPosPlayer, tuple(posBox)  # Trả về vị trí mới của người chơi và danh sách hộp

def isFailed(posBox):
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

    for box in posBox:
        if box not in posGoals:  # Nếu hộp không nằm trên mục tiêu
            # Tạo danh sách các vị trí xung quanh hộp
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                     (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1),
                     (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]

            for pattern in allPatterns:
                newBoard = [board[i] for i in pattern]

                # Kiểm tra các điều kiện thất bại
                if ((newBoard[1] in posWalls and newBoard[5] in posWalls) |
                   (newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls) |
                   (newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox) |
                   (newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox) |
                   (newBoard[1] in posBox and newBoard[6] in posBox and
                    newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls)):
                    return True
    return False


"""Implement all approcahes"""

def bfs(path):
    """Thuật toán tìm kiếm theo chiều rộng"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    Setup(path)

    # Thời gian bắt đầu
    time_start = time.time()
    weightList, layout = parse_file(path)

    # Vị trí bắt đầu của người chơi và các hộp
    beginBox = PosOfBoxes(gameState, weightList)
    checkPointBox = list(beginBox)  # Chuyển đổi thành danh sách để có thể sửa đổi

    beginPlayer = PosOfPlayer(gameState)

    # Danh sách để lưu trữ các vị trí
    positions = [item[0] for item in beginBox]  # Sử dụng list comprehension

    # Chuyển danh sách thành tuple
    positions = tuple(positions)  # Của đá

    # Trạng thái bắt đầu
    startState = (beginPlayer, positions)

    # Khởi tạo hàng đợi cho trạng thái và hành động
    frontier = collections.deque([[startState]])
    actions = collections.deque([[0]])

    # Tập hợp trạng thái đã khám phá và biến đếm số nút đã truy cập
    exploredSet = set()
    node_count = 0

    while frontier:  # Khi còn trạng thái trong hàng đợi
        node = frontier.popleft()  # Lấy trạng thái hiện tại
        node_action = actions.popleft()  # Lấy hành động tương ứng
        node_count += 1  # Tăng số nút đã truy cập

        # Kiểm tra nếu trạng thái hiện tại là trạng thái kết thúc
        if isEndState(node[-1][-1]):
            print(''.join(node_action[1:]))  # In hành động đã thực hiện

            tmpFirst = 0
            tmpSecond = 0
            totalWeight = 0

            for item in node:
                # Danh sách để lưu trữ các vị trí
                positionCheck = [item[0] for item in checkPointBox]  # Sử dụng list comprehension

                # Tìm tmpFirst
                for index, weight in checkPointBox:
                    if index not in item[1]:
                        tmpFirst = index

                # Tìm tmpSecond
                for index in item[1]:
                    if index not in positionCheck:
                        tmpSecond = index

                # Cập nhật checkPointBox
                for idx, cp_item in enumerate(checkPointBox):
                    if (tmpFirst == cp_item[0]):
                        totalWeight += cp_item[1]
                        # Tạo một tuple mới với giá trị đã thay đổi
                        checkPointBox[idx] = (tmpSecond, cp_item[1])  # Cập nhật trong danh sách

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB

            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {totalWeight}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{case}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: BFS\n")
                file.write(f'Path: {''.join(node_action[1:])}\n')
                file.write(f'Steps: {len(node_action[1:])}\n')
                file.write(f'Total Weight: {totalWeight}\n')
                file.write(f'Node: {node_count}\n')
                file.write(f'Time (ms): {elapsed_time:.2f}\n')
                file.write(f'Memory (MB): {memory_usage:.2f}\n\n')
            return ''.join(node_action[1:])  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái hiện tại chưa được khám phá
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])  # Thêm vào tập đã thăm

            # Lấy tất cả hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(node[-1][0], node[-1][1]): #Người, Box
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)  # Cập nhật vị trí mới

                # Kiểm tra tính hợp lệ của vị trí hộp mới
                if isFailed(newPosBox):
                    continue  # Nếu không hợp lệ, bỏ qua

                # Thêm trạng thái mới vào hàng đợi
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])  # Lưu hành động tương ứng
                weights.append(0)  # Cập nhật khối lượng mới khi hộp được di chuyển

def dfs(path):
    """Thuật toán tìm kiếm theo chiều sâu"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    # Thời gian bắt đầu
    Setup(path)
    time_start = time.time()
    weightList, layout = parse_file(path)

    # Vị trí bắt đầu của người chơi và các hộp
    beginBox = PosOfBoxes(gameState, weightList)
    checkPointBox = list(beginBox)  # Chuyển đổi thành danh sách để có thể sửa đổi

    beginPlayer = PosOfPlayer(gameState)

    # Danh sách để lưu trữ các vị trí
    positions = [item[0] for item in beginBox]  # Sử dụng list comprehension

    # Chuyển danh sách thành tuple
    positions = tuple(positions)  # Của đá

    # Trạng thái bắt đầu
    startState = (beginPlayer, positions)
    # Khởi tạo ngăn xếp cho trạng thái và hành động
    frontier = collections.deque([[startState]])
    actions = collections.deque([[0]])
    # Tập hợp trạng thái đã khám phá và biến đếm số nút đã truy cập
    exploredSet = set()
    node_count = 0

    while frontier:  # Khi còn trạng thái trong ngăn xếp
        node = frontier.pop()  # Lấy trạng thái hiện tại
        node_action = actions.pop()  # Lấy hành động tương ứng
        node_count += 1  # Tăng số nút đã truy cập

        # Kiểm tra nếu trạng thái hiện tại là trạng thái kết thúc
        if isEndState(node[-1][-1]):
            print(''.join(node_action[1:]))  # In hành động đã thực hiện

            tmpFirst = 0
            tmpSecond = 0
            totalWeight = 0

            for item in node:
                # Danh sách để lưu trữ các vị trí
                positionCheck = [item[0] for item in checkPointBox]  # Sử dụng list comprehension

                # Tìm tmpFirst
                for index, weight in checkPointBox:
                    if index not in item[1]:
                        tmpFirst = index

                # Tìm tmpSecond
                for index in item[1]:
                    if index not in positionCheck:
                        tmpSecond = index

                # Cập nhật checkPointBox
                for idx, cp_item in enumerate(checkPointBox):
                    if (tmpFirst == cp_item[0]):
                        totalWeight += cp_item[1]
                        # Tạo một tuple mới với giá trị đã thay đổi
                        checkPointBox[idx] = (tmpSecond, cp_item[1])  # Cập nhật trong danh sách

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB

            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {totalWeight}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{case}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: DFS\n")
                file.write(f'Path: {''.join(node_action[1:])}\n')
                file.write(f'Steps: {len(node_action[1:])}\n')
                file.write(f'Total Weight: {totalWeight}\n')
                file.write(f'Node: {node_count}\n')
                file.write(f'Time (ms): {elapsed_time:.2f}\n')
                file.write(f'Memory (MB): {memory_usage:.2f}\n\n')
            return ''.join(node_action[1:])  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái hiện tại chưa được khám phá
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])  # Thêm vào tập đã thăm

            # Lấy tất cả hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(node[-1][0], node[-1][1]): #Người, Box
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)  # Cập nhật vị trí mới

                # Kiểm tra tính hợp lệ của vị trí hộp mới
                if isFailed(newPosBox):
                    continue  # Nếu không hợp lệ, bỏ qua

                # Thêm trạng thái mới vào ngăn xếp
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])  # Lưu hành động tương ứng
                weights.append(0)  # Cập nhật khối lượng mới khi hộp được di chuyển

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

def cost(action, currentBoxPos, newBoxPos):
    """A cost function that computes the total cost based on actions"""
    # nếu action viết hoa thì + thêm weight
    # nếu không thì là 1
    if action[-1].islower():
        return 1
    else:
        positions = [item[0] for item in currentBoxPos]
        for index in range(len(positions)):
            if positions[index] != newBoxPos[index]:
                return index # trả về index của hộp bị đẩy
        return 1 + currentBoxPos[index][1]  # Trả về weight của hộp bị đẩy

def ucs(path):
    """Implement uniformCostSearch approach with optimization"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    time_start = time.time()  # Thời gian bắt đầu
    Setup(path)
    weightList, layout = parse_file(path)

    # Vị trí bắt đầu của người chơi và các hộp
    beginBox = PosOfBoxes(gameState, weightList)
    beginPlayer = PosOfPlayer(gameState)

    # Trạng thái bắt đầu
    startState = (beginPlayer, tuple([item[0] for item in beginBox]))
    frontier = PriorityQueue()
    frontier.push((startState, 0), 0)  # (state, accumulated_cost), priority=accumulated_cost
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0)  # Đưa hành động 0 ban đầu vào hàng đợi

    node_count = 0
    cost_so_far = {startState: 0}

    while not frontier.isEmpty():
        # Pop the state with the lowest cost (priority)
        (currentPlayerPos, currentBoxPos), current_cost = frontier.pop()
        node_action = actions.pop()
        node_count += 1

        # Kiểm tra xem đã đạt đến trạng thái kết thúc hay chưa
        if isEndState(currentBoxPos):  # currentBoxPos là vị trí của các hộp
            print(''.join(node_action[1:]))  # In các hành động đã thực hiện

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB

            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {current_cost}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{case}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: UCS\n")
                file.write(f'Path: {''.join(node_action[1:])}\n')
                file.write(f'Steps: {len(node_action[1:])}\n')
                file.write(f'Total Weight: {current_cost}\n')
                file.write(f'Node: {node_count}\n')
                file.write(f'Time (ms): {elapsed_time:.2f}\n')
                file.write(f'Memory (MB): {memory_usage:.2f}\n\n')
            return ''.join(node_action[1:])  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái chưa được khám phá
        if (currentPlayerPos, currentBoxPos) not in exploredSet:
            exploredSet.add((currentPlayerPos, currentBoxPos))

            # Duyệt qua các hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(currentPlayerPos, currentBoxPos):  # currentPlayerPos là vị trí người chơi, currentBoxPos là các hộp
                newPosPlayer, newPosBox = updateState(currentPlayerPos, currentBoxPos, action)

                # Bỏ qua trạng thái không hợp lệ
                if isFailed(newPosBox):
                    continue

                # Tính toán chi phí mới
                # Xác định hộp nào đang được đẩy để thêm trọng số của nó vào new_cost
                if action[-1].isupper():  # Nếu hành động là đẩy
                    # Tìm vị trí hộp mới
                    pushed_box_index = None
                    for index, box_pos in enumerate(currentBoxPos):
                        if box_pos != newPosBox[index]:
                            pushed_box_index = index
                            break
                    if pushed_box_index is not None:
                        new_cost = current_cost + weightList[pushed_box_index]
                    else:
                        new_cost = current_cost + 1  # Trường hợp không tìm thấy hộp bị đẩy
                else:
                    new_cost = current_cost + 1  # Nếu hành động không phải là đẩy, chi phí là 1

                new_state = (newPosPlayer, newPosBox)
                # Chỉ thêm trạng thái mới vào hàng đợi nếu chi phí mới nhỏ hơn chi phí trước đó
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    frontier.push((new_state, new_cost), new_cost)
                    actions.push(node_action + [action[-1]], new_cost)

def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    # Tách phần số và ma trận
    weights = list(map(int, lines[0].strip().split()))  # Dòng đầu tiên là số
    layout = [line.strip() for line in lines[1:]]  # Các dòng còn lại là ma trận
    return weights, layout


def heuristic(posPlayer, posBox):
    """Heuristic function for A* search"""
    # Tính tổng khoảng cách Manhattan từ mỗi hộp đến mục tiêu gần nhất
    total_distance = 0
    for box in posBox:
        min_distance = float('inf')
        for goal in posGoals:
            distance = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            if distance < min_distance:
                min_distance = distance
        total_distance += min_distance
    return total_distance

def astar(path):
    """Implement A* search approach with optimization to push only when current cost is less than previous cost"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    time_start = time.time()  # Thời gian bắt đầu
    Setup(path)
    weightList, layout = parse_file(path)

    # Vị trí bắt đầu của người chơi và các hộp
    beginBox = PosOfBoxes(gameState, weightList)
    beginPlayer = PosOfPlayer(gameState)

    # Trạng thái bắt đầu
    startState = (beginPlayer, tuple([item[0] for item in beginBox]))
    frontier = PriorityQueue()
    frontier.push((startState, 0), 0 + heuristic(beginPlayer, [item[0] for item in beginBox]))  # (state, accumulated_cost), priority=accumulated_cost + heuristic
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0)  # Đưa hành động 0 ban đầu vào hàng đợi

    node_count = 0
    cost_so_far = {startState: 0}

    while not frontier.isEmpty():
        # Pop the state with the lowest cost (priority)
        (currentPlayerPos, currentBoxPos), current_cost = frontier.pop()
        node_action = actions.pop()
        node_count += 1

        # Kiểm tra xem đã đạt đến trạng thái kết thúc hay chưa
        if isEndState(currentBoxPos):  # currentBoxPos là vị trí của các hộp
            print(''.join(node_action[1:]))  # In các hành động đã thực hiện

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB
            steps = ''.join(node_action[1:])
            non_push_steps = sum(1 for step in steps if step.islower())
            pushed_weight = current_cost - non_push_steps
            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {pushed_weight}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{case}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: A*\n")
                file.write(f'Path: {steps}\n')
                file.write(f'Steps: {len(node_action[1:])}\n')
                file.write(f'Total Weight: {pushed_weight}\n')
                file.write(f'Node: {node_count}\n')
                file.write(f'Time (ms): {elapsed_time:.2f}\n')
                file.write(f'Memory (MB): {memory_usage:.2f}\n\n')
            return steps  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái chưa được khám phá
        if (currentPlayerPos, currentBoxPos) not in exploredSet:
            exploredSet.add((currentPlayerPos, currentBoxPos))

            # Duyệt qua các hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(currentPlayerPos, currentBoxPos):  # currentPlayerPos là vị trí người chơi, currentBoxPos là các hộp
                newPosPlayer, newPosBox = updateState(currentPlayerPos, currentBoxPos, action)

                # Bỏ qua trạng thái không hợp lệ
                if isFailed(newPosBox):
                    continue

                # Tính toán chi phí mới
                if action[-1].isupper():  # Nếu hành động là đẩy
                    pushed_box_index = None
                    for index, box_pos in enumerate(currentBoxPos):
                        if box_pos != newPosBox[index]:
                            pushed_box_index = index
                            break
                    if pushed_box_index is not None:
                        new_cost = current_cost + weightList[pushed_box_index]
                    else:
                        new_cost = current_cost + 1  # Trường hợp không tìm thấy hộp bị đẩy
                else:
                    new_cost = current_cost + 1  # Nếu hành động không phải là đẩy, chi phí là 1

                # Chỉ thêm trạng thái mới vào hàng đợi nếu chi phí mới nhỏ hơn chi phí trước đó
                new_state = (newPosPlayer, newPosBox)
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    priority = new_cost + heuristic(newPosPlayer, newPosBox)
                    frontier.push((new_state, new_cost), priority)
                    actions.push(node_action + [action[-1]], priority)

gameState=""
posWalls=""
posGoals=""
def Setup(path):
    global gameState, posWalls, posGoals,weights,layout
    weights, layout = parse_file(path)
    gameState = transferToGameState(layout)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)


