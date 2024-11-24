import os

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

def map_grid_10_to_grid_50(grid_10, grid_50):
    mapping = {}
    for trajectory_id in grid_10.keys():
        coords_10 = extract_grid_coordinates(grid_10[trajectory_id])
        coords_50 = extract_grid_coordinates(grid_50[trajectory_id])

        for coord_10 in coords_10:
            if coord_10 not in mapping:
                mapping[coord_10] = set()  # 使用集合避免重复
            mapping[coord_10].update(coords_50)  # 添加到集合中以确保唯一性

    return mapping

# 处理不同文件集
for i in range(1, 64):
    print("处理文件集:", i)
    for grid_size in [10, 20, 30, 40]:
        grid10_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/{i}_1_grid.txt'
        grid50_file_path = f'../grid_output_taxi/{i}/grid50/{i}_1_grid.txt'
        output_file_path = f'../grid_output_taxi/{i}/grid{grid_size}/12gridmap.txt'

        if os.path.exists(grid10_file_path) and os.path.exists(grid50_file_path):
            grid_10_trajectories = read_trajectory_file(grid10_file_path)
            grid_50_trajectories = read_trajectory_file(grid50_file_path)

            grid_mapping = map_grid_10_to_grid_50(grid_10_trajectories, grid_50_trajectories)

            # 将结果写入文件
            with open(output_file_path, 'w') as output_file:
                for grid_10, grid_50_set in grid_mapping.items():
                    grid_50_str = ''.join(f"({c[0]},{c[1]})" for c in sorted(grid_50_set))  # 确保唯一并排序
                    output_file.write(f"{grid_10}: {grid_50_str}\n")
        else:
            print(f"文件未找到: {grid10_file_path} 或 {grid50_file_path}")
