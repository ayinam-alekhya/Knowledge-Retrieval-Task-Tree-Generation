import pickle
import json
import random
import math
from FOON_class import Object

# Checks if an ingredient exists in the kitchen
def check_if_exist_in_kitchen(kitchen_items, ingredient):
    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True
    return False

# Monte Carlo Tree Search (MCTS) implementation
def search_MCTS(kitchen_items, target_node, obj_nodes=[], func_units=[], obj_to_unit_map=[], iterations=1000):
    # List to store the selected task tree functional units
    task_sequence = []

    # A dictionary to store the success counts (wins) and number of attempts (trials) for each FU
    unit_stats = {idx: {"wins": 0, "trials": 0} for idx in range(len(func_units))}

    # Load the motion success probabilities from motion.txt
    motion_probs = get_motion_success_rates("motion.txt")

    # Perform the MCTS search for a given goal node
    def perform_mcts(goal):
        # List to store the sequence of units during the search
        selected_units = []
        visited = set()  # Track visited nodes to prevent re-exploring

        # Function to simulate task tree search starting from the goal node
        def simulate_task_tree(node):
            # If the node exists in the kitchen, return success
            if check_if_exist_in_kitchen(kitchen_items, node):
                return True

            # If the node has already been visited, skip to prevent cycles
            if node.id in visited:
                return False

            visited.add(node.id)  # Mark the node as visited

            # Retrieve the functional units that produce the node
            available_units = obj_to_unit_map[node.id]
            optimal_unit = None
            optimal_score = -float('inf')

            # Simulate each functional unit and select the best one
            for idx in available_units:
                unit_stats[idx]["trials"] += 1  # Increment the count of trials for this unit
                unit_successes = 0

                # Run multiple simulations for each unit
                for _ in range(iterations):
                    if simulate_unit_execution(func_units[idx], motion_probs):
                        unit_successes += 1

                # Update the success count for the functional unit
                unit_stats[idx]["wins"] += unit_successes

                # Calculate UCB1 score
                total_trials = sum([unit_stats[unit]["trials"] for unit in unit_stats])
                success_ratio = unit_stats[idx]["wins"] / unit_stats[idx]["trials"]
                exploration_bonus = math.sqrt(2 * math.log(total_trials) / unit_stats[idx]["trials"])
                ucb1_score = success_ratio + exploration_bonus

                # Update the best unit based on the highest score
                if ucb1_score > optimal_score:
                    optimal_score = ucb1_score
                    optimal_unit = idx

            # Add the optimal unit to the task tree
            if optimal_unit is not None:
                selected_units.append(optimal_unit)
                for input_node in func_units[optimal_unit].input_nodes:
                    simulate_task_tree(obj_nodes[input_node.id])  # Recurse for the input nodes

        simulate_task_tree(goal)
        return selected_units

    # Run MCTS for the target node
    task_tree_indices = perform_mcts(target_node)

    # Convert indices to functional units
    task_sequence = [func_units[index] for index in task_tree_indices]
    return task_sequence

# Simulate the execution of a functional unit using the success probabilities
def simulate_unit_execution(FU, success_probs):
    motion_key = FU.motion_node  # Get the motion associated with the FU
    probability = success_probs.get(motion_key, 0.5)  # Default to 50% success rate if not found
    return random.uniform(0, 1) <= probability

# Load success rates from the motion.txt file
def get_motion_success_rates(filepath):
    probabilities = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or '\t' not in line:
                continue
            motion, prob = line.split('\t')
            try:
                probabilities[motion] = float(prob)
            except ValueError:
                print(f"Skipping invalid entry for motion '{motion}' in {filepath}")
    return probabilities

# Save the task tree to a file
def save_paths_to_file(task_tree, path):
    print('writing generated task tree to ', path)
    with open(path, 'w') as _file:
        _file.write('//\n')
        for FU in task_tree:
            _file.write(FU.get_FU_as_text() + "\n")

# Reads the FOON graph from a pickle file
def read_universal_foon(filepath='FOON.pkl'):
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map

# Main function
if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon()

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))
    goal_nodes = json.load(open("goal_nodes.json"))
    
    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]
        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                output_task_tree = search_MCTS(kitchen_items, object, foon_object_nodes, foon_functional_units, foon_object_to_FU_map)
                break

