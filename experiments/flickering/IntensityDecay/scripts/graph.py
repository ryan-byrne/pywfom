import os
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

if __name__ == '__main__':
    os.chdir("..")
    colors = ["LIME", "GREEN", "BLUE", "RED"]
    freq = [1/300, 10, 25, 50]
    for c in colors:
        for f in freq:
            with open("data/%s_100p_%shz.csv" % (c, f), "r") as file:
                df = pd.read_csv(file, names=["TIME", c])
            file.close()
            plt.plot(df["TIME"], df[c])
            plt.title("%s at %s Hz" % (c, str(f)))
            plt.xlabel("Time")
            plt.ylabel("%s Intensity" % (c))
            plt.show()
