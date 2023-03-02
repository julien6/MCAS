from typing import Callable, Dict
from environment import Environment, AgentContext, Node, Process, Processes, Properties, \
    Agent, ListeningService, Firewall, FirewallRule, File, Action, EnvironmentPlayer


#  For t2 scenario
def observeReimagable(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC1"].properties.processes.agents[agentID].context\
            .knowledge["reimagable"] = envRef.nodes["PC1"].properties.reimagable


def switchOnReimagable(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC1"].properties.reimagable = True
        # del envRef.nodes["PC1"].properties.processes.agents[agentID].context.knowledge["reimagable"]


def switchOffReimagable(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC1"].properties.reimagable = False
        # del envRef.nodes["PC1"].properties.processes.agents[agentID].context.knowledge["reimagable"]


def doNothing(agentID: str, envRef: Environment) -> None:
    pass


def dumbBehaviourAttacker(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    if ("reimagable" in list(context.knowledge.keys())):
        if (context.knowledge["reimagable"] == True):
            del context.knowledge["reimagable"]
            return actionDict["switchOffReimagable"].function
    return actionDict["observeReimagable"].function


def dumbBehaviourDefender(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    if ("reimagable" in list(context.knowledge.keys())):
        if (context.knowledge["reimagable"] == False):
            del context.knowledge["reimagable"]
            return actionDict["switchOnReimagable"].function
    return actionDict["observeReimagable"].function


def dumbBehaviour(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    return actionDict["doNothing"].function


# For t3 scenario

# defender
def discoverLogsMalwareOnPC1(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        if (len(envRef.nodes["PC1"].properties.logs) > 0):
            envRef.nodes["PC1"].properties.value = 5
            for log in envRef.nodes["PC1"].properties.logs:
                if "scanPortExecuted" in log:
                    envRef.nodes["PC1"].properties.processes.agents[agentID] \
                        .context.knowledge["potentialMalware"] = log.split(" ")[-1]


def sendMalwareWarningToSimpleDefender2(agentID: str, envRef: Environment):
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC1"].properties.value = 30
        envRef.nodes["PC2"].properties.processes.agents["simpleDefender2"].context. \
            knowledge["potentialMalwareReceived"] = envRef.nodes["PC1"].properties.processes.agents[agentID] \
            .context.knowledge["potentialMalware"]
        del envRef.nodes["PC1"].properties.processes.agents[agentID] \
            .context.knowledge["potentialMalware"]


def discoverLogsMalwareOnPC2(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC2"].properties.processes.agents[agentID].running):
        if (len(envRef.nodes["PC2"].properties.logs) > 0):
            envRef.nodes["PC1"].properties.value = 10
            for log in envRef.nodes["PC2"].properties.logs:
                if "SSH" in log:
                    envRef.nodes["PC2"].properties.processes.agents[agentID] \
                        .context.knowledge["potentialMalwareSSH"] = log.split(" ")[0]


def detectMalwareBinaryFile(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC2"].properties.processes.agents[agentID].running):

        potentialMalwareSSH = envRef.nodes["PC2"].properties.processes.agents[agentID] \
            .context.knowledge["potentialMalwareSSH"]

        envRef.nodes["PC2"].properties.processes.agents[agentID] \
            .context.knowledge["identifiedMalwareBinary"] = envRef.nodes["PC2"].properties.processes. \
            agents[potentialMalwareSSH].context.binary_file_location


def removeMalwareBinaryFile(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC2"].properties.processes.agents[agentID].running):
        malwareName = envRef.nodes["PC2"].properties.processes.agents[agentID] \
            .context.knowledge["potentialMalwareSSH"]
        del envRef.nodes["PC2"].properties.processes.agents[malwareName]
        envRef.nodes["PC2"].properties.processes.agents[agentID] \
            .context.knowledge["deletedMalware"] = malwareName
        envRef.nodes["PC1"].properties.processes.agents["simpleDefender"] \
            .context.knowledge["malwareDeleted"] = True


def defenderBehaviour1(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    knowProperties = list(context.knowledge.keys())

    if ("malwareDeleted" in knowProperties):
        return actionDict["doNothing"].function

    if ("potentialMalware" in knowProperties):
        return actionDict["sendMalwareWarningToSimpleDefender2"].function

    if (not "potentialMalware" in knowProperties):
        return actionDict["discoverLogsMalwareOnPC1"].function

    return actionDict["doNothing"].function


def defenderBehaviour2(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    knowProperties = list(context.knowledge.keys())

    if ("deletedMalware" in knowProperties):
        return actionDict["doNothing"].function

    if ("identifiedMalwareBinary" in knowProperties):
        return actionDict["removeMalwareBinaryFile"].function

    if ("potentialMalwareSSH" in knowProperties):
        return actionDict["detectMalwareBinaryFile"].function

    if ("potentialMalwareReceived" in knowProperties):
        return actionDict["discoverLogsMalwareOnPC2"].function

    return actionDict["doNothing"].function


# attacker
def discoverLink(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC1"].properties.processes.agents[agentID].context.knowledge["discoveredLink"] = "PC2Link"


def scanPC2Ports(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):

        envRef.nodes["PC1"].properties.processes.agents[agentID].context.knowledge["PC2_PortNmap"] = envRef \
            .nodes["PC2"].properties.firewall.incoming

        envRef.nodes["PC1"].properties.processes.agents[agentID].context.knowledge["PC1_PortNmap"] = envRef \
            .nodes["PC1"].properties.firewall.outgoing

        envRef.nodes["PC1"].properties.logs = [
            "scanPortExecuted by {}".format(agentID)]


def moveToPC2WithSSH(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC1"].properties.processes.agents[agentID].running):
        envRef.nodes["PC2"].properties.processes.agents[agentID] = envRef.nodes["PC1"].properties.processes.agents[agentID]

        del envRef.nodes["PC1"].properties.processes.agents[agentID]

        envRef.nodes["PC2"].properties.processes.agents[agentID].context.knowledge["hostNode"] = "PC2"

        envRef.nodes["PC2"].properties.logs = [
            "{} logged in SSH".format(agentID)]


def gettingFlag(agentID: str, envRef: Environment) -> None:
    if (envRef.nodes["PC2"].properties.processes.agents[agentID].running):
        envRef.nodes["PC2"].properties.processes.agents[agentID].context.knowledge["rewardFlag"] = envRef \
            .nodes["PC2"].properties.other_properties[0]


def attackerBehaviour(agentID: str, context: AgentContext, actionDict: Dict[str, Action]) -> Callable[[str, Environment], None]:
    knowProperties = list(context.knowledge.keys())

    if ("rewardFlag" in knowProperties):
        return actionDict["doNothing"].function

    if ("hostNode" in knowProperties):
        if context.knowledge["hostNode"] == "PC2":
            return actionDict["gettingFlag"].function

    if (not "discoveredLink" in knowProperties):
        return actionDict["discoverLink"].function

    if (not "PC2_PortNmap" in knowProperties):
        return actionDict["scanPC2Ports"].function

    return actionDict["moveToPC2WithSSH"].function


network: Environment = Environment(nodes={
    "PC1": Node(
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
                actionID="ObserveFileSystem",
                description="Make the node not reimagable",
                cost=15,
                function=switchOffReimagable,
                success_probability=1)
        }
    )})


if __name__ == '__main__':

    from environment import deserialize, EnvironmentPlayer

    environmentPlayer: EnvironmentPlayer = EnvironmentPlayer(network)

    print(environmentPlayer.next())

    print(environmentPlayer.env)
