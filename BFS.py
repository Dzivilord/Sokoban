import re
import collections
import time
import psutil
import os

from sokoban import *

def bfs(path):
    """Thuật toán tìm kiếm theo chiều rộng"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    Setup(path)

    # Thời gian bắt đầu
    time_start = time.time()
    weightList, layout = parse_file(path)

    gameState = transferToGameState(layout)
    
    # Vị trí bắt đầu của người chơi và các hộp
    beginStone = PosOfStones(gameState, weightList)
    checkPointStone = list(beginStone)  # Chuyển đổi thành danh sách để có thể sửa đổi

    beginPlayer = PosOfPlayer(gameState)

    # Danh sách để lưu trữ các vị trí
    positions = [item[0] for item in beginStone]  # Sử dụng list comprehension

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
                positionCheck = [item[0] for item in checkPointStone]  # Sử dụng list comprehension

                # Tìm tmpFirst
                for index, weight in checkPointStone:
                    if index not in item[1]:
                        tmpFirst = index

                # Tìm tmpSecond
                for index in item[1]:
                    if index not in positionCheck:
                        tmpSecond = index

                # Cập nhật checkPointStone
                for idx, cp_item in enumerate(checkPointStone):
                    if (tmpFirst == cp_item[0]):
                        totalWeight += cp_item[1]
                        # Tạo một tuple mới với giá trị đã thay đổi
                        checkPointStone[idx] = (tmpSecond, cp_item[1])  # Cập nhật trong danh sách

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB

            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {totalWeight}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{str(case[0]).zfill(2)}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: BFS\n")
                file.write( f'Steps: {len(node_action[1:])}, ') 
                file.write(f'Total Weight: {totalWeight}, ')
                file.write(f'Node: {node_count}, ')
                file.write(f'Time (ms): {elapsed_time:.2f}, ')
                file.write(f'Memory (MB): {memory_usage:.2f}\n')
                file.write(f'Path: {''.join(node_action[1:])}\n\n')
            return ''.join(node_action[1:])  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái hiện tại chưa được khám phá
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])  # Thêm vào tập đã thăm

            # Lấy tất cả hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(node[-1][0], node[-1][1]): #Người, Stone
                newPosPlayer, newPosStone = updateState(node[-1][0], node[-1][1], action)  # Cập nhật vị trí mới

                # Kiểm tra tính hợp lệ của vị trí hộp mới
                if isFailed(newPosStone):
                    continue  # Nếu không hợp lệ, bỏ qua

                # Thêm trạng thái mới vào hàng đợi
                frontier.append(node + [(newPosPlayer, newPosStone)])
                actions.append(node_action + [action[-1]])  # Lưu hành động tương ứng
                weightList.append(0)  # Cập nhật khối lượng mới khi hộp được di chuyển