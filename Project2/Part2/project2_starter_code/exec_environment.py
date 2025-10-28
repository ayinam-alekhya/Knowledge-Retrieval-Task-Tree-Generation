import sys
from pathlib import Path
# Add the path to the zmqRemoteApi library
sys.path.append('/Users/alekhyaayinam/Desktop/Subject/Intro to AI/Ali_pro/Project2/Part1/project2_starter_code/zmqRemoteApi')
import numpy as np
from zmqRemoteApi import RemoteAPIClient
import time

folder_path = Path(__file__).resolve().parent

class Simulation():
    def __init__(self, sim_port=23004):
        self.sim_port = sim_port
        self.directions = ['Up', 'Down', 'Left', 'Right']
        self.initializeSim()

    def initializeSim(self):
        self.client = RemoteAPIClient('localhost', port=self.sim_port)
        self.client.setStepping(True)
        self.sim = self.client.getObject('sim')
        
        # When simulation is not running, ZMQ message handling could be a bit
        # slow, since the idle loop runs at 8 Hz by default. So let's make
        # sure that the idle loop runs at full speed for this program:
        self.defaultIdleFps = self.sim.getInt32Param(self.sim.intparam_idle_fps)
        self.sim.setInt32Param(self.sim.intparam_idle_fps, 0)  
        
        self.getObjectHandles()
        self.sim.startSimulation()
        self.dropObjects()
        self.getObjectsInBoxHandles()
    
    def getObjectHandles(self):
        self.tableHandle = self.sim.getObject('/Table')
        self.boxHandle = self.sim.getObject('/Table/Box')
    
    def dropObjects(self):
        self.blocks = 18
        frictionCube = 0.06
        frictionCup = 0.8
        blockLength = 0.016
        massOfBlock = 14.375e-03
        
        self.scriptHandle = self.sim.getScript(self.sim.scripttype_childscript, self.tableHandle)
        self.client.step()
        retInts, retFloats, retStrings = self.sim.callScriptFunction(
            'setNumberOfBlocks', self.scriptHandle,
            [self.blocks],
            [massOfBlock, blockLength, frictionCube, frictionCup],
            ['cylinder']
        )
        
        print('Wait until blocks finish dropping')
        max_attempts = 1000  # Adjust as needed based on simulation speed
        attempts = 0
        while True:
            self.client.step()
            signalValue = self.sim.getFloatSignal('toPython')
            if signalValue == 99:
                break
            attempts += 1
            if attempts >= max_attempts:
                print("Warning: Timeout waiting for blocks to settle.")
                break

    
    def getObjectsInBoxHandles(self):
        self.object_shapes_handles = []
        self.obj_type = "Cylinder"
        for obj_idx in range(self.blocks):
            obj_handle = self.sim.getObject(f':/Cylinder[0]')
            self.object_shapes_handles.append(obj_handle)

    def getObjectsPositions(self):
        pos_step = []
        box_position = self.sim.getObjectPosition(self.boxHandle, self.sim.handle_world)
        for obj_handle in self.object_shapes_handles:
            # Get the starting position of each object
            obj_position = self.sim.getObjectPosition(obj_handle, self.sim.handle_world)
            obj_position = np.array(obj_position) - np.array(box_position)
            pos_step.append(list(obj_position[:2]))
        return pos_step

    def getBoxPosition(self):
        box_position = self.sim.getObjectPosition(self.boxHandle,self.sim.handle_world)
        return box_position
    
    def getAbsoluteObjectsPositions(self):
        pos_step = []
        for obj_handle in self.object_shapes_handles:
            # get the starting position of source
            obj_position = self.sim.getObjectPosition(obj_handle,self.sim.handle_world)
            pos_step.append(list(obj_position[:2]))
        return pos_step
    
    def action(self, direction=None):
        if direction not in self.directions:
            print(f'Direction: {direction} invalid, please choose one from {self.directions}')
            return

        box_position = self.sim.getObjectPosition(self.boxHandle, self.sim.handle_world)
        _box_position = box_position.copy()
        span = 0.02
        steps = 5
        if direction == 'Up':
            idx = 1
            dirs = [1, -1]
        elif direction == 'Down':
            idx = 1
            dirs = [-1, 1]
        elif direction == 'Right':
            idx = 0
            dirs = [1, -1]
        elif direction == 'Left':
            idx = 0
            dirs = [-1, 1]

        for _dir in dirs:
            for _ in range(steps):
                _box_position[idx] += _dir * span / steps
                self.sim.setObjectPosition(self.boxHandle, self.sim.handle_world, _box_position)
                self.stepSim()

    def stepSim(self):
        self.client.step()

    def stopSim(self):
        self.sim.stopSimulation()

    def findObjsDistribution(self, objs, box_position):
        objs_dist = [0, 0, 0, 0]

        for obj in objs:
            
            if obj[0] >= box_position[0]:
                # object position is towards +ve X-axis
                if obj[1] >= box_position[1]:
                    # object position is towards +ve Y-axis
                    objs_dist[0] += 1
                else:
                    # object position is towards -ve Y-axis
                    objs_dist[3] += 1
            else:
                # object position is towards -ve X-axis
                if obj[1] >= box_position[1]:
                    # object position is towards +ve Y-axis
                    objs_dist[1] += 1
                else:
                    # object position is towards -ve Y-axis
                    objs_dist[2] += 1

        return objs_dist

    def findCurrentStateSpace(self):
        box_position = self.getBoxPosition()

        positions = self.getAbsoluteObjectsPositions()
        blue_objs = positions[:9]
        red_objs = positions[9:]        

        blue_objs_dist = self.findObjsDistribution(blue_objs, box_position)
        red_objs_dist = self.findObjsDistribution(red_objs, box_position)
        
        state_space = ""
        for i in range(4):
            state = "0"
            if (blue_objs_dist[i] >= 1) and (red_objs_dist[i] >= 1) and (abs(blue_objs_dist[i] - red_objs_dist[i]) == 0):
                state = "1"
            state_space += state

        return state_space


def convertBinaryToInt(binary):
    bin_str = str(binary)
    int_value = int(bin_str, 2)
    return int_value

def calculateStateReward(state_space):
    state_space = str(state_space)
    reward = 0
    for state in state_space:
        if state == "0":
            reward -= 1
        else:
            reward += 1
    
    return reward


def train_agent():
    # initialize q-table
    q_table = []
    for i in range(16):
        q_table.append([0, 0, 0, 0])

    # initializing variables
    exploration_probability = 1
    exploration_decreasing_decay = 0.001
    min_exploration_probability = 0.05
    gamma = 0.9
    lr = 0.5

    episode_reward_array = []

    episodes = 30
    steps = 5
    for episode in range(episodes):
        print(f'Running episode: {episode + 1}')
        env = Simulation()

        total_episode_reward = 0

        current_state_space = env.findCurrentStateSpace()
        current_state = convertBinaryToInt(current_state_space)

        for step in range(steps):
            
            if np.random.uniform(0, 1) < exploration_probability:
                direction = np.random.choice(env.directions)
                direction_index = env.directions.index(direction)
            else:
                direction_index = np.argmax(q_table[current_state])
                direction = env.directions[direction_index]

            env.action(direction=direction)

            next_state_space = env.findCurrentStateSpace()
            next_state = convertBinaryToInt(next_state_space)

            reward = calculateStateReward(next_state_space)

            current_state_q_value = q_table[current_state][direction_index]
            new_q_value = (1 - lr) * current_state_q_value + lr * (reward + gamma * np.max(q_table[next_state]))

            q_table[current_state][direction_index] = new_q_value

            total_episode_reward += reward
            current_state = next_state

        exploration_probability = max(min_exploration_probability, np.exp(-exploration_decreasing_decay * episode))

        episode_reward_array.append(total_episode_reward)
        
        env.stopSim()
    
    reward_text = ""
    for i, rew in enumerate(episode_reward_array):
        reward_text += f"Episode {i + 1}: {rew}\n"
    with open(str(folder_path) + "/rewards.txt", "w") as f:
        f.write(reward_text)   

    q_table_array = np.array(q_table)
    with open(str(folder_path) + r"/q-table.txt", "w") as q_table_file:  
        np.savetxt(q_table_file, q_table_array, fmt='%.10f')


def test_agent():
    with open(str(folder_path) + r"/q-table.txt", "r") as q_table_data:  
        q_table = []
        for line in q_table_data:
            items = line.split()
            array = []
            for item in items:
                array.append(float(item))
            q_table.append(array)
    
    goal_state_space = "1111"
    goal_state = convertBinaryToInt(goal_state_space)

    random_mixes = []
    q_learning_mixes = []

    episodes = 10
    steps = 30

    print("Running random action episodes:")
    for episode in range(episodes):
        print(f'Running episode: {episode + 1}')
        random_mixes.append([False, 0])
        env = Simulation()

        for step in range(steps):
            direction = np.random.choice(env.directions)

            env.action(direction=direction)

            next_state_space = env.findCurrentStateSpace()
            next_state = convertBinaryToInt(next_state_space)

            if next_state_space == goal_state_space:
                random_mixes[episode] = [True, step + 1]
                break
    
        env.stopSim()


    print("Running q-learning driven action episodes:")
    for episode in range(episodes):
        print(f'Running episode: {episode + 1}')
        q_learning_mixes.append([False, 0])
        env = Simulation()

        current_state_space = env.findCurrentStateSpace()
        current_state = convertBinaryToInt(current_state_space)

        for step in range(steps):
            direction_index = np.argmax(q_table[current_state])
            direction = env.directions[direction_index]

            env.action(direction=direction)

            next_state_space = env.findCurrentStateSpace()
            next_state = convertBinaryToInt(next_state_space)

            if next_state_space == goal_state_space:
                q_learning_mixes[episode] = [True, step + 1]
                break
    
        env.stopSim()

    exp_text = "Random Mixes: \n"
    for i, mix in enumerate(random_mixes):
        result = "Fail"
        tries = ""
        if mix[0]:
            result = "Pass"
            tries = f" - {mix[1]} steps"
        exp_text += f"Episode {i + 1}: {result}{tries}"
        exp_text += "\n"

    exp_text += "\n"
    exp_text += "Q-Learning Mixes: \n"
    for i, mix in enumerate(q_learning_mixes):
        result = "Fail"
        tries = ""
        if mix[0]:
            result = "Pass"
            tries = f" - {mix[1]} steps"
        exp_text += f"Episode {i + 1}: {result}{tries}"
        exp_text += "\n"

    with open(str(folder_path) + "/test-agent.txt", "w") as f:
        f.write(exp_text)

def main():
    train_agent()
    test_agent()
        

if __name__ == '__main__':
    main()
