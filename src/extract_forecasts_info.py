import numpy as np
import xarray as xr
#import scipy 


def extract_forecasts_info(data, lat, lon):
  ensemble = data.interp(longitude=lon, latitude=lat)
  mean_precipitation = ensemble.mean(dim='number')
  std_precipitation = ensemble.std(dim='number')
  return ensemble, mean_precipitation,std_precipitation