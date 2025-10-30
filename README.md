# Introduction to AI – Projects Overview

This repository contains two major projects completed as part of the **CAP5625 – Introduction to AI** course.  
Each project focuses on implementing foundational AI concepts through practical, simulation-based tasks.  

---

## 📂 Project 1: Knowledge Retrieval (FOON-Based Task Tree Generation)

### Overview
Project 1 explores **Functional Object-Oriented Networks (FOON)** — a structured knowledge representation used by robots to understand object–action relationships for performing manipulation tasks.  
Across three parts, this project implements progressively advanced **search algorithms** to retrieve optimal *task trees* (subgraphs) for preparing a goal object or dish.

### Structure
```
Project1/
│
├── Part1_Knowledge_Annotation/
│   ├── FOON txt files, sample kitchen, goal files
│   ├── Annotation script and visualization link
│   └── README.md
│
├── Part2_Search_Algorithms/
│   ├── Iterative Deepening Search (IDS)
│   ├── A* Search with cost and heuristic
│   └── README.md
│
└── Part3_MonteCarloTreeSearch/
    ├── MCTS implementation
    ├── motion.txt success rates integration
    └── README.md
```

### Part 1: FOON Annotation and Knowledge Representation
- Learned how **FOON graphs** encode relationships between objects, states, and motions.  
- Annotated actions into **functional units** (input objects → motion → output objects).  
- Parsed and visualized FOON graphs using the online FOON Visualizer.  
- Implemented a basic Python function to:
  - Load FOON files  
  - Retrieve functional units containing a goal object  
  - Identify available ingredients and utensils from a kitchen file  

### Part 2: Task Tree Extraction using Search Algorithms
- Implemented **Iterative Deepening Search (IDS)** and **A\*** to retrieve task trees for given goal objects.
- **IDS:** Explores nodes incrementally by depth until the goal is found.  
- **A\***: Uses a custom cost function (based on inverse of success rates) and heuristic (number of input objects) for optimal path selection.
- Generated two task tree outputs (`IDS_tree.txt`, `Astar_tree.txt`) and validated their correctness via FOON visualization.

### Part 3: Monte Carlo Tree Search (MCTS)
- Implemented **MCTS** to simulate random executions of task trees and optimize decision-making under uncertainty.
- Integrated success rates from `motion.txt` to probabilistically evaluate motion success.
- Performed:
  - **Simulation:** Random rollouts to estimate success
  - **Selection & Expansion:** Node exploration via exploitation vs. exploration balance
  - **Backpropagation:** Updating success statistics through the search tree
- Produced final **MCTS-based task tree** demonstrating adaptive, data-driven decision selection.

---

## 🤖 Project 2: Reinforcement Learning for Robotic Mixing & Aiming

### Overview
Project 2 introduces **Reinforcement Learning (RL)** through progressively complex implementations — from Q-Learning to Deep Q-Networks — to train an agent in the **CoppeliaSim** robotic simulator.  
The agent learns to mix two types of objects (e.g., liquids or solids) efficiently and later extend this learning to aiming tasks.

### Structure
```
Project2/
│
├── Part1_Environment_Setup/
│   ├── Scene setup using CoppeliaSim + ZeroMQ Remote API
│   └── Random action baseline + State/Action/Reward definitions
│
├── Part2_Q_Learning/
│   ├── Implementation of tabular Q-learning
│   ├── Q-table training, testing, and performance comparison
│   └── Reward logs per episode
│
└── Part3_Deep_Q_Learning/
    ├── DQN implementation using neural network
    ├── Training and evaluation logs
    └── Comparison of DQN vs. Q-learning performance
```

### Part 1: Environment Setup
- Configured **CoppeliaSim** environment and Python–Coppelia interface using **ZeroMQ Remote API**.  
- Implemented a baseline agent taking random actions to explore the environment.  
- Defined:
  - **State space:** Object positions, mixing uniformity  
  - **Action space:** Robot’s possible motions (e.g., stirring directions or speeds)  
  - **Reward function:** Based on the uniformity of mixing achieved  

### Part 2: Q-Learning Implementation
- Implemented **tabular Q-learning** to train the agent for optimal mixing.  
- Key tasks:
  - Initialized and updated the **Q-table**
  - Balanced exploration–exploitation using ε-greedy policy
  - Recorded reward per episode for performance tracking  
- Compared performance between:
  - Random action policy  
  - Learned Q-learning policy (showing higher success and efficiency)

### Part 3: Deep Q-Learning (DQN)
- Transitioned from discrete Q-table to **Deep Q-Network (DQN)** for continuous state representation.  
- Used a neural network to approximate the Q-function.  
- Tracked:
  - **Training rewards and TD errors**  
  - **Success rates over 100 trials**  
- Demonstrated improved convergence and generalization compared to tabular Q-learning.

---

## 🧩 Technologies & Tools
- **Languages:** Python 3  
- **Frameworks/Libraries:** NumPy, Matplotlib, PyTorch (for DQN)  
- **Simulation:** CoppeliaSim + ZeroMQ Remote API  
- **Data Representation:** FOON graphs, .txt formatted task trees  
- **Algorithms:** IDS, A\*, MCTS, Q-Learning, Deep Q-Learning  

---

## 🚀 How to Run
Each project folder contains its own `README.md` with environment setup, dependencies, and sample commands.  
Example (for Project 2):
```bash
python q_learning_train.py
python test_agent.py
```

For Project 1:
```bash
python foon_search.py --goal "scrambled egg" --state "cooked"
```

---

## 🎯 Learning Outcomes
- Understood **knowledge representation** for intelligent agents (FOON).  
- Applied **search algorithms** for reasoning and planning.  
- Gained hands-on experience with **Reinforcement Learning**, training agents in simulated environments.  
- Integrated classical AI methods and modern learning-based approaches.

---

## 📁 Repository Structure
```
Knowledge_Retrieval_Task_Tree_Generation/
├── Project1/
│   ├── Part1/
│   ├── Part2/
│   └── Part3/
└── Project2/
    ├── Part1/
    ├── Part2/
    └── Part3/
```

---

### Author
**Alekhya Ayinam**  
*Master’s in Computer Science – University of South Florida*  
📧 [alekhyaayinam@usf.edu](mailto:alekhyaayinam@usf.edu)
