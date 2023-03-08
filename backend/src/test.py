import functools

import gymnasium
import numpy as np
from gymnasium import spaces
from pettingzoo.test import api_test

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable
from utils import Values, CustomSpace
import random

NUM_ITERS = 10


def env(render_mode=None):

    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    env = PzEnvironment(render_mode=internal_render_mode)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class PzEnvironment(AECEnv):

    metadata = {"render_modes": ["human"], "name": "Network nodes"}

    def __init__(self, render_mode=None):

        self.possible_agents = ["defender", "attacker"]

        # Initialize our observation spaces (the same for attacker and defender for the moment)
        customEnvironmentSpace = {
            "reimagable": Values(False, True),
            "runningServices": {
                "ssh": Values("running", "pending", "stopped"),
                "excel": Values("running", "pending", "stopped")
            }
        }
        self.initialState = {
            "reimagable": 0,
            "runningServices": {
                "ssh": 0,
                "excel": 0
            }
        }
        self.customEnvironment = CustomSpace(customEnvironmentSpace)
        commonGymSpace = self.customEnvironment.convertToGymSpace()
        self.observation_spaces = {
            agent: commonGymSpace for agent in self.possible_agents
        }
        # ==========================

        # Initialize our action spaces
        customAttackerActionSpace = Values(
            "switchOffReimagable", "switchOffSSH", "observeReimagable")
        customAttackerActions = CustomSpace(customAttackerActionSpace)

        customDefenderActionSpace = Values(
            "switchOnReimagable", "switchOnSSH", "observeReimagable")
        customDefenderActions = CustomSpace(customDefenderActionSpace)

        self.customAgentActions = {
            "attacker": customAttackerActions,
            "defender": customDefenderActions
        }
        self.action_spaces = {
            "defender": customAttackerActions.convertToGymSpace(),
            "attacker": customDefenderActions.convertToGymSpace()
        }
        # ==========================

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
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        if len(self.agents) == 2:
            string = "Current state: {}".format(
                self.customEnvironment.convertToRender(self.state))
        else:
            string = "Game over"
        # print(string + "\n")

        return string

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
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state: Dict[str, Any] = self.initialState
        self.observations = {agent: {} for agent in self.agents}
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

        agent = self.agent_selection

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[agent] = 0

        print("Agent {} is playing action {}".format(
            agent, self.customAgentActions[agent].convertToRender(action)))

        # rewards for all agents are placed in the .rewards dictionary
        # fake rewards for the moment
        self.rewards[self.agents[0]], self.rewards[self.agents[1]] = (0, 0)

        # effecting actions on state
        if (self.customAgentActions[agent].convertToRender(action) == "observeReimagable"):
            self.observations[agent] = {
                "reimagable": self.state["reimagable"]}
        else:
            if agent == "attacker":
                if (self.customAgentActions[agent].convertToRender(action) == "switchOffReimagable"):
                    self.state["reimagable"] = 0
                if (self.customAgentActions[agent].convertToRender(action) == "switchOffSSH"):
                    self.state["runningServices"]["ssh"] = 2
            if agent == "defender":
                if (self.customAgentActions[agent].convertToRender(action) == "switchOnReimagable"):
                    self.state["reimagable"] = 1
                if (self.customAgentActions[agent].convertToRender(action) == "switchOnSSH"):
                    self.state["runningServices"]["ssh"] = 0

        if self.render_mode == "human":
            self.render()

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()


if __name__ == '__main__':
    e = env(render_mode="human")
    e.reset()

    def attackerBehavior(observation, agent):
        return random.choice([0, 2])

    def defenderBehavior(observation, agent):
        return random.choice([0, 2])

    agentBehaviors = {
        "attacker": attackerBehavior,
        "defender": defenderBehavior
    }

    # ce = self.customEnvironment.convertToRender(self.state)

    iteration = 1

    e.reset()

    itera = e.agent_iter(max_iter=10)
    a1 = itera.__iter__().__next__()

    e.step(2)

    a2 = itera.__iter__().__next__()

    e.step(2)

    a3 = itera.__iter__().__next__()

    e.step(2)

    a4 = itera.__iter__().__next__()

    print(a1, a2, a3, a4)

    # for agent in e.agent_iter(max_iter=10):

    #     print("============================")
    #     print("====== Iteration {} =========".format(iteration))
    #     observation, reward, termination, truncation, info = e.last()

    #     print("Obtained from last state : agent: {}; observation: {}; reward: {}; termination: {}; truncation: {}; info: {}".format(
    #         agent, observation, reward, termination, truncation, info))

    #     action = agentBehaviors[agent](observation, agent)

    #     e.step(action)

    #     print("Current knowledge for {}: ".format(
    #         agent) + str(e.observe(agent)))

    #     iteration += 1

    #     print("============================")
