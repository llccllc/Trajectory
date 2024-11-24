import random
import os

class GridTrajectoryReplacer:
    def __init__(self, grid_file_template, trajectory_file_template, output_file_template, folder_range):
        """
        初始化 GridTrajectoryReplacer 类
        :param grid_file_template: 网格文件路径模板
        :param trajectory_file_template: 轨迹文件路径模板
        :param output_file_template: 输出文件路径模板
        :param folder_range: 要处理的文件夹范围
        """
        self.grid_file_template = grid_file_template
        self.trajectory_file_template = trajectory_file_template
        self.output_file_template = output_file_template
        self.folder_range = folder_range

    def load_grid_to_coordinates(self, grid_file):
        """
        从网格文件中加载网格和经纬度数据
        :param grid_file: 网格文件路径
        :return: 一个字典，键为网格坐标，值为对应的经纬度列表
        """
        grid_to_coords = {}
        with open(grid_file, 'r') as f:
            for line in f:
                grid_key, coords = line.split(":")
                coords_list = coords.strip().split(")(")
                coords_list = [tuple(map(float, coord.strip("()").split(","))) for coord in coords_list]
                grid_to_coords[grid_key.strip()] = coords_list
        return grid_to_coords

    def load_trajectories(self, trajectory_file):
        """
        从轨迹文件中加载轨迹数据
        :param trajectory_file: 轨迹文件路径
        :return: 一个字典，键为轨迹ID，值为网格坐标列表
        """
        trajectories = {}
        with open(trajectory_file, 'r') as f:
            for line in f:
                tra_id, grid_locs = line.split(":")
                grid_locs = grid_locs.strip().split(")(")
                grid_locs = [tuple(map(int, loc.strip("()").split(","))) for loc in grid_locs]
                trajectories[tra_id.strip()] = grid_locs
        return trajectories

    def replace_grid_with_coordinates(self, trajectories, grid_to_coords):
        """
        将轨迹中的网格坐标替换为对应的经纬度
        :param trajectories: 包含网格坐标的轨迹字典
        :param grid_to_coords: 网格与经纬度对应关系的字典
        :return: 替换后的轨迹字典
        """
        replaced_trajectories = {}
        for tra_id, grid_locs in trajectories.items():
            replaced_trajectories[tra_id] = []
            for grid_loc in grid_locs:
                grid_key = f"({grid_loc[0]},{grid_loc[1]})"
                if grid_key in grid_to_coords:
                    # 随机从对应网格的经纬度列表中选取一个经纬度
                    replaced_trajectories[tra_id].append(random.choice(grid_to_coords[grid_key]))
                else:
                    print(f"Warning: No coordinates found for grid {grid_key}")
        return replaced_trajectories

    def save_replaced_trajectories(self, output_file, replaced_trajectories):
        """
        将替换后的轨迹保存到文件
        :param output_file: 输出文件路径
        :param replaced_trajectories: 替换后的轨迹数据字典
        """
        with open(output_file, 'w') as f:
            for tra_id, coords in replaced_trajectories.items():
                coord_str = "".join([f"({lat},{lon})" for lat, lon in coords])
                f.write(f"{tra_id}:{coord_str}\n")

    def process(self):
        """
        遍历文件夹并处理每个文件夹中的数据
        """
        for folder_idx in self.folder_range:
            print(f"Processing folder {folder_idx:03d}...")
            grid_file = self.grid_file_template.format(folder_idx=folder_idx)
            trajectory_file = self.trajectory_file_template.format(folder_idx=folder_idx)
            output_file = self.output_file_template.format(folder_idx=folder_idx)

            # 检查文件是否存在
            if not os.path.exists(grid_file):
                print(f"Grid file {grid_file} 不存在，跳过文件夹 {folder_idx:03d}。")
                continue
            if not os.path.exists(trajectory_file):
                print(f"Trajectory file {trajectory_file} 不存在，跳过文件夹 {folder_idx:03d}。")
                continue

            # Step 1: 读取网格与经纬度数据
            grid_to_coords = self.load_grid_to_coordinates(grid_file)

            # Step 2: 读取轨迹数据
            trajectories = self.load_trajectories(trajectory_file)

            # Step 3: 替换网格坐标为经纬度
            replaced_trajectories = self.replace_grid_with_coordinates(trajectories, grid_to_coords)

            # Step 4: 保存替换后的轨迹
            self.save_replaced_trajectories(output_file, replaced_trajectories)

        print("所有文件夹的轨迹文件替换已完成。")


# 使用类
# if __name__ == "__main__":
#     grid_file_template = "../sumTra/{folder_idx:03d}/grid10/11gridloca.txt"
#     trajectory_file_template = "../sumTra/{folder_idx:03d}/grid10/sim/selected_trajectories.txt"
#     output_file_template = "../sumTra/{folder_idx:03d}/grid10/result/replaced_trajectories.txt"
#     folder_range = range(1, 4)  # 可根据需要修改范围
#
#     replacer = GridTrajectoryReplacer(grid_file_template, trajectory_file_template, output_file_template, folder_range)
#     replacer.process()
