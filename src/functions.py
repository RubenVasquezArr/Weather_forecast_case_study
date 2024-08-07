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
import folium
from folium import plugins
from folium.raster_layers import ImageOverlay
import rasterio
from rasterio.plot import reshape_as_image
from matplotlib.colors import Normalize, PowerNorm, LinearSegmentedColormap
import scipy
import matplotlib.dates as mdates
import os
import sys

server = ECMWFDataServer()

class df:
    '''This class includes all needed functions to download a list of files from the ecmwf forecast data of total precipitation.
    The functions can easily adapted for other parameters like temperature, humidity, wind etc. Visit therefore the documentation of the parameters of enfo and
    change param in the following functions.

    https://apps.ecmwf.int/datasets/data/s2s-realtime-instantaneous-accum-ecmf/levtype=sfc/type=pf
    '''

    def download_ecmwf_pf(date):
        """
        Download the ECMWF perturbed forecast total precipitation data for a specific date and the next 144 forecast steps.

        This function retrieves the ensemble perturbed forecast data from the ECMWF for the specified date,
        downloading the total precipitation data at 6-hour intervals for the next 144 forecast hours.
        The input value `date` should be a string in the format 'YYYY-MM-DD'. The retrieved data is saved
        to a NetCDF file named 'enfo_pf_YYYY_MM_DD.nc'.

        Parameters:
        -----------
        date : str
            The date for which to download the perturbed forecast data, in the format 'YYYY-MM-DD'.

        Raises:
        -------
        ValueError:
            If the date is not in the correct format 'YYYY-MM-DD'.
        RuntimeError:
            If the download fails due to an API exception or any other error.

        Example:
        --------
        download_ecmwf_pf('2024-05-18')

        Notes:
        ------
        The function uses the ECMWF API to retrieve the data. Ensure that the ECMWF API client is properly
        configured and authenticated before calling this function.
        """

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
        """
        Download the ECMWF control forecast total precipitation data for a specific date and the next 144 forecast steps.

        This function retrieves the ensemble control forecast data from the ECMWF for the specified date,
        downloading the total precipitation data at 6-hour intervals for the next 144 forecast hours.
        The input value `date` should be a string in the format 'YYYY-MM-DD'. The retrieved data is saved
        to a NetCDF file named 'enfo_cf_YYYY_MM_DD.nc'.

        Parameters:
        -----------
        date : str
            The date for which to download the control forecast data, in the format 'YYYY-MM-DD'.

        Raises:
        -------
        ValueError:
            If the date is not in the correct format 'YYYY-MM-DD'.
        RuntimeError:
            If the download fails due to an API exception or any other error.

        Example:
        --------
        download_ecmwf_cf('2024-05-18')

        Notes:
        ------
        The function uses the ECMWF API to retrieve the data. Ensure that the ECMWF API client is properly
        configured and authenticated before calling this function.
        """

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

    def get_source_files(extensions:list[str], cf_or_pf="pf") -> list[str]:
        """
        Retrieves a list of file paths from a specific directory, filtered by file extensions and a keyword.

        Parameters:
        -----------
        extensions : list[str]
            A list of file extensions to filter the files (e.g., ['.nc', '.txt']).
        cf_or_pf : str, optional
            A keyword to filter the files by, default is 'pf'.
            'pf' stands for the perturbed forecast, 'cf' for control.

        Returns:
        --------
        list[str]
            A sorted list of file paths that match the specified extensions and contain the keyword.

        Example:
        --------
        >>> get_source_files(['.csv'], 'pf')
        ['/path/to/Weather_forecast_case_study/src/data/file1_pf.csv', '/path/to/Weather_forecast_case_study/src/data/file2_pf.csv']
        """
        filenames = []
        base_path = os.getcwd()
        source_dir = 'Weather_forecast_case_study/src/data'
        all_files = os.listdir(source_dir)
        for file in all_files:
            for extension in extensions:
                if file.endswith(extension) and file.find(cf_or_pf) != -1:
                    filenames.append(os.path.join(source_dir, file))
        filenames = sorted(filenames)
        return filenames

class plots:
    '''This class includes all function to create plots of the forecast data.'''
    def extract_region(self, dataset, lat_min, lat_max, lon_min, lon_max):
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

    def read_data(self, dataset):
        """
        Read in the dataset and return the values of variables total precipitation, longitude, latitude, and time.
        Optionally, return the 'number' variable if it exists in the dataset.

        Parameters:
        -----------
        dataset : xarray.Dataset
            The dataset containing the required variables: total precipitation (tp), longitude (lon or longitude),
            latitude (lat or latitude), and time. Optionally, it may contain 'number'.

        Returns:
        --------
        tuple
            A tuple containing the following variables:
            - tp (xarray.DataArray): Total precipitation data.
            - lon (xarray.DataArray): Longitude values.
            - lat (xarray.DataArray): Latitude values.
            - time (xarray.DataArray): Time values.
            - number (numpy.ndarray, optional): Ensemble member numbers if present in the dataset.

        Raises:
        -------
        ValueError:
            If any of the required variables (tp, lon, lat, time) are not found in the dataset.
            If the dataset is missing required fields.

        Notes:
        ------
        The function supports datasets with either 'lon'/'lat' or 'longitude'/'latitude' naming conventions
        for the spatial dimensions. It ensures that all required variables are present before returning their values.
        """

        tp = dataset.tp

        # Support both lon/lat and longitude/latitude
        if 'longitude' in dataset:
            lon = dataset.longitude
        elif 'lon' in dataset:
            lon = dataset.lon
        else:
            raise ValueError("Longitude dimension not found in the dataset.")

        if 'latitude' in dataset:
            lat = dataset.latitude
        elif 'lat' in dataset:
            lat = dataset.lat
        else:
            raise ValueError("Latitude dimension not found in the dataset.")

        if 'time' in dataset:
            time = dataset.time
        else:
            raise ValueError("Time dimension not found in the dataset.")

        time = dataset.time

        if any(v is None for v in [tp, lon, lat, time]):
            raise ValueError("Dataset is missing required fields")

        if hasattr(dataset, 'number'):
            number = dataset.number.values
            return tp, lon, lat, time, number
        else:
            return tp, lon, lat, time


    def plot_map_tp(self, dataset, date, cbar_range=None, addtitle=None):
        """Plot the precipitation for the whole area on a specified date.

        This function plots the precipitation data for a given date, displaying all available timesteps
        (00, 06, 12, 18 hours) from that day. The precipitation data is visualized on a map using contour plots.
        Optionally, a colorbar range can be specified, and a custom title can be added to the figure.

        Parameters:
        -----------
        dataset : xarray.Dataset
            The dataset containing the precipitation data, along with longitude, latitude, and time.
        date : str
            The date for which the precipitation should be plotted, in the format 'YYYY-MM-DD'.
        cbar_range : float, optional
            The upper bound for the colorbar range. If not specified, the default range of 0 to 100 is used.
        addtitle : str, optional
            An additional string to be appended to the figure title.

        Raises:
        -------
        ValueError:
            If the date format is invalid or the specified date is out of range.

        Example:
        --------
        plot_map_tp(dataset, '2024-05-18', cbar_range=50, addtitle='Heavy Rainfall Event')

        Notes:
        ------
        The function reads the necessary data from the dataset, checks for valid date formats,
        and creates subplots for the specified times. The resulting figure includes coastlines,
        borders, and rivers for better geographical context. A horizontal colorbar is added below
        all subplots to indicate precipitation levels in kg/m². The final figure is saved as a PNG file.
        """
        tp, lon, lat, time = self.read_data(dataset)
        if cbar_range is not None:
            bounds =  np.linspace(0, cbar_range, 21)
        else:
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
        suptitle = f"Forecast of {date_first_day}"
        if addtitle:
            suptitle += f" - {addtitle}"
        fig.suptitle(suptitle, fontsize=16)

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

    def extract_forecasts_info(data, lat, lon):
        """
        Extracts forecast information for a specific geographic location.

        This function interpolates the provided dataset to extract the ensemble, mean, and standard deviation of
        precipitation forecasts for a specified latitude and longitude.

        Parameters:
        -----------
        data : xarray.Dataset
            The dataset containing the forecast data with dimensions of time, latitude, and longitude.
        lat : float
            The latitude of the location for which to extract forecast information.
        lon : float
            The longitude of the location for which to extract forecast information.

        Returns:
        --------
        tuple
            A tuple containing three elements:
            - ensemble (xarray.DataArray): The interpolated ensemble precipitation data at the specified location.
            - mean_precipitation (xarray.DataArray): The mean precipitation forecast at the specified location.
            - std_precipitation (xarray.DataArray): The standard deviation of the precipitation forecast at the specified location.
        """
        ensemble = data.interp(longitude=lon, latitude=lat)
        mean_precipitation = ensemble.mean(dim='number')
        std_precipitation = ensemble.std(dim='number')
        return ensemble, mean_precipitation,std_precipitation

    def create_colormap():
        """
        Creates a custom colormap with transparency for zero values.

        This function defines a colormap with transparency for zero values and a red color for maximum values. The colormap
        is discretized into a specified number of bins.

        Returns:
        --------
        LinearSegmentedColormap
            A LinearSegmentedColormap object that can be used for visualizing data with transparency for zero values.
        """
        # Define a colormap with transparency for zero values
        colors = [(1, 1, 1, 0.7), (1, 0, 0, 0.7)]  # Transparent for 0, red for max
        n_bins = 10  # Discretizes the interpolation into bins
        cmap_name = 'red_rain'
        cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
        return cm

    def add_raster_to_map(map_obj, raster_path, layer_name, colormap):
        """
        Adds a raster layer to a Folium map with the specified colormap.

        This function reads a raster file, normalizes its values, applies a colormap, and adds the resulting image overlay
        to the provided Folium map object.

        Parameters:
        -----------
        map_obj : folium.Map
            The Folium map object to which the raster layer will be added.
        raster_path : str
            The path to the raster file to be added to the map.
        layer_name : str
            The name of the layer to be added to the map.
        colormap : LinearSegmentedColormap
            The colormap to be applied to the raster data.

        Returns:
        --------
        None
        """
        with rasterio.open(raster_path) as src:
            bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
            image = src.read(1)  # Read the first band

            # Normalize image
            #norm = Normalize(vmin=image.min(), vmax=image.max())
            norm = PowerNorm(gamma=0.5, vmin=image.min(), vmax=300)  # gamma < 1 for exponential scaling

            image_normalized = norm(image)

            # Apply colormap
            image_colored = colormap(image_normalized)

            # Convert to uint8
            image_colored = (image_colored * 255).astype(np.uint8)

            img_overlay = ImageOverlay(image=image_colored, bounds=bounds, name=layer_name, overlay=True, control=True)
            img_overlay.add_to(map_obj)
