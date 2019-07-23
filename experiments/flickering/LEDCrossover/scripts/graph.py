import os
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

class Graph(object):

    def graph():
        plt.plot(x_value, y_value)
        plt.ylabel("Intensity")
        plt.xlabel("Time Elapsed (ms)")
        plt.show()

if __name__ == '__main__':
    os.chdir("..")
    freq = [5]
    colors = ["LIME", "GREEN", "BLUE", "RED"]
    for f in freq:
        with open("data/100p_%shz.csv" % (f), "r") as file:
            df = pd.read_csv(file, names=["TIME", "LIME", "GREEN", "BLUE", "RED"])
        file.close()
    for color in colors:
        if color == "LIME":
            c = "y"
        else:
            c = color[0].lower()
        plt.scatter(df["TIME"], df[color], c=c)
        plt.plot(df["TIME"], df[color], c=c)
    plt.show()
