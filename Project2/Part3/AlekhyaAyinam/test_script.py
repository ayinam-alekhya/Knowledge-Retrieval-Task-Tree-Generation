import numpy as np
from tensorflow.keras.models import load_model
from pathlib import Path
from main_script import EnvironmentSimulator, binary_to_array

# Path configuration
project_dir = Path(__file__).resolve().parent
trained_model_file = 'DeepQNetwork_model.h5'

def compute_reward(state):
    return sum(1 if char == "1" else -1 for char in state)

def test_trained_dqn():
    # Parameters for testing
    state_size = 4
    action_size = 4
    episodes = 100  # Number of testing episodes
    steps_per_episode = 30

    # Load the trained model
    trained_model_file = 'DeepQNetwork_model.h5'
    model = load_model(trained_model_file)

    # Initialize results
    successful_trials = 0
    test_results = []

    for episode in range(episodes):
        print(f'Running Test Episode {episode + 1}')
        environment = EnvironmentSimulator()
        current_state_binary = environment.derive_state_representation()
        current_state = binary_to_array(current_state_binary)
        episode_success = False

        for step in range(steps_per_episode):
            # Predict the best action based on the current state
            q_values = model.predict(current_state, verbose=0)
            action = np.argmax(q_values[0])

            # Perform the action in the environment
            environment.move_container(environment.movements[action])

            # Get the next state
            next_state_binary = environment.derive_state_representation()
            current_state = binary_to_array(next_state_binary)

            # Check if goal state is reached
            if next_state_binary == "1111":
                successful_trials += 1
                test_results.append(f"Episode {episode + 1}: Success in {step + 1} steps")
                episode_success = True
                break

        if not episode_success:
            test_results.append(f"Episode {episode + 1}: Failed")

        environment.stop_simulation()

    # Save results to a .txt file
    results_file = project_dir / "test_results.txt"
    with open(results_file, "w") as file:
        for result in test_results:
            file.write(result + "\n")
        file.write(f"\nTotal Successful Trials: {successful_trials} out of {episodes}\n")

    print(f"Test results saved to {results_file}")


if __name__ == '__main__':
    test_trained_dqn()
