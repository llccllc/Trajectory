import os
from main2 import process_trajectory
from za.aemarkov import MarkovChainProcessor
from za.afdis import TrajectoryProcessor
from za.agsim import TrajectorySimulator

# 定义文件夹范围和网格大小列表
folder_range = range(1, 10)  # 处理文件夹 1 到 2
grid_sizes = [10, 20, 30, 40, 50]  # 网格大小列表

input_dir = '../output_taxi/'  # 输入文件夹路径

# 处理每个文件夹和网格大小
for file_index in folder_range:
    input_file_name = f'{file_index}_1.txt'

    # 检查输入文件是否存在
    input_file = os.path.join(input_dir, input_file_name)
    if not os.path.exists(input_file):
        print(f"输入文件 {input_file} 不存在，跳过该文件。")
        continue

    # 为每个文件创建单独的文件夹
    for n in grid_sizes:
        # 动态生成输出文件夹路径，带上当前网格数
        output_dir = f'../grid_output_taxi/{file_index}/grid{n}/'

        # 检查输出文件夹是否存在，不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"输出文件夹 {output_dir} 不存在，已自动创建。")

        # 输出文件名
        output_file_name = f'{file_index}_1_grid.txt'
        output_file = os.path.join(output_dir, output_file_name)

        # 保存每个网格的坐标到 11gridloca.txt 文件
        gridloca_file = os.path.join(output_dir, '11gridloca.txt')

        # 处理轨迹数据
        try:
            process_trajectory(input_file, output_file, n, gridloca_file)
            print(f"网格化处理完成，结果已保存至 {output_file}，网格坐标已保存至 {gridloca_file}")
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {e}")

# 实例化 MarkovChainProcessor 并处理每个网格大小
processor = MarkovChainProcessor()

for folder_idx in folder_range:
    for n in grid_sizes:
        input_file = f'../grid_output_taxi/{folder_idx}/grid{n}/{folder_idx}_1_grid.txt'
        output_file_05 = f'../grid_output_taxi/{folder_idx}/grid{n}/05first_order_markov'
        output_file_06 = f'../grid_output_taxi/{folder_idx}/grid{n}/06first_order_transition_counts'

        # 处理文件
        processor.process_files(input_file, output_file_05, output_file_06)

# 处理所有轨迹文件的路径并调用 TrajectoryProcessor
file_paths = [
    (
        f'../grid_output_taxi/{folder_idx}/grid{grid_size}/{folder_idx}_1_grid.txt',
        f'../grid_output_taxi/{folder_idx}/grid{grid_size}/07start',
        f'../grid_output_taxi/{folder_idx}/grid{grid_size}/08end',
        f'../grid_output_taxi/{folder_idx}/grid{grid_size}/09length'
    )
    for folder_idx in folder_range
    for grid_size in grid_sizes
]

processor = TrajectoryProcessor()
processor.process_all(file_paths)

# 调用 TrajectorySimulator 模拟轨迹
n = 10  # 轨迹条数倍数

for folder_idx in folder_range:
    try:
        print(f"正在处理文件夹 {folder_idx:03d} ...")

        for grid_size in grid_sizes:
            # 定义文件路径
            trajectory_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/{folder_idx}_1_grid.txt'
            initial_prob_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/07start'
            length_prob_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/09length'
            markov_chain_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/05first_order_markov'
            output_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/10simulation{n}'

            simulator = TrajectorySimulator(
                folder_idx, n, trajectory_file, initial_prob_file, length_prob_file, markov_chain_file, output_file
            )
            simulator.run_simulation()

    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
