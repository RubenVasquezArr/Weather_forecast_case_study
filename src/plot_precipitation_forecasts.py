import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import scipy 
import pandas as pd
import matplotlib.dates as mdates


def plot_precipitation_forecasts(ensemble, mean_precipitation, std_precipitation):
    #First we create the plot
    fig, ax = plt.subplots()
    #first we mark the day we want, the 18 of may
    ax.axvline(
        pd.to_datetime("05/18/2024"),
        linestyle = '--',
        linewidth = 3,
        color='gray',
        label="18 of May")
    #to get the label of the ensemble lines, we draw only the first one
    ax.plot(
        ensemble.time,
        ensemble.tp.sel(number = ensemble.number.values[0]),
        color='lightblue',
        alpha=0.5,
        label="Ensemble")
    #then we plot all the rest, witout label. i we add a label here, the legend would have too many labels, one for each ensemble
    ax.plot(
        ensemble.time,
        ensemble.tp.sel(number = ensemble.number.values[1:]),
        color='lightblue',
        alpha=0.5)
    #here we plot the mean precipitation of the forecast ensemble 
    ax.plot(
        mean_precipitation.time,
        mean_precipitation.tp,
        color='blue',
        linewidth=2,
        label="Mean Forecast")
    #here we plot the standar deviation of the  precipitation of the forecast ensemble 
    plt.fill_between(
        mean_precipitation.time, 
        mean_precipitation.tp-std_precipitation.tp, 
        mean_precipitation.tp+std_precipitation.tp,
        color='yellow', 
        label="SD Forecast",
        linewidth= 1)
    #finally some details
    ax.set_title(f"Precipitation Forecast of {str(ensemble.time.values[0]).partition('T')[0]}")
    ax.set_xlabel('Day')
    ax.set_ylabel('Precipitation [mm]')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.legend()
    plt.show()
 