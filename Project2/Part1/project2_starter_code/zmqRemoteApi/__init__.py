# import sys
# sys.path.append('..')
# from src.coppeliasim_zmqremoteapi_client import *
# print('warning: import zmqRemoteApi is deprecated. Please use import coppeliasim_zmqremoteapi_client instead.')

import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'zmqRemoteApi', 'src'))

from coppeliasim_zmqremoteapi_client import RemoteAPIClient

