import sys
import os
import unittest
from matplotlib.testing.decorators import cleanup
from unittest.mock import patch

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from shapely import geometry
import pandas as pd
from ecmwfapi import ECMWFDataServer
import ecmwfapi

# Add path to scr functions.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the functions/ classes to test
from functions import df, plots
plotter = plots()
# create unittests for the different functions

# class df
# unit tests for function download_ecmwf
class TestDownloadECMWF_PF(unittest.TestCase):
    @patch('ecmwfapi.api.ECMWFDataServer.retrieve')
    def test_download_success(self, mock_retrieve):
        # Simulate successful download
        mock_retrieve.return_value = None
        try:
            df.download_ecmwf_pf('2024-05-13')
        except Exception as e:
            self.fail(f"download_ecmwf_pf raised an exception unexpectedly: {e}")

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError) as context:
            df.download_ecmwf_pf('20240513')
        # Output of the actual error message for checking
        print(f"Actual error message: {context.exception}")
        self.assertTrue("Date has to be in the format: 'YYYY-MM-DD'." in str(context.exception))

    @patch('ecmwfapi.api.ECMWFDataServer.retrieve')
    def test_download_failure(self, mock_retrieve):
        # Simulate API errors
        mock_retrieve.side_effect = ecmwfapi.api.APIException("Some API error")
        with self.assertRaises(RuntimeError) as context:
            df.download_ecmwf_pf('2024-05-13')
        # Output of the actual error message for checking
        print(f"Actual error message: {context.exception}")
        self.assertTrue("Download failed for 2024-05-13. APIException: 'Some API error'" in str(context.exception))

    @patch('ecmwfapi.api.ECMWFDataServer.retrieve')
    def test_general_exception(self, mock_retrieve):
        # Simulate general error
        mock_retrieve.side_effect = Exception("Some general error")
        with self.assertRaises(RuntimeError) as context:
            df.download_ecmwf_pf('2024-05-13')
        # Output of the actual error message for checking
        print(f"Actual error message: {context.exception}")
        self.assertTrue("Download failed for 2024-05-13. Error: Some general error" in str(context.exception))
# unit tests for download_ecmwf_cf
class TestDownloadECMWFCF_cf(unittest.TestCase):

    @patch.object(ECMWFDataServer, 'retrieve')
    def test_download_success(self, mock_retrieve):
        # Simulate successful download
        date = '2024-05-13'
        expected_filename = f'enfo_cf_2024_05_13.nc'

        mock_retrieve.return_value = None

        try:
            df.download_ecmwf_cf(date)
        except Exception as e:
            self.fail(f"Exception raised: {e}")

        # Check whether the retrieve method was called with the correct parameters
        mock_retrieve.assert_called_once()
        call_args = mock_retrieve.call_args[0][0]
        self.assertEqual(call_args['date'], date)
        self.assertEqual(call_args['type'], 'cf')
        self.assertEqual(call_args['target'], expected_filename)

    def test_invalid_date_format(self):
        # Test of invalid date format
        invalid_date = '20240513'
        with self.assertRaises(ValueError) as context:
            df.download_ecmwf_cf(invalid_date)
        self.assertEqual(str(context.exception), "Date has to be in the format: 'YYYY-MM-DD'.")

    @patch('ecmwfapi.api.ECMWFDataServer.retrieve')
    def test_download_failure(self, mock_retrieve):
        # Simulate download error
        mock_retrieve.side_effect = ecmwfapi.api.APIException("Some API error")
        date = '2024-05-13'
        
        with self.assertRaises(RuntimeError) as context:
            df.download_ecmwf_cf(date)
        # Output of the actual error message for checking
        print(f"Actual error message: {context.exception}")
        self.assertIn(f"Download failed for {date}. APIException: 'Some API error'", str(context.exception))

    @patch('ecmwfapi.api.ECMWFDataServer.retrieve')
    def test_general_error(self, mock_retrieve):
        # Simulate general error
        mock_retrieve.side_effect = ValueError("Some general error")
        date = '2024-05-13'
        
        with self.assertRaises(RuntimeError) as context:
            df.download_ecmwf_cf(date)
        # Output of the actual error message for checking
        print(f"Actual error message: {context.exception}")
        self.assertIn(f"Download failed for {date}. Error: Some general error", str(context.exception))

        self.assertIn(f"Download failed for {date}. Error: Some general error", str(context.exception))

# unit tests for function get_datelist
class TestGetDateList(unittest.TestCase):
    
    def test_valid_dates(self):
        result = df.get_datelist('2024-05-13', '2024-05-19')
        expected = [
            '2024-05-13',
            '2024-05-14',
            '2024-05-15',
            '2024-05-16',
            '2024-05-17',
            '2024-05-18',
            '2024-05-19'
        ]
        self.assertEqual(result, expected)
    
    def test_same_start_end_date(self):
        result = df.get_datelist('2024-05-13', '2024-05-13')
        expected = ['2024-05-13']
        self.assertEqual(result, expected)
    
    def test_end_before_start_date(self):
        with self.assertRaises(ValueError) as context:
            df.get_datelist('2024-05-19', '2024-05-13')
        self.assertEqual(str(context.exception), "End date cannot be before start date.")
    
    def test_invalid_date_format(self):
        with self.assertRaises(ValueError) as context:
            df.get_datelist('20240513', '2024-05-19')
        self.assertEqual(str(context.exception), "Invalid date format. Please use 'YYYY-MM-DD'.")
    
    def test_invalid_start_date_format(self):
        with self.assertRaises(ValueError) as context:
            df.get_datelist('2024-05-100', '2024-05-13')
        self.assertEqual(str(context.exception), "Invalid date format. Please use 'YYYY-MM-DD'.")
    
    def test_invalid_end_date_format(self):
        with self.assertRaises(ValueError) as context:
            df.get_datelist('2024-05-13', '2024-0519')
        self.assertEqual(str(context.exception), "Invalid date format. Please use 'YYYY-MM-DD'.")
    
    def test_non_string_input(self):
        with self.assertRaises(ValueError) as context:
            df.get_datelist(20240513, '2024-05-19')
        self.assertEqual(str(context.exception), "Both startdate and enddate must be strings.")

# class plots
class TestExtractRegion(unittest.TestCase):

    def setUp(self):
        # Setup code, load example dataset for testing
        # Example dataset with 'latitude' and 'longitude'
        self.dataset_with_latlon = xr.Dataset({
            'temperature': (('latitude', 'longitude'), [[10, 20], [30, 40]]),
            'latitude': (['latitude'], [0, 1]),
            'longitude': (['longitude'], [0, 1]),
        })

        # Example dataset with 'lat' and 'lon'
        self.dataset_with_latlon_alt = xr.Dataset({
            'temperature': (('lat', 'lon'), [[10, 20], [30, 40]]),
            'lat': (['lat'], [0, 1]),
            'lon': (['lon'], [0, 1]),
        })

    def test_extract_region_with_latlon(self):
        # Test with valid region boundaries
        lat_min = 0
        lat_max = 1
        lon_min = 0
        lon_max = 1
        result = plotter.extract_region(self.dataset_with_latlon, lat_min, lat_max, lon_min, lon_max)
        
        self.assertEqual(result.latitude.values.tolist(), [0, 1])
        self.assertEqual(result.longitude.values.tolist(), [0, 1])
        self.assertEqual(result.temperature.values.tolist(), [[10, 20], [30, 40]])

    def test_extract_region_with_latlon_alt(self):
        # Test with valid region boundaries using alternative dimensions
        lat_min = 0
        lat_max = 1
        lon_min = 0
        lon_max = 1
        result = plotter.extract_region(self.dataset_with_latlon_alt, lat_min, lat_max, lon_min, lon_max)
        
        self.assertEqual(result.lat.values.tolist(), [0, 1])
        self.assertEqual(result.lon.values.tolist(), [0, 1])
        self.assertEqual(result.temperature.values.tolist(), [[10, 20], [30, 40]])

    def test_extract_region_out_of_bounds(self):
        # Test with out-of-bounds region boundaries
        lat_min = -1
        lat_max = 2
        lon_min = -1
        lon_max = 2
        result = plotter.extract_region(self.dataset_with_latlon, lat_min, lat_max, lon_min, lon_max)
        
        # Check if 'latitude' and 'longitude' are in the resulting dataset
        self.assertIn('latitude', result.coords)
        self.assertIn('longitude', result.coords)
        
        # Check if 'temperature' variable is in the resulting dataset
        self.assertIn('temperature', result.variables)
        
        # Check the values of 'longitude' variable
        if len(result.longitude) > 0:
            expected_lon = [0, 1]
            actual_lon = result['longitude'].values.tolist()
            self.assertEqual(actual_lon, expected_lon)
        else:
            self.fail("No longitude values found in the extracted region.")

class TestReadData(unittest.TestCase):
    def setUp(self):
        # example data for tests
        self.reader = plotter
        self.tp = np.random.rand(10)
        self.lon = np.linspace(-180, 180, 10)
        self.lat = np.linspace(-90, 90, 10)
        self.time = np.arange(10)
        self.number = np.random.randint(0, 10, 10)

    def test_read_data_with_number(self):
        # Dataset with 'number'
        dataset = xr.Dataset(
            {
                'tp': (['time'], self.tp),
                'longitude': (['time'], self.lon),
                'latitude': (['time'], self.lat),
                'time': (['time'], self.time),
                'number': (['time'], self.number)
            }
        )
        
        tp, lon, lat, time, number = self.reader.read_data(dataset)
        
        np.testing.assert_array_equal(tp, self.tp)
        np.testing.assert_array_equal(lon, self.lon)
        np.testing.assert_array_equal(lat, self.lat)
        np.testing.assert_array_equal(time, self.time)
        np.testing.assert_array_equal(number, self.number)

    def test_read_data_without_number(self):
        # Dataset without 'number'
        dataset = xr.Dataset(
            {
                'tp': (['time'], self.tp),
                'longitude': (['time'], self.lon),
                'latitude': (['time'], self.lat),
                'time': (['time'], self.time)
            }
        )
        
        tp, lon, lat, time = self.reader.read_data(dataset)
        
        np.testing.assert_array_equal(tp, self.tp)
        np.testing.assert_array_equal(lon, self.lon)
        np.testing.assert_array_equal(lat, self.lat)
        np.testing.assert_array_equal(time, self.time)

    def test_read_data_with_lon_lat(self):
        # Dataset with 'lon' and 'lat' instead of 'longitude' and 'latitude'
        dataset = xr.Dataset(
            {
                'tp': (['time'], self.tp),
                'lon': (['time'], self.lon),
                'lat': (['time'], self.lat),
                'time': (['time'], self.time)
            }
        )
        
        tp, lon, lat, time = self.reader.read_data(dataset)
        
        np.testing.assert_array_equal(tp, self.tp)
        np.testing.assert_array_equal(lon, self.lon)
        np.testing.assert_array_equal(lat, self.lat)
        np.testing.assert_array_equal(time, self.time)

class TestPlotMapTP(unittest.TestCase):
    def setUp(self):
        # Initialisiere den DataReader
        self.reader = plotter
        self.tp = np.random.rand(4, 10, 10)  # Example data
        self.lon = np.linspace(-180, 180, 10)
        self.lat = np.linspace(-90, 90, 10)
        self.time = pd.date_range("2023-01-01", periods=4, freq='6H')  # Example times

    @cleanup
    def test_plot_map_tp_default(self):
        dataset = xr.Dataset(
            {
                'tp': (['time', 'lat', 'lon'], self.tp),
                'lon': (['lon'], self.lon),
                'lat': (['lat'], self.lat),
                'time': (['time'], self.time)
            }
        )
        
        self.reader.plot_map_tp(dataset, '2023-01-01')
        plt.close()

    @cleanup
    def test_plot_map_tp_with_cbar_range(self):
        dataset = xr.Dataset(
            {
                'tp': (['time', 'lat', 'lon'], self.tp),
                'lon': (['lon'], self.lon),
                'lat': (['lat'], self.lat),
                'time': (['time'], self.time)
            }
        )
        
        self.reader.plot_map_tp(dataset, '2023-01-01', cbar_range=50)
        plt.close()

    @cleanup
    def test_plot_map_tp_with_addtitle(self):
        dataset = xr.Dataset(
            {
                'tp': (['time', 'lat', 'lon'], self.tp),
                'lon': (['lon'], self.lon),
                'lat': (['lat'], self.lat),
                'time': (['time'], self.time)
            }
        )
        
        self.reader.plot_map_tp(dataset, '2023-01-01', addtitle='Mean')
        plt.close()

# running Unittests 
if __name__ == '__main__':
    unittest.main()