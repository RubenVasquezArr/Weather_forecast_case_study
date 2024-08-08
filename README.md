# Weather Forecast Case Study
 Accurately predicting precipitation events can be very challenging, particularly in terms of duration, amount, and location of the rainfall. The further into the future one looks, the less accurate the forecasts become. This project focuses on the short- and medium-term forecasting of a heavy rainfall event in Western Germany in May 2024. For this purpose, the historical forecast data from the European Centre for Medium-Range Weather Forecasts (ECMWF) for a period before the predicted event will be examined, as well as how these forecasts have evolved over time.

Part of the project will be the access and downloading of the forecast data, processing and visualizing these data. The following sections describe the structure of the repository and included files and needed modules, instructions how to access the data, description of the data processing part and final conclusions.

Autors: Luisa Reske, Rubén Vásquez Arredondo

## Table of Contents
1. [Weather Forecast Case Study Documentation](#weather-forecast-case-study-documentation)
2. [Needed Python Modules](#needed-python-modules)
3. [Structure of the Project](#structure-of-the-project)
4. [Accessing the Forecast Data from ECMWF](#accessing-the-forecast-data-from-eCMWF)
5. [Accessing ERA5 Data from Copernicus Climate Data Store](#accessing-era5-data-from-copernicus-climate-data-store)
6. [Functions and Unittests](#functions-and-Unittests)
7. [Data Analysis](#data-analysis)
8. [Results and Insights](#results-and-insights)
9. [Conclusions](#conclusions)
 
## Weather Forecast Case Study Documentation

Accurately predicting precipitation events can be very challenging, particularly in terms of duration, amount, and location of the rainfall. The further into the future one looks, the less accurate the forecasts become. This project focuses on the short- and medium-term forecasting of a heavy rainfall event in Western Germany in May 2024. For this purpose, the historical forecast data from the European Centre for Medium-Range Weather Forecasts (ECMWF) for a period before the predicted event will be examined, as well as how these forecasts have evolved over time.

Part of the project will be the access and downloading of the forecast data, processing and visualizing these data. The following sections describe the structure of the repository and include files and needed modules, instructions on how to access the data, description of the data processing part, and final conclusions.

## Needed Python Modules

Please ensure the following programs and modules are correctly implemented to use the notebooks from this directory:
- numpy
- xarray
- matplotlib
- datetime
- pandas
- shapely
- cartopy
- re
- sys
- os
- ecmwfapi
- cdsapi
- unittest
- folium
- rasterio

## Structure of the Project

The Directory has the following structure:

```bash
Repository/
├── data/
│ ├── control/     # Control files from ECMWF
│ ├── era5/        # Files from ERA5
│ ├── perturbed/   # Perturbed forecasts files from ECMWF
│ └── raster/      # Processed data
├── src/
│ ├── notebooks/   # Notebooks files
│ └── functions.py # Python functions
├── tests/
│ └── unittests.py # Unit tests
├── LICENSE
└── README.md
```

To replicate this project, follow these steps in the presented order:

## Accessing the Forecast Data from ECMWF

Comprehensive documentation on how to download ENFO data and install all necessary packages is available here: [Access ECMWF Public Datasets - ECMWF Web API - ECMWF Confluence Wiki](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets).

The `df` class encompasses all the essential functions required to download the perturbed and control forecasts for a specific date or a list of dates. Examples can be found in the `ecmwf_download` notebook. Note that an account on the ECMWF website is necessary for data download. Additionally, a personal key must be saved in the user's home directory. Ensure that the ECMWF API Python module (`ecmwfapi`) is correctly installed.

The Jupyter notebook `ecmwf_download.ipynb` demonstrates the procedure for downloading a time series.

Perturbed forecast data is available directly in the NetCDF format and can be seamlessly utilized in subsequent analyses. However, control forecast data is provided in GRIB format and must be converted to NetCDF for equivalent data analysis as perturbed forecasts. The shell script `convert_grib_to_netcdf.sh` facilitates this conversion using CDO. Therefore, ensure that CDO is properly installed ([CDO Installation](https://code.mpimet.mpg.de/projects/cdo)). Alternatively, modify the `download_ecmwf_cf` function to set the `format` parameter to `netcdf`.

## Accessing ERA5 Data from Copernicus Climate Data Store

To compare the forecasts with actual weather conditions, we use reanalysis data from ERA5, accessible via the Copernicus Climate Data Store ([ERA5 Complete Dataset](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-complete?tab=form)).

The ERA5 variable for total precipitation is in units of [m], whereas the ECMWF data is in units of [kg/m²]. To convert from meters to kilograms per square meter, multiply the ERA5 values by 1000 and update the metadata accordingly to avoid confusion. Instructions for this process are provided in the `download_era5.ipynb` notebook. Ensure that the `cdsapi` client is correctly installed and that you have an account for the Copernicus Climate Data Store.

## Functions and Unittests

All functions required for plotting and data analysis in the subsequent steps are implemented in the `functions.py` file. These functions and classes are imported at the beginning of the data analysis notebooks, which are located in the `src` directory.
Unit tests for all defined functions are included in the `unittests.py` file, which can be found in the `tests` directory.
All downloaded data should be saved in the `data` directory.

## Data Analysis

The following notebooks perform data processing and analysis:

- `ecmwf_timeseries_map.ipynb`: Plotting the Forecast Data (control, mean and standard deviation of Ensemble) for the whole Germany for the 18th of May.
- `ecmwf_forecasts_maps.ipynb`: First approximation to map the evolution of the forecast, producing static maps of rain for Germany.
- `ecmwf_forecasts_plots.ipynb`: Plots the ECMWF data of forecast for the 18th of May 2024, from different days to understand the evolution of the forecast up to this day, including mean forecast and standard deviation.
- `era5_enfo_comparison.ipynb`: Showing the difference between the mean of ensemble forecast and ERA5.
- `raster_processing.ipynb`: To study the evolution of the forecast for the 18th of May 2024, we use ERA5 and ECMWF data to produce rasters, for future visual analysis.
- `raster_interactive_map.ipynb`: To study the evolution of the forecast for the 18th of May 2024, we use previously produced rasters, and then mapped with leaflet and the folium library.

## Results and Insights

Five days before Saturday, May 18, 2024, heavy rainfall is forecasted for southern and western Germany for the entire day. The rainfall is expected to be concentrated in two main areas: one in the western Rhine region and the other in the south along the border between Baden-Württemberg and Bavaria (cf 13/05). By the forecast on May 14, the main rainfall areas shift further south (cf 14/05), and by May 15, they move significantly northward (cf 15/05). Two days before the event, only one maximum rainfall area remains in western Germany (cf 16/05), which then shifts southwards from the Rhine region towards Freiburg (cf 17/05). On the day of the event, only very light rainfall is predicted for southern Germany throughout the day (cf 18/05).

The ensemble mean spatial distribution follows the same pattern, although the amount of rainfall is lower (pf mean). The development of precipitation uncertainty can be observed through the standard deviation of the ensemble values. At the beginning of the week, the highest uncertainty is in the area of potential heavy rain. This uncertainty increases until Wednesday. In the following days, it decreases as the forecasted day approaches. By Friday and Saturday, only low standard deviations are noticeable (pf std).

Uncertainty regarding the total precipitation amount increases the further the event is in the future. The forecast can be so erroneous that no rain occurs at all. The forecast is much more reliable in predicting the absence of precipitation in areas where none is forecasted and less reliable for regions where precipitation is possible given the current weather development.

An interactive map of the world forecast for the 18 of may of 2024 can be acceded [here](https://htmlview.glitch.me/?https://github.com/RubenVasquezArr/Weather_forecast_case_study/blob/main/interactive_map_red.html)/. At the upper right of the map there is a filter to select only de desired layer. Each layer is the forecast of each day for the 18 of may, and finally the last layer is the era5 reanalysis data. 

## Conclusions

In conclusion, this case study demonstrates the challenges and variability in short- and medium-term weather forecasting, particularly for heavy rainfall events. The analysis shows that while ensemble forecasting can provide valuable insights into potential weather scenarios and uncertainties, it is crucial to continuously update and refine predictions as the event approaches. The integration of multiple data sources, such as ECMWF and ERA5, enhances the robustness of the analysis. Future work could focus on improving the conversion and integration processes, as well as exploring other forecasts from different sources.
 
