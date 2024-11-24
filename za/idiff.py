class MarkovDataComparator:
    def __init__(self, file_11sim, file_05):
        """
        初始化类并解析文件
        :param file_11sim: 11sim 数据文件路径
        :param file_05: 05 数据文件路径
        """
        self.file_11sim = file_11sim
        self.file_05 = file_05
        self.data_11sim = self.parse_data_file(self.file_11sim)
        self.data_05 = self.parse_data_file(self.file_05)

    def parse_data_file(self, file_path):
        """
        解析数据文件，将数据存储在字典中
        :param file_path: 数据文件路径
        :return: 解析后的字典，键为状态转换，值为概率
        """
        data = {}
        with open(file_path, 'r') as f:
            for line in f:
                # 按照格式 ((lat1, lon1)(lat2, lon2)) probability 解析每一行
                parts = line.split()
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = float(parts[1])
                    # 将 key 转换为元组：((lat1, lon1), (lat2, lon2))
                    key = eval(key_part.replace(')(', '),('))  # 转换为元组
                    data[key] = value_part
        return data

    def find_missing_keys(self):
        """
        找出 data_05 中存在但在 data_11sim 中缺失的键
        :return: 缺失的键列表
        """
        return set(self.data_05.keys()) - set(self.data_11sim.keys())

    def compare_probabilities(self):
        """
        比较两个文件中共同存在的键的概率值差异
        :return: 概率差异的字典，键为状态转换，值为两个文件中的概率差异
        """
        common_keys = set(self.data_11sim.keys()) & set(self.data_05.keys())
        return {key: self.data_05[key] - self.data_11sim[key] for key in common_keys}

    def report_differences(self):
        """
        输出缺失的键和概率差异的报告
        """
        # 1. 找出 11sim 中缺失的键
        missing_in_11sim = self.find_missing_keys()

        # 2. 比较共同存在的键的概率差异
        probability_differences = self.compare_probabilities()
        k=0
        # 输出结果
        print(f"11sim中缺失的状态转换总数: {len(missing_in_11sim)}")
        if missing_in_11sim:
            print("以下状态转换在11sim中缺失：")
            for key in missing_in_11sim:
                print(f"{key}: {self.data_05[key]}")

        print("\n共同存在的状态转换的概率差异：")
        if probability_differences:
           for key, diff in probability_differences.items():
               print(f"{key}: {diff}")
               k=k+abs(diff)
        else:
            print("没有共同存在的状态转换。")
        print(k)
# 使用示例
if __name__ == "__main__":
    # 文件路径（更新为你本地的实际路径）
    file_11sim = '../sumTra/041/sim2/markov_transition_counts.txt'
    file_05 = '../sumTra/041/06first_order_transition_counts'

    # 创建 MarkovDataComparator 类实例
    comparator = MarkovDataComparator(file_11sim, file_05)
    # 输出缺失状态转换和概率差异
    comparator.report_differences()
