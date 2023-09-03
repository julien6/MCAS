from flask import Flask, Response, request
from flask_cors import CORS
import os
import time
import json
from typing import Dict, List, Any
from simulation_models.cyborg.CyborgEnvironment import CyborgEnvironment
# from simulation_models.cyst.cyst_environment import CystEnvironment
# from simulation_models.mcas._mcas_environment import McasEnvironment
from simulation_models.SimulationModel import SimulationModel

app = Flask(__name__)
CORS(app)


# for simulation
env: SimulationModel = None
simulation_engine: str = None
number_of_episodes: int = None
number_of_iterations: int = None
iteration_pause_duration: int = None


@app.post('/set-simulation-scenario-plan')
def set_simulation_scenario():
    simulation_engine = request.args.get("simulation_engine", "CybORG")
    number_of_episodes = int(request.args.get("number_of_episodes", 1))
    number_of_iterations = int(request.args.get("number_of_iterations", 1))
    iteration_pause_duration = int(
        request.args.get("iteration_pause_duration", 0))
    scenario_plan = {}
    try:
        scenario_plan = request.json
    except Exception as e:
        raise e

    if simulation_engine == "CYST":
        # env = CystEnvironment(scenario_plan)
        pass

    if simulation_engine == "MCAS":
        # env = McasEnvironment(scenario_plan)
        pass

    if simulation_engine == "CybORG":
        global env
        env = CyborgEnvironment(
            scenario_plan, max_episode=number_of_episodes, max_iteration=number_of_iterations)

    return Response("", status=200, mimetype='application/json')


@app.get("/next-simulation")
def next_iteration():
    """Update environment to next state (next iteration and/or episode)
    Returns None when max episode and max iteration is reached.
    """
    global env
    res = env.next()
    if res == None:
        return "Max iteration reached"
    else:
        return res