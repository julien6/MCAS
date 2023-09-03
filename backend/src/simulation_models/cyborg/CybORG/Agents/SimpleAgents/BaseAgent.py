from gym import Space
from gym.utils import seeding
import numpy as np
from CybORG.Shared import Results
from typing import Any

from CybORG.Simulator.Actions.Action import Action, Sleep


class BaseAgent:
    def __init__(self, name: str, np_random=None):
        self.name = name
        if np_random is None:
            np_random, seed = seeding.np_random()
        self.np_random = np_random

    def train(self, results: Results):
        """allows an agent to learn a policy"""
        raise NotImplementedError

    def get_action(self, observation, action_space):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space"""
        raise NotImplementedError

    def end_episode(self):
        """Allows an agent to update its internal state"""
        raise NotImplementedError

    def set_initial_values(self, action_space, observation):
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"


class PzBaseAgent(BaseAgent):

    def cyborg_to_pz_action(self, action: Action, actions_mapping: Any) -> int:
        return list({act: _action for act, _action in actions_mapping.items(
        ) if str(_action) == str(action) and action.get_params() == _action.get_params()})[0]

    def pz_to_cyborg_action(self, action: int, actions_mapping: Any) -> Action:
        return actions_mapping[action]

    def get_action(self, cyborg_observation, cyborg_action_space, pz_observation=None, pz_action_space=None, actions_mapping=None):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space
        including pettingzoo observations"""
        raise NotImplementedError

class PzRandom(PzBaseAgent):

    def get_action(self, cyborg_observation, cyborg_action_space, pz_observation: np.ndarray =None, pz_action_space: Space=None, actions_mapping=None):
        return self.pz_to_cyborg_action(pz_action_space.sample(), actions_mapping)