from flask import Flask, Response, request
from flask_cors import CORS
import os
import json
from typing import Dict, List
from scenario import network, switchOnReimagable, switchOffReimagable,\
    dumbBehaviour, doNothing, dumbBehaviourAttacker, dumbBehaviourDefender, observeReimagable, \
    discoverLink, scanPC2Ports, moveToPC2WithSSH, gettingFlag, attackerBehaviour, \
    defenderBehaviour1, defenderBehaviour2, discoverLogsMalwareOnPC1, sendMalwareWarningToSimpleDefender2, \
    discoverLogsMalwareOnPC2, detectMalwareBinaryFile, removeMalwareBinaryFile
from environment import deserialize, EnvironmentPlayer

app = Flask(__name__)
CORS(app)

environmentPlayer: EnvironmentPlayer = None

worldStateFolder = "worldStates"

metrics: Dict[str, List] = {}

# our common environment object to play with
# environment = new Environment()


def prepareEnvironmentForGraph(env: Dict):
    return {
        "nodes": [{"id": nodeID, "label": nodeID, "data": node} for nodeID, node in env["nodes"].items()],
        "edges": []
    }


def prepareEnvironmentForBackend(env: Dict):
    preparedEnv = {"nodes": {}}
    for node in env["nodes"]:
        if "data" in list(node.keys()):
            preparedEnv["nodes"][node["id"]] = node["data"]
    return preparedEnv


@app.route("/")
def hello_world():
    return "MCAS Backend"


@app.get("/createExample")
def createExample():
    global environmentPlayer
    environmentPlayer = EnvironmentPlayer(network, iterationMax=1000)
    logs = "A new example environment was created"
    print(logs)
    return {"environment": prepareEnvironmentForGraph(environmentPlayer.env.serialize()), "logs": logs}


@app.get("/metrics")
def getMetrics():
    return metrics


@app.get("/worldState")
def getWorldState():
    filePath = request.args.get("filePath")
    if filePath == None:
        filePath = ""
    fileContent = {}
    try:
        if (filePath.split(".")[-1] == "json"):
            fileContent = json.load(
                open("./" + worldStateFolder + "/" + filePath, "r"))

        global environmentPlayer

        if (environmentPlayer != None):
            environmentPlayer = EnvironmentPlayer(
                env=deserialize(
                    fileContent,
                    {
                        "switchOnReimagable": switchOnReimagable,
                        "switchOffReimagable": switchOffReimagable,
                        "dumbBehaviour": dumbBehaviour,
                        "doNothing": doNothing,
                        "dumbBehaviourAttacker": dumbBehaviourAttacker,
                        "dumbBehaviourDefender": dumbBehaviourDefender,
                        "observeReimagable": observeReimagable,
                        "discoverLink": discoverLink,
                        "scanPC2Ports": scanPC2Ports,
                        "moveToPC2WithSSH": moveToPC2WithSSH,
                        "gettingFlag": gettingFlag,
                        "attackerBehaviour": attackerBehaviour,
                        "defenderBehaviour1": defenderBehaviour1,
                        "defenderBehaviour2": defenderBehaviour2,
                        "discoverLogsMalwareOnPC1": discoverLogsMalwareOnPC1,
                        "sendMalwareWarningToSimpleDefender2": sendMalwareWarningToSimpleDefender2,
                        "discoverLogsMalwareOnPC2": discoverLogsMalwareOnPC2,
                        "detectMalwareBinaryFile": detectMalwareBinaryFile,
                        "removeMalwareBinaryFile": removeMalwareBinaryFile


                    }),
                fileName=environmentPlayer.fileName,
                iterationMax=environmentPlayer.iterationMax)
        else:
            environmentPlayer = EnvironmentPlayer(
                env=deserialize(
                    fileContent,
                    {
                        "switchOnReimagable": switchOnReimagable,
                        "switchOffReimagable": switchOffReimagable,
                        "dumbBehaviour": dumbBehaviour,
                        "doNothing": doNothing,
                        "dumbBehaviourAttacker": dumbBehaviourAttacker,
                        "dumbBehaviourDefender": dumbBehaviourDefender,
                        "observeReimagable": observeReimagable,
                        "discoverLink": discoverLink,
                        "scanPC2Ports": scanPC2Ports,
                        "moveToPC2WithSSH": moveToPC2WithSSH,
                        "gettingFlag": gettingFlag,
                        "attackerBehaviour": attackerBehaviour,
                        "defenderBehaviour1": defenderBehaviour1,
                        "defenderBehaviour2": defenderBehaviour2,
                        "discoverLogsMalwareOnPC1": discoverLogsMalwareOnPC1,
                        "sendMalwareWarningToSimpleDefender2": sendMalwareWarningToSimpleDefender2,
                        "discoverLogsMalwareOnPC2": discoverLogsMalwareOnPC2,
                        "detectMalwareBinaryFile": detectMalwareBinaryFile,
                        "removeMalwareBinaryFile": removeMalwareBinaryFile
                    }), iterationMax=1000)

    except Exception as e:
        return [{"error": str(e)}]

    return prepareEnvironmentForGraph(fileContent)


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
    if environmentPlayer == None:
        return {
            "nodes": [],
            "edges": []
        }
    return prepareEnvironmentForGraph(environmentPlayer.env.serialize())


def extractMetricsFromCurrent() -> None:
    totalValue = 0
    for nodedID, node in environmentPlayer.env.nodes.items():
        totalValue += node.properties.value
    if (not "value" in list(metrics.keys())):
        metrics["value"] = []
    metrics["value"] += [totalValue]


@app.get("/nextWorldState")
def getNextWorldState():
    agentID, logs = environmentPlayer.next()
    extractMetricsFromCurrent()
    print(metrics)
    return {"environment": prepareEnvironmentForGraph(environmentPlayer.env.serialize()), "logs": logs, "agentID": agentID,
            "metrics": metrics}


@app.get("/iterateOverWorldState")
def getIteratedNextWorldState():
    maxIteration = int(request.args.get("maxIteration"))
    logsAcc = []
    lastAgent = ""
    for i in range(0, maxIteration):
        lastAgent, logs = environmentPlayer.next()
        extractMetricsFromCurrent()
        logsAcc += [logs]
    return {"environment": prepareEnvironmentForGraph(environmentPlayer.env.serialize()), "logs": logsAcc, "agentID": lastAgent, "metrics": metrics}


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
    print(data)
    data = prepareEnvironmentForBackend(data)
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
