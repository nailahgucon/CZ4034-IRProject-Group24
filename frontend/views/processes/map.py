import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pickle

def plot(list_places):
    loc = [i.get("location") for i in list_places]
    lat=[]
    lon=[]
    init_points = 3
    for i in loc:
        loc_ = i.split(",")
        lat.append(float(loc_[0]))
        lon.append(float(loc_[1]))
    names = [i.get("Name") for i in list_places]

    fig, ax = plt.subplots()
    ax.scatter(x=lat[:init_points], y=lon[:init_points])

    points, = ax.plot(lat[0], lon[0])

    ax.set_xlabel('Latitude')
    fig.subplots_adjust(left=0.25, bottom=0.25)

    axfreq = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    points_slider = Slider(
        ax=axfreq,
        label='Number of points',
        valmin=3,
        valmax=10,
        valinit=init_points,
    )

    # # The function to be called anytime a slider's value changes
    def update(val):
        points.set_xdata(lat[:val])
        points.set_ydata(lon[:val])
        # fig.canvas.draw_idle()
    
    points_slider.on_changed(update)

    # plt.savefig('books_read.png')
    pickle.dump(fig, open('frontend/views/plots/dist.fig.pickle', 'wb'))
    


# The parametrized function to be plotted
# def f(t, amplitude, frequency):
#     return amplitude * np.sin(2 * np.pi * frequency * t)

# t = np.linspace(0, 1, 1000)

# Define initial parameters
# init_amplitude = 5
# init_frequency = 3

# Create the figure and the line that we will manipulate
# fig, ax = plt.subplots()
# line, = ax.plot(t, f(t, init_amplitude, init_frequency), lw=2)
# ax.set_xlabel('Time [s]')

# # adjust the main plot to make room for the sliders
# fig.subplots_adjust(left=0.25, bottom=0.25)

# Make a horizontal slider to control the frequency.
# axfreq = fig.add_axes([0.25, 0.1, 0.65, 0.03])
# freq_slider = Slider(
#     ax=axfreq,
#     label='Frequency [Hz]',
#     valmin=0.1,
#     valmax=30,
#     valinit=init_frequency,
# )

# Make a vertically oriented slider to control the amplitude
# axamp = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
# amp_slider = Slider(
#     ax=axamp,
#     label="Amplitude",
#     valmin=0,
#     valmax=10,
#     valinit=init_amplitude,
#     orientation="vertical"
# )


# The function to be called anytime a slider's value changes
# def update(val):
#     line.set_ydata(f(t, amp_slider.val, freq_slider.val))
#     fig.canvas.draw_idle()


# # register the update function with each slider
# freq_slider.on_changed(update)
# amp_slider.on_changed(update)

# # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
# resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
# button = Button(resetax, 'Reset', hovercolor='0.975')


# def reset(event):
#     freq_slider.reset()
#     amp_slider.reset()
# button.on_clicked(reset)

# plt.show()