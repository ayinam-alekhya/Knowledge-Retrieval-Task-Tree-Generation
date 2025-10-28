import sys
import numpy as np
# Change to the path of your ZMQ python API
sys.path.append('\zmqRemoteApi')
from pathlib import Path
from zmqRemoteApi import RemoteAPIClient
import time

folder_path = Path(__file__).resolve().parent


class Simulation:
    def __init__(self, sim_port=23000):
        self.sim_port = sim_port
        self.directions = ['Up', 'Down', 'Left', 'Right']
        self.initialize_simulation()

    def initialize_simulation(self):
        self.client = RemoteAPIClient('localhost', port=self.sim_port)
        self.client.setStepping(True)
        self.sim = self.client.getObject('sim')

        self.default_idle_fps = self.sim.getInt32Param(self.sim.intparam_idle_fps)
        self.sim.setInt32Param(self.sim.intparam_idle_fps, 0)

        self.get_object_handles()
        self.sim.startSimulation()
        self.drop_objects()
        self.get_object_handles_in_box()

    def get_object_handles(self):
        self.table_handle = self.sim.getObject('/Table')
        self.box_handle = self.sim.getObject('/Table/Box')

    def drop_objects(self):
        self.num_blocks = 18
        friction_cube = 0.06
        friction_cup = 0.8
        block_length = 0.016
        block_mass = 14.375e-03

        script_handle = self.sim.getScript(self.sim.scripttype_childscript, self.table_handle)
        self.client.step()
        self.sim.callScriptFunction(
            'setNumberOfBlocks', script_handle,
            [self.num_blocks], [block_mass, block_length, friction_cube, friction_cup], ['cylinder']
        )

        while True:
            self.client.step()
            signal = self.sim.getFloatSignal('toPython')
            if signal == 99:
                for _ in range(20):
                    self.client.step()
                break

    def get_object_handles_in_box(self):
        self.object_handles = []
        self.obj_type = "Cylinder"
        for idx in range(self.num_blocks):
            handle = self.sim.getObjectHandle(f'{self.obj_type}{idx}')
            self.object_handles.append(handle)

    def fetchBoxPosition(self):
        return self.sim.getObjectPosition(self.box_handle, self.sim.handle_world)

    def fetchAbsoluteObjectPositions(self):
        positions = []
        for handle in self.object_handles:
            position = self.sim.getObjectPosition(handle, self.sim.handle_world)
            positions.append(list(position[:2]))
        return positions

    def determineObjectDistribution(self, objects, box_position):
        distribution = [0, 0, 0, 0]
        for obj in objects:
            if obj[0] >= box_position[0]:
                if obj[1] >= box_position[1]:
                    distribution[0] += 1
                else:
                    distribution[3] += 1
            else:
                if obj[1] >= box_position[1]:
                    distribution[1] += 1
                else:
                    distribution[2] += 1
        return distribution

    def deriveCurrentStateSpace(self):
        box_position = self.fetchBoxPosition()
        positions = self.fetchAbsoluteObjectPositions()
        blue_objects = positions[:9]
        red_objects = positions[9:]

        blue_dist = self.determineObjectDistribution(blue_objects, box_position)
        red_dist = self.determineObjectDistribution(red_objects, box_position)

        state_space = ""
        for i in range(4):
            if blue_dist[i] >= 1 and red_dist[i] >= 1 and abs(blue_dist[i] - red_dist[i]) == 0:
                state_space += "1"
            else:
                state_space += "0"

        return state_space

    def perform_action(self, direction=None):
        if direction not in self.directions:
            print(f'Invalid direction: {direction}. Choose from {self.directions}')
            return

        box_position = self.sim.getObjectPosition(self.box_handle, self.sim.handle_world)
        movement = 0.02
        steps = 5
        idx, dir_values = (1, [1, -1]) if direction in ['Up', 'Down'] else (0, [1, -1])

        for dir_value in dir_values:
            for _ in range(steps):
                box_position[idx] += dir_value * movement / steps
                self.sim.setObjectPosition(self.box_handle, self.sim.handle_world, box_position)
                self.client.step()

    def stop_simulation(self):
        self.sim.stopSimulation()


def binaryToInteger(binary_string):
    return int(str(binary_string), 2)


def computeStateReward(state_representation):
    return sum(1 if state == "1" else -1 for state in state_representation)


def trainModel():
    q_table = np.zeros((16, 4))
    exploration_rate = 1.0
    decay_rate = 0.001
    min_exploration = 0.01
    discount_factor = 0.85
    learning_rate = 0.2
    total_rewards = []

    for episode in range(200):
        print(f"Training Episode {episode + 1}")
        env = Simulation()
        total_episode_reward = 0
        current_state = binaryToInteger(env.deriveCurrentStateSpace())

        for _ in range(30):
            action = np.random.choice(len(env.directions)) if np.random.rand() < exploration_rate else np.argmax(q_table[current_state])
            env.perform_action(direction=env.directions[action])
            next_state = binaryToInteger(env.deriveCurrentStateSpace())
            reward = computeStateReward(env.deriveCurrentStateSpace())

            q_table[current_state, action] = (1 - learning_rate) * q_table[current_state, action] + \
                                              learning_rate * (reward + discount_factor * np.max(q_table[next_state]))
            total_episode_reward += reward
            current_state = next_state

        exploration_rate = max(min_exploration, np.exp(-decay_rate * episode))
        total_rewards.append(total_episode_reward)
        env.stop_simulation()

    with open(str(folder_path / "episode_rewards.txt"), "w") as file:
        for i, reward in enumerate(total_rewards):
            file.write(f"Episode {i + 1}: {reward}\n")

    np.savetxt(str(folder_path / "q_table.txt"), q_table, fmt="%.10f")


if __name__ == '__main__':
    trainModel()
