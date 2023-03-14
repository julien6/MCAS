from collections import OrderedDict
from functools import reduce
import gymnasium
import numpy as np
from gymnasium import spaces
from pettingzoo.test import api_test
import re

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable, Union, Tuple
import json
from environmentModel import Environment

from flatten_json import flatten, unflatten
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
        agtPropSpace = []
        actPropSpace = {}
        extendedEffectsProperties = []
        for nodeID, node in self.environment.items():
            agentsOnNode = ['["{}"]["properties"]["processes"]["agents"]["{}"]'.format(nodeID, agentName) for agentName in list(
                node["properties"]["processes"]["agents"].keys())]

            for agentOnNode in agentsOnNode:
                actPropSpace[agentOnNode] = []

            agtPropSpace += agentsOnNode
            for actionName, action in node["actions"].items():
                effectProperties = list(action["effects"].items())
                for effectPropertyName, effectPropertyValue in effectProperties:
                    extendedPropertyName = effectPropertyName
                    extendedPropertyValue = effectPropertyValue
                    if "#[" in str(extendedPropertyValue):
                        for match in re.compile(r"#(\[.*?\])[^\[]").finditer(" " + extendedPropertyValue + " "):
                            propertyName = match.groups(0)[0]
                            prop = self.getValueFromJsonPath(
                                self.environment, propertyName)
                            extendedPropertyValue = extendedPropertyValue.replace(
                                "#" + propertyName, str(prop))
                    if "[#AgentID]" in effectPropertyName:
                        effectProperties.remove(
                            (effectPropertyName, effectPropertyValue))
                        for agentOnNode in agentsOnNode:
                            extendedPropertyName = effectPropertyName.replace(
                                "[#AgentID]", agentOnNode)
                            effectProperties += [(extendedPropertyName,
                                                  extendedPropertyValue)]

                extendedEffectsProperties += effectProperties

                for agentOnNode in agentsOnNode:
                    actPropSpace[agentOnNode] += [(actionName, action)]

        allObsPropSpace = [prop for prop in list([(prop[0], prop[1])
                                                  for prop in extendedEffectsProperties]) if "knowledge" in prop[0]]

        obsPropSpace = {
            agentName: [obProp for obProp in allObsPropSpace if agentName in obProp[0]] for agentName in agtPropSpace
        }
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
        actionName, action = list(self.fromActGymToActProp(
            {agentPropID: actionGymID}).values())[0]
        print("\t -> Action {} is being played by {}".format(actionName, agentPropID))
        precondition: str = action["precondition"]
        booleanExpression = precondition
        areAllPropertiesPresent = True
        for match in re.compile(r"(\[.*?\])[^\[]").finditer(" " + precondition + " "):
            initialConditionProperty = match.groups(0)[0]
            conditionProperty = initialConditionProperty.replace(
                "[#AgentID]", agentPropID)

            conditionPropertyValue = str(self.getValueFromJsonPath(
                self.environment, conditionProperty))
            if conditionPropertyValue == None:
                areAllPropertiesPresent = False
                print("error: property {} is not present".format(conditionProperty))
                break
            booleanExpression = booleanExpression.replace(
                initialConditionProperty, conditionPropertyValue)

        if (areAllPropertiesPresent):
            observations: List[Property] = []
            agentObservation: Dict = {agent: {} for agent in self.agtPropSpace}
            expression = expr(booleanExpression)
            expression = str(expression).replace(
                "False", "0").replace("True", "1")
            preconditionSatisfied = True if int(
                expr2truthtable(expr(expression))) == 1 else False
            if (not preconditionSatisfied):
                print("error: precondition not meet : {}".format(precondition))
            for propName, propValue in action["effects"].items():
                if ("[#AgentID]" in propName):
                    propName = propName.replace("[#AgentID]", agentPropID)
                # first remove all properties in current state that have the same propName as
                # the properties we want to add
                lastValue = self.getValueFromJsonPath(
                    self.environment, propName)
                if lastValue != None:
                    self.delValueFromJsonPath(self.environment, propName)
                # then adding new properties and their values
                if propValue != None:
                    if ("#[" in str(propValue)):
                        for match in re.compile(r"#(\[.*\])").finditer(" " + propValue + " "):
                            propValue = propValue.replace(
                                "#" + match.groups(0)[0], str(self.getValueFromJsonPath(self.environment, match.groups(0)[0])))
                    for match in re.compile(r'^(\[\".*?\"\]\[\"properties\"\]\[\"processes\"\]\[\"agents\"\]\[\".*?\"\])\[\"knowledge\"\]').finditer(propName):
                        agentKnowledgeName = match.groups(0)[0]
                        print("\t -> new agent {} knowledge property: ({}, {})".format( agentKnowledgeName, propName, propValue))
                        extendedPropName = copy(propName)
                        extendedPropName = extendedPropName.replace('{}["knowledge"]'.format(agentKnowledgeName), "")[2:-2]
                        agentObservation[agentKnowledgeName][extendedPropName] = propValue
                    # adding new properties in environment (whether in agents knowledge or not)
                    self.setValueFromJsonPath(
                        self.environment, propName, propValue)

        return agentObservation


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