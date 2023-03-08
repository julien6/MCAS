import functools
import random
from typing import Any, Callable, Dict, Union, List, Tuple
from dataclasses import dataclass
import dataclasses
import json
from dataclasses_serialization.json import JSONSerializer

import gymnasium
import numpy as np
from gymnasium import spaces
# from pettingzoo.test import api_test

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable

from utils import CustomSpace, Values
# from actionLibrary import ActionLibrary
# from behaviourLibrary import BehaviourLibrary


@dataclass
class Process:
    name: str
    running: bool
    description: str


@dataclass
class ListeningService (Process):
    allowedCredentials: List[str]


@dataclass
class AgentContext:
    binary_file_location: str
    possible_actions: List[Callable]
    knowledge: Any


@dataclass
class Action:
    actionID: str
    description: str
    success_probability: float
    function: Callable
    cost: int


@dataclass
class Agent(Process):
    context: AgentContext
    behaviour: Callable[[str, AgentContext,
                         Dict[str, Action]], Callable[[str, Any], None]]


@dataclass
class File:
    file_name: str
    permission: str
    type: str
    hash: str


@dataclass
class Processes:
    agents: Dict[str, Agent]
    services: Dict[str, ListeningService]
    other_processes: Dict[str, Process]


@dataclass
class FirewallRule:
    port: str
    permission: str
    reason: str


@dataclass
class Firewall:
    outgoing: List[FirewallRule]
    incoming: List[FirewallRule]


@dataclass
class Properties:
    processes: Processes
    file_system: Dict[str, File]
    firewall: Firewall
    installed_softwares: List[str]
    installed_operating_system: str
    reimagable: bool
    value: int
    sla_weight: float
    accessible_nodes: List[Tuple[str, str]]
    other_properties: List[str]
    logs: List[str]


@dataclass
class Node:
    meta_data: any
    properties: Properties
    actions: Dict[str, Action]


class Environment:
    nodes: Dict[str, Node]

    def __init__(self, nodes: Dict[str, Node] = {}) -> None:
        self.nodes = nodes

    def __str__(self) -> str:
        return str(self.serialize())

    def getAgentIDandNode(self) -> List[Tuple[str,str]]:
        agentIDs = []
        for nodeID, node in self.nodes.items():
            agentIDs += [(agentID, nodeID)
                         for agentID in list(node.properties.processes.agents.keys())]
        return agentIDs

    def getAgentByID(self, agentID: str) -> Tuple[Agent, str]:
        for nodeID, node in self.nodes.items():
            if agentID in list(node.properties.processes.agents.keys()):
                return (node.properties.processes.agents[agentID], nodeID)

    def getAgentByIDonNode(self, agentID: str, nodeID: str) -> Agent:
        if (not agentID in list(self.nodes[nodeID].properties.processes.agents.keys())):
            return None
        return self.nodes[nodeID].properties.processes.agents[agentID]

    def runAgentOnNode(self, agentID: str, agentNodeID: str) -> str:
        agent = self.getAgentByIDonNode(agentID, agentNodeID)
        if agent == None:
            return ""

        chosenAction: Callable[[str, Environment],
                               None] = agent.behaviour(agentID, agent.context, self.nodes[agentNodeID].actions)
        log: str = "Agent {} located on node {} is playing action {} ({})".format(
            agent.name, agentNodeID, chosenAction.__name__, self.nodes[agentNodeID].actions[chosenAction.__name__].description)
        chosenAction(agentID, self)
        print(log)
        return log

    def serialize(self) -> Dict:
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Callable):
                    return o.__name__
                if isinstance(o, Environment):
                    return {"nodes": o.nodes}
                if isinstance(o, type):
                    return o.__name__
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)
        return json.loads(json.dumps(self, cls=EnhancedJSONEncoder))


def deserialize(jsonDict: Dict, functions: Dict = {}) -> Environment:

    def deserializeAgent(agent: Dict) -> Agent:
        context = agent["context"]

        return Agent(
            name=agent["name"],
            running=agent["running"],
            description=agent["description"],
            context=AgentContext(
                binary_file_location=context["binary_file_location"],
                possible_actions=[eval(possibleAction, functions)
                                  for possibleAction in context["possible_actions"]],
                knowledge=context["knowledge"]
            ),
            behaviour=eval(agent["behaviour"], functions)
        )

    def deserializeAgents(agents: Dict) -> Dict[str, Agent]:
        return {agentID: deserializeAgent(agent) for agentID, agent in agents.items()}

    def deserializeService(service: Dict) -> ListeningService:
        return ListeningService(
            name=service["name"],
            running=service["running"],
            description=service["description"],
            allowedCredentials=service["allowedCredentials"]
        )

    def deserializeServices(services: Dict) -> Dict[str, ListeningService]:
        return {serviceID: deserializeService(service) for serviceID, service in services.items()}

    def deserializeProcess(process: Dict) -> Process:
        return Process(
            name=process["name"],
            running=process["running"],
            description=process["description"]
        )

    def deserializeOtherProcesses(otherProcesses: Dict) -> Dict[str, Process]:
        return {processID: deserializeProcess(process) for processID, process in otherProcesses.items()}

    def deserializeFileSystem(fileSystem: Dict) -> Dict[str, File]:
        return {path: JSONSerializer.deserialize(File, file) for path, file in fileSystem.items()}

    def deserializeFirewall(firewall: Dict) -> Firewall:
        return JSONSerializer.deserialize(Firewall, firewall)

    def deserializeProperties(properties: Dict) -> Properties:
        return Properties(
            processes=Processes(
                agents=deserializeAgents(properties["processes"]["agents"]),
                services=deserializeServices(
                    properties["processes"]["services"]),
                other_processes=deserializeOtherProcesses(
                    properties["processes"]["other_processes"])
            ),
            file_system=deserializeFileSystem(properties["file_system"]),
            firewall=deserializeFirewall(properties["firewall"]),
            installed_softwares=properties["installed_softwares"],
            installed_operating_system=properties["installed_operating_system"],
            reimagable=properties["reimagable"],
            value=properties["value"],
            sla_weight=properties["sla_weight"],
            accessible_nodes=properties["accessible_nodes"],
            logs=properties["logs"],
            other_properties=properties["other_properties"])

    def deserializeAction(action: Dict):
        return Action(
            actionID=action["actionID"],
            description=action["description"],
            success_probability=action["success_probability"],
            cost=action["cost"],
            function=eval(action["function"], functions)
        )

    def deserializeActions(actions: Dict) -> Dict[str, Action]:
        return {actionID: deserializeAction(action) for actionID, action in actions.items()}

    def deserializeNode(node: Dict) -> Node:
        return Node(
            meta_data=node["meta_data"],
            properties=deserializeProperties(node["properties"]),
            actions=deserializeActions(node["actions"])
        )

    nodes: Dict[str, Node] = {}
    for nodeID, node in jsonDict["nodes"].items():
        nodes[nodeID] = deserializeNode(node)

    return Environment(nodes=nodes)


class PzEnvironment(AECEnv):

    metadata = {"render_modes": ["human"], "name": "Network nodes"}

    def __init__(self, supportEnv: Environment, render_mode=None):

        print("OKKKKKKKK")

        self.possible_agents = [agentID for (agentID, _) in supportEnv.getAgentIDandNode()]

        # Initialize our observation spaces (the same for attacker and defender for the moment)
        # fake environment for the moment... todo : integrate support environment in pz environment
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

        allActions = []
        for nodeID, node in supportEnv.nodes.items():
            actionsOnNode = list(node.actions.keys())
            for actionOnNode in actionsOnNode:
                if not actionOnNode in allActions:
                    allActions += [actionOnNode]
        allActions = CustomSpace(Values(allActions))
        self.customAgentActions = {}
        for agent in self.possible_agents:
            self.customAgentActions[agent] = allActions

        self.action_spaces = {}
        for agent in self.possible_agents:
            self.action_spaces[agent] = allActions.convertToGymSpace()

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

        # print("Agent {} is playing action {}".format(
        #     agent, self.customAgentActions[agent].convertToRender(action)))

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


def env(supportEnv: Environment, render_mode=None):

    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    env = PzEnvironment(render_mode=internal_render_mode, supportEnv = supportEnv)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class EnvironmentPlayer:

    pzEnvironment: PzEnvironment
    envSupport: Environment
    iteration: int
    iterationMax: int
    agentID: List[str]
    fileName: str

    def saveFile(self):
        f = open("./worldStates/{}".format(self.fileName), "w+")
        json.dump(self.envSupport.serialize(), f)

    def __init__(self, envSupport: Environment, fileName: str = "defaultExample.json", iterationMax=10) -> None:
        self.envSupport = envSupport
        self.pzEnvironment = env(render_mode="", supportEnv=self.envSupport)
        self.iteration = 0
        self.iterationMax = iterationMax
        self.agentOnNodeIDs = envSupport.getAgentIDandNode()
        self.totalAgentNumber = len(self.agentOnNodeIDs)
        self.fileName = fileName
        self.saveFile()
        self.pzEnvironment.reset()

    def next(self) -> Tuple[str, str]:

        def attackerBehavior(observation, agent):
            return random.choice([0, 2])

        def defenderBehavior(observation, agent):
            return random.choice([0, 2])

        agentBehaviors = {
            "attacker1": attackerBehavior,
            "defender1": defenderBehavior
        }

        itera = self.pzEnvironment.agent_iter()

        # return the next agent to play
        agentID = itera.__iter__().__next__()

        """
        # get all observations, reward from last state (i.e all properties in agent sub-objects in the support environment)
        observation, reward, termination, truncation, info = self.pzEnvironment.last()

        # make the agent use all observations... to choose an action (i.e a number as a Values("Action1", "Action2", ...))
        action = agentBehaviors[agentID](observation, agentID)
        """

        # ... to adapt ...

        _, nodeID = self.envSupport.getAgentByID(agentID)

        self.agentOnNodeIDs = self.envSupport.getAgentIDandNode()
        self.totalAgentNumber = len(self.agentOnNodeIDs)

        if self.iteration >= self.iterationMax:
            print("Reached maxIteration !")
            return ""

        self.iteration += 1

        logs = self.envSupport.runAgentOnNode(agentID, nodeID)
        logs = "Iteration {}: ".format(self.iteration) + logs
        self.saveFile()

        self.pzEnvironment.step(0) # change properties of the support environment + logs in 'infos')

        return (agentID, logs)


if __name__ == '__main__':

    #  Some action functions
    def switchOnReimagable(agentID: str, envRef: Environment) -> None:
        envRef.nodes["PC"].properties.reimagable = True

    def switchOffReimagable(agentID: str, envRef: Environment) -> None:
        envRef.nodes["PC"].properties.reimagable = False

    # Some behaviour functions
    # def dumbBehaviour(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    #     return context.possible_actions[0]

    # Some behaviour functions
    def dumbBehaviour(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
        return actionDict["switchOffReimagable"].function

    network: Environment = Environment(nodes={
        "PC": Node(
            meta_data={},
            properties=Properties(
                processes=Processes(
                    agents={
                        "attacker1": Agent(name="simpleAttacker",
                                           running=True, description="A simple attacker",
                                           context=AgentContext(
                                               binary_file_location="C:\\Users\mwlr.exe",
                                               possible_actions=[
                                                   switchOffReimagable],
                                               knowledge={}),
                                           behaviour=dumbBehaviour),
                        "defender1": Agent(name="simpleDefender",
                                           running=True,
                                           description="A simple defender",
                                           context=AgentContext(
                                               binary_file_location="C:\\Users\dfdr.exe",
                                               possible_actions=[
                                                   switchOnReimagable],
                                               knowledge={}),
                                           behaviour=dumbBehaviour)
                    },
                    services={
                        "HTTPS": ListeningService("HTTPS", True, "HTTPS Service", []),
                        "SSH": ListeningService("SSH", True, "SSH Service", ["lambda/password123"])
                    },
                    other_processes={
                        "excel": Process("Excel", True, "Excel application")
                    }),
                file_system={
                    "C:\\Users\\.private": File("pwd.txt", "*", "text_file", "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
                },
                firewall=Firewall(
                    outgoing=[FirewallRule("RDP", "ALLOW", ""), FirewallRule("sudo", "ALLOW", ""), FirewallRule(
                        "SSH", "ALLOW", ""), FirewallRule("HTTP", "ALLOW", "")],
                    incoming=[FirewallRule("RDP", "ALLOW", ""), FirewallRule(
                        "SSH", "ALLOW", ""), FirewallRule("HTTP", "ALLOW", "")]
                ),
                installed_operating_system="Windows/12",
                installed_softwares="MSOffice/2021",
                accessible_nodes=[],
                other_properties=[],
                logs=[],
                reimagable=True,
                sla_weight=0.7,
                value=15,
            ),
            actions={
                "switchOnReimagable": Action(
                    actionID="switchOnReimagable",
                    description="Make the node reimagable",
                    success_probability=1,
                    function=switchOnReimagable,
                    cost=100),
                "switchOffReimagable": Action(
                    actionID="switchOfReimagable",
                    description="Make the node not reimagable",
                    cost=15,
                    function=switchOffReimagable,
                    success_probability=1)
            }
        )})

    player = EnvironmentPlayer(network, iterationMax=10)

    # print(player.envSupport)

    # print("\n\n")
    player.next()
    player.next()
    player.next()
    player.next()
    # print("\n\n")

    # print(player.envSupport)
