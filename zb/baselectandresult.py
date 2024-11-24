import re
import random
import numpy as np
import os
import time

class TrajectoryAnalyzer:
    def __init__(self, total_iterations, iteration_step):
        """
        初始化 TrajectoryAnalyzer 类
        :param total_iterations: 总的迭代次数
        :param iteration_step: 每多少次迭代生成一个文件
        """
        self.total_iterations = total_iterations
        self.iteration_step = iteration_step

    def analyze(self, template_file, simulation_file, original_trajectory_file, output_folder):
        """
        分析轨迹文件并保存结果
        :param template_file: 模板文件路径
        :param simulation_file: 模拟轨迹文件路径
        :param original_trajectory_file: 原始轨迹文件路径
        :param output_folder: 输出文件夹路径
        """
        # Step 0: 检查文件是否存在
        if not os.path.exists(template_file) or os.path.getsize(template_file) == 0:
            print(f"文件 {template_file} 不存在或为空，跳过处理。")
            return

        if not os.path.exists(simulation_file) or os.path.getsize(simulation_file) == 0:
            print(f"文件 {simulation_file} 不存在或为空，跳过处理。")
            return

        if not os.path.exists(original_trajectory_file) or os.path.getsize(original_trajectory_file) == 0:
            print(f"文件 {original_trajectory_file} 不存在或为空，跳过处理。")
            return

        start_time = time.time()  # 开始计时

        # 确保输出文件目录存在
        os.makedirs(output_folder, exist_ok=True)

        # 初始化模板数据和转移次数
        transitions, result_vector = [], []
        pattern_template = re.compile(r'\(\((\d+),(\d+)\)\((\d+),(\d+)\)\)\s+(\d+)')

        # Step 1: 读取模板文件
        with open(template_file, 'r') as file:
            for line in file:
                match = pattern_template.match(line.strip())
                if match:
                    x1, y1, x2, y2, count = match.groups()
                    transitions.append(((int(x1), int(y1)), (int(x2), int(y2))))
                    result_vector.append(int(count))

        # Step 2: 读取原始轨迹文件
        original_trajectories = []
        with open(original_trajectory_file, 'r') as file:
            for line in file:
                original_trajectories.append(line.strip())

        # Step 3: 读取模拟文件的轨迹
        generated_trajectories = []
        with open(simulation_file, 'r') as file:
            for line in file:
                generated_trajectories.append(line.strip())

        total_generated = len(generated_trajectories)

        # Step 5: 初始化两个向量
        result_vector_np = np.array(result_vector)

        # 新增矩阵，用来保存所有轨迹的转移次数
        trajectory_matrix = []

        # Step 6: 生成迭代数据
        all_results = []

        for iteration in range(self.total_iterations):
            total_simulated_vector = [0] * len(result_vector)
            cumulative_selected_vector = [0] * len(result_vector)

            selected_indices = random.sample(range(total_generated), int(len(original_trajectories) * 1))
            selection_vector = [1 if i in selected_indices else 0 for i in range(total_generated)]
            selection_vector_np = np.array(selection_vector)

            pattern_simulation = re.compile(r'\((\d+),(\d+)\)')
            transition_index_map = {transition: idx for idx, transition in enumerate(transitions)}

            with open(simulation_file, 'r') as file:
                for line_index, line in enumerate(file):
                    traj_name, traj_data = line.strip().split(':')
                    trajectory_vector = [0] * len(result_vector)
                    match = pattern_simulation.findall(traj_data)

                    for i in range(len(match) - 1):
                        prev_state = (int(match[i][0]), int(match[i][1]))
                        next_state = (int(match[i + 1][0]), int(match[i + 1][1]))
                        transition = (prev_state, next_state)

                        if transition in transition_index_map:
                            idx = transition_index_map[transition]
                            trajectory_vector[idx] += 1

                    trajectory_matrix.append(trajectory_vector)

                    total_simulated_vector = [total_simulated_vector[i] + trajectory_vector[i] for i in
                                              range(len(total_simulated_vector))]

                    if selection_vector[line_index] == 1:
                        cumulative_selected_vector = [cumulative_selected_vector[i] + trajectory_vector[i] for i in
                                                      range(len(cumulative_selected_vector))]
            cumulative_selected_vector_np = np.array(cumulative_selected_vector)
            diff_np = abs(cumulative_selected_vector_np - result_vector_np)
            cumulative_selected_vector_np[cumulative_selected_vector_np != 0] = 1

            result = cumulative_selected_vector_np

            all_results.append({
                'iteration': iteration + 1,
                'selection_vector': selection_vector_np.tolist(),
                'result_vector': result.tolist(),
                'diff_vector': diff_np.tolist()
            })

        # Step 7: 按指定范围将数据写入文件
        sample_folder = os.path.join(output_folder, "sample")
        os.makedirs(sample_folder, exist_ok=True)

        for step in range(1, self.total_iterations // self.iteration_step + 1):
            iteration_count = step * self.iteration_step
            output_file = os.path.join(sample_folder, f"{iteration_count}_iterations.txt")

            with open(output_file, 'w') as out_file:
                for result in all_results[:iteration_count]:
                    out_file.write(f"Iteration {result['iteration']}\n")
                    out_file.write(f"Selection Vector: {result['selection_vector']}\n")
                    out_file.write(f"Result Vector: {result['result_vector']}\n")
                    out_file.write(f"Diff Vector: {result['diff_vector']}\n\n")

        print(f"文件夹 处理完成: {output_folder}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"文件夹 总用时: {elapsed_time:.2f} 秒")


if __name__ == "__main__":
    total_start_time = time.time()  # 开始计时

    folder_range = range(1,501)
    total_iterations = 500  # 用户输入的总迭代次数
    iteration_step = 100  # 用户输入的每多少次迭代生成一个文件

    analyzer = TrajectoryAnalyzer(total_iterations, iteration_step)
    grid_sizes = [10,20,30,40, 50]  # 网格大小列表

    # 遍历每个 grid_size 和 folder_idx
    for grid_size in grid_sizes:
        grid_version = f"grid{grid_size}"
        for folder_idx in folder_range:
            template_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/06first_order_transition_counts'
            simulation_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/10simulation'
            original_trajectory_file = f'../grid_output_taxi/{folder_idx}/{grid_version}/{folder_idx}_1_grid.txt'
            output_folder = f'../grid_output_taxi/{folder_idx}/{grid_version}/sim/'

            analyzer.analyze(template_file, simulation_file, original_trajectory_file, output_folder)

    total_end_time = time.time()  # 结束计时
    total_elapsed_time = total_end_time - total_start_time
    print(f"所有文件夹处理完成，总用时: {total_elapsed_time:.2f} 秒")
