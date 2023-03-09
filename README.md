### **WARNING : this projet is a work in progress, onging changes are likely to break some of the functionalities**

# Multi Cyber Agent Simulator
**Multi Cyber Agent Simulator (MCAS)** is intended to implement the Dec-POMDP model of an environment made up from node network on which attack and defender agents are interacting each other and modifying the same environment.

## Project Goals
This project is largely inspired by the context of [CyberBattleSim](https://github.com/microsoft/CyberBattleSim) in a multi-agent approach.
It aims to provide a way to simulate a network of nodes on which  attack actions are coordinately applied by attacking agents according to a realistic based attack scenario.
Additionally, like cyber-attackers, it also aims to implement defenders whose behaviors result in different organization (whether pre-determined or not).
Consequences of applied action brings out a new environment state, optionally changing the agent knowledge and observations and bringing agents closer or further from their local goals.

## Requirements
- Python version >= 3.9
- Node version >= v18.14.x

## Installation
In "backend", type "python install requirements.txt"
Then, in "backend/src", type: "python -m flask --app server run"

In "frontend", type "npm install"
Then, in "frontend", type "npm run start"

Open a webpage at http://localhost:4200/
The user interface should be displayed

## Basic interface usage

When using terminal, avaialbe command lines are

- ls : list avaialbe environment scenarios
- load [environment_file.json]

![alt text](https://github.com/julien6/MCAS/blob/main/blop/basics.gif?raw=true)

- next : so next agent plays to interact with environment / other agents

![alt text](https://github.com/julien6/MCAS/blob/main/blop/next.gif?raw=true)

- iterate_over [number of iteration] : so several iteration can occur in a single command

![alt text](https://github.com/julien6/MCAS/blob/main/blop/iterate_over.gif?raw=true)

