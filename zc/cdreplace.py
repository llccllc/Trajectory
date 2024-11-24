import os
import random


def read_trajectory_file(file_path):
    trajectories = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                trajectory_id = parts[0]
                grid_coordinates = parts[1].strip()
                trajectories[trajectory_id] = grid_coordinates
    return trajectories


def extract_grid_coordinates(coordinates):
    return [tuple(map(int, coord.strip('()').split(','))) for coord in coordinates.split(')(')]


def read_grid_map(file_path):
    grid_map = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                grid_coord = tuple(map(int, parts[0].strip('() ').split(',')))
                grid_50_coords = parts[1].strip().split(')(')
                grid_map[grid_coord] = [tuple(map(int, coord.strip('()').split(','))) for coord in grid_50_coords]
    return grid_map


def read_probability_counts(file_path):
    counts = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                coord = tuple(map(int, parts[0].strip('()').split(',')))
                count = int(parts[1].strip())
                counts[coord] = count
    return counts


def manhattan_distance(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


# 循环处理文件
for i in range(1,64):
    print("Processing:", i)
    for grid_size in range(10, 41, 10):  # 从10到40的网格
        grid10_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/selected_trajectories.txt'
        grid_map_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/12gridmap.txt'
        counts_file_path = f'../grid_output_taxi/{i}/grid.txt'

        output_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/14gridmap_output.txt'  # 输出文件路径

        if os.path.exists(grid10_file_path) and os.path.exists(grid_map_file_path):
            # 读取轨迹和网格映射
            grid_10_trajectories = read_trajectory_file(grid10_file_path)
            grid_map = read_grid_map(grid_map_file_path)
            probability_counts = read_probability_counts(counts_file_path)

            with open(output_file_path, 'w') as output_file:  # 打开输出文件
                # 处理每个轨迹
                for trajectory_id, coords in grid_10_trajectories.items():
                    new_coords = []
                    prev_coord = None

                    #print(f"Processing trajectory ID: {trajectory_id}, coordinates: {coords}")

                    for coord in extract_grid_coordinates(coords):
                        # 查找当前坐标对应的 grid_50_coordinates
                        valid_grid_50 = grid_map.get(coord, [])
                        #print("valid_grid_50:", valid_grid_50)

                        # 计算当前 grid_50 的权重
                        weights = [probability_counts.get(g, 0) for g in valid_grid_50]
                        #print("weights:", weights)
                        #print("Sum of weights:", sum(weights))

                        if not new_coords:
                            # 第一个点从概率前5的 grid_50 中选择
                            if valid_grid_50:
                                top_indices = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)[:3]
                                top_coords = [valid_grid_50[i] for i in top_indices]
                                top_weights = [weights[i] for i in top_indices]
                                if top_weights and sum(top_weights) > 0:  # 确保权重有效
                                    random_coord = random.choices(top_coords, weights=top_weights, k=1)[0]
                                    new_coords.append(random_coord)
                                    prev_coord = random_coord
                        else:
                            # 确保新的坐标与前一个坐标的曼哈顿距离小于等于1
                            valid_coord_found = False
                            attempts = 0
                            while not valid_coord_found and attempts < 20:
                                if valid_grid_50 and sum(weights) > 0:  # 确保 valid_grid_50 和权重有效
                                    random_coord = random.choices(valid_grid_50, weights=weights, k=1)[0]
                                    if random_coord and manhattan_distance(prev_coord, random_coord) <= 1:
                                        new_coords.append(random_coord)
                                        prev_coord = random_coord
                                        valid_coord_found = True
                                attempts += 1

                            # 如果找不到有效的坐标，则直接随机选择一个
                            if not valid_coord_found:
                                if valid_grid_50 and sum(weights) > 0:  # 确保 valid_grid_50 和权重有效
                                    random_coord = random.choices(valid_grid_50, weights=weights, k=1)[0]
                                    if random_coord:
                                        new_coords.append(random_coord)
                                        prev_coord = random_coord

                    # 格式化新坐标字符串并写入输出文件
                    new_coords_str = ''.join(f"({c[0]},{c[1]})" for c in new_coords)
                    output_file.write(f"{trajectory_id}: {new_coords_str}\n")  # 写入文件
        else:
            print(f"文件未找到: {grid10_file_path} 或 {grid_map_file_path}")
