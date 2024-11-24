import os
import re

class TrajectorySelector:
    def __init__(self, predicted_file_path, trajectory_file_path, output_file_path):
        """
        初始化 TrajectorySelector 类
        :param predicted_file_path: 预测结果文件的路径
        :param trajectory_file_path: 轨迹文件的路径
        :param output_file_path: 输出文件的路径
        """
        self.predicted_file_path = predicted_file_path
        self.trajectory_file_path = trajectory_file_path
        self.output_file_path = output_file_path

    def process_folder(self):
        """
        处理单个文件夹中的预测文件和轨迹文件，选择所有预测为1的轨迹并保存。
        """
        # 检查文件是否存在
        if not os.path.exists(self.predicted_file_path):
            print(f"Predicted file {self.predicted_file_path} 不存在，跳过。")
            return
        if not os.path.exists(self.trajectory_file_path):
            print(f"Trajectory file {self.trajectory_file_path} 不存在，跳过。")
            return

        predicted_vectors = []
        selected_trajectories = []

        # Step 1: 读取Predicted向量
        with open(self.predicted_file_path, 'r') as file:
            for line in file:
                if line.startswith("Predicted:"):
                    vector_str = line.strip().split(": ")[1]
                    vector = list(map(int, vector_str.strip('[]').split(', ')))
                    predicted_vectors.append(vector)

        # Step 2: 打开轨迹文件，逐行读取轨迹
        with open(self.trajectory_file_path, 'r') as trajectory_file:
            all_trajectories = trajectory_file.readlines()

        # Step 3: 根据Predicted向量的"1"选取轨迹
        for vector in predicted_vectors:
            selected_trajectories.extend(
                [all_trajectories[i] for i, value in enumerate(vector) if value == 1]
            )

        # 将选中的轨迹写入输出文件
        with open(self.output_file_path, 'w') as output_file:
            for trajectory in selected_trajectories:
                output_file.write(f"{trajectory.strip()}\n")

        print(f"选中轨迹已保存到 {self.output_file_path}")

# 使用类
if __name__ == "__main__":
    folder_range = range(1, 2)  # 处理的文件夹范围
    grid_sizes = [10, 20, 30, 40, 50]  # 处理的网格大小

    # 循环处理每个文件夹和每个网格大小
    for folder_idx in folder_range:
        for grid_size in grid_sizes:
            predicted_file_path = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/sim/new_predicted_selection.txt'
            trajectory_file_path = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/10simulation'
            output_file_path = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/selected_trajectories.txt'

            selector = TrajectorySelector(
                predicted_file_path,
                trajectory_file_path,
                output_file_path
            )
            selector.process_folder()  # 处理单个文件夹
