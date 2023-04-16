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
from environmentModel import Environment
from random import shuffle
from os import remove, path


def env(environment: Union[Environment, Any], render_mode=None):

    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    env = McasEnvironment(node_environment=environment,
                          render_mode=internal_render_mode)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    # env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    # env = wrappers.OrderEnforcingWrapper(env)
    return env


# For MARL
alpha = 0.1
gamma = 0.6
epsilon = 0.1
qTable = {}


class McasEnvironment(AECEnv):

    metadata = {"render_modes": ["human"], "name": "Network nodes"}

    envMngr: EnvironmentMngr

    def __init__(self, node_environment: Union[Environment, Any], render_mode=None):

        self.envMngr = EnvironmentMngr(nodeEnvironment=node_environment)

        self.possible_agents = self.envMngr.agtPropSpace

        # ====================
        # TODO: voir ce qu'un agent peut observer réellement sur un SI
        # TODO: ajouter et integrer des precondition_script et postcondition_script
        # TODO : l'espace d'observation est seulement l'union de toutes les propriétés des "effect actions"
        # TODO: avoir les actions implémentées dans le code mais les afficher dans le json lors de la serialization sous forme de {...precondition... effects...}
        # TODO: avoir des classes de comportement dans le code bien organisées avec les actions dans plusieurs fichiers
        # TODO: avoir une fonction envAfterEffect qui agit après chaque execution d'une action par un agent pour faire appliquer les éventuels after-effects
        # TODO : décoreller les identifiants des jsons avec les identifiants attachés aux agents (peu importe sur quel noeud ils se trouvent)
        # ====================
        self.observation_spaces = self.envMngr.obsGymSpace

        self.action_spaces = self.envMngr.actGymSpace

        self.render_mode = render_mode

    # this cache ensures that same space object is returned for the same agent
    # allows action space seeding to work as expected
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    # @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.action_spaces[agent]

    def render(self):
        """
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        """
        renderedState = json.dumps(self.envMngr.environment, indent=4)
        # print(renderedState)
        return renderedState

    def observe(self, agent):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        return self.observations[agent]

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass

    def reset(self, seed=None, return_info=False, options=None):
        """
        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - terminations
        - truncations
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.
        Here it sets up the state dictionary which is used by step() and the observations dictionary which is used by step() and observe()
        """

        self.envMngr.reset()

        self.agents = self.possible_agents
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = self.envMngr.initialEnvironment

        obser0 = {agent: self.envMngr.getValueFromJsonPath(
            self.envMngr.environment, '["{}"]["properties"]["processes"]["agents"]["{}"]["knowledge"]'
            .format(self.envMngr.getNodeIDPropFromAgtID(agent), agent)) for agent in self.agents}

        obser = {agent: {'["{}"]["properties"]["processes"]["agents"]["{}"]["knowledge"]["{}"]'
                         .format(self.envMngr.getNodeIDPropFromAgtID(agent), agent, propName): propValue for propName, propValue in properties.items()} for agent, properties in obser0.items()}

        self.observations = self.envMngr.fromObsPropToObsGym(
            {agent: list(OrderedDict(obs).items()) for agent, obs in obser.items()})

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def step(self, action):
        """
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - terminations
        - truncations
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        """
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and STATES the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next live agent
            self._was_dead_step(action)
            return

        currentAgent = self.agent_selection

        obs = self.envMngr.applyAction(action, currentAgent)

        reward, end = self.envMngr.getReward(
            currentAgent, obs, self.observations)

        if (currentAgent == "attacker1"):
            print("REWARD:", reward)
        self.rewards[currentAgent] = reward

        self._cumulative_rewards[currentAgent] += reward

        ################# For Q-Learning ###############
        if (currentAgent == "attacker1"):
            print("Updating the QTable")
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
        ################################################

        self.observations[currentAgent] = obs[currentAgent]

        self.state = self.envMngr.environment

        if self.render_mode == "human":
            self.render()

        if (end):
            print("Agent {} finished".format(currentAgent))

        self.terminations[currentAgent] = end

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()


class EnvironmentPlayer:
    env: McasEnvironment
    iteration: int
    iterationMax: int
    fileName: str
    itera: Any
    rewardsStatsFile: str
    rewardsAveragePerEpisodeFile: str
    av: int

    ######## Q-Learning ########
    def attacker1MARL(self, agent, observation: any, reward):
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

    ######## Decision Tree #########
    def attacker1Behaviour(self, agent, observation: any, reward):
        def _attacker1Behaviour(observation: any):
            prettyObs = {propName.split(
                '[\"knowledge\"]')[-1][2:-2]: prop for propName, prop in observation.items()}
            if prettyObs.get("nodeLocation", None) == "PC2":
                return "gettingFlag"
            if prettyObs.get("foundNode", None) == "PC2Link":
                return "moveToPC2"
            else:
                if (prettyObs.get("foundNode", None) == None):
                    return "findPC2Link"
                else:
                    return "nmap"
        return self.env.envMngr.getActGymID(agent, _attacker1Behaviour(dict(OrderedDict(self.env.envMngr
                                                                       .fromObsGymToObsProp({agent: observation})[agent]))))

    def defender1Behaviour(self, agent, observation: any, reward):
        def _defender1Behaviour(observation: any):
            prettyObs = {propName.split(
                '[\"knowledge\"]')[-1][2:-2]: prop for propName, prop in observation.items()}
            return "doNothing"
        return self.env.envMngr.getActGymID(agent, _defender1Behaviour(dict(OrderedDict(self.env.envMngr
                                                                       .fromObsGymToObsProp({agent: observation})[agent]))))

    def defender2Behaviour(self, agent, observation: any, reward):
        def _defender2Behaviour(observation: any):
            prettyObs = {propName.split(
                '[\"knowledge\"]')[-1][2:-2]: prop for propName, prop in observation.items()}
            return "doNothing"
        return self.env.envMngr.getActGymID(agent, _defender2Behaviour(dict(OrderedDict(self.env.envMngr
                                                                       .fromObsGymToObsProp({agent: observation})[agent]))))
    ###############

    def saveFile(self, filePath: str):
        f = open(self.fileName, "w+")
        json.dump(self.env.envMngr.environment, f)

    def dumpEnvironment(self) -> str:
        return json.dumps(self.env.envMngr.environment)

    def dictEnvironment(self) -> Any:
        return self.env.envMngr.environment

    def writeStats(self, statsFile: str, logs: str) -> None:
        f = open(statsFile, "a+")
        f.write(logs + "\n")
        f.close()

    def __init__(self, env: McasEnvironment, iterationMax=2 ** 63) -> None:
        self.env = env
        self.iteration = 0
        self.iterationMax = iterationMax
        self.rewardsStatsFile = "rewards.csv"
        self.rewardsAveragePerEpisodeFile = "rewardsAveragePerEpisode.csv"
        self.av = 0

        if(path.exists(self.rewardsStatsFile)):
            remove(self.rewardsStatsFile)
        self.writeStats(self.rewardsStatsFile, "epoch;episode;reward")

        if(path.exists(self.rewardsAveragePerEpisodeFile)):
            remove(self.rewardsAveragePerEpisodeFile)
        self.writeStats(self.rewardsAveragePerEpisodeFile, "episode;averageReward")

        #################
        self.decisionTree: Any = {
            "attacker1": self.attacker1Behaviour,
            "defender1": self.defender1Behaviour,
            "defender2": self.defender2Behaviour
        }

        self.marl: Any = {
            "attacker1": self.attacker1MARL,
            "defender1": self.defender1Behaviour,
            "defender2": self.defender2Behaviour
        }
        self.qTable = {}

        self.random: Any = {}
        #################

        self.env.reset()
        self.itera = self.env.agent_iter().__iter__()

    def next(self) -> Tuple[str, str]:
        if self.iteration >= self.iterationMax:
            print("Reached maxIteration !")
            return ""

        # return the next agent to play
        agent = self.itera.__next__()

        # print("Agent: ", agent)

        observation, reward, termination, truncation, info = self.env.last()

        if (agent == "attacker1"):
            self.av += int(reward)
            self.writeStats(self.rewardsStatsFile, "{};{};{}".format(
                str(self.iteration%15), str(int(self.iteration/15)), str(reward)))
            if(self.iteration%15==0):
                self.writeStats(self.rewardsAveragePerEpisodeFile, "{};{}".format(str(int(self.iteration/15)), str(float(self.av/5))))
                self.av = 0

        observationProp = self.env.envMngr.fromObsGymToObsProp(
            {agent: observation})

        action = None
        lastValues = None
        if not termination:
            # print("last:{}".format(json.dumps({"observation": observationProp, "reward": reward,
            #                                 "termination": termination, "truncation": truncation, "info": info})))

            # action = self.decisionTree[agent](agent, observation)
            action = self.marl[agent](agent, observation, reward)

            actionPropName = self.env.envMngr.getActPropID(agent, action)

            if (agent == "attacker1"):
                print("\t\tchosen action: {} ({})".format(
                    actionPropName, action))

            # actionPropName = self.env.envMngr.getActPropID(agent, action)

            self.env.step(action)
            lastValues = {"agent": agent, "observation": observationProp, "reward": reward,
                          "termination": termination, "truncation": truncation, "info": info, "nextAction": actionPropName}

        lastValues = {"agent": agent, "observation": observationProp, "reward": reward,
                      "termination": termination, "truncation": truncation, "info": info, "nextAction": None}

        self.iteration += 1
        logs = "Iteration {}: {}".format(
            self.iteration, json.dumps(lastValues))
        # self.saveFile()
        return (agent, logs)


def loadFile(filePath: str):
    newDictEnv = json.load(open(filePath, "r"))
    return EnvironmentPlayer(McasEnvironment(
        node_environment={"nodes": newDictEnv}, render_mode="human"))


if __name__ == '__main__':

    envPlayer: EnvironmentPlayer = loadFile("worldStates/t1.json")

    for k in range(0, 50):
        print("============= Episode {} ===================".format(str(k)))
        for i in range(0, 15):
            print("---- Epoch {} ----".format(str(i)))
            envPlayer.next()
            print("")
        envPlayer.env.reset()
        print("\n\n")
