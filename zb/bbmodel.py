import numpy as np
from keras.models import Sequential
from keras.layers import Dense
import os

class NeuralNetworkTrainer:
    def __init__(self, folder_range, grid_size, epochs=200, batch_size=62, threshold=0.17):
        """
        初始化 NeuralNetworkTrainer 类
        :param folder_range: 要处理的文件夹范围
        :param grid_size: 网格大小
        :param epochs: 训练模型的迭代次数
        :param batch_size: 每次批量训练的样本数
        :param threshold: 用于将连续输出转换为 0 和 1 的阈值
        """
        self.folder_range = folder_range
        self.grid_size = grid_size  # 新增参数，指定网格大小
        self.epochs = epochs
        self.batch_size = batch_size
        self.threshold = threshold

    def load_data(self, file_path):
        """
        加载给定文件中的 Selection Vector 和 Result Vector 数据
        :param file_path: 文件路径
        :return: (selection_vectors, result_vectors) 数组
        """
        selection_vectors = []
        result_vectors = []

        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith("Selection Vector"):
                    print("Selection Vector",line)
                    selection_vector = list(map(int, line.strip().split(": ")[1].strip('[]').split(', ')))
                    selection_vectors.append(selection_vector)
                elif line.startswith("Result Vector"):
                    print("Result Vector",line)
                    result_vector = list(map(int, line.strip().split(": ")[1].strip('[]').split(', ')))
                    result_vectors.append(result_vector)

        return np.array(selection_vectors), np.array(result_vectors)

    def train_and_save_model(self, folder_idx, file_path, output_folder):
        """
        训练神经网络模型并保存预测结果
        :param folder_idx: 当前文件夹索引
        :param file_path: 数据文件路径
        :param output_folder: 输出结果文件夹路径
        """
        # 加载数据
        selection_vectors, result_vectors = self.load_data(file_path)

        if selection_vectors.size == 0 or result_vectors.size == 0:
            print(f"文件 {file_path} 数据为空，跳过。")
            return

        # 构建神经网络模型
        model = Sequential()
        model.add(Dense(128, input_dim=result_vectors.shape[1], activation='relu'))  # 结果向量作为输入
        model.add(Dense(64, activation='relu'))
        model.add(Dense(selection_vectors.shape[1], activation='sigmoid'))  # 选择向量作为输出

        # 编译模型
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        # 训练模型
        model.fit(result_vectors, selection_vectors, epochs=self.epochs, batch_size=self.batch_size)

        # 使用训练好的模型进行预测
        predicted_selection = model.predict(result_vectors)

        # 将 predicted_selection 的连续输出转换为 0 和 1
        predicted_selection_binary = (predicted_selection > self.threshold).astype(int)

        # 保存模型
        model_path = os.path.join(output_folder, 'result_to_selection_mapping_model.h5')
        model.save(model_path)

        # 将 predicted_selection 和真实的 selection_vectors 写入文件
        output_file = os.path.join(output_folder, 'predicted_vs_actual_selections.txt')
        with open(output_file, 'w') as f:
            f.write("Predicted Selections vs Actual Selections\n")
            f.write("===================================\n")
            for predicted, actual in zip(predicted_selection_binary, selection_vectors):
                predicted_str = ', '.join(map(str, predicted))
                actual_str = ', '.join(map(str, actual))
                f.write(f"Predicted: [{predicted_str}]\n")
                f.write(f"Actual   : [{actual_str}]\n")
                f.write("\n")

        print(f"文件夹 {folder_idx:03d} 处理完成，结果已保存到 {output_file}")

    def process_folders(self):
        """
        处理多个文件夹中的数据，训练模型并保存结果
        """
        for folder_idx in self.folder_range:
            # 动态生成文件路径，使用指定的网格大小
            file_path = f'../grid_output_taxi/{folder_idx}/grid{self.grid_size}/sim/sample/500_iterations.txt'
            output_folder = f'../grid_output_taxi/{folder_idx}/grid{self.grid_size}/sim/'

            # 检查文件是否存在，避免报错
            if not os.path.exists(file_path):
                print(f"文件 {file_path} 不存在，跳过。")
                continue

            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)

            # 训练并保存模型和预测结果
            self.train_and_save_model(folder_idx, file_path, output_folder)


# 使用类进行处理
if __name__ == "__main__":
    folder_range = range(1, 501)  # 要处理的文件夹范围
    grid_sizes = [10, 20, 30, 40, 50]  # 多个网格大小

    # 遍历每个 grid_size
    for grid_size in grid_sizes:
        print(f"正在处理 grid_size: {grid_size} ...")
        trainer = NeuralNetworkTrainer(folder_range, grid_size, epochs=200, batch_size=62, threshold=0.17)
        trainer.process_folders()
        print(f"grid_size: {grid_size} 处理完成。")
