from typing import Any, Callable, Dict, Union, List, Tuple
from dataclasses import dataclass
import dataclasses
import json
from dataclasses_serialization.json import JSONSerializer
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

    def getAgentIDandNode(self) -> List[str]:
        agentIDs = []
        for nodeID, node in self.nodes.items():
            agentIDs += [(agentID, nodeID)
                         for agentID in list(node.properties.processes.agents.keys())]
        return agentIDs

    def getAgentByID(self, agentID: str) -> Tuple[Agent, str]:
        for nodeID, node in self.nodes:
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


class EnvironmentPlayer:
    env: Environment
    iteration: int
    iterationMax: int
    agentID: List[str]
    fileName: str

    def saveFile(self):
        f = open("./worldStates/{}".format(self.fileName), "w+")
        json.dump(self.env.serialize(), f)

    def __init__(self, env: Environment, fileName: str = "defaultExample.json", iterationMax=10) -> None:
        self.env = env
        self.iteration = 0
        self.iterationMax = iterationMax
        self.agentOnNodeIDs = env.getAgentIDandNode()
        self.totalAgentNumber = len(self.agentOnNodeIDs)
        self.fileName = fileName
        self.saveFile()

    def next(self) -> Tuple[str, str]:

        self.agentOnNodeIDs = self.env.getAgentIDandNode()
        self.totalAgentNumber = len(self.agentOnNodeIDs)

        if self.iteration >= self.iterationMax:
            print("Reached maxIteration !")
            return ""
        multipliedAgentOnNodesIDs = []
        nbActionPerTurn = 1
        for agentOnNodeID in self.agentOnNodeIDs:
            for i in range(0, nbActionPerTurn):
                multipliedAgentOnNodesIDs += [agentOnNodeID]

        (agentID,
         nodeID) = multipliedAgentOnNodesIDs[self.iteration % (self.totalAgentNumber * nbActionPerTurn)]
        self.iteration += 1
        logs = self.env.runAgentOnNode(agentID, nodeID)
        logs = "Iteration {}: ".format(self.iteration) + logs
        self.saveFile()
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

    print(player.env)

    print("\n\n")
    player.next()
    print("\n\n")

    print(player.env)
