import sys
import numpy as np
# Change to the path of your ZMQ python API
sys.path.append('\zmqRemoteApi')
import random
import tensorflow as tf
from tensorflow.keras import layers
from pathlib import Path
from zmqRemoteApi import RemoteAPIClient

# Path configuration
project_dir = Path(__file__).resolve().parent
trained_model_file = 'DeepQNetwork_model.h5'

class EnvironmentSimulator:
    def __init__(self, port=23000):
        self.port = port
        self.movements = ['Up', 'Down', 'Left', 'Right']
        self.setup_environment()

    def setup_environment(self):
        self.client = RemoteAPIClient('localhost', port=self.port)
        self.client.setStepping(True)
        self.simulation = self.client.getObject('sim')

        self.default_idle_speed = self.simulation.getInt32Param(self.simulation.intparam_idle_fps)
        self.simulation.setInt32Param(self.simulation.intparam_idle_fps, 0)

        self.identify_simulation_objects()
        self.simulation.startSimulation()
        self.spawn_objects()
        self.track_objects()

    def identify_simulation_objects(self):
        self.table = self.simulation.getObject('/Table')
        self.container = self.simulation.getObject('/Table/Box')

    def spawn_objects(self):
        self.total_blocks = 18
        block_friction = 0.06
        cup_friction = 0.8
        block_size = 0.016
        block_mass = 14.375e-03

        child_script = self.simulation.getScript(self.simulation.scripttype_childscript, self.table)
        self.client.step()
        self.simulation.callScriptFunction(
            'setNumberOfBlocks', child_script,
            [self.total_blocks], [block_mass, block_size, block_friction, cup_friction], ['cylinder']
        )

        while True:
            self.client.step()
            signal = self.simulation.getFloatSignal('toPython')
            if signal == 99:
                for _ in range(20):
                    self.client.step()
                break

    def track_objects(self):
        self.objects_in_box = []
        obj_type = "Cylinder"
        for i in range(self.total_blocks):
            handle = self.simulation.getObjectHandle(f'{obj_type}{i}')
            self.objects_in_box.append(handle)

    def fetch_container_position(self):
        return self.simulation.getObjectPosition(self.container, self.simulation.handle_world)

    def fetch_object_positions(self):
        positions = []
        for obj in self.objects_in_box:
            position = self.simulation.getObjectPosition(obj, self.simulation.handle_world)
            positions.append(list(position[:2]))
        return positions

    def calculate_quadrant_distribution(self, objects, container_position):
        quadrant_counts = [0, 0, 0, 0]
        for obj in objects:
            if obj[0] >= container_position[0]:
                if obj[1] >= container_position[1]:
                    quadrant_counts[0] += 1
                else:
                    quadrant_counts[3] += 1
            else:
                if obj[1] >= container_position[1]:
                    quadrant_counts[1] += 1
                else:
                    quadrant_counts[2] += 1
        return quadrant_counts

    def derive_state_representation(self):
        container_position = self.fetch_container_position()
        object_positions = self.fetch_object_positions()
        blue_objects = object_positions[:9]
        red_objects = object_positions[9:]

        blue_distribution = self.calculate_quadrant_distribution(blue_objects, container_position)
        red_distribution = self.calculate_quadrant_distribution(red_objects, container_position)

        state = ""
        for i in range(4):
            if blue_distribution[i] >= 1 and red_distribution[i] >= 1 and abs(blue_distribution[i] - red_distribution[i]) == 0:
                state += "1"
            else:
                state += "0"

        return state

    def move_container(self, movement=None):
        if movement not in self.movements:
            print(f'Invalid movement: {movement}. Choose from {self.movements}')
            return

        container_position = self.simulation.getObjectPosition(self.container, self.simulation.handle_world)
        shift_distance = 0.02
        steps = 5
        index, directions = (1, [1, -1]) if movement in ['Up', 'Down'] else (0, [1, -1])

        for direction in directions:
            for _ in range(steps):
                container_position[index] += direction * shift_distance / steps
                self.simulation.setObjectPosition(self.container, self.simulation.handle_world, container_position)
                self.client.step()

    def stop_simulation(self):
        self.simulation.stopSimulation()


class DQN:
    def __init__(self, input_size, output_size):
        self.input_size = input_size
        self.output_size = output_size
        self.experiences = []
        self.discount_factor = 0.85
        self.exploration_rate = 1.0
        self.min_exploration = 0.01
        self.exploration_decay = 0.995
        self.learning_rate = 0.005
        self.network = self.create_network()

    def create_network(self):
        model = tf.keras.Sequential([
            layers.Dense(32, activation='relu', input_dim=self.input_size),
            layers.Dense(32, activation='relu'),
            layers.Dense(self.output_size, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), loss='mse')
        return model

    def store_experience(self, state, action, reward, next_state, is_terminal):
        self.experiences.append((state, action, reward, next_state, is_terminal))

    def select_action(self, state):
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(self.output_size)
        predictions = self.network.predict(state, verbose=0)
        return np.argmax(predictions[0])

    def update_model(self, batch_size):
        if len(self.experiences) < batch_size:
            return

        # Randomly sample a minibatch from experiences
        minibatch = random.sample(self.experiences, batch_size)

        for state, action, reward, next_state, terminal in minibatch:
            target = reward
            if not terminal:
                target += self.discount_factor * np.amax(self.network.predict(next_state, verbose=0)[0])

            target_vector = self.network.predict(state, verbose=0)
            target_vector[0][action] = target
            self.network.fit(state, target_vector, epochs=1, verbose=0)

        # Decay exploration rate
        if self.exploration_rate > self.min_exploration:
            self.exploration_rate *= self.exploration_decay


def binary_to_array(binary):
    return np.array([[int(char) for char in str(binary)]])

def compute_reward(state):
    return sum(1 if char == "1" else -1 for char in state)

def train_dqn():
    state_size = 4
    action_size = 4
    agent = DQN(state_size, action_size)

    total_episodes = 300
    steps_per_episode = 30
    batch_size = 32
    training_log = []  # To store episode rewards and TD errors

    for episode in range(total_episodes):
        print(f'Starting Episode {episode + 1}')
        environment = EnvironmentSimulator()
        current_state_binary = environment.derive_state_representation()
        current_state = binary_to_array(current_state_binary)

        episode_reward = 0

        for step in range(steps_per_episode):
            # Select an action using the policy
            action = agent.select_action(current_state)
            # Perform the action in the environment
            environment.move_container(environment.movements[action])
            # Get the new state
            next_state_binary = environment.derive_state_representation()
            next_state = binary_to_array(next_state_binary)
            # Compute the reward for the new state
            reward = compute_reward(next_state_binary)
            terminal_state = next_state_binary == "1111"

            # Store experience in the replay buffer
            agent.store_experience(current_state, action, reward, next_state, terminal_state)
            # Update episode reward
            episode_reward += reward
            current_state = next_state

            if terminal_state:
                break

        # Perform DQN updates and log TD errors
        td_errors = []  # To store TD errors for the current episode
        if len(agent.experiences) >= batch_size:
            minibatch = random.sample(agent.experiences, batch_size)

            for state, action, reward, next_state, terminal in minibatch:
                target = reward
                if not terminal:
                    target += agent.discount_factor * np.amax(agent.network.predict(next_state, verbose=0)[0])

                target_vector = agent.network.predict(state, verbose=0)
                td_error = target - target_vector[0][action]  # Calculate TD error
                td_errors.append(td_error)

                target_vector[0][action] = target
                agent.network.fit(state, target_vector, epochs=1, verbose=0)

            # Decay exploration rate
            if agent.exploration_rate > agent.min_exploration:
                agent.exploration_rate *= agent.exploration_decay

        # Log episode reward and TD errors
        training_log.append(f"Episode {episode + 1}, Reward: {episode_reward}, Epsilon: {agent.exploration_rate:.3f}")
        training_log.append(f"TD Errors: {td_errors}")
        environment.stop_simulation()

    # Save the training log to a .txt file
    training_log_file = project_dir / "training_log.txt"
    with open(training_log_file, "w") as file:
        for log in training_log:
            file.write(log + "\n")

    print(f"Training log saved to {training_log_file}")

    # Save the trained model in .h5 format
    trained_model_file = 'DeepQNetwork_model.h5'
    agent.network.save(trained_model_file)
    print(f"Model saved as {trained_model_file}")

if __name__ == '__main__':
    train_dqn()
