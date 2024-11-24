import os
import re
import numpy as np
from keras.models import load_model


class ResultVectorPredictor:
    def __init__(self, folder_range, fill_value=1, num_vectors_to_generate=1, threshold=0.17):
        """
        初始化 ResultVectorPredictor 类
        :param folder_range: 要处理的文件夹范围
        :param fill_value: 生成 result_vectors 时的填充值
        :param num_vectors_to_generate: 生成 result_vectors 的数量
        :param threshold: 用于将连续输出转换为 0 和 1 的阈值
        """
        self.folder_range = folder_range
        self.fill_value = fill_value
        self.num_vectors_to_generate = num_vectors_to_generate
        self.threshold = threshold

    def generate_new_result_vectors(self, vector_length):
        """
        生成新的 result_vectors
        :param vector_length: 生成的 result_vectors 的长度
        :return: 生成的 result_vectors 矩阵 (numpy array)
        """
        result_vectors = np.full((self.num_vectors_to_generate, vector_length), self.fill_value)
        return result_vectors

    def get_result_vector_length(self, file_path):
        """
        从文件中提取 Result Vector 的列数
        :param file_path: 文件路径
        :return: result_vector 的列数
        """
        pattern_result_vector = re.compile(r'Result Vector: \[(.*?)\]')

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在。")

        with open(file_path, 'r') as f:
            for line in f:
                result_match = pattern_result_vector.match(line.strip())
                if result_match:
                    result_vector = list(map(int, result_match.group(1).split(', ')))
                    return len(result_vector)

        return 0

    def get_trajectory_count(self, trajectory_file_path):
        """
        读取 04index_trajectory.plt 文件中的条数
        :param trajectory_file_path: 文件路径
        :return: 文件中的条数
        """
        if not os.path.exists(trajectory_file_path):
            raise FileNotFoundError(f"文件 {trajectory_file_path} 不存在。")

        with open(trajectory_file_path, 'r') as f:
            lines = f.readlines()

        return len(lines)

    def adjust_selection_vectors(self, selection_vector, required_count):
        """
        调整 selection_vectors 中的 1 的数量，使其与要求的条数一致
        :param selection_vector: 二进制选择向量
        :param required_count: 需要的 1 的数量
        :return: 调整后的选择向量
        """
        current_count = np.sum(selection_vector)
       # print(current_count,required_count)
        if current_count >= required_count*0.75:
            return selection_vector

        # 获取所有为 0 的索引
        zero_indices = np.where(selection_vector == 0)[0]

        # 随机选择一些 0 的索引并将其设置为 1
        indices_to_flip = np.random.choice(zero_indices, int(required_count*0.75) - current_count, replace=False)
        selection_vector[indices_to_flip] = 1

        return selection_vector

    def predict_for_folder(self, folder_idx, model_path, result_file_path, output_file_path, trajectory_file_path):
        """
        为指定文件夹生成新的 result_vectors 并进行预测
        :param folder_idx: 文件夹索引
        :param model_path: 模型文件路径
        :param result_file_path: Result Vector 文件路径
        :param output_file_path: 预测结果的输出文件路径
        :param trajectory_file_path: 轨迹文件路径，用于获取条数
        """
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            print(f"模型文件 {model_path} 不存在，跳过该文件夹。")
            return

        # 加载训练好的模型
        model = load_model(model_path)

        # 获取 result_vector 的长度
        try:
            known_result_vector_length = self.get_result_vector_length(result_file_path)
        except FileNotFoundError as e:
            print(e)
            return

        if known_result_vector_length == 0:
            print(f"未能从文件中找到 Result Vector 或文件格式错误，跳过文件夹 {folder_idx:03d}。")
            return

        # 生成新的 result_vectors
        new_result_vectors = self.generate_new_result_vectors(known_result_vector_length)

        # 使用训练好的模型进行预测
        new_predicted_selection_vectors = model.predict(new_result_vectors)

        # 将预测结果转换为 0 和 1
        binary_new_predicted_selection_vectors = (new_predicted_selection_vectors >= self.threshold).astype(int)

        # 获取 04index_trajectory.plt 文件中的条数
        try:
            required_count = self.get_trajectory_count(trajectory_file_path)
        except FileNotFoundError as e:
            print(e)
            return

        # 调整选择向量中的 1 的数量
        for i, selection_vector in enumerate(binary_new_predicted_selection_vectors):
            binary_new_predicted_selection_vectors[i] = self.adjust_selection_vectors(selection_vector, required_count)

        # 保存新的预测结果到文件
        with open(output_file_path, 'w') as f:
            f.write("Predicted Selection Vectors for New Result Vectors\n")
            f.write("=================================================\n")
            for predicted in binary_new_predicted_selection_vectors:
                predicted_str = ', '.join(f'{value}' for value in predicted)
                f.write(f"Predicted: [{predicted_str}]\n")
                f.write("\n")

        print(f"文件夹 {folder_idx} 的新预测已保存到 {output_file_path}")

    def process_folders(self, model_path_template, result_file_path_template, output_file_path_template,
                        trajectory_file_path_template):
        """
        遍历文件夹，处理每个文件夹的数据并生成预测
        :param model_path_template: 模型文件路径的模板
        :param result_file_path_template: Result Vector 文件路径的模板
        :param output_file_path_template: 预测结果的输出文件路径模板
        :param trajectory_file_path_template: 轨迹文件路径的模板
        """
        for folder_idx in self.folder_range:
            model_path = model_path_template.format(folder_idx=folder_idx)
            result_file_path = result_file_path_template.format(folder_idx=folder_idx)
            output_file_path = output_file_path_template.format(folder_idx=folder_idx)
            trajectory_file_path = trajectory_file_path_template.format(folder_idx=folder_idx)

            self.predict_for_folder(folder_idx, model_path, result_file_path, output_file_path, trajectory_file_path)

# 使用类进行预测
if __name__ == "__main__":
    folder_range = range(1,2)  # 要处理的文件夹范围
    grid_sizes = [10, 20 ,30 ,40 ,50]  # 要处理的网格大小

    # 实例化并处理文件夹
    predictor = ResultVectorPredictor(folder_range, fill_value=1, num_vectors_to_generate=1, threshold=0.17)

    # 遍历文件夹和网格大小，并生成对应的模板路径
    for folder_idx in folder_range:
        for grid_size in grid_sizes:
            model_path_template = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/sim/result_to_selection_mapping_model.h5'
            result_file_path_template = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/sim/sample/500_iterations.txt'
            output_file_path_template = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/sim/new_predicted_selection.txt'
            trajectory_file_path_template = f'../grid_output_taxi/{folder_idx}/grid{grid_size}/{folder_idx}_1_grid.txt'

            # 单次调用预测，不再重复调用
            predictor.predict_for_folder(folder_idx, model_path_template, result_file_path_template,
                                         output_file_path_template, trajectory_file_path_template)

