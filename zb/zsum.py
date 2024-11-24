from zb.baselectandresult import TrajectoryAnalyzer
from zb.bbmodel import NeuralNetworkTrainer
from zb.bcpredict import ResultVectorPredictor
from zb.bdselectTrs import TrajectorySelector

# 定义文件夹范围和网格大小列表
folder_range = range(88, 100)  # 文件夹范围
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
