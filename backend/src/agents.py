from collections import OrderedDict
import functools

import gymnasium
import numpy as np
from gymnasium import spaces
from pettingzoo.test import api_test
from copy import copy
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable, Tuple, Union
import random
import json
from environment import EnvironmentMngr
from backend.src.older.environmentModel import Environment
from random import shuffle
from os import remove, path


def fromObsToState(observations: List[int]) -> str:
    return "".join(observations)


def fromStateToObs(obsState: str) -> List[int]:
    return [int(gymId) for gymId in obsState.split("")]


class Agent:

    envMngr: EnvironmentMngr
    agentID: str

    def __init__(self, envMngr: EnvironmentMngr, agentID: str) -> None:
        self.envMngr = envMngr
        self.agentID = agentID

    def nextAction(self, observationGym: Any, reward: float) -> int:
        pass


class MARLAgent(Agent):

    alpha: float
    gamma: float
    epsilon: float
    qTable: Dict

    def __init__(self, alpha: int = 0.1, gamma: int = 0.6, epsilon: int = 0.1) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qTable = {}

    def nextAction(self, observation: any, reward):

        state = fromObsToState(observation)

        ################# Updating the QTable from last observations ###############
        state = "".join([str(x) for x in self.observations[currentAgent]])
        # print("state: ", state, " ; ", self.envMngr.fromObsGymToObsProp(self.observations)[currentAgent])
        next_state = "".join([str(x) for x in obs[currentAgent]])
        # print("next_state: ", next_state, " ; ", self.envMngr.fromObsGymToObsProp(obs)[currentAgent])
        reward = self.rewards[currentAgent]
        # print("reward: ", reward)

        old_value = 0 if qTable.get(state, {}).get(
            action, None) == None else qTable[state][action]
        # print("old_value: ", old_value)
        next_max = max(list(qTable.get(next_state, {"k": 0}).values()))
        # print("next_max: ", next_max)

        new_value = (1 - alpha) * old_value + alpha * \
            (reward + gamma * next_max)

        # print("new_value: ", new_value)
        qTable.setdefault(state, {})
        qTable[state][action] = new_value
        # print("QTable", qTable)
        #######################################################################

        ################# Updating the QTable from last observations ###############
        observedState = "".join(list([str(gymProp)
                                for gymProp in observation]))
        if random.uniform(0, 1) < epsilon:
            print(
                "Exploring the space to know which reward is associated with an action in a given state")
            # Explore action space
            action = self.env.envMngr.actGymSpace[agent].sample()
        else:
            if (qTable.get(observedState, None) == None):
                print(
                    "Exploring the space to know which reward is associated with an action in a given state")
                action = self.env.envMngr.actGymSpace[agent].sample()
            else:
                print("Using the QValues")
                # print("For state ", observedState, " 'action -> reward' QValues are ", qTable[observedState])
                print("For state ", self.env.envMngr.fromObsGymToObsProp({agent: observation})[agent], " 'action -> reward' QValues are ", {
                    self.env.envMngr.fromActGymToActPropID({agent: actGym})[agent]: qValue for actGym, qValue in qTable[observedState].items()})

                # print(self.env.envMngr.fromActGymToActPropID({agent: list(qTable.get(observedState).keys())[0]}))

                availableQValues = list(OrderedDict(
                    qTable.get(observedState)).values())
                maxActionQValueForCurrentState = max(availableQValues)

                if len(availableQValues) < len(list(self.env.envMngr.actPropSpace[agent])):
                    if maxActionQValueForCurrentState < 0:
                        otherActions = [actionGym for actionGym in range(0, len(list(
                            self.env.envMngr.actPropSpace[agent]))) if actionGym not in list(OrderedDict(qTable.get(observedState)).keys())]
                        shuffle(otherActions)
                        return otherActions[0]

                maxActionQValueForCurrentStateGymID = [action for action, qValue in qTable.get(
                    observedState).items() if qValue == maxActionQValueForCurrentState][0]
                # print("for state ", observedState, " available QValues are ", qTable.get(observedState))
                action = maxActionQValueForCurrentStateGymID  # Exploit learned values
        return action
        ############################


class DecisionTreeAgent(Agent):

    stateActionMapping: Dict[str, int]

    def __init__(self, stateActionMapping: Dict[str, int]) -> None:
        self.stateActionMapping = stateActionMapping

    def nextAction(self, observation: any, reward):
        return self.stateActionMapping[fromObsToState(observation)]


class RandomAgent(Agent):
    def nextAction(self, observation: any, reward):
        return self.envMngr.actGymSpace[self.agentID].sample()


class LazyAgent(Agent):
    def nextAction(self, observation: any, reward) -> int:
        return self.envMngr.fromActPropIDToActGym({self.agentID: "doNothing"})[self.agentID]
