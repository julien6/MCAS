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
from backend.src.agents import Agent, DecisionTreeAgent, IdleAgent, LazyAgent, MARLAgent, RandomAgent
from environment import EnvironmentMngr
from backend.src.older.environmentModel import Environment
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

        self.observations = self.envMngr.fromObsPropToObsGym(
            {agent: self.envMngr.getAgentObservations(agent) for agent in self.agents})

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
            self._was_dead_step(action)
            return

        currentAgent = self.agent_selection

        obs = self.envMngr.applyAction(action, currentAgent)

        reward, end = self.envMngr.getReward(
            currentAgent, obs, self.observations)

        self.rewards[currentAgent] = reward

        self._cumulative_rewards[currentAgent] += reward

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
    iterator: Any
    agents: Dict[str, Agent]

    def __init__(self, env: McasEnvironment, iterationMax=2 ** 63) -> None:
        self.env = env
        self.iteration = 0
        self.iterationMax = iterationMax
        self.env.reset()
        self.iterator = self.env.agent_iter().__iter__()

    def init_agent_behaviours(self):

        singleAttackerDT: Dict[str, int]
        singleDefenderDT: Dict[str, int]

        attacker1DT: Dict[str, int]
        attacker2DT: Dict[str, int]

        defender1DT: Dict[str, int]
        defender2DT: Dict[str, int]

        agent: Agent
        for agent in self.env.envMngr.agtPropSpace:
            behaviour = self.env.envMngr.getAgentBehaviour(agent)
            if behaviour == "idle":
                self.agents[agent] = LazyAgent(self.env.envMngr, agent)
            if behaviour == "random":
                self.agents[agent] = RandomAgent(self.env.envMngr, agent)
            if behaviour == "singleAttackerDT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, singleAttackerDT)
            if behaviour == "singleDefenderDT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, singleDefenderDT)
            if behaviour == "attacker1DT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, attacker1DT)
            if behaviour == "attacker2DT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, attacker2DT)
            if behaviour == "defender1DT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, defender1DT)
            if behaviour == "defender2DT":
                self.agents[agent] = DecisionTreeAgent(self.env.envMngr, agent, defender2DT)
            if behaviour == "marl":
                self.agents[agent] = MARLAgent(self.env.envMngr, agent)

    def next(self) -> Tuple[str, str]:

        if self.iteration >= self.iterationMax:
            print("Reached maxIteration !")
            return ""

        # return the next agent to play
        agent = self.iterator.__next__()

        observation, reward, termination, truncation, info = self.env.last()

        observationProp = self.env.envMngr.fromObsGymToObsProp(
            {agent: observation})

        ####
        action1 = self.env.envMngr.fromActPropToActGym("action1")
        action2 = self.env.envMngr.fromActPropToActGym("action2")
        action3 = self.env.envMngr.fromActPropToActGym("action3")
        ####

        action = None
        if not termination:
            action = self.agents[agent].nextAction(observation[agent], reward)
            actionPropName = self.env.envMngr.getActPropID(agent, action)
            print("\t\tchosen action: {} ({})".format(actionPropName, action))

        self.env.step(action)

        lastValues = {"agent": agent, "observation": observationProp, "reward": reward,
                      "termination": termination, "truncation": truncation, "info": info, "nextAction": action}

        self.iteration += 1
        logs = "Iteration {}: {}".format(
            self.iteration, json.dumps(lastValues))
        return (agent, logs)

    def dumpEnvironment(self) -> str:
        return json.dumps(self.env.envMngr.environment)

    def dictEnvironment(self) -> Any:
        return self.env.envMngr.environment


def loadFile(filePath: str):
    newDictEnv = json.load(open(filePath, "r"))
    return EnvironmentPlayer(McasEnvironment(
        node_environment=newDictEnv, render_mode="human"))


if __name__ == '__main__':

    envPlayer: EnvironmentPlayer = loadFile("worldStates/t1.json")

    # for k in range(0, 50):
    #     print("============= Episode {} ===================".format(str(k)))
    #     for i in range(0, 15):
    #         print("---- Epoch {} ----".format(str(i)))
    #         envPlayer.next()
    #         print("")
    #     envPlayer.env.reset()
    #     print("\n\n")
