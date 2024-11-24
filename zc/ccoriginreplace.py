import os
import random
from collections import Counter

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

def read_grid_50_coordinates(file_path):
    grid_50_coords = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                coords = parts[1].strip()
                coords_list = coords.replace(')', '').split('(')
                for coord in coords_list:
                    if coord:
                        grid_50_coords.append(tuple(map(int, coord.split(','))))
    return grid_50_coords

# 循环处理文件
for i in range(1,64):
    for grid_size in range(10, 41, 10):  # 从10到40的网格
        print("i",i,grid_size)
        grid10_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/selected_trajectories.txt'
        grid50_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/12gridmapselect.txt'
        output_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/13gridmap_origin_output.txt'

        if os.path.exists(grid10_file_path) and os.path.exists(grid50_file_path):
            # 读取网格坐标
            grid_10_trajectories = read_trajectory_file(grid10_file_path)
            grid_50_coordinates = read_grid_50_coordinates(grid50_file_path)

            # 将结果写入文件
            with open(output_file_path, 'w') as output_file:
                for trajectory_id, coords in grid_10_trajectories.items():
                    new_coords = []
                    for coord in extract_grid_coordinates(coords):
                        # 针对每个坐标随机选择 6 次
                        selected_coords = [random.choice(grid_50_coordinates) for _ in range(6)]
                        # 统计出现次数并选择概率最高的坐标
                        most_common_coord = Counter(selected_coords).most_common(1)[0][0]
                        new_coords.append(most_common_coord)

                    # 格式化新坐标字符串
                    new_coords_str = ''.join(f"({c[0]},{c[1]})" for c in new_coords)
                    output_file.write(f"{trajectory_id}: {new_coords_str}\n")
        else:
            print(f"文件未找到: {grid10_file_path} 或 {grid50_file_path}")
