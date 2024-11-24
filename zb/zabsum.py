import os
from main2 import process_trajectory
from za.aemarkov import MarkovChainProcessor
from za.afdis import TrajectoryProcessor
from za.agsim import TrajectorySimulator

# 定义文件夹范围和网格大小列表
folder_range = range(7, 8)  # 处理文件夹 1 到 2
grid_sizes = [ 20]  # 网格大小列表

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
            output_file = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/10simulation'

            simulator = TrajectorySimulator(
                folder_idx, n, trajectory_file, initial_prob_file, length_prob_file, markov_chain_file, output_file
            )
            simulator.run_simulation()

    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
from zb.baselectandresult import TrajectoryAnalyzer
from zb.bbmodel import NeuralNetworkTrainer
from zb.bcpredict import ResultVectorPredictor
from zb.bdselectTrs import TrajectorySelector

# 定义文件夹范围和网格大小列表
folder_range = range(1, 1000)  # 文件夹范围
grid_sizes = [10,20,30,40,50]  # 网格大小列表

total_iterations = 500  # 用户输入的总迭代次数
iteration_step = 100  # 用户输入的每多少次迭代生成一个文件

analyzer = TrajectoryAnalyzer(total_iterations, iteration_step)

# 遍历文件夹和网格大小，调用 analyze 函数
for grid_size in grid_sizes:
    grid_version = f"grid{grid_size}"

    for folder_idx in folder_range:
        # 定义文件路径
        template_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/06first_order_transition_counts'
        simulation_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/10simulation'
        original_trajectory_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/{folder_idx}_1_grid.txt'
        output_folder = f'../grid_output_taxi/{folder_idx}/{grid_version}/sim/'

        # 调用 analyze 函数处理数据
        try:
            analyzer.analyze(template_file, simulation_file, original_trajectory_file, output_folder)
            print(f"分析完成，结果保存到 {output_folder}")
        except Exception as e:
            print(f"处理文件夹 {folder_idx} 的网格 {grid_size} 时出错: {e}")

        # NeuralNetworkTrainer 训练
        trainer = NeuralNetworkTrainer(folder_range, grid_size, epochs=200, batch_size=62, threshold=0.17)
        trainer.process_folders()

        # 定义模板路径并正确格式化
        model_path_template = '../grid_output_taxi/{folder_idx}/{grid_version}/sim/result_to_selection_mapping_model.h5'
        result_file_path_template = '../grid_output_taxi/{folder_idx}/{grid_version}/sim/sample/100_iterations.txt'
        output_file_path_template = '../grid_output_taxi/{folder_idx}/{grid_version}/sim/new_predicted_selection.txt'
        trajectory_file_path_template = '../grid_output_taxi/{folder_idx}/{grid_version}/{folder_idx}_1_grid.txt'

        # 实例化并处理文件夹
        predictor = ResultVectorPredictor(folder_range, fill_value=1, num_vectors_to_generate=1, threshold=0.17)

        # 传递 folder_idx 和 grid_version 参数
        predictor.process_folders(
            model_path_template.format(folder_idx=folder_idx, grid_version=grid_version),
            result_file_path_template.format(folder_idx=folder_idx, grid_version=grid_version),
            output_file_path_template.format(folder_idx=folder_idx, grid_version=grid_version),
            trajectory_file_path_template.format(folder_idx=folder_idx, grid_version=grid_version)
        )

        # 处理 TrajectorySelector
        predicted_file_template = '../grid_output_taxi/{folder_idx}/{grid_version}/sim/new_predicted_selection.txt'
        trajectory_file_template = '../grid_output_taxi/{folder_idx}/{grid_version}/10simulation'
        output_file_template = '../grid_output_taxi/{folder_idx}/{grid_version}/sim/selected_trajectories.txt'

        selector = TrajectorySelector(
            folder_range,
            predicted_file_template.format(folder_idx=folder_idx, grid_version=grid_version),
            trajectory_file_template.format(folder_idx=folder_idx, grid_version=grid_version),
            output_file_template.format(folder_idx=folder_idx, grid_version=grid_version)
        )

        # 调用 process_all_folders 并传递格式化后的文件路径
        selector.process_all_folders()
