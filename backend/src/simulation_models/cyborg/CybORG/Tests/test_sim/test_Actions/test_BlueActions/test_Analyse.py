import pytest 
import itertools 
from copy import deepcopy

from simulation_models.cyborg.CybORG.Tests.test_sim.sim_fixtures import compromised_cyborg, SCENARIOS
from simulation_models.cyborg.CybORG.Agents.Utils import ObservationWrapper
from simulation_models.cyborg.CybORG.Simulator.Actions import Analyse, ExploitRemoteService, PrivilegeEscalate
from simulation_models.cyborg.CybORG.Shared.Enums import SessionType, OperatingSystemType, ProcessType, ProcessState, TrinaryEnum
from simulation_models.cyborg.CybORG.Tests.EphemeralPort import Win2008EphemeralPort, LinuxEphemeralPort

SCENARIO = 'Scenario2'
HOSTS = SCENARIOS[SCENARIO]['Hosts']

EXPLOIT_PARAMETERS = ['session', 'agent', 'hostname']

@pytest.fixture(params=HOSTS, scope='module')
def target_host(request):
    return request.param

@pytest.fixture(scope='module')
def target_ip(cyborg, target_host):
    return cyborg.get_ip_map()[target_host]

@pytest.fixture(scope='module')
def cyborg(target_host):
    return compromised_cyborg(SCENARIO, stop_host=target_host, stop_value=3)

@pytest.fixture(scope='module')
def action(target_host):
    return Analyse(hostname=target_host, session=0, agent='Blue')

@pytest.fixture(scope='module')
def observation(cyborg, action):
    results = cyborg.step(action=action, agent='Blue')

    return ObservationWrapper(results.observation)

def test_Analyse_success(observation, target_host):
    assert observation.success == True

def test_Analyse_num_hosts(observation, target_host):
    expected_value = 1 if target_host not in ('User0', 'Defender') else 0

    assert len(observation.hosts) == expected_value

def test_Analyse_interfaces(observation, target_ip, target_host):
    interface = []
    expected_interface = interface

    assert observation.get_interfaces(target_ip) == expected_interface

def test_Analyse_processes(observation, target_ip, target_host):
    expected_processes = []

    assert observation.get_processes(target_ip) == expected_processes

def test_Analyse_sessions(observation, target_ip, target_host, cyborg):
    agent_session = HOSTS.index(target_host)
    expected_sessions = []

    assert observation.get_sessions(target_ip) == expected_sessions

def test_Analyse_os_info(observation, target_ip, target_host):
    expected_os_info = {}

    assert observation.get_os_info(target_ip) == expected_os_info

@pytest.fixture(params=EXPLOIT_PARAMETERS, scope='module')
def junk_action(action, request):
    junk_action = deepcopy(action) 
    setattr(junk_action, request.param, 'Junk')

    return junk_action

@pytest.fixture(scope='module')
def junk_observation(cyborg, junk_action):
    results = cyborg.step(action=junk_action, agent='Red')

    return results.observation

def test_Analyse_junk_input_observation(junk_observation, junk_action):
    assert junk_observation == {'success':TrinaryEnum.UNKNOWN}


@pytest.fixture(scope='module')
def last_action(cyborg, junk_observation):
    # Junk observation required to ensure cyborg actually executes junk action
    return cyborg.get_last_action('Red')

def test_Analyse_junk_input_action(last_action):
    assert last_action.name == 'InvalidAction'

def test_Analyse_junk_input_replaced_action(last_action, junk_action):
    assert getattr(last_action, 'action') == junk_action

def test_Analyse_unscanned(cyborg, target_host, action):
    cyborg.reset()
    action = Analyse(hostname=target_host, agent='Red', session=0)
    results = cyborg.step(action=action, agent='Red')

    assert results.observation == {'success': TrinaryEnum.UNKNOWN}
