import os
from za.afdis import TrajectoryProcessor  # 从 afdis 导入 TrajectoryProcessor 类

class TrajectoryDistributionProcessor:
    def __init__(self, folder_range, input_file_template, output_file_start_template, output_file_end_template, output_file_length_template):
        """
        初始化 TrajectoryDistributionProcessor 类
        :param folder_range: 要处理的文件夹范围
        :param input_file_template: 输入文件路径的模板
        :param output_file_start_template: 初始分布文件输出路径的模板
        :param output_file_end_template: 终点分布文件输出路径的模板
        :param output_file_length_template: 长度分布文件输出路径的模板
        """
        self.folder_range = folder_range
        self.input_file_template = input_file_template
        self.output_file_start_template = output_file_start_template
        self.output_file_end_template = output_file_end_template
        self.output_file_length_template = output_file_length_template
        self.processor = TrajectoryProcessor()  # 实例化 TrajectoryProcessor

    def ensure_file_exists(self, file_path):
        """
        如果文件不存在，创建一个空文件。
        :param file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file_path):
            open(file_path, 'w').close()  # 创建空文件

    def process_folder(self, folder_idx):
        """
        处理指定的文件夹中的轨迹文件，计算初始分布、终点分布和长度分布并保存。
        :param folder_idx: 文件夹索引
        """
        input_file = self.input_file_template.format(folder_idx=folder_idx)
        output_file_start = self.output_file_start_template.format(folder_idx=folder_idx)
        output_file_end = self.output_file_end_template.format(folder_idx=folder_idx)
        output_file_length = self.output_file_length_template.format(folder_idx=folder_idx)

        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"文件 {input_file} 不存在，跳过文件夹 {folder_idx:03d}")
            return

        # 确保输出文件存在（创建目录和空文件）
        self.ensure_file_exists(output_file_start)
        self.ensure_file_exists(output_file_end)
        self.ensure_file_exists(output_file_length)

        # 使用 TrajectoryProcessor 的方法处理数据
        self.processor.process_files(
            input_file,
            output_file_start,  # 输出初始分布文件路径
            output_file_end,  # 输出终点分布文件路径
            output_file_length  # 输出长度分布文件路径
        )

    def process_all_folders(self):
        """
        处理所有指定的文件夹
        """
        for folder_idx in self.folder_range:
            print(f"Processing folder {folder_idx:03d} ...")
            self.process_folder(folder_idx)


# if __name__ == "__main__":
#     folder_range = range(0, 4)  # 你可以调整文件夹范围
#     input_file_template = '../sumTra/{folder_idx:03d}/grid10/sim/selected_trajectories.txt'
#     output_file_start_template = '../sumTra/{folder_idx:03d}/grid10/result/07start'
#     output_file_end_template = '../sumTra/{folder_idx:03d}/grid10/result/08end'
#     output_file_length_template = '../sumTra/{folder_idx:03d}/grid10/result/09length'
#
#     processor = TrajectoryDistributionProcessor(
#         folder_range,
#         input_file_template,
#         output_file_start_template,
#         output_file_end_template,
#         output_file_length_template
#     )
#     processor.process_all_folders()
