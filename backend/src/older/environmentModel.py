from typing import Any, Dict, Tuple
from dataclasses import dataclass

Property = Tuple[str, str]


@dataclass
class Process:
    name: str
    running: bool


@dataclass
class ListeningService (Process):
    allowedCredentials: Dict[str, str]


@dataclass
class Action:
    description: str
    success_probability: float
    precondition: str  # boolean expression of the precondition properties
    effects: Dict[str, Property]
    cost: int


@dataclass
class Agent(Process):
    knowledge: Dict[str, str]
    binary_file_location: str


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
    outgoing: Dict[str, FirewallRule]
    incoming: Dict[str, FirewallRule]


@dataclass
class Properties:
    processes: Processes
    file_system: Dict[str, File]
    firewall: Firewall
    installed_softwares: Dict[str, str]
    installed_operating_system: str
    reimagable: bool
    value: int
    sla_weight: float
    accessible_nodes: Dict[str, Tuple[str, str]]
    other_properties: Dict[str, str]
    logs: Dict[str, str]


@dataclass
class Node:
    meta_data: any
    properties: Properties
    actions: Dict[str, Action]


@dataclass
class Environment:
    nodes: Dict[str, Node]


environmentTest = Environment({
    "PC1": Node(
        meta_data={},
        properties=Properties(
            processes=Processes(
                agents={
                    "attacker1": Agent(name="simpleAttacker",
                                       running=True,
                                       binary_file_location="C:\\Users\mwlr.exe",
                                       knowledge={
                                           "knowHowToSwitchOnReimagablePC1": True,
                                           "hasRootPrivilege": True
                                       }),
                    "defender1": Agent(name="simpleDefender",
                                       running=True,
                                       binary_file_location="C:\\Users\dfdr.exe",
                                       knowledge={
                                           "knowHowToSwitchOnReimagablePC1": True,
                                           "hasRootPrivilege": True
                                       })
                },
                services={
                    "HTTPS": ListeningService("HTTPS", True, {}),
                    "SSH": ListeningService("SSH", True, {"lambda": "lambda/password123"})
                },
                other_processes={
                    "excel": Process("Excel", True)
                }),
            file_system={
                "C:\\Users\\.private": File("pwd.txt", "*", "text_file", "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
            },
            firewall=Firewall(
                outgoing={"RDP": FirewallRule("RDP", "ALLOW", ""), "sudo": FirewallRule("sudo", "ALLOW", ""), "SSH": FirewallRule(
                    "SSH", "ALLOW", ""), "HTTP": FirewallRule("HTTP", "ALLOW", "")},
                incoming={"RDP": FirewallRule("RDP", "ALLOW", ""), "SSH": FirewallRule(
                    "SSH", "ALLOW", ""), "HTTP": FirewallRule("HTTP", "ALLOW", "")}
            ),
            installed_operating_system="Windows/12",
            installed_softwares="MSOffice/2021",
            accessible_nodes={},
            other_properties={},
            logs={},
            reimagable=True,
            sla_weight=0.7,
            value=15,
        ),
        actions={
            "doNothing": Action(
                description="Do nothing",
                precondition='True',
                effects={},
                success_probability=1,
                cost=100),
            "helloWorld": Action(
                description="Do nothing",
                precondition='True',
                effects={'[#AgentID]["knowledge"]["message"]': "Hello World"},
                success_probability=1,
                cost=100),
            "switchOnReimagableOnPC1": Action(
                description="Make the node reimagable",
                precondition='~["PC1"]["properties"]["reimagable"]&[#AgentID]["running"]&([#AgentID]["knowledge"]["knowHowToSwitchOnReimagablePC1"]|[#AgentID]["knowledge"]["observation"]["hasRootPrivilege"])',
                effects={
                    '["PC1"]["properties"]["reimagable"]': 'True',
                    '["PC1"]["properties"]["logs"]["reimagableSetToTrue"]': None,
                    '[#AgentID]["knowledge"]["firstSwitchOn"]': True},
                success_probability=1,
                cost=100),
            "discoverNodePC2": Action(
                description="Discover the node PC2",
                precondition='[#AgentID]["running"]',
                effects={'[#AgentID]["knowledge"]["knowNeighbours"]': "PC2"},
                cost=15,
                success_probability=1),
            "observeReimagableOnNodePC1": Action(
                description="Observe the reimagable value on node PC1",
                precondition='[#AgentID]["running"]',
                effects={'[#AgentID]["knowledge"]["reimagable"]':
                         '#["PC1"]["properties"]["reimagable"]'},
                cost=15,
                success_probability=1),
            "observeSoftwaresOnNodePC1": Action(
                description="Observe the installed software on node PC1",
                precondition='[#AgentID]["running"]',
                effects={'[#AgentID]["knowledge"]["installedSoftwareOnNodePC1"]':
                         '#["PC1"]["properties"]["installed_softwares"]'},
                cost=15,
                success_probability=1),
            "switchOffReimagableOnPC1": Action(
                description="Make the node not reimagable",
                precondition='["PC1"]["properties"]["reimagable"]&[#AgentID]["running"]',
                effects={'["PC1"]["properties"]["reimagable"]': 'False', '["PC1"]["logs"]["reimagableSetToFalse"]': 'reimagable set to false',
                         '["PC1"]["properties"]["logs"]["reimagableSetToTrue"]': None, '[#AgentID]["knowledge"]["secretFileLocation"]': 'C:\\secret.txt'},
                cost=15,
                success_probability=1)
        }
    ),
    "PC2": Node(
        meta_data={},
        properties=Properties(
            processes=Processes(
                agents={
                    "attacker2": Agent(name="simpleAttacker2",
                                       running=True,
                                       binary_file_location="C:\\Users\mwlr.exe",
                                       knowledge={}),
                    "defender2": Agent(name="simpleDefender2",
                                       running=True,
                                       binary_file_location="C:\\Users\dfdr.exe",
                                       knowledge={})
                },
                services={
                    "HTTPS": ListeningService("HTTPS", True, {}),
                    "SSH": ListeningService("SSH", True, {"lambda": "lambda/password123"})
                },
                other_processes={
                    "excel": Process("Excel", True)
                }),
            file_system={
                "C:\\Users\\.private": File("pwd.txt", "*", "text_file", "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")
            },
            firewall=Firewall(
                outgoing={"RDP": FirewallRule("RDP", "ALLOW", ""), "sudo": FirewallRule("sudo", "ALLOW", ""), "SSH": FirewallRule(
                    "SSH", "ALLOW", ""), "HTTP": FirewallRule("HTTP", "ALLOW", "")},
                incoming={"RDP": FirewallRule("RDP", "ALLOW", ""), "SSH": FirewallRule(
                    "SSH", "ALLOW", ""), "HTTP": FirewallRule("HTTP", "ALLOW", "")}
            ),
            installed_operating_system="Windows/12",
            installed_softwares="MSOffice/2021",
            accessible_nodes={},
            other_properties={},
            logs={},
            reimagable=True,
            sla_weight=0.7,
            value=15,
        ),
        actions={
            "doNothing": Action(
                description="Do nothing",
                precondition='True',
                effects={},
                success_probability=1,
                cost=100),
            "helloWorld": Action(
                description="Do nothing",
                precondition='True',
                effects={'[#AgentID]["knowledge"]["message"]': "Hello World"},
                success_probability=1,
                cost=100),
            "switchOnReimagableOnPC2": Action(
                description="Make the node reimagable",
                precondition="",
                effects={'["PC2"]["properties"]["reimagable"]': "True"},
                success_probability=1,
                cost=100),
            "switchOffReimagableOnPC2": Action(
                description="Make the node not reimagable",
                precondition="",
                effects={'["PC2"]["properties"]["reimagable"]': "False"},
                cost=15,
                success_probability=1)
        }
    )
})

if __name__ == '__main__':
    print(environmentTest)
