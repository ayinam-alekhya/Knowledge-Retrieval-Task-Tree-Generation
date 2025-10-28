KNOWLEDGE RETRIEVAL (PART 1)  - README


Overview


This program helps find functional units from a FOON (Functional Object-Oriented Network) based on kitchen items, utensils, and goal nodes. It identifies functional units for each kitchen item, utensil, and the goal nodes provided in `goal_nodes.json`.


Files Required


Make sure these files are in the same folder as `test_script.py` before running the program:


- FOON_class.py: Defines the `Object` class and methods for handling FOON objects.
- FOON.txt: The FOON network in a text file (initial format).
- FOON.pkl: A pickled file that contains the FOON network (functional units, object nodes, and mappings).
- goal_nodes.json: Lists the goal nodes you want to search for in FOON.
- kitchen.json: Lists the kitchen items available for use.
- utensils.txt: Contains a list of utensils available in the kitchen.
- search.py: Contains search functions for performing BFS and interacting with FOON.
- preprocess.py: A script for preprocessing FOON data (if needed).
- test_script.py: The main script that ties everything together and runs the program.


Prerequisites


1. Python 3.6 must be installed.
2. All files mentioned above should be in the same folder.


Running the Program
Once you have all the files in the same folder, run the script with this command:
1. Step 1: Open a terminal or command prompt.
2. Step 2: Navigate to the directory where all files are located.
3. Step 3: Run the main script using Python:
                python test_script.py


What the Program Does


1. Loads FOON data:
   - If you haven't already, run preprocess.py to convert FOON.txt into FOON.pkl .Reads the FOON network from `FOON.pkl` using functions from `search.py`.


2. Processes Kitchen Items and Utensils:
   - Reads kitchen items from `kitchen.json` and utensils from `utensils.txt`.
   - Searches for functional units in FOON where these items are either input or output nodes.
   - Results are saved to a file called `kitchen_items_functional_units.txt`.


3. Searches for Goal Nodes:
   - Reads the goal nodes from `goal_nodes.json`.
   - Searches the FOON for task trees using the BFS-based `search_BFS()` function.
   - Identifies functional units where the goal nodes are output nodes.
   - Results are printed to the console and optionally saved to files named ‘Goal_nodes_FunctionalUnits_<goal_label>.txt’.


Output Files


- The results for kitchen items and utensils will be saved in ‘kitchen_items_functional_units.txt’.
- If any goal nodes are found, separate files will be created with names like ‘Goal_nodes_FunctionalUnits_<goal_label>.txt’, each containing the functional units for that specific goal node.


Troubleshooting


- File not found error: Make sure all files are in the same directory.
- JSON decoding errors: Double-check that `kitchen.json` and `goal_nodes.json` are correctly formatted.
- Python issues: Ensure you're using Python 3.6+ and have all required files in the same folder.