import re
from collections import defaultdict
import os


class MarkovTrajectoryProcessor:
    def __init__(self, folder_range, trajectory_file_template, transition_counts_file_template, transition_probabilities_file_template):
        """
        初始化 MarkovTrajectoryProcessor 类
        :param folder_range: 要处理的文件夹范围
        :param trajectory_file_template: 轨迹文件路径模板
        :param transition_counts_file_template: 转移次数文件路径模板
        :param transition_probabilities_file_template: 转移概率文件路径模板
        """
        self.folder_range = folder_range
        self.trajectory_file_template = trajectory_file_template
        self.transition_counts_file_template = transition_counts_file_template
        self.transition_probabilities_file_template = transition_probabilities_file_template

    def process_folder(self, folder_idx):
        """
        处理指定文件夹中的轨迹文件，计算并保存马尔科夫转移次数和转移概率。
        :param folder_idx: 文件夹索引
        """
        trajectory_file_path = self.trajectory_file_template.format(folder_idx=folder_idx)
        transition_counts_file_path = self.transition_counts_file_template.format(folder_idx=folder_idx)
        transition_probabilities_file_path = self.transition_probabilities_file_template.format(folder_idx=folder_idx)

        # 检查文件是否存在
        if not os.path.exists(trajectory_file_path):
            print(f"文件 {trajectory_file_path} 不存在，跳过文件夹 {folder_idx:03d}。")
            return

        # 读取轨迹文件
        with open(trajectory_file_path, 'r') as file:
            trajectories = file.readlines()

        # 初始化马尔科夫转移字典
        transition_counts = defaultdict(lambda: defaultdict(int))

        # 提取每条轨迹并统计状态转移
        for trajectory in trajectories:
            # 使用正则表达式提取所有状态对
            states = re.findall(r'\((\d+),(\d+)\)', trajectory)

            # 遍历每条轨迹中的状态对，计算转移
            for i in range(len(states) - 1):
                state_A = (int(states[i][0]), int(states[i][1]))  # 当前状态
                state_B = (int(states[i + 1][0]), int(states[i + 1][1]))  # 下一个状态
                transition_counts[state_A][state_B] += 1

        # 计算马尔科夫转移概率
        transition_probabilities = defaultdict(lambda: defaultdict(float))

        # 对每个状态A计算转移概率
        for state_A, transitions in transition_counts.items():
            total_transitions_from_A = sum(transitions.values())  # 从状态A出发的所有转移次数总和

            # 计算从状态A到其他状态的转移概率
            for state_B, count in transitions.items():
                transition_probabilities[state_A][state_B] = count / total_transitions_from_A

        # 将马尔科夫转移数保存到文件
        with open(transition_counts_file_path, 'w') as counts_file:
            for state_A, transitions in transition_counts.items():
                for state_B, count in transitions.items():
                    counts_file.write(f"(({state_A[0]},{state_A[1]})({state_B[0]},{state_B[1]})) {count}\n")

        # 将马尔科夫转移概率保存到文件
        with open(transition_probabilities_file_path, 'w') as probabilities_file:
            for state_A, transitions in transition_probabilities.items():
                for state_B, probability in transitions.items():
                    probabilities_file.write(f"(({state_A[0]},{state_A[1]})({state_B[0]},{state_B[1]})) {probability:.4f}\n")

        print(f"文件夹 {folder_idx:03d} 的马尔科夫转移数已保存到 {transition_counts_file_path}")
        print(f"文件夹 {folder_idx:03d} 的马尔科夫转移概率已保存到 {transition_probabilities_file_path}")

    def process_all_folders(self):
        """
        处理所有指定范围内的文件夹
        """
        for folder_idx in self.folder_range:
            print(f"Processing folder {folder_idx:03d}...")
            self.process_folder(folder_idx)


# 使用类
# if __name__ == "__main__":
#     folder_range = range(1, 4)  # 假设要处理 sumTra/000 到 sumTra/002
#     trajectory_file_template = '../sumTra/{folder_idx:03d}/grid10/sim/selected_trajectories.txt'
#     transition_counts_file_template = '../sumTra/{folder_idx:03d}/grid10/sim/markov_transition_counts.txt'
#     transition_probabilities_file_template = '../sumTra/{folder_idx:03d}/grid10/sim/markov_transition_probabilities.txt'
#
#     processor = MarkovTrajectoryProcessor(
#         folder_range,
#         trajectory_file_template,
#         transition_counts_file_template,
#         transition_probabilities_file_template
#     )
#
#     processor.process_all_folders()
