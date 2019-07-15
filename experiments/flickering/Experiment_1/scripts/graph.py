import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

class Graph(object):

    def graph(file):
        
        path = "C:/Users/rbyrne/eclipse-workspace/splassh/experiments/flickering/Experiment_1/data"
        data = pd.read_csv( path+"/"+file,
                            delimiter="\t",
                            names=["Timestamp", "Time", "Intensity"])

        t_0 = float(data["Time"][0])
        t = [float(t_i)-t_0 for t_i in data["Time"]]
        i = data["Intensity"]
        plt.plot(t, i)
        plt.ylabel("Intensity")
        plt.xlabel("Time Elapsed (ms)")
        plt.show()

if __name__ == '__main__':
    Graph.graph("100_sat_LIME_intensity_5.txt")
