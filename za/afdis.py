import os
from collections import defaultdict

class TrajectoryProcessor:
    def __init__(self):
        pass

    def read_trajectory_data(self, input_file):
        trajectories = {}
        with open(input_file, 'r') as file:
            for line in file:
                if line.strip():
                    traj_name, traj_data = line.split(':')
                    traj_points = traj_data.strip().split(')')
                    traj_points = [p.replace('(', '').split(',') for p in traj_points if p]
                    traj_points = [(int(x), int(y)) for x, y in traj_points]
                    trajectories[traj_name] = traj_points
        return trajectories

    def calculate_initial_distribution(self, trajectories):
        initial_state_counts = defaultdict(int)
        total_trajectories = len(trajectories)
        for traj_name, traj_points in trajectories.items():
            if traj_points:
                initial_state = traj_points[0]
                initial_state_counts[initial_state] += 1
        initial_probabilities = {state: count / total_trajectories for state, count in initial_state_counts.items()}
        return initial_probabilities

    def calculate_length_distribution(self, trajectories):
        length_counts = defaultdict(int)
        total_trajectories = len(trajectories)
        for traj_name, traj_points in trajectories.items():
            length = len(traj_points)
            length_counts[length] += 1
        length_probabilities = {length: count / total_trajectories for length, count in length_counts.items()}
        return length_probabilities

    def calculate_terminal_distribution(self, trajectories):
        terminal_state_counts = defaultdict(int)
        total_trajectories = len(trajectories)
        for traj_name, traj_points in trajectories.items():
            if traj_points:
                terminal_state = traj_points[-1]
                terminal_state_counts[terminal_state] += 1
        terminal_probabilities = {state: count / total_trajectories for state, count in terminal_state_counts.items()}
        return terminal_probabilities

    def save_probabilities(self, output_file, probabilities, is_length=False):
        with open(output_file, 'w') as file:
            for key, prob in probabilities.items():
                if is_length:
                    file.write(f"Length {key}: {prob}\n")
                else:
                    file.write(f"({key[0]},{key[1]}): {prob}\n")

    def process_files(self, input_file, output_file_start, output_file_end, output_file_length):
        if not os.path.exists(input_file):
            print(f"File {input_file} does not exist, skipping")
            return
        trajectories = self.read_trajectory_data(input_file)
        initial_probabilities = self.calculate_initial_distribution(trajectories)
        self.save_probabilities(output_file_start, initial_probabilities)
        print(f"Initial distribution probabilities saved to: {output_file_start}")
        terminal_probabilities = self.calculate_terminal_distribution(trajectories)
        self.save_probabilities(output_file_end, terminal_probabilities)
        print(f"Terminal distribution probabilities saved to: {output_file_end}")
        length_probabilities = self.calculate_length_distribution(trajectories)
        self.save_probabilities(output_file_length, length_probabilities, is_length=True)
        print(f"Length distribution probabilities saved to: {output_file_length}")

    def process_all(self, file_paths):
        for input_file, output_file_start, output_file_end, output_file_length in file_paths:
            self.process_files(input_file, output_file_start, output_file_end, output_file_length)

