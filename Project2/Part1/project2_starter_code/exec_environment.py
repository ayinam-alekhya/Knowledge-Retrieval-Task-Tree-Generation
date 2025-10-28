"""
This code communicates with the CoppeliaSim software and simulates shaking a container to mix objects of different colors.

Install dependencies:
https://www.coppeliarobotics.com/helpFiles/en/zmqRemoteApiOverview.htm

MacOS: coppeliaSim.app/Contents/MacOS/coppeliaSim -GzmqRemoteApi.rpcPort=23004 ~/path/to/file/mix_Intro_to_AI.ttt
Ubuntu: ./coppeliaSim.sh -GzmqRemoteApi.rpcPort=23004 ~/path/to/file/mix_Intro_to_AI.ttt
"""

import sys
# Add the path to the zmqRemoteApi library
sys.path.append('/Users/alekhyaayinam/Desktop/Subject/Intro to AI/Ali_pro/Project2/Part1/project2_starter_code/zmqRemoteApi')
import numpy as np
from zmqRemoteApi import RemoteAPIClient
import time

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
    
    def action(self, direction=None):
        if direction not in self.directions:
            print(f'Direction: {direction} invalid, please choose one from {self.directions}')
            return
        print(f"Action taken: {direction}")

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


def main():
    episodes = 10
    steps = 20
    for episode in range(episodes):
        print(f"\nRunning episode: {episode + 1}")
        env = Simulation()
        for step in range(steps):
            direction = np.random.choice(env.directions)
            env.action(direction=direction)
            positions = env.getObjectsPositions()
            print(f"Step {step + 1}: Object positions (relative to box): {positions}")
        env.stopSim()

if __name__ == '__main__':
    main()
