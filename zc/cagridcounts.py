from collections import defaultdict
import os

# 遍历文件
for i in range(1, 501):
    grid_counts = defaultdict(int)  # 创建一个新的字典以存储当前文件的 counts
    file_path = f'../grid_output_taxi/{i}/grid50/selected_trajectories.txt'

    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取轨迹数据
        with open(file_path, 'r') as file:
            for line in file:
                # 提取轨迹中的坐标
                coordinates = line.split(':')[1].strip().split(')(')
                for coord in coordinates:
                    # 清理坐标格式
                    coord = coord.replace('(', '').replace(')', '')
                    grid_counts[coord] += 1

        # 保存结果到新文件
        output_path = f'../grid_output_taxi/{i}/grid.txt'
        with open(output_path, 'w') as output_file:
            for grid, count in grid_counts.items():
                output_file.write(f"({grid}): {count}\n")
    else:
        print(f"文件不存在: {file_path}")
