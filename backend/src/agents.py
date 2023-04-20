from collections import OrderedDict
from typing import Dict, List, Any
from environment import EnvironmentMngr
from random import shuffle

import random


def fromObsToState(observations: List[int]) -> str:
    return "".join([str(obs) for obs in observations])


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
    lastObsState: str

    def __init__(self, envMngr: EnvironmentMngr, agentID: str, alpha: int = 0.1, gamma: int = 0.6, epsilon: int = 0.2) -> None:
        super().__init__(envMngr, agentID)
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qTable = {}
        self.lastObsState = None
        self.lastAction = None

    def nextAction(self, observation: str, reward) -> int:
        # If this is the first time, choose randomly
        if (self.lastObsState == None or self.lastAction == None):
            self.lastObsState = fromObsToState(observation)
            self.lastAction = self.envMngr.actGymSpace[self.agentID].sample()
            return self.lastAction
        else:
            # First, update the QTable with previous explored state
            previous_state = self.lastObsState

            state = fromObsToState(observation)
            last_action = self.lastAction

            old_value = 0 if self.qTable.get(previous_state, {}).get(
                last_action, None) == None else self.qTable[previous_state][last_action]
            next_max = max(list(self.qTable.get(state, {"k": 0}).values()))

            new_value = (1 - self.alpha) * old_value + self.alpha * \
                (reward + self.gamma * next_max)

            self.qTable.setdefault(previous_state, {})
            self.qTable[previous_state][last_action] = new_value

            action = None
            # Second, explore states randomly or using QTable
            if random.uniform(0, 1) < self.epsilon:
                print(
                    "Exploring the space to know which reward is associated with an action in a given state")
                # Explore action space
                # action = self.envMngr.actGymSpace[self.agentID].sample()

                otherActions = [actionGym for actionGym in range(0, len(list(
                    self.envMngr.actPropSpace[self.agentID]))) if
                    actionGym not in list(OrderedDict(self.qTable.get(state, {})).keys())]
                if (len(otherActions) == 0):
                    action = self.envMngr.actGymSpace[self.agentID].sample()
                else:
                    shuffle(otherActions)
                    action = otherActions[0]

            else:
                if (self.qTable.get(state, None) == None):
                    print(
                        "Exploring the space to know which reward is associated with an action in a given state")
                    action = self.envMngr.actGymSpace[self.agentID].sample()
                else:
                    print("Using the QValues")
                    print("For state ", self.envMngr.fromObsGymToObsProp({self.agentID: observation})[self.agentID],
                          " 'action -> reward' QValues are ", {
                        self.envMngr.fromActGymToActPropID({self.agentID: actGym})[
                            self.agentID]: qValue for actGym, qValue in self.qTable[state].items()})

                    availableQValues = list(OrderedDict(
                        self.qTable.get(state)).values())
                    maxActionQValueForCurrentState = max(availableQValues)

                    if len(availableQValues) < len(list(self.envMngr.actPropSpace[self.agentID])):
                        if (maxActionQValueForCurrentState <= 0):
                            print(
                                "Exploring the space to know which reward is associated with an action in a given state")
                            otherActions = [actionGym for actionGym in range(0, len(list(
                                self.envMngr.actPropSpace[self.agentID]))) if
                                actionGym not in list(OrderedDict(self.qTable.get(state)).keys())]
                            shuffle(otherActions)

                            self.lastAction = otherActions[0]
                            self.lastObsState = state

                            return self.lastAction

                    maxActionQValueForCurrentStateGymID = [action for action, qValue in self.qTable.get(
                        state).items() if qValue == maxActionQValueForCurrentState][0]
                    # print("for state ", state, " available QValues are ", self.qTable.get(state))
                    action = maxActionQValueForCurrentStateGymID  # Exploit learned values

        self.lastAction = action
        self.lastObsState = state

        return action


class DecisionTreeAgent(Agent):

    actionsList: List[int]

    def __init__(self, envMngr: EnvironmentMngr, agentID: str, actionsList: List[str]) -> None:
        super().__init__(envMngr, agentID)
        self.actionsList = [self.envMngr.fromActPropIDToActGym(
            {self.agentID: action})[self.agentID] for action in actionsList]

    def nextAction(self, observation: any, reward) -> int:
        if len(self.actionsList) == 0:
            return self.envMngr.fromActPropIDToActGym({self.agentID: "doNothing"})[self.agentID]
        return self.actionsList.pop(0)


class RandomAgent(Agent):
    def nextAction(self, observation: any, reward) -> int:
        return self.envMngr.actGymSpace[self.agentID].sample()


class LazyAgent(Agent):
    def nextAction(self, observation: any, reward) -> int:
        return self.envMngr.fromActPropIDToActGym({self.agentID: "doNothing"})[self.agentID]
