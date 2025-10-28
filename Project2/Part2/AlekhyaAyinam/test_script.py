import numpy as np
from pathlib import Path
from main_script import Simulation, binaryToInteger

folder_path = Path(__file__).resolve().parent


def testModel():
    q_table = np.loadtxt(str(folder_path / "q_table.txt"))
    random_results, q_learning_results = [], []

    for test in range(10):
        print(f"Testing Episode {test + 1} - Random Actions")
        env = Simulation()
        for step in range(30):
            env.perform_action(direction=np.random.choice(env.directions))
            if env.deriveCurrentStateSpace() == "1111":
                random_results.append([True, step + 1])
                break
        else:
            random_results.append([False, 30])
        env.stop_simulation()

        print(f"Testing Episode {test + 1} - Q-Learning Actions")
        env = Simulation()
        state = binaryToInteger(env.deriveCurrentStateSpace())
        for step in range(30):
            env.perform_action(direction=env.directions[np.argmax(q_table[state])])
            if env.deriveCurrentStateSpace() == "1111":
                q_learning_results.append([True, step + 1])
                break
        else:
            q_learning_results.append([False, 30])
        env.stop_simulation()

    with open(str(folder_path / "test_results.txt"), "w") as file:
        file.write("Random Action Results:\n")
        for i, (success, steps) in enumerate(random_results):
            file.write(f"Episode {i + 1}: {'Pass' if success else 'Fail'} - {steps} steps\n")
        file.write("\nQ-Learning Results:\n")
        for i, (success, steps) in enumerate(q_learning_results):
            file.write(f"Episode {i + 1}: {'Pass' if success else 'Fail'} - {steps} steps\n")


if __name__ == '__main__':
    testModel()
