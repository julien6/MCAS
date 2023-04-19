from collections import OrderedDict
from functools import reduce
import gymnasium
import numpy as np
from gymnasium import spaces
from pettingzoo.test import api_test
import re

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable, Union, Tuple, Set
import json
from environmentModel import Environment

import dataclasses
from environmentModel import environmentTest, Property
from environmentModel import Agent
from copy import copy
from pyeda.boolalg.expr import exprvar, expr
from pyeda.boolalg.table import expr2truthtable


# not usefull for the moment
def remakeList(jsonEntry: Dict[str, Dict[str, Any]]) -> Any:
    if all((key.isdigit() and isinstance(key, str)) for key in list(jsonEntry.keys())):
        indexes = list(jsonEntry.keys())
        l = [None] * len(indexes)
        for index in indexes:
            l[int(index)] = None
            l[int(index)] = jsonEntry[index]
        return l
    else:
        jsonRes = copy(jsonEntry)
        for key in jsonEntry:
            if isinstance(jsonEntry[key], dict):
                jsonRes[key] = remakeList(jsonEntry[key])
        return jsonRes


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class EnvironmentMngr:

    # the current environment model instance (dict of Nodes), such as:
    # {
    #    "node1": {
    #        "properties": {
    #           ...#current_properties...
    #        },
    #        "actions": {
    #           ...
    #           "action1": {
    #               "precondition": #boolean_property_expression,
    #               "effects": [#potential_effect_properties]
    #           }
    #           ...
    #       }
    #       ...
    #    }
    # }
    # it is to be modified only by actions
    environment: Any

    # initial environment used for reseting
    initialEnvironment: Any

    # all gathered possibles properties to be observed (i.e all possible actions effects properties), such as:
    # [("propertyName1", "propertyValue1"), ("propertyName2", "propertyValue2"), ...]
    obsPropSpace: Dict

    # gym space used to describe any observation in the same format:
    # for instance, if obsPropSpace = [property1, property2],
    # then, observation can be:
    #   - [None, None]
    #   - [None, property2]
    #   - [property1, None]
    #   - [property1, property2]
    # Coding with 0 = None and 1 = property, we have either [0,0] or [0,1] or [1,0] or [1,1]
    # so an observation is like [boolValue, boolValue] which is given by MultiBinary(2)
    obsGymSpace: spaces.Dict

    # all gathered possibles actions to be played, such as
    # [
    #   ("doNothing", {"description": "Do nothing", "success_probability": 1, "precondition": "True", "effects": {}, "cost": 100}),
    #   ("helloWorld", { "description": "Hello world", "success_probability": 1, "precondition": "True", "effects":
    #               { "[#AgentID][\"knowledge\"][\"message\"]": "Hello World"},"cost": 100},),
    #   ...
    # ]
    actPropSpace: OrderedDict

    # gym space used to describe any action in the same format:
    # for instance, if actPropSpace = [action1, action2, action3],
    # then, an action can be either action1 or action2 or action3
    # Coding with 0 = action1, 1 = action2 and 2 = action3, we have either 0 or 1 or 2
    # so an action is like x with x in {0,1,2} which is given by Discrete(3)
    actGymSpace: spaces.Dict

    # the list of all possible agents names (with full name path)
    agtPropSpace: List[str]

    def __init__(self, nodeEnvironment: Union[Environment, Any]) -> None:

        self.environment = json.loads(json.dumps(
            nodeEnvironment, cls=EnhancedJSONEncoder))["nodes"]

        self.initialEnvironment = copy(self.environment)

        # getting all observable properties, all possible action, all possible agent
        self.obsPropSpace, self.actPropSpace, self.agtPropSpace = self.getPropSpaces()

        # # getting observation and aciton spaces as Gym spaces as a vector and a finite number interval
        self.obsGymSpace = spaces.Dict({agentName: spaces.MultiBinary(len(
            agentObsPropSpace)) for agentName, agentObsPropSpace in self.obsPropSpace.items()})
        self.actGymSpace = spaces.Dict({agentName: spaces.Discrete(len(
            agentActPropSpace)) for agentName, agentActPropSpace in self.actPropSpace.items()})

    def reset(self):
        self.environment = self.initialEnvironment

    def getNodeIDPropFromAgtID(self, agentName: str) -> str:
        for nodeID, node in self.environment["nodes"].items():
            if agentName in list(node["processes"]["agents"].keys()):
                return nodeID

    def getValueFromJsonPath(self, jsonEntry, jsonPath):
        obj = jsonEntry
        for jsonKey in jsonPath[1:-1].split("]["):
            obj = obj.get(jsonKey[1:-1], None)
            if obj == None:
                return obj
        return obj

    def delValueFromJsonPath(self, jsonEntry, jsonPath):
        def _delValueFromJsonPath(jsonEntry, jsonKeys):
            if len(jsonKeys) == 1:
                del jsonEntry[jsonKeys[0]]
            else:
                key = jsonKeys.pop()
                _delValueFromJsonPath(jsonEntry[key], jsonKeys)
                return
        jsonKeys = [jsonKey[1:-1] for jsonKey in jsonPath[1:-1].split("][")]
        jsonKeys.reverse()
        return _delValueFromJsonPath(jsonEntry, jsonKeys)

    def setValueFromJsonPath(self, jsonEntry, jsonPath, value):
        def _setValueFromJsonPath(jsonEntry, jsonKeys):
            key = jsonKeys.pop()
            if (not key in jsonEntry.keys()):
                jsonEntry[key] = {}
            if len(jsonKeys) == 0:
                jsonEntry[key] = value
                return
            else:
                if type(jsonEntry[key]) == str:
                    jsonEntry[key] = {}
                _setValueFromJsonPath(jsonEntry[key], jsonKeys)

        jsonKeys = [jsonKey[1:-1] for jsonKey in jsonPath[1:-1].split("][")]
        jsonKeys.reverse()
        return _setValueFromJsonPath(jsonEntry, jsonKeys)

    def getPropSpaces(self) -> Tuple:
        agtPropSpace: List[str] = []
        actPropSpace: List[Tuple[str, Dict]] = []
        obsPropSpace: Dict[str, List] = {}
        agentsOnNodes = {}

        # Retrieving all agents on the node with their initial observations
        for nodeID, node in self.environment["nodes"].items():
            agentsOnNodes[nodeID] = list(
                node["processes"]["agents"].keys())
            agtPropSpace += agentsOnNodes[nodeID]
            for agent in agentsOnNodes:
                obsPropSpace[agent] = [("{}.processes.agents.{}.observations.{}".format(nodeID, agent, propID), propValue)
                                       for propID, propValue in list(node["processes"]["agents"][agent]["observations"].items())]

        actPropSpace = [(actionID, action) for actionID,
                        action in list(self.environment["actions"].items())]

        # Once we got all the agents, we can infer all of their potential observations
        for actionID, action in self.environment["actions"].items():

            # retrieve the post condition properties
            actionPostcondition = action["postcondition"]
            for propID, propValue in actionPostcondition.items():

                # as any agent can be on any node, we must infer the potential effects for {{node}} and {{agent}} shortcuts
                for nodeID in self.environment["nodes"].keys():
                    for agent in agtPropSpace:

                        # we replace variable shortcuts with all possible values for nodes and agents
                        inferedPropID = propID.replace(
                            "\{\{agent\}\}", "{}.processes.agents.{}".format(nodeID, agent))
                        inferedPropID = propValue.replace(
                            "\{\{node\}\}", nodeID)
                        inferedPropValue = propValue.replace(
                            "\{\{agent\}\}", "{}.processes.agents.{}".format(nodeID, agent))
                        inferedPropValue = propValue.replace(
                            "\{\{node\}\}", nodeID)

                        # the infered property for the agent is inserted in the possible observable properties set
                        obsPropSpace[agent].add(
                            (inferedPropID, inferedPropValue))

        return (obsPropSpace, actPropSpace, agtPropSpace)

    def fromActGymToActProp(self, actionGymDict):
        return {agentName: self.actPropSpace[agentName][actGymID] for agentName, actGymID in actionGymDict.items()}

    def fromActGymToActPropID(self, actionGymDict):
        return {agentName: self.actPropSpace[agentName][actGymID][0] for agentName, actGymID in actionGymDict.items()}

    def fromActPropToActGym(self, actionPropDict):
        return {agentName: int(self.actPropSpace[agentName].index(actProp)) for agentName, actProp in actionPropDict.items()}

    def fromActPropIDToActGym(self, actionPropDict):
        return {agentName: int([actProp[0] for actProp in self.actPropSpace[agentName]].index(actPropID)) for agentName, actPropID in actionPropDict.items()}

    def fromObsGymToObsProp(self, observationGymDict):
        return {agentName: [self.obsPropSpace[agentName][observationGymIndex] for observationGymIndex in range(0, len(observationGymVector)) if observationGymVector[observationGymIndex] == 1] for agentName, observationGymVector in observationGymDict.items()}

    def fromObsPropToObsGym(self, observationPropDict):
        return {agentName: [(1 if (observationProp in observationPropVector) else 0) for observationProp in self.obsPropSpace[agentName]] for agentName, observationPropVector in observationPropDict.items()}

    def getActGymID(self, agent, actionPropID):
        return list(self.fromActPropIDToActGym({agent: actionPropID}).values())[0]

    def getActPropID(self, agent, actionGymID):
        return list(self.fromActGymToActPropID({agent: actionGymID}).values())[0]

    def applyAction(self, actionGymID: int, agentPropID: str):
        """
        Apply action postcondition changes for the current agent
        """

        agentNodeID = self.getNodeIDPropFromAgtID(agentPropID)

        actionName, action = list(self.fromActGymToActProp(
            {agentPropID: actionGymID}).values())[0]
        precondition: str = action["precondition"]

        # We first infer the shortcut values for {{agent}} and {{node}} 
        precondition = precondition.replace(
            "\{\{agent\}\}", "{}.processes.agents.{}".format(agentNodeID, agentPropID))
        precondition = precondition.replace("\{\{node\}\}", agentNodeID)

        # Then, we want to replace the json path with the json environment value
        areAllPropertiesPresent = True
        for match in re.compile(r"([a-zA-Z0-9_]*\.[a-zA-Z0-9_]*)").finditer(" " + precondition + " "):
            conditionComponent = match.groups(0)[0]
            valuedConditionComponent = self.getValueFromJsonPath(self.environment, ["nodes"] + conditionComponent)
            if (valuedConditionComponent == None):
                areAllPropertiesPresent = False
                break
            if type(valuedConditionComponent) == str:
                valuedConditionComponent = '"{}"'.format(valuedConditionComponent)
            else:
                valuedConditionComponent = str(valuedConditionComponent)
            precondition = precondition.replace(conditionComponent, valuedConditionComponent)

        if (areAllPropertiesPresent):
            precondition = precondition.replace(
                '"', '').replace("=", "<=>")
            # print("EXPRESSION  ", booleanExpression)
            expression = expr(precondition)
            expression = str(expression).replace(
                "False", "0").replace("True", "1")
            preconditionSatisfied = True if int(
                expr2truthtable(expr(expression))) == 1 else False
            if (not preconditionSatisfied):
                print("error: precondition not meet : {}".format(precondition))
            else:

                # apply the post condition properties
                actionPostcondition = action["postcondition"]
                for propID, propValue in actionPostcondition.items():

                    # infering shortcut values
                    inferedPropID = propID.replace(
                    "\{\{agent\}\}", "{}.processes.agents.{}".format(agentNodeID, agentPropID))
                    inferedPropID = propValue.replace(
                    "\{\{node\}\}", agentNodeID)
                    inferedPropValue = propValue.replace(
                    "\{\{agent\}\}", "{}.processes.agents.{}".format(agentNodeID, agentPropID))
                    inferedPropValue = propValue.replace(
                    "\{\{node\}\}", agentNodeID)

                    # valuation of the json path with real value for the value part of the action
                    for match in re.compile(r"([a-zA-Z0-9_]*\.[a-zA-Z0-9_]*)").finditer(" " + inferedPropValue + " "):
                        valueComponent = match.groups(0)[0]
                        valuedValueComponent = self.getValueFromJsonPath(self.environment, '["nodes"]' + valueComponent)
                        if (valuedValueComponent == None):
                            print("error: no matching value for {}".format(valueComponent))
                            valuedValueComponent = "None"
                        if type(valuedValueComponent) == str:
                            valuedValueComponent = '"{}"'.format(valuedValueComponent)
                        else:
                            valuedValueComponent = str(valuedValueComponent)
                        inferedPropValue = inferedPropValue.replace(valueComponent, valuedValueComponent)

                    # updating the environment
                    self.setValueFromJsonPath(self.environment, '["nodes"]' + inferedPropID, inferedPropValue)

            # retrieving the observations and taking into account the fact the agent might have moved to another node
            agentNodeID = self.getNodeIDPropFromAgtID(agentPropID)
            agentObservation = self.environment["nodes"][agentNodeID]["processes"]["agents"][agentPropID]["observations"]

        return self.fromObsPropToObsGym({agent: list(OrderedDict(obs).items()) for agent, obs in agentObservation.items()})

    def getReward(self, agent, observations) -> float:

        # it can use the environment instead of the using only observations of the current agent
        rwds = {
            "attacker1": {
                "foundNode": {
                    "PC2Link": 10
                },
                "nodeLocation": {
                    "PC2": 100
                },
                "foundPassword": {
                    "abc": 200
                }
            },
            "defender1": {

            },
            "defender2": {

            }
        }

        reward: float = -1

        for obsProp in self.fromObsGymToObsProp({agent: observations[agent]})[agent]:
            obsPropName = obsProp[0].split("[\"knowledge\"]")[-1][2:-2]
            obsPropValue = obsProp[1]
            for rewObsPropName in list(rwds[agent].keys()):
                if rewObsPropName == obsPropName:
                    if obsPropValue == list(rwds[agent][rewObsPropName].keys())[0]:
                        reward += list(rwds[agent][rewObsPropName].values())[0]

        return reward


if __name__ == '__main__':
    # new envMng from a predefined two nodes state
    envMngr = EnvironmentMngr(nodeEnvironment=environmentTest)

    gymSpace = envMngr.obsGymSpace  # geting the gym observation space
    obsGymSample = gymSpace.sample()  # to a sample (as an agent would)

    #  an agent is choosing an action in actGymSpace[agent]
    actGym = envMngr.fromActPropIDToActGym(
        {'["PC1"]["properties"]["processes"]["agents"]["attacker1"]': "observeReimagableOnNodePC1"})
    actGym = [x[1] for x in actGym.items()][0]

    obsProp = envMngr.applyAction(actGym,
                                  '["PC1"]["properties"]["processes"]["agents"]["attacker1"]')

    print(obsProp, "\n\n\n")

    obsGym = envMngr.fromObsPropToObsGym(obsProp)

    print(obsGym)

    obsProp2 = envMngr.fromObsGymToObsProp(obsGym)

    print(obsProp2)
