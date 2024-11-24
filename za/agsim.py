import random
import os

class TrajectorySimulator:
    def __init__(self, folder_idx, n, trajectory_file, initial_prob_file, length_prob_file, markov_chain_file, output_file):
        self.folder_idx = folder_idx
        self.n = n

        self.trajectory_file = trajectory_file
        self.initial_prob_file = initial_prob_file
        self.length_prob_file = length_prob_file
        self.markov_chain_file = markov_chain_file
        self.output_file = output_file
        self.trajectories = self.read_trajectory_file(self.trajectory_file)
        self.initial_prob = self.read_initial_distribution(self.initial_prob_file)
        self.length_prob = self.read_length_distribution(self.length_prob_file)
        self.markov_prob = self.read_markov_chain(self.markov_chain_file)

    def ensure_file_exists(self, file_path, file_description):
        if not os.path.exists(file_path):
            print(f"{file_description} {file_path} 不存在，正在创建新的文件...")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                pass

    def read_trajectory_file(self, file_path):
        trajectories = {}
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    traj_name, traj_data = line.split(':')
                    traj_points = traj_data.strip().split(')')
                    traj_points = [p.replace('(', '').split(',') for p in traj_points if p]
                    traj_points = [(int(x), int(y)) for x, y in traj_points]
                    trajectories[traj_name.strip()] = traj_points
        return trajectories

    def read_initial_distribution(self, file_path):
        initial_prob = {}
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    state, prob = line.split(':')
                    state = tuple(map(int, state.strip('()').split(',')))
                    prob = float(prob)
                    initial_prob[state] = prob
        return initial_prob

    def read_length_distribution(self, file_path):
        length_prob = {}
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    length_str, prob = line.split(':')
                    length = int(length_str.split()[1])
                    prob = float(prob)
                    length_prob[length] = prob
        return length_prob

    def read_markov_chain(self, file_path):
        markov_prob = {}
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    states_part, prob = line.rsplit(' ', 1)
                    prob = float(prob.strip())
                    states = states_part.strip('()').split(')(')
                    prev_state = tuple(map(int, states[0].split(',')))
                    next_state = tuple(map(int, states[1].split(',')))

                    if prev_state not in markov_prob:
                        markov_prob[prev_state] = {}
                    markov_prob[prev_state][next_state] = prob
        return markov_prob

    def select_random_from_distribution(self, distribution):
        rand_val = random.random()
        cumulative_prob = 0.0
        for item, prob in distribution.items():
            cumulative_prob += prob
            if rand_val < cumulative_prob:
                return item
        return list(distribution.keys())[-1]

    def simulate_trajectory(self):
        start_point = self.select_random_from_distribution(self.initial_prob)
        length = self.select_random_from_distribution(self.length_prob)
        trajectory = [start_point]

        for _ in range(length - 1):
            prev_point = trajectory[-1]
            if prev_point in self.markov_prob:
                next_point = self.select_random_from_distribution(self.markov_prob[prev_point])
                trajectory.append(next_point)
            else:
                break

        return trajectory

    def simulate_multiple_trajectories(self, num_trajectories):
        trajectories = []
        for _ in range(num_trajectories * self.n):  # 使用 n 倍生成轨迹
            traj = self.simulate_trajectory()
            trajectories.append(traj)
        return trajectories

    def save_simulated_trajectories(self, trajectories):
        with open(self.output_file, 'w') as file:
            for i, traj in enumerate(trajectories, 1):
                traj_str = ''.join([f"({x[0]},{x[1]})" for x in traj])
                file.write(f"tra{i}:{traj_str}\n")

    def run_simulation(self):
        num_trajectories = len(self.trajectories)
        trajectories = self.simulate_multiple_trajectories(num_trajectories)
        self.save_simulated_trajectories(trajectories)
        print(f"{num_trajectories * self.n} 条轨迹已保存到 '{self.output_file}' 文件中.")

