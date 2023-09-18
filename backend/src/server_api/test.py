import matplotlib.pyplot as plt, mpld3
import numpy as np

fig, ax = plt.subplots()
ax.plot(np.random.rand(20), '-o', alpha=0.5,
        color='black', linewidth=5,
        markerfacecolor='green',
        markeredgecolor='lightgreen',
        markersize=20,
        markeredgewidth=10)
ax.grid(True, color='#EEEEEE', linestyle='solid')
ax.set_xlim(-2, 22)
ax.set_ylim(-0.1, 1.1)

mpld3.save_json(fig, open("./data.json", "w+"))