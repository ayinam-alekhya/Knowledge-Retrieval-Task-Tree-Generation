import pickle
import json
import heapq  # for priority queue used in A*

from FOON_class import Object

# -----------------------------------------------------------------------------------------------------------------------------#

# Utility function to check if an ingredient exists in the kitchen
def check_ingredient_in_kitchen(kitchen_items, ingredient):
    """
    parameters: kitchen_items (list) - List of items in the kitchen
                ingredient (Object) - Object representing the ingredient to search for
    returns: True if the ingredient exists in the kitchen, False otherwise
    """
    for item in kitchen_items:
        if (item["label"] == ingredient.label and
                sorted(item["states"]) == sorted(ingredient.states) and
                sorted(item["ingredients"]) == sorted(ingredient.ingredients) and
                item["container"] == ingredient.container):
            return True
    return False

# -----------------------------------------------------------------------------------------------------------------------------#
# Load success rates from motion.txt
def load_success_rates(file_path="motion.txt"):
    """
    Load the success rates from a file and return as a dictionary
    with functional unit IDs as keys and success rates as values.
    Skips lines that are not properly formatted.
    """
    success_rates = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Ignore empty lines or lines that don't have two values
            if not line.strip():
                continue
            parts = line.strip().split('\t')  # Splitting by tab instead of comma
            if len(parts) != 2:
                print(f"Skipping malformed line: {line.strip()}")
                continue
            try:
                fu_id = parts[0]  # Function unit name or id
                success_rate = float(parts[1])
                success_rates[fu_id] = success_rate
            except ValueError:
                print(f"Skipping line with invalid data: {line.strip()}")
                continue
    return success_rates

# -----------------------------------------------------------------------------------------------------------------------------#

# A* Search algorithm with cost and heuristic functions
def search_A_star(kitchen_items=[], goal_node=None, success_rates=None, foon_object_nodes=[], foon_functional_units=[], foon_object_to_FU_map=[], utensils=[]):
    """
    A* search algorithm
    parameters: kitchen_items (list) - List of items in the kitchen
                goal_node (Object) - The target node to search for
                success_rates (dict) - A dictionary with functional unit IDs and their success rates
                foon_object_nodes (list) - List of object nodes in the FOON
                foon_functional_units (list) - List of functional units in the FOON
                foon_object_to_FU_map (dict) - Dictionary mapping object nodes to functional units
                utensils (list) - List of utensils to check during search
    returns: task_tree_units (list) - List of functional units representing the task tree
    """
    # Priority queue for A* search
    open_list = []
    heapq.heappush(open_list, (0, goal_node.id, 0))  # (f(n), node_id, g(n))

    reference_task_tree = []
    searched_items = {}

    while open_list:
        _, current_item_index, current_cost = heapq.heappop(open_list)

        if current_item_index in searched_items and current_cost >= searched_items[current_item_index]:
            continue
        searched_items[current_item_index] = current_cost

        current_node = foon_object_nodes[current_item_index]

        # If the current node is in the kitchen, skip further processing
        if check_ingredient_in_kitchen(kitchen_items, current_node):
            continue

        candidate_units = foon_object_to_FU_map[current_item_index]
        selected_candidate_idx = candidate_units[0]  # Selecting the first path

        # Avoid revisiting the same functional unit
        if selected_candidate_idx in reference_task_tree:
            continue
        reference_task_tree.append(selected_candidate_idx)

        # Cost function: inverse of the success rate from motion.txt
        unit_success_rate = success_rates.get(selected_candidate_idx, 1)  # Default success rate is 1 if not found
        unit_cost = 1 / unit_success_rate

        # Explore input nodes (children)
        for input_node in foon_functional_units[selected_candidate_idx].input_nodes:
            node_id = input_node.id
            new_cost = current_cost + unit_cost  # Increment cost by the functional unit's cost

            # Heuristic function: number of input objects (fewer inputs preferred)
            heuristic_value = len(foon_functional_units[selected_candidate_idx].input_nodes)

            estimated_cost = new_cost + heuristic_value  # A* f(n) = g(n) + h(n)
            heapq.heappush(open_list, (estimated_cost, node_id, new_cost))

    reference_task_tree.reverse()
    task_tree_units = [foon_functional_units[i] for i in reference_task_tree]
    return task_tree_units

# -----------------------------------------------------------------------------------------------------------------------------#

# Iterative Deepening Search (IDS) 
def search_IDS(kitchen_items=[], goal_node=None, foon_object_nodes=[], foon_functional_units=[], foon_object_to_FU_map=[], utensils=[]):
    """
    Iterative Deepening Search (IDS) algorithm
    parameters: kitchen_items (list) - List of items in the kitchen
                goal_node (Object) - The target node to search for
                foon_object_nodes (list) - List of object nodes in the FOON
                foon_functional_units (list) - List of functional units in the FOON
                foon_object_to_FU_map (dict) - Dictionary mapping object nodes to functional units
                utensils (list) - List of utensils to check during search
    returns: task_tree_units (list) - List of functional units representing the task tree
    """
    depth_limit = 0

    while depth_limit >= 0:
        reference_task_tree = []
        items_to_search = [[goal_node.id, 0]]
        searched_items = []
        skipped_items = []

        while items_to_search:
            node_id, current_depth = items_to_search.pop(0)

            # Skip nodes that exceed the current depth limit
            if current_depth > depth_limit:
                skipped_items.append(node_id)
                continue

            # Skip already explored nodes
            if node_id in searched_items:
                continue
            searched_items.append(node_id)

            current_node = foon_object_nodes[node_id]

            # If the current node is not in the kitchen, look for its parent functional unit
            if not check_ingredient_in_kitchen(kitchen_items, current_node):
                candidate_units = foon_object_to_FU_map[node_id]
                selected_candidate_idx = candidate_units[0]  # Selecting the first path

                # Avoid revisiting already processed functional units
                if selected_candidate_idx in reference_task_tree:
                    continue
                reference_task_tree.append(selected_candidate_idx)

                # Add input nodes of the functional unit for further exploration
                sibling_nodes = []
                for input_node in foon_functional_units[selected_candidate_idx].input_nodes:
                    node_idx = input_node.id
                    flag = True
                    if input_node.label in utensils and len(input_node.ingredients) == 1:
                        for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                            if node2.label == input_node.ingredients[0] and node2.container == input_node.label:
                                flag = False
                                break
                    if flag:
                        sibling_nodes.append(node_idx)

                # Add sibling nodes to be searched next
                items_to_search = [[sibling_node, current_depth + 1] for sibling_node in sibling_nodes] + items_to_search

        if skipped_items:
            depth_limit += 1
        else:
            reference_task_tree.reverse()
            task_tree_units = [foon_functional_units[i] for i in reference_task_tree]
            return task_tree_units

# -----------------------------------------------------------------------------------------------------------------------------#

# Breadth-First Search (BFS) function 
def search_BFS(kitchen_items=[], goal_node=None, foon_object_nodes=[], foon_functional_units=[], foon_object_to_FU_map=[], utensils=[]):
    """
    Breadth-First Search (BFS) algorithm
    parameters: kitchen_items (list) - List of items in the kitchen
                goal_node (Object) - The target node to search for
                foon_object_nodes (list) - List of object nodes in the FOON
                foon_functional_units (list) - List of functional units in the FOON
                foon_object_to_FU_map (dict) - Dictionary mapping object nodes to functional units
                utensils (list) - List of utensils to check during search
    returns: task_tree_units (list) - List of functional units representing the task tree
    """
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of items already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue

        items_already_searched.append(current_item_index)
        current_item = foon_object_nodes[current_item_index]

        if not check_ingredient_in_kitchen(kitchen_items, current_item):
            candidate_units = foon_object_to_FU_map[current_item_index]
            selected_candidate_idx = candidate_units[0]  # selecting the first path

            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # all input of the selected FU need to be explored
            for node in foon_functional_units[selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[0] and node2.container == node.label:
                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    reference_task_tree.reverse()
    task_tree_units = [foon_functional_units[i] for i in reference_task_tree]
    return task_tree_units

# -----------------------------------------------------------------------------------------------------------------------------#

# Function to write the output task tree to a file
def save_task_tree_to_file(task_tree, file_path):
    """
    parameters: task_tree (list) - List of functional units to save
                file_path (str) - Path where the task tree will be saved
    """
    print(f'Writing task tree to {file_path}')
    with open(file_path, 'w') as file:
        file.write('//\n')
        for FU in task_tree:
            file.write(FU.get_FU_as_text() + "\n")

# -----------------------------------------------------------------------------------------------------------------------------#

# Reads the universal FOON from a pickle file and returns the functional units, object nodes, and object-to-FU map
def load_universal_foon(file_path='FOON.pkl'):
    """
    parameters: file_path (str) - Path to the pickle file containing FOON data
    returns: functional_units (list), object_nodes (list), object_to_FU_map (dict)
    """
    with open(file_path, 'rb') as foon_file:
        foon_data = pickle.load(foon_file)
    return foon_data["functional_units"], foon_data["object_nodes"], foon_data["object_to_FU_map"]

# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    # Load FOON data and utensils from respective files
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = load_universal_foon()

    with open('utensils.txt', 'r') as utensil_file:
        utensils = [line.strip() for line in utensil_file]

    kitchen_items = json.load(open('kitchen.json'))
    goal_nodes = json.load(open('goal_nodes.json'))
    
    # Load success rates for A* search
    success_rates = load_success_rates()

    # Search for each goal node in the FOON graph using IDS, BFS, and A* search
    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        goal_found = False
        for foon_object in foon_object_nodes:
            if foon_object.check_object_equal(node_object):
                goal_found = True

                # Perform IDS search and save the result
                task_tree_ids = search_IDS(kitchen_items, foon_object, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, utensils)
                save_task_tree_to_file(task_tree_ids, f'output_IDS_{node["label"]}.txt')

                # Perform BFS search and save the result
                task_tree_bfs = search_BFS(kitchen_items, foon_object, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, utensils)
                save_task_tree_to_file(task_tree_bfs, f'output_BFS_{node["label"]}.txt')

                # Perform A* search and save the result
                task_tree_a_star = search_A_star(kitchen_items, foon_object, success_rates, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, utensils)
                save_task_tree_to_file(task_tree_a_star, f'output_A_star_{node["label"]}.txt')

                break

        if not goal_found:
            print(f'{node_object.label} - Goal node not found')
