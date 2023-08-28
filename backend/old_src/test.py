import json
import matplotlib.pyplot as plt

agentsRewards = {}

marlRewards = json.load(open("marl.json", "r"))

for agent, rewards in marlRewards.items():
    if (agent == "attacker1"):
        agentsRewards["MARL_attacker1"] = rewards
    if (agent == "attacker2"):
        agentsRewards["MARL_attacker2"] = rewards
    if (agent == "defender1"):
        agentsRewards["defender1"] = rewards
    if (agent == "defender2"):
        agentsRewards["defender2"] = rewards

dtRewards = json.load(open("dt.json", "r"))

for agent, rewards in dtRewards.items():
    if (agent == "attacker1"):
        agentsRewards["DT_attacker1"] = rewards
    if (agent == "attacker2"):
        agentsRewards["DT_attacker2"] = rewards
    if (agent == "defender1"):
        agentsRewards["defender1"] = rewards
    if (agent == "defender2"):
        agentsRewards["defender2"] = rewards

print(agentsRewards.keys())

x = [int(episodeIndex) for episodeIndex in range(0, 1000)]

markers = ["v", "o", "x", "s", "*", ".", "+", "s", "d"]
scales = [20, 70, 20, 20, 70, 20]

for agent, averageCumulativeRewards in agentsRewards.items():
    plt.scatter(x, averageCumulativeRewards, marker=markers.pop(0),
                s=scales.pop(0), alpha=0.2, label=agent)

plt.rcParams.update({'font.size': 20})

# plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.legend(bbox_to_anchor=(0.22, 1.0), loc='upper right')
plt.tight_layout()
plt.xlabel("Episodes", size=15)
plt.ylabel("Average of rewards by episode", size=15)
plt.show()
