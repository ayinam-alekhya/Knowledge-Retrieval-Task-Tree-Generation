import json
import pickle
from FOON_class import Object
from search_IDS_A_star import search_IDS, search_A_star, load_universal_foon, load_success_rates, save_task_tree_to_file

# Utility function to create a dummy object for testing
def create_test_object(label, states, ingredients, container):
    obj = Object(label)
    obj.states = states
    obj.ingredients = ingredients
    obj.container = container
    return obj

def find_goal_node_in_foon(goal_object, foon_object_nodes):
    """
    Find the corresponding goal node in the FOON object nodes.
    If a matching node is found, return the node with its id.
    """
    for node in foon_object_nodes:
        if (node.label == goal_object.label and
            sorted(node.states) == sorted(goal_object.states) and
            sorted(node.ingredients) == sorted(goal_object.ingredients) and
            node.container == goal_object.container):
            return node
    return None

def load_test_data():
    """
    Load all necessary test data for the searches.
    """
    # Load FOON data (can replace with test data path)
    functional_units, object_nodes, object_to_FU_map = load_universal_foon('FOON.pkl')
    
    # Load kitchen items (can replace with actual test data)
    with open('kitchen.json', 'r') as kitchen_file:
        kitchen_items = json.load(kitchen_file)
    
    # Load goal nodes (can replace with actual test data)
    with open('goal_nodes.json', 'r') as goal_file:
        goal_nodes = json.load(goal_file)
    
    # Load utensils
    with open('utensils.txt', 'r') as utensil_file:
        utensils = [line.strip() for line in utensil_file]
    
    # Load success rates for A* search 
    success_rates = load_success_rates('motion.txt')
    
    return functional_units, object_nodes, object_to_FU_map, kitchen_items, goal_nodes, utensils, success_rates

# Test IDS search
def test_IDS_search():
    functional_units, object_nodes, object_to_FU_map, kitchen_items, goal_nodes, utensils, _ = load_test_data()
    
    # Pick a goal node from the test data
    for goal in goal_nodes:
        goal_object = create_test_object(goal["label"], goal["states"], goal["ingredients"], goal["container"])
        
        # Find the matching goal node in FOON object nodes
        foon_goal_node = find_goal_node_in_foon(goal_object, object_nodes)
        
        if foon_goal_node is None:
            print(f"Goal node {goal['label']} not found in FOON")
            continue
        
        # Perform IDS search
        print(f"Testing IDS search for goal: {goal['label']}")
        result = search_IDS(kitchen_items, foon_goal_node, object_nodes, functional_units, object_to_FU_map, utensils)
        
        # Save the output (adjust file path if needed)
        save_task_tree_to_file(result, f'Test_IDS_output_{goal["label"]}.txt')
        
        # Assert that result is not empty (you can replace with more specific assertions)
        assert result, f"IDS failed to find a solution for {goal['label']}"
        print(f"IDS search for {goal['label']} passed.\n")

# Test A* search
def test_A_star_search():
    functional_units, object_nodes, object_to_FU_map, kitchen_items, goal_nodes, utensils, success_rates = load_test_data()

    # Pick a goal node from the test data
    for goal in goal_nodes:
        goal_object = create_test_object(goal["label"], goal["states"], goal["ingredients"], goal["container"])
        
        # Find the matching goal node in FOON object nodes
        foon_goal_node = find_goal_node_in_foon(goal_object, object_nodes)
        
        if foon_goal_node is None:
            print(f"Goal node {goal['label']} not found in FOON")
            continue
        
        # Perform A* search
        print(f"Testing A* search for goal: {goal['label']}")
        result = search_A_star(kitchen_items, foon_goal_node, success_rates, object_nodes, functional_units, object_to_FU_map, utensils)
        
        # Save the output (adjust file path if needed)
        save_task_tree_to_file(result, f'Test_A_star_output_{goal["label"]}.txt')
        
        # Assert that result is not empty (you can replace with more specific assertions)
        assert result, f"A* failed to find a solution for {goal['label']}"
        print(f"A* search for {goal['label']} passed.\n")


if __name__ == '__main__':
    # Run IDS search test
    test_IDS_search()

    # Run A* search test
    test_A_star_search()

 
