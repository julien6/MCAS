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
from environmentModel import Environment, environmentTest


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


class McasEnvironment(AECEnv):

    metadata = {"render_modes": ["human"], "name": "Network nodes"}

    envMngr: EnvironmentMngr

    def __init__(self, node_environment: Union[Environment, Any], render_mode=None):

        self.envMngr = EnvironmentMngr(nodeEnvironment=node_environment)

        self.possible_agents = self.envMngr.agtPropSpace

        # TODO: voir ce qu'un agent peut observer réellement sur un SI
        # TODO : l'espace d'observation est seulement l'union de toutes les propriétés des "effect actions"
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
        self.observations = {agent: self.envMngr.getValueFromJsonPath(
            self.envMngr.environment, '{}["knowledge"]'.format(agent)) for agent in self.agents}
        """
        Our agent_selector utility allows easy cyclic stepping through the agents list.
        """
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

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[currentAgent] = 0

        # rewards for all agents are placed in the rewards dictionary
        # fake rewards for the moment
        for agent in self.agents:
            self.rewards[agent] = 0

        obs = self.envMngr.applyAction(action, currentAgent)

        self.observations[currentAgent] = obs[currentAgent]

        self.state = self.envMngr.environment

        if self.render_mode == "human":
            self.render()

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()


class EnvironmentPlayer:
    env: McasEnvironment
    iteration: int
    iterationMax: int
    fileName: str
    itera: Any

    def saveFile(self, filePath: str):
        f = open(self.fileName, "w+")
        json.dump(self.env.envMngr.environment, f)

    def dumpEnvironment(self) -> str:
        return json.dumps(self.env.envMngr.environment)

    def dictEnvironment(self) -> Any:
        return self.env.envMngr.environment

    def __init__(self, env: McasEnvironment, iterationMax=2 ** 63) -> None:
        self.env = env
        self.iteration = 0
        self.iterationMax = iterationMax

        self.env.reset()
        self.itera = self.env.agent_iter().__iter__()

    def next(self) -> Tuple[str, str]:
        if self.iteration >= self.iterationMax:
            print("Reached maxIteration !")
            return ""

        # return the next agent to play
        agent = self.itera.__next__()
        observation, reward, termination, truncation, info = self.env.last()
        print("===============================")
        prettyAgentName = copy(agent)
        prettyAgentName = prettyAgentName.replace("\"", "'")

        action = self.env.envMngr.getActGymID(agent, "helloWorld")

        actionPropName = self.env.envMngr.getActPropID(agent, action)

        self.env.step(action)
        lastValues = {"agent": prettyAgentName, "observation": observation, "reward": reward,
                                 "termination": termination, "truncation": truncation, "info": info, "nextAction": actionPropName}
        print(json.dumps(lastValues, indent=2))

        self.iteration += 1
        logs = "Iteration {}: {}".format(self.iteration, json.dumps(lastValues))
        # self.saveFile()
        return (prettyAgentName, logs)


def loadFile(filePath: str):
    newDictEnv = json.load(open(filePath, "r"))
    return EnvironmentPlayer(McasEnvironment(
        node_environment={"nodes": newDictEnv}, render_mode="human"))


if __name__ == '__main__':

    e: McasEnvironment = env(environment=environmentTest, render_mode="human")

    e.reset()

    # TODO : avoir des actions qui ne soient pas propres à un noeud mais génériques

    # i = 1

    # for agent in e.agent_iter(max_iter=7):
    #     observation, reward, termination, truncation, info = e.last()
    #     print("===============================")
    #     print("======== Iteration {} ==========".format(str(i)))
    #     prettyAgentName = copy(agent)
    #     prettyAgentName = prettyAgentName.replace("\"", "'")
    #     print(json.dumps({"agent": prettyAgentName, "observation": observation, "reward": reward,
    #                       "termination": termination, "truncation": truncation, "info": info}, indent=4))
    #     action = e.envMngr.getActGymID(agent, "helloWorld")
    #     print("")
    #     e.step(action)
    #     print("")
    #     i += 1

    itera = e.agent_iter().__iter__()

    # return the next agent to play
    agent = itera.__next__()
    observation, reward, termination, truncation, info = e.last()
    print("===============================")
    prettyAgentName = copy(agent)
    prettyAgentName = prettyAgentName.replace("\"", "'")
    print(json.dumps({"agent": prettyAgentName, "observation": observation, "reward": reward,
                      "termination": termination, "truncation": truncation, "info": info}, indent=4))
    action = e.envMngr.getActGymID(agent, "helloWorld")
    e.step(action)

    # return the next agent to play
    agent = itera.__next__()
    observation, reward, termination, truncation, info = e.last()
    print("===============================")
    prettyAgentName = copy(agent)
    prettyAgentName = prettyAgentName.replace("\"", "'")
    print(json.dumps({"agent": prettyAgentName, "observation": observation, "reward": reward,
                      "termination": termination, "truncation": truncation, "info": info}, indent=4))
    action = e.envMngr.getActGymID(agent, "helloWorld")
    e.step(action)
