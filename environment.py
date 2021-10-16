from __future__ import division
from __future__ import print_function

import abc
import tensorflow as tf
import numpy as np

import tf_agents
from tf_agents.environments import py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import tf_py_environment
from tf_agents.environments import utils
from tf_agents.specs import array_spec
from tf_agents.environments import wrappers
from tf_agents.environments import suite_gym
from tf_agents.trajectories import time_step as ts

from pynput.keyboard import Key, Controller
from tf_agents.typing.types import Optimizer

from ScreenCapture.render import get_screen
from ClientInput.pressKey import execute_action


class CSGOEnvironment(py_environment.PyEnvironment):

    def __init__(self):

        # self.action_spec = array.spec.BoundedArraySpec(shape = (5,), dtype = np.int32, minimum = [0, 0, 0, 0, 0], maximum = [1, 1, 1, 1, 1], name = 'action')
        self._action_spec = array_spec.BoundedArraySpec((1,), dtype = np.float32, minimum = 0, maximum = 1, name = 'action')

        self._observation_spec = {

            # Screenshot of game. Array is the dimensions of the image.
            'image': array_spec.BoundedArraySpec((480, 640, 4), np.float32, minimum=0,
                                                maximum=255),
            # Observation of the current client state in the game. This will change.
            # 'gamestate': array_spec.BoundedArraySpec((4,), np.int32, minimum=0, maximum = 1)}
            'gamestate': array_spec.BoundedArraySpec((4,), np.float32, minimum=0,
                                                maximum=1)}

        self._state = [0,0,0,0,0]
        self._episode_ended = False

        self.controller = Controller()
        self._num_actions = 4

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec
# Game ends so restart.
    def _reset(self):
    # TODO: Restart CSGO.

        self._state = [0, 0, 0, 0, 0]
        self._episode_ended = False
        # return ts.restart(np.array([self._state], dtype=np.int32))
        return ts.restart(self.render())

    def _step(self, action):
        if self._episode_ended:
        # The last action ended the episode. Ignore the current action and start
        # a new episode.
            return self.reset()
        # Execute movement in game.
        # self.move(action)
        execute_action(action, self.controller)

        if self.game_over():
            return ts.termination(np.array(self._state, dtype=np.int32), 0)

        if self._episode_ended:
            return ts.termination(observation = [self.render(), np.zeros(4)], reward=reward, discount=1.0)

        # for movement in action:
        #     if movement:
        #         reward = 100
        #         return ts.transition(observation = [self.render(), np.zeros(4)], reward=reward, discount=1.0)
        #     else:
        #         return ts.transition(observation = [self.render(), np.zeros(4)], reward=0.0, discount=1.0)
        if action[0]:
            reward = 100
            return ts.transition(observation = [self.render(), np.zeros(4)], reward=reward, discount=1.0)
        elif action[1]:
            reward = 100
            return ts.transition(observation = [self.render(), np.zeros(4)], reward=reward, discount=1.0)
        else:
            reward = 0
            return ts.transition(observation = [self.render(), np.zeros(4)], reward=0.0, discount=1.0)

    def render(self, mode='rgb_array'):

        # Grab screenshot of CSGO and normalize.
        # return np.divide(get_screen(), 255, dtype=np.float32)


    # def move(self, action):
    #     # TODO: For every action, simulate a key press and then execute.
    #     if action[0]:
    #     print('Move Forward')
    #     if action[1]:
    #     print('Move Backwards')
    #     if action[2]:
    #     print('Move Right')
    #     if action[3]:
    #     print('Move Left')
    #     if action[4]:
    #     print('Shoot')
        return np.zeros(shape=(4,), dtype=np.float32), np.divide(get_screen(), 255, dtype=np.float32)

    def game_over(self):
        return self._episode_ended

if __name__ == '__main__':

    # action_array = np.zeros(shape=(5,), dtype=np.int32)
    action_array = np.zeros(shape=(4,), dtype=np.int32)
    print('action')
    # Adjust the action array to adjust the actions.

    action_array[3] = 1

    # environment = CSGOEnvironment()
    # print('env')
    # time_step = environment.reset()
    # print(time_step)
    # cumulative_reward = time_step.reward

    env = CSGOEnvironment()
    print('env')
    tf_env = tf_py_environment.TFPyEnvironment(env)
    print('tf_env')
    q_net = tf_agents.networks.q_network.QNetwork(
        tf_env.observation_spec(),
        tf_env.action_spec(),
        preprocessing_layers=None,
        preprocessing_combiner=None,
        fc_layer_params=(100,)
    )
#     tf_agents.networks.q_network.QNetwork(
#     input_tensor_spec, action_spec, preprocessing_layers=None,
#     preprocessing_combiner=None, conv_layer_params=None, fc_layer_params=(75, 40),
#     dropout_layer_params=None, activation_fn=tf.keras.activations.relu,
#     kernel_initializer=None, batch_squash=True, dtype=tf.float32,
#     name='QNetwork'
# )

    agent = dqn_agent.DqnAgent(
        tf_env.time_step_spec(),
        tf_env.action_spec(),
        q_network = q_net,
        optimizer = optimizer,
        td_error_loss_fn = common.element_wise_squared_loss,
        train_step_counter = tf.Variable(0)
    )

    agent.initialize()


    time_step = tf_env.reset()
    num_steps = 3
    transitions = []
    reward = 0
    for _ in range(num_steps):
        action = tf.random_uniform([1], 0, 9, dtype=tf.int32)
        # applies the action and returns the new TimeStep.
        next_time_step = tf_env.step(action)
        transitions.append([time_step, action, next_time_step])
        reward += next_time_step.reward
        time_step = next_time_step

    # np_transitions = tf.nest.map_structure(lambda x: x.numpy(), transitions)
    # print('\n'.join(map(str, np_transitions)))
    # print('Total reward:', reward.numpy())

    # for _ in range(3):
        # time_step = environment.step(action_array)
        # print(time_step)
        # cumulative_reward += time_step.reward
        time_step = env.reset()
        print(time_step)
        cumulative_reward = time_step.reward

        # environment._episode_ended = True
        # time_step = environment.step(action_array)
        # cumulative_reward += time_step.reward
        # print('Final Reward = ', cumulative_reward)
        for _ in range(3):
            time_step = env.step(action_array)
            print(time_step)
            cumulative_reward += time_step.reward

        utils.validate_py_environment(env, episodes=5)
        # environment._episode_ended = True
        # time_step = environment.step(action_array)
        cumulative_reward += time_step.reward
        print('Final Reward = ', cumulative_reward)
