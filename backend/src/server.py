from flask import Flask, Response, request
from flask_cors import CORS
import os
import json
from typing import Dict, List
from env import EnvironmentPlayer, McasEnvironment, env, loadFile
from backend.src.older.environmentModel import environmentTest

app = Flask(__name__)
CORS(app)

environmentPlayer: EnvironmentPlayer = None

worldStateFolder = "worldStates"

metrics: Dict[str, List] = {}


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
