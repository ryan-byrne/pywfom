import pandas as pd
import matplotlib.pyplot as plt

path = "C:/Users/rbyrne/eclipse-workspace/splassh/experiments/flickering/Experiment_1/data"
red = pd.read_csv(  path+"/red.txt",
                    delimiter="\t",
                    names=["Time", "Timestamp", "Intensity"])

t = red["Time"]
i = red["Intensity"]

plt.plot(t, i)
plt.show()
