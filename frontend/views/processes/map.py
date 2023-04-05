import matplotlib
import numpy as np

matplotlib.use('Agg')
import pickle

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def plot(list_places):
    init_points = 3
    nearest = list_places[:init_points]
    names = [i.get("Name") for i in nearest]
    loc = [i.get("location") for i in nearest]
    lat=[]
    lon=[]
    for i in loc:
        loc_ = i.split(",")
        lat.append(float(loc_[0]))
        lon.append(float(loc_[1]))

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(x=lat, y=lon)
    for i, txt in enumerate(names):
        ax.annotate(txt, (lat[i], lon[i]))
    
    plt.title("Scatter plot of 2 nearest places")
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")

    pickle.dump(fig, open('frontend/views/plots/dist.fig.pickle', 'wb'))
