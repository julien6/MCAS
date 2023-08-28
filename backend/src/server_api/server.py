from flask import Flask, Response, request
from flask_cors import CORS
import os
import time
import json
from typing import Dict, List, Any
from pettingzoo import AECEnv
from backend.src.simulation_models.cyborg.cyborg_environment import CyborgEnvironment

from backend.src.simulation_models.cyst.cyst_environment import CystEnvironment
from backend.src.simulation_models.mcas._mcas_environment import McasEnvironment

# from env import EnvironmentPlayer, McasEnvironment, env, loadFile
# from backend.src.older.environmentModel import environmentTest

app = Flask(__name__)
CORS(app)

# environmentPlayer: EnvironmentPlayer = None

# worldStateFolder = "worldStates"

# metrics: Dict[str, List] = {}

# for simulation
env: AECEnv = None
simulation_engine: str = None
number_of_episodes: int = None
number_of_iterations: int = None
iteration_pause_duration: int = None
scenario_plan: Any = None
pause: bool = False


@app.post('/set-simulation-scenario-plan')
def set_simulation_scenario():
    simulation_engine = request.args.get("simulation_engine", "mcas")
    number_of_episodes = request.args.get("number_of_episodes", 1)
    number_of_iterations = request.args.get("number_of_iterations", 1)
    iteration_pause_duration = request.args.get("iteration_pause_duration", 0)
    scenario_plan = {}
    try:
        scenario_plan = request.json
    except Exception as e:
        raise e

    if simulation_engine == "CYST":
        env = CystEnvironment(scenario_plan)

    if simulation_engine == "MCAS":
        env = McasEnvironment(scenario_plan)

    if simulation_engine == "CybORG":
        env = CyborgEnvironment(scenario_plan)

    return Response("", status=200, mimetype='application/json')


@app.get("/pause-resume-simulation")
def pause_simulation():
    pause = not pause


@app.get("/start-simulation")
def start_simulation():

    for episode_number in range(0, number_of_episodes):

        env.reset(seed=42)
        for agent in env.agent_iter(max_iter=number_of_iterations):

            if pause:
                return env.scenario_data()

            observation, reward, termination, truncation, info = env.last()
            action = env.agent_instance(agent).next_action(observation, reward)
            env.step(action)

            time.sleep(iteration_pause_duration)

        return env.scenario_data()

# ==============================================


@app.route("/")
def hello_world():
    return "MCAS Backend"


@app.get("/createExample")
def createExample():
    global environmentPlayer
    e: McasEnvironment = env(environment=environmentTest, render_mode="human")
    environmentPlayer = EnvironmentPlayer(env=e)

    logs = "A new example environment was created"
    print(logs)
    return {"environment": environmentPlayer.dictEnvironment(), "logs": logs}


@app.get("/metrics")
def getMetrics():
    return metrics


@app.get("/worldState")
def getWorldState():
    filePath = request.args.get("filePath")
    if filePath == None:
        return {}
    try:
        global environmentPlayer
        if (filePath.split(".")[-1] == "json"):
            environmentPlayer = loadFile(
                "./" + worldStateFolder + "/" + filePath)
    except Exception as e:
        return [{"error": str(e)}]
    return environmentPlayer.dictEnvironment()


@app.get("/worldStateList")
def getWorldStateList():
    path = request.args.get("path")
    if path == None:
        path = ""
    listDir = []
    try:
        listDir = os.listdir("./" + worldStateFolder + "/" + path)
    except Exception as e:
        return [{"error": str(e)}]
    return listDir


@app.get("/currentWorldState")
def getCurrentWorldState():
    global environmentPlayer
    if environmentPlayer == None:
        return {}
    return environmentPlayer.dictEnvironment()


def extractMetricsFromCurrent() -> None:
    totalValue = 0
    global environmentPlayer
    for nodedID, node in environmentPlayer.dictEnvironment().items():
        totalValue += node["properties"]["value"]
    if (not "value" in list(metrics.keys())):
        metrics["value"] = []
    metrics["value"] += [totalValue]


@app.get("/nextWorldState")
def getNextWorldState():
    global environmentPlayer
    agentID, logs = environmentPlayer.next()
    extractMetricsFromCurrent()
    return {"environment": environmentPlayer.dictEnvironment(), "logs": logs, "agentID": agentID.split("']['")[-1][:-2],
            "metrics": metrics}


@app.get("/iterateOverWorldState")
def getIteratedNextWorldState():
    maxIteration = int(request.args.get("maxIteration"))
    logsAcc = []
    lastAgent = ""
    global environmentPlayer
    for i in range(0, maxIteration):
        lastAgent, logs = environmentPlayer.next()
        extractMetricsFromCurrent()
        logsAcc += [logs]
    return {"environment": environmentPlayer.dictEnvironment(), "logs": logsAcc, "agentID": lastAgent.split("']['")[-1][:-2], "metrics": metrics}


@app.post('/saveWorldState')
def saveWorldState():
    path = request.args.get("filePath")
    if ("." not in list(path)):
        return Response("Invalid file name", status=400, mimetype='application/json')
    data = {}
    try:
        data = request.json
    except Exception as e:
        raise e
    f = open("./" + worldStateFolder + "/" + path, "w+")
    f.write(json.dumps(data))
    f.close()
    return Response("", status=200, mimetype='application/json')


@app.post('/worldState')
def uploadworldState():
    f = request.files.getlist("file")[0]
    f.save(worldStateFolder + "/" + f.filename)
    return Response("Success", status=200, mimetype='application/json')


@app.delete('/worldState')
def deleteWorldState():
    try:
        os.remove("./" + worldStateFolder + "/" + request.args["filePath"])
    except Exception as e:
        print(str(e))
        return Response(str(e), status=400, mimetype='application/json')
    return Response("", status=200, mimetype='application/json')
