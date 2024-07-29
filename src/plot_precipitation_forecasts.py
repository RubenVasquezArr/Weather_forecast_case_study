import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import scipy 
import pandas as pd
import matplotlib.dates as mdates


def plot_precipitation_forecasts(ensemble, mean_precipitation, std_precipitation, xlim=None, ylim=None):
    """
        Generates a plot of precipitation forecasts, including ensemble forecasts, mean forecast, and standard deviation.

        Parameters:
        ensemble (dataset): A dataset containing ensemble forecast data, with dimensions of time and number (ensemble member).
        mean_precipitation (dataset): A dataset containing the mean precipitation forecast.
        std_precipitation (dataset): A dataset containing the standard deviation of precipitation forecast.

        Returns:
        A plot displaying:
        - Ensemble forecasts (light blue lines)
        - Mean forecast (blue line)
        - Standard deviation of forecast (yellow shaded area)
        - A vertical line marking May 18th, 2024 (gray dashed line)

        Plot Details:
        - Title: Precipitation Forecast of [start date]
        - X-axis: Day (formatted as mm-dd)
        - Y-axis: Precipitation [mm]
        - Legend: Ensemble, Mean Forecast, SD Forecast
        """
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
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    plt.legend()
    plt.show()

    def extract_forecasts_info(data, lat, lon):
        """
        Interpolates weather forecast data to a specific latitude and longitude,
        and calculates the mean and standard deviation of precipitation across ensemble members.

        Parameters:
        data (xarray.Dataset): The weather forecast data containing ensemble members.
        lat (float): The latitude for interpolation.
        lon (float): The longitude for interpolation.

        Returns:
        tuple: A tuple containing:
            - ensemble (xarray.DataArray): Interpolated ensemble forecast data at the given location.
            - mean_precipitation (xarray.DataArray): Mean precipitation across ensemble members.
            - std_precipitation (xarray.DataArray): Standard deviation of precipitation across ensemble members.
        """
        ensemble = data.interp(longitude=lon, latitude=lat)
        mean_precipitation = ensemble.mean(dim='number')
        std_precipitation = ensemble.std(dim='number')
        return ensemble, mean_precipitation,std_precipitation
        