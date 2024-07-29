from ecmwfapi import ECMWFDataServer
import ecmwfapi
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import cartopy.crs as crs
import cartopy.feature as cfeature
from shapely import geometry
import pandas as pd

server = ECMWFDataServer()

class df:
    '''This class includes all needed functions to download a list of files from the ecmwf forecast data of total precipitation.
    The functions can easily adapted for other parameters like temperature, humidity, wind etc. Visit therefore the documentation of the parameters of enfo and 
    change param in the following functions.
    
    https://apps.ecmwf.int/datasets/data/s2s-realtime-instantaneous-accum-ecmf/levtype=sfc/type=pf
    '''

    def download_ecmwf_pf(date):
        '''Download the enfo total precipitation forecast data (perturbed forecast) from ECMWF via ECMWFAPI client for a specific date and the next 144 forecast timesteps.
        The input value date should be a string in the format 'YYYY-MM-DD'.'''
        
        # check if date has the correct format
        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            raise ValueError("Date has to be in the format: 'YYYY-MM-DD'.")
            
        year, month, day = date.split('-')
        filename = f'enfo_pf_{year}_{month}_{day}.nc'

        try:
            server.retrieve({
                "class": "s2",                # Dataset class
                "dataset": "s2s",             # Dataset name
                "date": date,                 # Date range
                "expver": "prod",             # Experiment version
                "levtype": "sfc",             # Level type
                "model": "glob",              # Model type
                "number": "1/to/100",                # Ensemble member numbers from 1 to 100
                "origin": "ecmf",             # Originating centre
                "param": "228228",            # Parameter (total precipitation)
                "step": "0/6/12/18/24/30/36/42/48/54/60/66/72/78/84/90/96/102/108/114/120/126/132/138/144", # Forecast steps in 6-hour intervals (maximum 1104)
                "stream": "enfo",             # Stream
                "time": "00:00:00",           # Forecast time (start)
                "type": "pf",                 # Forecast type (perturbed forecast)
                "format": "netcdf",           # Output format as netcdf
                "target": filename            # Target file name
            })
            print(f"Successfully downloaded data for {date} to {filename}")
        except ecmwfapi.api.APIException as e:
            raise RuntimeError(f"Download failed for {date}. APIException: {e}")
        except Exception as e:
            raise RuntimeError(f"Download failed for {date}. Error: {e}")
    
    def download_ecmwf_cf(date):
        '''download enfo total precipitation data from ecmwf the control forecast for a specific date and the next 144 forecast steps.
        The input value date should be a string in the format 'YYYY-MM-DD'. '''

        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            raise ValueError("Date has to be in the format: 'YYYY-MM-DD'.")
            
        year, month, day = date.split('-')
        filename = f'enfo_cf_{year}_{month}_{day}.nc'

        try:
            server.retrieve({
                "class": "s2",
                "dataset": "s2s",
                "date": date,
                "expver": "prod",
                "levtype": "sfc",
                "model": "glob",
                "origin": "ecmf",
                "param": "228228",
                "step": "0/6/12/18/24/30/36/42/48/54/60/66/72/78/84/90/96/102/108/114/120/126/132/138/144",
                "stream": "enfo",
                "time": "00:00:00",
                "type": "cf",
                "target": filename
            })
            print(f"Successfully downloaded control forecast data from {date} to {filename}")
        
        except ecmwfapi.api.APIException as e:
            raise RuntimeError(f"Download failed for {date}. APIException: {e}")
        except Exception as e:
            raise RuntimeError(f"Download failed for {date}. Error: {e}")
    
    def get_datelist(startdate, enddate):
        '''Returns a list of dates between startdate and enddate, inclusive.
        
        Input:
            startdate (str): Start date in the format 'YYYY-MM-DD'.
            enddate (str): End date in the format 'YYYY-MM-DD'.
        
        Returns:
            list: List of dates in the format 'YYYY-MM-DD'.
        
        Raises:
            ValueError: If startdate or enddate is not a string, or if dates are not in the correct format, 
                        or if enddate is before startdate.
        '''
        
        # Validation of the input parameters
        if not isinstance(startdate, str) or not isinstance(enddate, str):
            raise ValueError("Both startdate and enddate must be strings.")
        
        try:
            start_date = datetime.strptime(startdate, '%Y-%m-%d')
            end_date = datetime.strptime(enddate, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")
        
        if end_date < start_date:
            raise ValueError("End date cannot be before start date.")
        
        # Empty list, which will be returned at the end of function
        date_list = []
        
        # Loop from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return date_list

class plots:
    '''This class includes all function to create plots of the forecast data.'''
    def extract_region(dataset, lat_min, lat_max, lon_min, lon_max):
        """
        Extracts data from an xarray Dataset for a specific geographic region.

        Parameters:
        dataset (xarray.Dataset): Input xarray Dataset containing the data.
        lat_min (float): Minimum latitude of the region.
        lat_max (float): Maximum latitude of the region.
        lon_min (float): Minimum longitude of the region.
        lon_max (float): Maximum longitude of the region.

        Returns:
        xarray.Dataset: Subset of the input dataset containing data only for the specified region.
        """
        # Ensure lat_min <= lat_max and lon_min <= lon_max
        lat_min, lat_max = sorted([lat_min, lat_max])
        lon_min, lon_max = sorted([lon_min, lon_max])
        
        # Select latitude and longitude slices based on available dimensions
        if 'latitude' in dataset.dims and 'longitude' in dataset.dims:
            subset = dataset.sel(latitude=(dataset.latitude >= lat_min) & (dataset.latitude <= lat_max), longitude=(dataset.longitude >= lon_min) & (dataset.longitude <= lon_max))
        elif 'lat' in dataset.dims and 'lon' in dataset.dims:
            subset = dataset.sel(lat=(dataset.lat >= lat_min) & (dataset.lat <= lat_max), lon=(dataset.lon >= lon_min) & (dataset.lon <= lon_max))
        else:
            raise ValueError("Latitude or longitude dimensions not found in the dataset.")
        
        return subset
    
    def read_data(dataset):
        '''Read in dataset and return the values of variables total precipitation, lon, lat, time and number (optional)'''

        tp = dataset.tp
        lon = dataset.lon
        lat = dataset.lat
        time = dataset.time
        if any(v is None for v in [tp, lon, lat, time]):
            raise ValueError("Dataset is missing required fields")
        if hasattr(dataset, 'number'):
            number = dataset.number.values
            return tp, lon, lat, time, number
        else:
            return tp, lon, lat, time
        
    def plot_map_tp(dataset, date):
        '''Plot the precipitation for the whole area. Choose one date and all timesteps available from this day will be plotted.'''
        tp, lon, lat, time = read_data(dataset)
        bounds = np.linspace(0, 100, 51)
        
        # Convert time to pandas datetime
        time = pd.to_datetime(time, errors='coerce')  # Coerce invalid dates to NaT
        
        if time.isnull().any():
            raise ValueError("Invalid date format or range")
        
        # Define the times to plot for the specific date (00, 6, 12, 18 hours)
        times_to_plot = pd.to_datetime([
            f"{date}T00:00:00.000000000",
            f"{date}T06:00:00.000000000",
            f"{date}T12:00:00.000000000",
            f"{date}T18:00:00.000000000"
        ])
        
        # Create subplots
        fig, axs = plt.subplots(1, len(times_to_plot), figsize=(16, 6), subplot_kw={'projection': crs.Mercator()})
        contour_plots = []
        for i, t in enumerate(times_to_plot):
            if t in time:
                index = np.where(time == t)[0][0]
                
                ax = axs[i]
                ax.coastlines()
                ax.add_feature(cfeature.BORDERS)
                ax.add_feature(cfeature.RIVERS, color='darkslategrey')
                
                filled_vimd = ax.contourf(lon, lat, tp[index, :, :], levels=bounds, transform=crs.PlateCarree(), cmap='BuPu')
                contour_plots.append(filled_vimd)
                
                title = t.strftime("%d/%m/%Y %H:%M")
                ax.set_title(title)
        
        # Add a single colorbar below all subplots
        cbar_ax = fig.add_axes([0.1, -0.1, 0.8, 0.05])  # [left, bottom, width, height]
        cbar = fig.colorbar(contour_plots[0], cax=cbar_ax, orientation='horizontal', format='%.1f')
        cbar.set_label('[kg/m²]', fontsize=12)
        # Add overall title
        date_first_day = pd.to_datetime(time[0]).strftime("%d/%m/%Y")
        fig.suptitle(f"Forecast of {date_first_day}", fontsize=16)
        
        plt.tight_layout()
        plt.show()
        saveas = pd.to_datetime(time[0]).strftime("%Y_%m_%d")
        plt.savefig(f'forecast_precipitation_map_{saveas}.png')
        plt.close()
    
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
    

        