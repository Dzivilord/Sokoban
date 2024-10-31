from sokoban import *

def ucs(path):
    """Implement uniformCostSearch approach with optimization"""
    number = re.findall(r'\d+', path)
    case = [int(num) for num in number]
    time_start = time.time()  # Thời gian bắt đầu
    Setup(path)
    weightList, layout = parse_file(path)

    # Vị trí bắt đầu của người chơi và các hộp
    beginStone = PosOfStones(gameState, weightList)
    beginPlayer = PosOfPlayer(gameState)

    # Trạng thái bắt đầu
    startState = (beginPlayer, tuple([item[0] for item in beginStone]))
    frontier = PriorityQueue()
    frontier.push((startState, 0), 0)  # (state, accumulated_cost), priority=accumulated_cost
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0)  # Đưa hành động 0 ban đầu vào hàng đợi

    node_count = 0
    cost_so_far = {startState: 0}

    while not frontier.isEmpty():
        # Pop the state with the lowest cost (priority)
        (currentPlayerPos, currentStonePos), current_cost = frontier.pop()
        node_action = actions.pop()
        node_count += 1

        # Kiểm tra xem đã đạt đến trạng thái kết thúc hay chưa
        if isEndState(currentStonePos):  # currentStonePos là vị trí của các hộp
            print(''.join(node_action[1:]))  # In các hành động đã thực hiện

            # Tính toán thời gian và bộ nhớ sử dụng
            end_time = time.time()
            elapsed_time = (end_time - time_start) * 1000  # Thời gian tính bằng mili giây
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Bộ nhớ tính bằng MB

            # In kết quả
            print(f'Steps: {len(node_action[1:])}, Total Weight: {current_cost}, Node: {node_count}, Time (ms): {elapsed_time:.2f}, Memory (MB): {memory_usage:.2f}')

            # Ghi kết quả vào file
            output_path = f'output/output-{str(case[0]).zfill(2)}.txt'
            with open(output_path, 'a') as file:
                file.write("Algorithms: UCS\n")
                file.write(f'Steps: {len(node_action[1:])}, ')
                file.write(f'Total Weight: {current_cost}, ')
                file.write(f'Node: {node_count}, ')
                file.write(f'Time (ms): {elapsed_time:.2f}, ')
                file.write(f'Memory (MB): {memory_usage:.2f}\n')
                file.write(f'Path: {''.join(node_action[1:])}\n\n')
            return ''.join(node_action[1:])  # Trả về chuỗi hành động đã thực hiện

        # Nếu trạng thái chưa được khám phá
        if (currentPlayerPos, currentStonePos) not in exploredSet:
            exploredSet.add((currentPlayerPos, currentStonePos))

            # Duyệt qua các hành động hợp lệ từ trạng thái hiện tại
            for action in legalActions(currentPlayerPos, currentStonePos):  # currentPlayerPos là vị trí người chơi, currentStonePos là các hộp
                newPosPlayer, newPosStone = updateState(currentPlayerPos, currentStonePos, action)

                # Bỏ qua trạng thái không hợp lệ
                if isFailed(newPosStone):
                    continue

                # Tính toán chi phí mới
                # Xác định hộp nào đang được đẩy để thêm trọng số của nó vào new_cost
                if action[-1].isupper():  # Nếu hành động là đẩy
                    # Tìm vị trí hộp mới
                    pushed_Stone_index = None
                    for index, Stone_pos in enumerate(currentStonePos):
                        if Stone_pos != newPosStone[index]:
                            pushed_Stone_index = index
                            break
                    if pushed_Stone_index is not None:
                        new_cost = current_cost + weightList[pushed_Stone_index]
                    else:
                        new_cost = current_cost + 1  # Trường hợp không tìm thấy hộp bị đẩy
                else:
                    new_cost = current_cost + 1  # Nếu hành động không phải là đẩy, chi phí là 1

                new_state = (newPosPlayer, newPosStone)
                # Chỉ thêm trạng thái mới vào hàng đợi nếu chi phí mới nhỏ hơn chi phí trước đó
                if new_state not in cost_so_far or new_cost < cost_so_far[new_state]:
                    cost_so_far[new_state] = new_cost
                    frontier.push((new_state, new_cost), new_cost)
                    actions.push(node_action + [action[-1]], new_cost)