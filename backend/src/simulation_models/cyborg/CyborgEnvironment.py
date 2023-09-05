from ipaddress import IPv4Address, IPv4Network
from typing import Any, Dict, List
from simulation_models.cyborg.CybORG import CybORG
from simulation_models.cyborg.CybORG.Agents.SimpleAgents.BaseAgent import PzBaseAgent, PzRandom
from simulation_models.cyborg.CybORG.Agents.Wrappers.CommsPettingZooParallelWrapper import AgentCommsPettingZooParallelWrapper, ActionsCommsPettingZooParallelWrapper
from simulation_models.cyborg.CybORG.Simulator.Actions.Action import Action, Sleep
from simulation_models.cyborg.CybORG.Simulator.Scenarios.FileReaderScenarioGenerator import FileReaderScenarioGenerator
from simulation_models.cyborg.CybORG.Simulator.Scenarios.DroneSwarmScenarioGenerator import DroneSwarmScenarioGenerator
from simulation_models.cyborg.CybORG.Agents.Wrappers.PettingZooParallelWrapper import PettingZooParallelWrapper
from simulation_models.cyborg.CybORG.Agents import B_lineAgent, BlueReactRestoreAgent, BlueReactRemoveAgent, SleepAgent, DroneRedAgent, \
    RandomAgent, BaseAgent, RedMeanderAgent
from os.path import dirname
from pprint import pprint
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import inspect
from simulation_models.cyborg.CybORG.Agents.Wrappers.TrueTableWrapper import true_obs_to_table
from simulation_models.cyborg.CybORG.Simulator.SimulationController import SimulationController
import json
import enum

from simulation_models.SimulationModel import SimulationModel
from networkx.readwrite.json_graph.node_link import node_link_data

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            return str(o)
        if isinstance(o, IPv4Address):
            return str(o)
        if isinstance(o, IPv4Network):
            return str(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


class CyborgEnvironment(SimulationModel):

    def __init__(self, scenario_plan: Any, max_episode: int = 1, max_iteration: int = 1) -> None:
        super().__init__(max_episode, max_iteration)

        # path = inspect.getfile(CybORG)
        # path = dirname(path) + f'/Simulator/Scenarios/scenario_files/Scenario1b.yaml'
        # sg = FileReaderScenarioGenerator(path)

        sg = DroneSwarmScenarioGenerator(num_drones=10)

        env = CybORG(sg, 'sim')

        # self.wrapped_cyborg = PettingZooParallelWrapper(env)
        # self.wrapped_cyborg = AgentCommsPettingZooParallelWrapper(env)
        self.wrapped_cyborg = PettingZooParallelWrapper(env)
        self.wrapped_cyborg.reset(42)

        self.max_eps = max_episode
        self.max_its = max_iteration

        # agents = {agent: RandomAgent() for agent in ["Blue", "Red", "Green"]}

        self.agents = {f"blue_agent_{agent}": PzRandom(
            name=f"blue_agent_{agent}") for agent in range(10)}

        self.iteration_data = {}

        self.pz_observations = None
        self.pz_observation_spaces = None
        self.pz_action_spaces = None
        self.cyborg_observations = None
        self.cyborg_action_spaces = None

        self.agents_actions = None
        self.agents_observations = None
        self.agents_rewards = None
        self.true_states = None
        self.action_spaces = None
        self.observation_spaces = None

    def gym_to_cyborg_actions(self, gym_actions) -> Dict:
        gym_cyborg_mapping = self.wrapped_cyborg.agent_actions
        return {
            agent: gym_cyborg_mapping[agent][gym_action] for agent, gym_action in gym_actions.items()
        }

    def get_agent_state(self, agent_name: str):
        """Returns the full knowledge of an agent
        """
        true_state = self.wrapped_cyborg.env.get_agent_state(agent_name)
        state = json.loads(json.dumps(
            true_state, cls=EnhancedJSONEncoder, indent=4))
        return state

    def get_team_agent_mapping(self):
        """Return the host agent mapping
        """
        return self.wrapped_cyborg.env.environment_controller.team_assignments

    def get_true_state(self):
        """Returns the real full host nodes data
        """
        true_state = self.wrapped_cyborg.env.get_agent_state("True")
        state = json.loads(json.dumps(
            true_state, cls=EnhancedJSONEncoder, indent=4))
        return state

    def next(self, requested_info: List = ["episode_number", "iteration_number", "observation_spaces", "agents_actions",
                                           "agents_observations", "agents_rewards", "true_states"]) -> Dict:

        if self.current_it == 0:

            print("Episode {}".format(str(self.current_ep)))

            # PettingZoo observations and action spaces
            self.pz_observations = self.wrapped_cyborg.reset()
            self.pz_observation_spaces = self.wrapped_cyborg._observation_spaces
            self.pz_action_spaces = self.wrapped_cyborg.action_spaces

            #  CybORG observations and action spaces
            self.cyborg_observations = {agent: self.wrapped_cyborg.env.get_observation(agent)
                                        for agent in self.wrapped_cyborg.agents}
            # cyborg_observation_space = {agent: self.wrapped_cyborg.env.get_observation_space(
            #     agent) for agent in self.wrapped_cyborg.agents}
            self.cyborg_action_spaces = {agent: self.wrapped_cyborg.env.get_action_space(
                agent) for agent in self.wrapped_cyborg.agents}

            # =========== Data to save =============

            # Initialization for current episode
            self.agents_actions = {
                agent: None for agent in self.wrapped_cyborg.agents}
            self.agents_observations = {agent: observations.tolist()
                                        for agent, observations in self.pz_observations.items()}
            self.agents_rewards = {
                agent: None for agent in self.wrapped_cyborg.agents}
            self.true_states = self.get_true_state()

            self.action_spaces = {agent: sp.n for agent,
                                  sp in self.pz_action_spaces.items()}
            self.observation_spaces = {agent: sp.nvec.tolist()
                                       for agent, sp in self.pz_observation_spaces.items()}

        else:
            actions = {}
            for agent_name, agent in self.agents.items():
                if agent_name in self.wrapped_cyborg.agents:
                    # action can be in PettingZoo or Cyborg
                    action = None
                    # if the agent needs to include the pettingzoo observations and action spaces to choose the next action (AI)
                    if isinstance(agent, PzBaseAgent):
                        action = agent.get_action(self.cyborg_observations[agent_name],
                                                  self.cyborg_action_spaces[agent_name],
                                                  self.pz_observations[agent_name],
                                                  self.pz_action_spaces[agent_name],
                                                  self.wrapped_cyborg.agent_actions[agent_name])
                    # use regular Cyborg observation and action spaces
                    else:
                        action = agent.get_action(
                            self.cyborg_observations[agent_name], self.cyborg_action_spaces[agent_name])

                    # if the chosen action is not Pz encoded, encode it to
                    if isinstance(action, Action):
                        action = list({act: _action for act, _action in self.wrapped_cyborg.agent_actions[agent_name].
                                       items() if str(_action) == str(action) and
                                       action.get_params() == _action.get_params()})[0]

                    actions[agent_name] = action

            # Applying actions (actions must be in PettingZoo encoding)
            self.pz_observations, rew, done, info = self.wrapped_cyborg.step(
                actions)

            # ===================
            # getting iteration data
            self.agents_actions = actions
            self.agents_observations = [{agent: observations.tolist()
                                         for agent, observations in self.pz_observations.items()}]
            self.agents_rewards = rew
            self.true_states = self.get_true_state()
            # ===================

            # getting the cyborg observation
            # self.cyborg_observations = {agent: self.wrapped_cyborg.env.get_observation(agent)
            #                             for agent in self.wrapped_cyborg.agents}
            # to get the cyborg actions
            # self.cyborg_actions = {agent: self.wrapped_cyborg.env.get_last_action(agent)
            #                        for agent in self.wrapped_cyborg.agents}

        print("Iteration {}".format(str(self.current_it)))

        if "episode_number" in requested_info:
            self.iteration_data["episode_number"] = self.current_ep
        if "iteration_number" in requested_info:
            self.iteration_data["iteration_number"] = self.current_it
        if "observation_spaces" in requested_info:
            self.iteration_data["observation_spaces"] = self.observation_spaces
        if "agents_actions" in requested_info:
            self.iteration_data["agents_actions"] = self.agents_actions
        if "agents_observations" in requested_info:
            self.iteration_data["agents_observations"] = self.agents_observations
        if "agents_rewards" in requested_info:
            self.iteration_data["agents_rewards"] = self.agents_rewards
        if "true_states" in requested_info:
            self.iteration_data["true_states"] = self.true_states
        if "network_graph" in requested_info:
            self.iteration_data["network_graph"] = node_link_data(self.wrapped_cyborg.env.environment_controller.state.link_diagram)
        if "team_agent_mapping" in requested_info:
            self.iteration_data["team_agent_mapping"] = self.get_team_agent_mapping()

        self.current_it += 1
        if self.current_it == self.max_its:
            self.current_ep += 1
            self.current_it = 0

        if self.current_ep >= self.max_eps:
            return None

        if self.current_ep >= self.max_eps and self.current_it > 0:
            return None

        return self.iteration_data


if __name__ == '__main__':

    ce = CyborgEnvironment({}, max_episode=3, max_iteration=5)

    res = None
    while True:
        res = ce.next(["episode_number", "iteration_number",
                      "agents_actions", "agents_observations", "network_graph"])
        if res != None:
            print("\t", end="")
            print(res)
            pass
        else:
            break

# ===============================================================
# Graphical visualizations to make at the end of an episode
#
#   - network topology graph showing host nodes with
#       - agents deployed on / their session with other host nodes for red, green and blue teams
#       - connections between host nodes (with minimal details such as process name, ip address...)
#           - with a frame encompassing host nodes of the same subnet
#
#   - table with all information of host nodes with
#       - sessions, processes, files, OS, ...
#       - logs of event ocurring on host nodes
#
#   - logs for each agent in each team with
#       - received observations (including messages)
#       - actions made
#
#   - pixel visualization of the temporal observed behavior for each agent in each team
#       - using observation and action spaces and observation and action
#
#   - histogram showing chosen actions frequency for each agent in each team
#       - using stacked observations and actions at the end of an episode (or during a pause), display an action and observation histogram
#
#   - pie chart showing how distributed actions are for each agent in each team
#       - using stacked observations and actions at the end of an episode (or during a pause), display an action and observation pie chart
#
#   - sequence diagrams showing applied actions (even itself) and received observations (show agents using sessions)
#       - with an environment actor standing for the environment receiving action and sending back observations to agents
#       - with only agents of the same team (especially showing exchanged messages)
#       - with all the teams (especially showing attacks/countermeasures applied to blue, green, red teams)
