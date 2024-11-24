import os
from collections import defaultdict


class MarkovChainProcessor:
    def __init__(self):
        pass

    def read_trajectory_data(self, input_file):
        trajectories = {}
        with open(input_file, 'r') as file:
            for line in file:
                if line.strip():
                    traj_name, traj_data = line.split(':')
                    traj_points = traj_data.strip().replace(')(', ') (').split()
                    cleaned_points = []
                    for point in traj_points:
                        point = point.replace('(', '').replace(')', '')
                        try:
                            x, y = map(int, point.split(','))
                            cleaned_points.append((x, y))
                        except ValueError as e:
                            print(f"Error parsing point: {e}. Line: {line}")
                    if cleaned_points:
                        trajectories[traj_name] = cleaned_points
        return trajectories

    def calculate_first_order_markov(self, trajectories):
        transition_counts = defaultdict(int)
        first_order_markov = defaultdict(lambda: defaultdict(int))
        for traj_name, traj_points in trajectories.items():
            if len(traj_points) < 2:
                continue
            for i in range(len(traj_points) - 1):
                prev_state = traj_points[i]
                current_state = traj_points[i + 1]
                first_order_markov[prev_state][current_state] += 1
                transition_key = (prev_state, current_state)
                transition_counts[transition_key] += 1
        return first_order_markov, transition_counts

    def calculate_probabilities(self, first_order_markov):
        transition_probabilities = {}
        for prev_state, transitions in first_order_markov.items():
            total_transitions = sum(transitions.values())
            transition_probabilities[prev_state] = {state: count / total_transitions for state, count in
                                                    transitions.items()}
        return transition_probabilities

    def save_first_order_markov(self, output_file, first_order_markov, transition_probabilities):
        with open(output_file, 'w') as file:
            for prev_state, next_states in first_order_markov.items():
                for next_state in next_states:
                    prob = transition_probabilities[prev_state][next_state]
                    state_str = f"(({prev_state[0]},{prev_state[1]})({next_state[0]},{next_state[1]})) {prob}"
                    file.write(state_str + "\n")

    def save_transition_counts(self, output_file, transition_counts):
        with open(output_file, 'w') as file:
            for transition, count in transition_counts.items():
                transition_str = f"(({transition[0][0]},{transition[0][1]})({transition[1][0]},{transition[1][1]})) {count}"
                file.write(transition_str + "\n")

    def process_files(self, input_file, output_file_05, output_file_06):
        if not os.path.exists(input_file):
            print(f"File {input_file} does not exist, creating an empty file.")
            os.makedirs(os.path.dirname(input_file), exist_ok=True)
            with open(input_file, 'w') as file:
                pass
            return
        print(f"Processing file: {input_file}")
        trajectories = self.read_trajectory_data(input_file)
        first_order_markov, transition_counts = self.calculate_first_order_markov(trajectories)
        transition_probabilities = self.calculate_probabilities(first_order_markov)
        self.save_first_order_markov(output_file_05, first_order_markov, transition_probabilities)
        print(f"First-order Markov chain probabilities saved to: {output_file_05}")
        self.save_transition_counts(output_file_06, transition_counts)
        print(f"First-order Markov chain counts saved to: {output_file_06}")
