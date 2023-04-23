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

markers = ["v", "o", "x", ".", "*", "+", "s", "d"]

for agent, averageCumulativeRewards in agentsRewards.items():
    plt.scatter(x, averageCumulativeRewards, marker=markers.pop(0),
                s=70, alpha=0.25, label=agent)

plt.rcParams.update({'font.size': 20})

# plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.legend(bbox_to_anchor=(0.7, 0.1), loc='lower left')
plt.tight_layout()
plt.xlabel("Episodes", size=25)
plt.ylabel("Average of rewards by episode", size=25)

# plt.savefig('/home/julien/Bureau/graphs.pdf')

plt.show()
