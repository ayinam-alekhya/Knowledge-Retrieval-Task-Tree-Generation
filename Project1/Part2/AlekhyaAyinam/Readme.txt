README for FOON Task Tree Extraction Project Part 2

Overview
This project implements search algorithms to extract task trees from a Functional Object-Oriented Network (FOON). The task tree outlines the steps required to prepare a dish using the available ingredients and utensils in the kitchen. We implemented two search algorithms along with given BFS: A star, Iterative Deepening Search (IDS), and Breadth-First Search (BFS).

Features:
1. A star Search: Uses a cost and heuristic function to select the most efficient path in FOON.
   - Cost function: Inverse of the success rate from the motion.txt file.
   - Heuristic: The number of input objects (fewer inputs are preferred).
   
2. Iterative Deepening Search (IDS): Increases the depth of search incrementally until a solution is found. This algorithm selects the first valid path it encounters.

3. Breadth-First Search (BFS): Explores the FOON graph level by level until it finds a solution.

Input Files:
The program requires the following input files:
1. FOON data file (FOON.pkl): Contains the structure of the FOON, including functional units and object nodes.
2. Kitchen items file (kitchen.json): Lists the ingredients and utensils available in the kitchen.
3. Goal nodes file (goal_nodes.json): Specifies the object name, state, ingredients, and container for the goal object.
4. Utensils file (utensils.txt): Lists the available utensils.
5. Motion file (motion.txt): Contains the success rates for each functional unit, used by A star search.

Output:
The program produces two task trees for each goal object:
1. Task tree from IDS (output_IDS_<goal>.txt)
2. Task tree from A star (output_A_star_<goal>.txt)

If the goal node does not exist, the program will print a message stating that the goal node was not found.

Project Files:
1. search_IDS_A_star.py: Contains the implementation of A star, IDS, and BFS search algorithms.
2. test_script.py: A test script to automatically test the search algorithms using the provided FOON data and kitchen items.
3. FOON.pkl: The FOON structure stored as a pickle file.
4. kitchen.json: JSON file containing kitchen items and utensils.
5. goal_nodes.json: JSON file with the goal object nodes.
6. utensils.txt: A text file listing the available utensils.
7. motion.txt: File containing success rates for functional units.

How to Run the Program:

1. Install Required Packages:
Ensure you have Python 3 installed. The following Python packages are required:
   - pickle (included in Python 3)
   - heapq (included in Python 3)
   - json (included in Python 3)

No external packages are needed for this project.

2. Running the Program:
The main functionality is in the search_IDS_A_star.py script, and you can test it using the provided test_script.py.

Steps to Execute:
1. Ensure that the input files (FOON.pkl, kitchen.json, goal_nodes.json, utensils.txt, and motion.txt) are in the same directory as search_IDS_A_star.py.
2. Run the test script:
   python test_script.py

This script will invoke A star and IDS searches and will save the output in separate .txt files for each goal node.

Example:

For a goal node "whipped cream":
- Output: 
  - output_IDS_whipped_cream.txt: Task tree generated using IDS.
  - output_A_star_whipped_cream.txt: Task tree generated using A star.

Project Structure:
.
├── search_IDS_A_star.py           # Main script with A star, IDS, BFS implementations
├── test_script.py                 # Test script for automating tests
├── FOON_.pkl                      # FOON data
├── kitchen.json                   # kitchen items
├── goal_nodes.json                # goal objects
├── utensils.txt                   # utensils
├── motion.txt                     # Success rates for functional units
└── output_IDS_<goal>.txt          # Task tree output from IDS (generated)
└── output_A_star_<goal>.txt       # Task tree output from A star (generated)

Notes:
- Ensure the input files are in the correct format. The FOON.pkl file must contain valid FOON data, and the kitchen.json and goal_nodes.json files must be formatted as JSON.
- The motion.txt file should be a tab-separated file with functional unit names and their success rates.

