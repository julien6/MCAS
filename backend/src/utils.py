import functools

import gymnasium
import numpy as np
from gymnasium import spaces
from pettingzoo.test import api_test

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

from typing import Dict, List, Any, Callable, Union
import json


class Action:
    precondition: str
    outcomes: Dict


class Agent:
    own_properties: Dict
    knowledge: Dict


class OtherProperties:
    reimagibility: bool


class Properties:
    processes: Dict[str, Agent]
    otherProperties: OtherProperties


class Environment:
    properties: Properties
    actions: Dict[str, Action]
    engine: Callable[[Any], None]

    def __init__(self, properties: Properties, actions: Dict[str, Action], engine: Callable[[Any], None] = lambda env: None) -> None:
        self.properties = properties
        self.actions = actions
        self.engine = engine

    def afterEffect(self):
        self.engine(self)

# ===========================

class Values:
    values: List[Any]

    def __init__(self, *args):
        self.values = args


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class CustomSpace:

    customEnvironment: Any

    def __init__(self, customEnvironment: Any) -> None:
        self.customEnvironment = customEnvironment

    def _convertToGymSpace(self, space):
        if type(space) == dict:
            converted = {}
            keys = list(space.keys())
            for key in keys:
                if (isinstance(space[key], Values)):
                    converted[key] = spaces.Discrete(len(space[key].values))
                else:
                    converted[key] = self._convertToGymSpace(space[key])
            return spaces.Dict(converted)
        if type(space) == list:
            converted = []
            for element in space:
                if (isinstance(element, Values)):
                    converted += [len(element.values)]
            return spaces.MultiDiscrete(converted)
        if isinstance(space, Values):
            return spaces.Discrete(len(space.values))

    def convertToGymSpace(self) -> Union[spaces.Dict, spaces.MultiDiscrete, spaces.Discrete]:
        return self._convertToGymSpace(self.customEnvironment)

    def _convertToRender(self, sample, mapping):
        if type(sample) == dict:
            mapped = {}
            keys = list(sample.keys())
            for key in keys:
                if (type(sample[key]) == int):
                    mapped[key] = mapping[key].values[sample[key]]
                else:
                    mapped[key] = self._convertToRender(
                        sample[key], mapping[key])
            return mapped
        if type(sample) == list:
            mapped = []
            for i in range(0, len(sample)):
                if (isinstance(sample[i], int)):
                    mapped += [mapping[i].values[sample[i]]]
            return mapped
        if type(sample) == int:
            return mapping.values[sample]

    def convertToRender(self, environmentState):
        return self._convertToRender(json.loads(json.dumps(environmentState, cls=NpEncoder)), self.customEnvironment)


if __name__ == '__main__':
    # e = env(render_mode="human")
    # api_test(e)

    agent_knowledge = {
        "properties": {
            "accessible_nodes": {
                "PC2": [Values(None, "SSH"), Values(None, "RDP")],
            },
            "file_system": {
                "C:\\Users\\.private": {
                    "file_name": Values(None, "pwd.txt"),
                    "hash": Values(None, "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"),
                    "permission": Values(None, "*"),
                    "type": Values(None, "text_file")
                }
            },
            "firewall": {
                "incoming": {
                    "RDP": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "RDP"),
                    },
                    "SSH": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "SSH"),
                    },
                    "HTTP": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "HTTP"),
                    }
                },
                "outgoing": {
                    "RDP": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "RDP"), },
                    "sudo": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "sudo"), },
                    "SSH": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "SSH"), },
                    "HTTP": {
                        "permission": Values(None, "ALLOW"),
                        "port": Values(None, "HTTP"), }
                }
            },
            "installed_operating_system": Values(None, "Windows/12"),
            "installed_softwares": Values(None, "MSOffice/2021"),
            "other_properties": {},
            "processes": {
                "other_processes": {
                    "excel": {
                        "name": Values(None, "Excel"),
                        "running": Values(None, True)
                    }
                },
                "services": {
                    "HTTPS": {
                        "allowedCredentials": [],
                        "name": Values(None, "HTTPS"),
                        "running": Values(None, True)
                    },
                    "SSH": {
                        "allowedCredentials": [
                            Values(None, "lambda/password123")
                        ],
                        "name": Values(None, "SSH"),
                        "running": Values(None, True)
                    }
                }
            },
            "reimagable": Values(None, True, False),
        }
    }

    #  TODO : make the Values() to allow Values(None, {any space description dict to be converted})
    # agent_knowledge = Values(None, Values({"k": Values(None, "values")}))

    # ce = CustomSpace(agent_knowledge)

    # ceGymSpace = ce.convertToGymSpace()

    # print("Gym Space: " + str(ceGymSpace))

    # sample = ceGymSpace.sample()

    # # print("\n\n")

    # print("Gym sample: " + str(sample))

    # readableSample = ce.convertToRender(sample)

    # print(readableSample)

    # ================================

    # d = Values(None, {
    #     "filePath": Values(None, "pwd")
    # })

    # d = spaces.Dict({
    #     "ok": spaces.MultiDiscrete([3,4])
    # })

    # res1 = d.sample()

    # # res = d.from_jsonable(res1)

    # print(res1)
