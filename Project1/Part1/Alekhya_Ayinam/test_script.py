import json
from search import read_universal_foon, search_BFS, save_paths_to_file
from FOON_class import Object

def load_kitchen_items_and_utensils(kitchen_filepath, utensils_filepath):
    """
    Load kitchen items and utensils from files.
    """
    with open(kitchen_filepath, 'r') as kitchen_file:
        kitchen_items = json.load(kitchen_file)
    
    utensils = []
    with open(utensils_filepath, 'r') as utensil_file:
        for line in utensil_file:
            utensils.append(line.strip())
    
    return kitchen_items, utensils

def find_functional_units_for_kitchen_items(kitchen_items, utensils, foon_functional_units, foon_object_nodes):
    """
    For each item in the kitchen or utensils, find the functional units where they are input or output,
    and write the results to a text file.
    """
    with open("kitchen_items_functional_units.txt", "w") as f:
        for item in kitchen_items:
            item_object = Object(item["label"])
            item_object.states = item.get("states", [])
            item_object.ingredients = item.get("ingredients", [])
            item_object.container = item.get("container", None)
            
            f.write(f"Searching functional units for kitchen item: {item['label']}\n")
            search_functional_units(item_object, foon_functional_units, f)
        
        for utensil in utensils:
            utensil_object = Object(utensil)
            utensil_object.states = []
            utensil_object.ingredients = []
            utensil_object.container = None
            
            f.write(f"Searching functional units for utensil: {utensil}\n")
            search_functional_units(utensil_object, foon_functional_units, f)

def search_functional_units(item_object, foon_functional_units, file_handle):
    """
    Search for functional units where the given item_object is either an input or an output,
    and write the results to the file.
    """
    found_units = []
    
    for FU in foon_functional_units:
        # Check if the item is an input or output node
        input_found = False
        output_found = False
        
        for input_node in FU.input_nodes:
            if input_node.check_object_equal(item_object):
                input_found = True
                break
        
        for output_node in FU.output_nodes:
            if output_node.check_object_equal(item_object):
                output_found = True
                break

        # Write messages before writing the functional unit to the file
        if input_found:
            file_handle.write(f"Found in input of functional unit:\n{FU.get_FU_as_text()}\n")
            found_units.append(FU)
        
        if output_found:
            file_handle.write(f"Found in output of functional unit:\n{FU.get_FU_as_text()}\n")
            found_units.append(FU)
    
    if not found_units:
        file_handle.write(f"No functional units found for {item_object.label}\n")


def find_goal_functional_units(goal_nodes, kitchen_items, foon_functional_units, foon_object_nodes, foon_object_to_FU_map, utensils):
    """
    For each goal node, find the relevant functional units where the goal node is in the output nodes.
    """
    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                # Perform BFS search to get the task tree
                output_task_tree = search_BFS(kitchen_items, object, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, utensils)
                
                # Now, find functional units where this node_object is in the output
                print(f"Functional units for goal node {node['label']}:")
                goal_units = []
                for FU in output_task_tree:
                    for output_node in FU.output_nodes:
                        if output_node.check_object_equal(node_object):
                            print(FU.get_FU_as_text())  # Output the functional unit where the goal node is an output
                            goal_units.append(FU)

                # Save paths for these functional units (optional)
                if goal_units:
                    save_paths_to_file(goal_units, 'Goal_nodes_FunctionalUnits_{}.txt'.format(node["label"]))

                break

if __name__ == '__main__':
    # Load the FOON data
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon()

    # Load utensils and kitchen items
    kitchen_items, utensils = load_kitchen_items_and_utensils('kitchen.json', 'utensils.txt')

    # Load goal nodes
    goal_nodes = json.load(open("goal_nodes.json"))

    # Find functional units for each kitchen item and utensil and store output in a text file
    find_functional_units_for_kitchen_items(kitchen_items, utensils, foon_functional_units, foon_object_nodes)

    # Find functional units for each goal node
    find_goal_functional_units(goal_nodes, kitchen_items, foon_functional_units, foon_object_nodes, foon_object_to_FU_map, utensils)
