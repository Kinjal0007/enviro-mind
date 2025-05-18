import cdsapi
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging
import zipfile
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopernicusDataService:
    def __init__(self):
        self.client = cdsapi.Client()
        
    async def get_air_quality_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch air quality data from Copernicus
        """
        try:
            # Get current date
            now = datetime.utcnow()
            
            # Request air quality data
            result = self.client.retrieve(
                'cams-global-atmospheric-composition-forecasts-gfas',
                {
                    'variable': [
                        'particulate_matter_2.5um',  # PM2.5
                        'particulate_matter_10um',   # PM10
                        'carbon_monoxide',           # CO
                        'nitrogen_dioxide',          # NO2
                        'ozone',                     # O3
                        'sulphur_dioxide',           # SO2
                    ],
                    'model_level': '60',
                    'date': now.strftime('%Y-%m-%d'),
                    'time': '00:00',
                    'leadtime_hour': '0',
                    'area': [
                        latitude + 0.1,  # North
                        longitude - 0.1,  # West
                        latitude - 0.1,   # South
                        longitude + 0.1,  # East
                    ],
                    'format': 'netcdf',
                }
            )
            
            # Process the data
            with xr.open_dataset(result.download()) as ds:
                return {
                    'pm2p5': float(ds['pm2p5'].values[0]),
                    'pm10': float(ds['pm10'].values[0]),
                    'co': float(ds['co'].values[0]),
                    'no2': float(ds['no2'].values[0]),
                    'o3': float(ds['o3'].values[0]),
                    'so2': float(ds['so2'].values[0]),
                    'timestamp': now.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error fetching air quality data: {str(e)}")
            raise

    async def get_weather_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch weather data from Copernicus ERA5 dataset
        """
        try:
            # Use a date we know is available (2025-05-12)
            target_date = datetime(2025, 5, 12)
            
            # Create area parameter used in both requests
            area = [
                latitude + 0.5,  # North
                longitude - 0.5,  # West
                latitude - 0.5,   # South
                longitude + 0.5,  # East
            ]
            
            # Request 1: Get instantaneous parameters (like temperature, dewpoint)
            logger.info("Requesting instantaneous parameters (temperature, dewpoint)...")
            temp_result = self.client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '2m_temperature',           # t2m in NetCDF
                        '2m_dewpoint_temperature',  # d2m in NetCDF
                    ],
                    'year': target_date.strftime('%Y'),
                    'month': target_date.strftime('%m'),
                    'day': target_date.strftime('%d'),
                    'time': '12:00',
                    'area': area,
                    'format': 'netcdf',
                    'grid': [0.25, 0.25],
                }
            )
            
            # Request 2: Get accumulated parameters (precipitation, radiation)
            logger.info("Requesting accumulated parameters (precipitation, radiation)...")
            accum_result = self.client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        'total_precipitation',      # tp in NetCDF
                        'surface_solar_radiation_downwards',  # ssrd in NetCDF
                    ],
                    'year': target_date.strftime('%Y'),
                    'month': target_date.strftime('%m'),
                    'day': target_date.strftime('%d'),
                    'time': '12:00',
                    'area': area,
                    'format': 'netcdf',
                    'grid': [0.25, 0.25],
                }
            )
            
            # Initialize variables
            temperature = None
            dewpoint = None
            humidity = None
            precipitation = None
            uv_index = None
            
            # Process temperature data
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = temp_result.download()
                logger.info(f"Downloaded temperature file: {file_path}")
                
                # Handle different file types
                nc_path = self._extract_or_use_file(file_path, temp_dir)
                
                # Process temperature file
                with xr.open_dataset(nc_path, engine='netcdf4') as ds:
                    logger.info(f"Temperature file variables: {list(ds.variables.keys())}")
                    
                    # Extract temperature (t2m)
                    if 't2m' in ds:
                        temperature = float(ds['t2m'].values.ravel()[0] - 273.15)  # Convert K to °C
                    logger.info(f"Temperature value: {temperature}")
                    
                    # Extract dewpoint temperature (d2m)
                    if 'd2m' in ds:
                        dewpoint = float(ds['d2m'].values.ravel()[0] - 273.15)  # Convert K to °C
                        
                        # Calculate relative humidity from temperature and dewpoint
                        if temperature is not None:
                            humidity = self._calculate_humidity_from_dewpoint(temperature, dewpoint)
                    
                    logger.info(f"Dewpoint value: {dewpoint}")
                    logger.info(f"Humidity value: {humidity}")
            
            # Process accumulated parameters data
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = accum_result.download()
                logger.info(f"Downloaded accumulated parameters file: {file_path}")
                
                # Handle different file types
                nc_path = self._extract_or_use_file(file_path, temp_dir)
                
                # Process accumulated parameters file
                with xr.open_dataset(nc_path, engine='netcdf4') as ds:
                    logger.info(f"Accumulated parameters file variables: {list(ds.variables.keys())}")
                    
                    # Extract precipitation (tp)
                    if 'tp' in ds:
                        # tp is in meters, convert to mm (1m = 1000mm)
                        precipitation = float(ds['tp'].values.ravel()[0] * 1000)
                    logger.info(f"Precipitation value: {precipitation}")
                    
                    # Extract solar radiation and calculate UV index (ssrd)
                    if 'ssrd' in ds:
                        solar_radiation = float(ds['ssrd'].values.ravel()[0])
                        logger.info(f"Solar radiation value: {solar_radiation}")
                        # Convert W/m² to UV index (typical conversion factor)
                        uv_index = solar_radiation / 25.0  # Basic conversion
                        # Cap UV index at reasonable values (typically 0-15)
                        uv_index = min(max(uv_index, 0), 15)
                    logger.info(f"UV index value: {uv_index}")
            
            return {
                'temperature': temperature,
                'humidity': humidity,  # Now we have humidity
                'precipitation': precipitation,
                'uv_index': uv_index,
                'timestamp': target_date.isoformat()
            }
                
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise

    def _extract_or_use_file(self, file_path, temp_dir):
        """Helper method to handle different file types returned by API"""
        if file_path.endswith('.zip'):
            # Extract the ZIP file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            # Find the NetCDF file in the extracted files
            nc_files = [f for f in os.listdir(temp_dir) if f.endswith('.nc')]
            if not nc_files:
                raise Exception("No NetCDF file found in the downloaded data")
            return os.path.join(temp_dir, nc_files[0])
        elif file_path.endswith('.nc'):
            return file_path
        else:
            raise Exception(f"Unexpected file type returned: {file_path}")

    def _calculate_humidity_from_dewpoint(self, temperature, dewpoint):
        """
        Calculate relative humidity from temperature and dewpoint
        Formula: RH = 100 * exp((17.625 * dewpoint) / (243.04 + dewpoint)) / exp((17.625 * temperature) / (243.04 + temperature))
        """
        try:
            # Calculate saturation vapor pressure at temperature
            es_t = 6.112 * np.exp(17.67 * temperature / (temperature + 243.5))
            
            # Calculate saturation vapor pressure at dewpoint
            es_d = 6.112 * np.exp(17.67 * dewpoint / (dewpoint + 243.5))
            
            # Calculate relative humidity
            rh = (es_d / es_t) * 100
            
            # Clamp to valid range
            rh = min(max(rh, 0), 100)
            
            return rh
        except Exception as e:
            logger.error(f"Error calculating humidity: {str(e)}")
            return None

    def _calculate_warnings(self, weather: Dict) -> List[Dict]:
        """
        Calculate weather warnings, including seasonal factors
        """
        warnings = []
        
        # Get current month for seasonal adjustments
        current_month = datetime.utcnow().month
        is_winter = current_month in [12, 1, 2]
        is_spring = current_month in [3, 4, 5]
        is_summer = current_month in [6, 7, 8]
        is_fall = current_month in [9, 10, 11]
        
        # Temperature warnings
        temp = weather['temperature']
        if temp is not None:
            # Heat warnings (more stringent in early summer when people aren't acclimated)
            heat_threshold = float(os.getenv('HEAT_WAVE_TEMP_THRESHOLD', 35))
            if is_spring and temp > (heat_threshold - 2):  # Lower threshold in spring
                warnings.append({
                    'type': 'heat_wave',
                    'severity': 'moderate',
                    'message': f'Early season heat alert: Temperature is {temp:.1f}°C'
                })
            elif temp > heat_threshold:
                warnings.append({
                    'type': 'heat_wave',
                    'severity': 'high',
                    'message': f'Heat wave warning: Temperature is {temp:.1f}°C'
                })
                
            # Cold warnings (more stringent in early winter)
            cold_threshold = float(os.getenv('COLD_WAVE_TEMP_THRESHOLD', 0))
            if is_fall and temp < (cold_threshold + 2):  # Higher threshold in fall
                warnings.append({
                    'type': 'cold_wave',
                    'severity': 'moderate',
                    'message': f'Early season cold alert: Temperature is {temp:.1f}°C'
                })
            elif temp < cold_threshold:
                warnings.append({
                    'type': 'cold_wave',
                    'severity': 'high',
                    'message': f'Cold weather warning: Temperature is {temp:.1f}°C'
                })
        
        # UV index warnings (more stringent in spring when skin is less prepared)
        uv_index = weather['uv_index']
        if uv_index is not None:
            uv_threshold = float(os.getenv('UV_INDEX_HIGH_THRESHOLD', 6))
            if is_spring and uv_index > (uv_threshold - 1):  # Lower threshold in spring
                warnings.append({
                    'type': 'uv_warning',
                    'severity': 'high',
                    'message': f'Spring UV warning: UV index is {uv_index:.1f}, skin may be more sensitive'
                })
            elif uv_index > uv_threshold:
                warnings.append({
                    'type': 'uv_warning',
                    'severity': 'moderate',
                    'message': f'High UV index warning: {uv_index:.1f}'
                })
            
        # Precipitation warnings including snowstorms
        precipitation = weather['precipitation']
        if precipitation is not None and precipitation > 0:
            if temp is not None and temp < 2:  # Expanded range for snow (not just below freezing)
                # More severe warning in spring/fall when snow is unexpected
                if is_winter:
                    severity = 'moderate' if precipitation > 10 else 'low'
                    warnings.append({
                        'type': 'snowstorm',
                        'severity': severity,
                        'message': f'Snow expected: {precipitation:.1f}mm potential accumulation'
                    })
                else:
                    severity = 'high'  # Out-of-season snow is more disruptive
                    warnings.append({
                        'type': 'snowstorm',
                        'severity': severity,
                        'message': f'Unseasonable snow warning: {precipitation:.1f}mm potential accumulation'
                    })
            elif precipitation > 25:  # Heavy rain
                warnings.append({
                    'type': 'heavy_rain',
                    'severity': 'moderate',
                    'message': f'Heavy rain warning: {precipitation:.1f}mm expected'
                })
                
        # Pollen warnings (based on season and humidity)
        humidity = weather['humidity']
        if humidity is not None:
            # Spring - tree pollen season
            if is_spring and temp > 10 and humidity < 70:
                warnings.append({
                    'type': 'pollen',
                    'severity': 'high',
                    'message': 'High tree pollen likely: warm spring conditions'
                })
            # Early summer - grass pollen season
            elif is_summer and current_month == 6 and temp > 18 and humidity < 65:
                warnings.append({
                    'type': 'pollen',
                    'severity': 'high',
                    'message': 'High grass pollen likely: warm early summer conditions'
                })
            # Late summer/early fall - weed pollen season
            elif (is_summer and current_month == 8) or (is_fall and current_month == 9) and temp > 15:
                warnings.append({
                    'type': 'pollen',
                    'severity': 'moderate',
                    'message': 'Elevated weed pollen likely: late summer/early fall conditions'
                })
            
        return warnings

    async def get_environmental_status(self, latitude: float, longitude: float) -> Dict:
        """
        Get comprehensive environmental status
        """
        try:
            # Get both air quality and weather data
            air_quality = await self.get_air_quality_data(latitude, longitude)
            weather = await self.get_weather_data(latitude, longitude)
            
            # Calculate AQI
            aqi = self._calculate_aqi(air_quality)
            
            # Calculate warnings
            warnings = self._calculate_warnings(weather)
            
            return {
                'air_quality': air_quality,
                'weather': weather,
                'aqi': aqi,
                'warnings': warnings,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting environmental status: {str(e)}")
            raise

    def _calculate_aqi(self, air_quality: Dict) -> Dict:
        """
        Calculate Air Quality Index
        """
        # Extract values
        pm2p5 = air_quality['pm2p5']
        pm10 = air_quality['pm10']
        co = air_quality['co']
        no2 = air_quality['no2']
        o3 = air_quality['o3']
        so2 = air_quality['so2']
        
        # Calculate individual AQI components
        components = {
            'pm2p5': self._calculate_pm2p5_aqi(pm2p5),
            'pm10': self._calculate_pm10_aqi(pm10),
            'co': self._calculate_co_aqi(co),
            'no2': self._calculate_no2_aqi(no2),
            'o3': self._calculate_o3_aqi(o3),
            'so2': self._calculate_so2_aqi(so2)
        }
        
        # Overall AQI is the maximum of all components
        overall_aqi = max(components.values())
        
        return {
            'overall': overall_aqi,
            'components': components
        }

    # AQI calculation helper methods
    def _calculate_pm2p5_aqi(self, concentration: float) -> int:
        if concentration <= 12.0:
            return self._linear_scale(concentration, 0, 12.0, 0, 50)
        elif concentration <= 35.4:
            return self._linear_scale(concentration, 12.1, 35.4, 51, 100)
        elif concentration <= 55.4:
            return self._linear_scale(concentration, 35.5, 55.4, 101, 150)
        elif concentration <= 150.4:
            return self._linear_scale(concentration, 55.5, 150.4, 151, 200)
        elif concentration <= 250.4:
            return self._linear_scale(concentration, 150.5, 250.4, 201, 300)
        else:
            return self._linear_scale(concentration, 250.5, 500.4, 301, 500)

    def _calculate_pm10_aqi(self, concentration: float) -> int:
        if concentration <= 54:
            return self._linear_scale(concentration, 0, 54, 0, 50)
        elif concentration <= 154:
            return self._linear_scale(concentration, 55, 154, 51, 100)
        elif concentration <= 254:
            return self._linear_scale(concentration, 155, 254, 101, 150)
        elif concentration <= 354:
            return self._linear_scale(concentration, 255, 354, 151, 200)
        elif concentration <= 424:
            return self._linear_scale(concentration, 355, 424, 201, 300)
        else:
            return self._linear_scale(concentration, 425, 604, 301, 500)

    def _calculate_co_aqi(self, concentration: float) -> int:
        if concentration <= 4.4:
            return self._linear_scale(concentration, 0, 4.4, 0, 50)
        elif concentration <= 9.4:
            return self._linear_scale(concentration, 4.5, 9.4, 51, 100)
        elif concentration <= 12.4:
            return self._linear_scale(concentration, 9.5, 12.4, 101, 150)
        elif concentration <= 15.4:
            return self._linear_scale(concentration, 12.5, 15.4, 151, 200)
        elif concentration <= 30.4:
            return self._linear_scale(concentration, 15.5, 30.4, 201, 300)
        else:
            return self._linear_scale(concentration, 30.5, 50.4, 301, 500)

    def _calculate_no2_aqi(self, concentration: float) -> int:
        if concentration <= 53:
            return self._linear_scale(concentration, 0, 53, 0, 50)
        elif concentration <= 100:
            return self._linear_scale(concentration, 54, 100, 51, 100)
        elif concentration <= 360:
            return self._linear_scale(concentration, 101, 360, 101, 150)
        elif concentration <= 649:
            return self._linear_scale(concentration, 361, 649, 151, 200)
        elif concentration <= 1249:
            return self._linear_scale(concentration, 650, 1249, 201, 300)
        else:
            return self._linear_scale(concentration, 1250, 2049, 301, 500)

    def _calculate_o3_aqi(self, concentration: float) -> int:
        if concentration <= 54:
            return self._linear_scale(concentration, 0, 54, 0, 50)
        elif concentration <= 70:
            return self._linear_scale(concentration, 55, 70, 51, 100)
        elif concentration <= 85:
            return self._linear_scale(concentration, 71, 85, 101, 150)
        elif concentration <= 105:
            return self._linear_scale(concentration, 86, 105, 151, 200)
        elif concentration <= 200:
            return self._linear_scale(concentration, 106, 200, 201, 300)
        else:
            return self._linear_scale(concentration, 201, 404, 301, 500)

    def _calculate_so2_aqi(self, concentration: float) -> int:
        if concentration <= 35:
            return self._linear_scale(concentration, 0, 35, 0, 50)
        elif concentration <= 75:
            return self._linear_scale(concentration, 36, 75, 51, 100)
        elif concentration <= 185:
            return self._linear_scale(concentration, 76, 185, 101, 150)
        elif concentration <= 304:
            return self._linear_scale(concentration, 186, 304, 151, 200)
        elif concentration <= 604:
            return self._linear_scale(concentration, 305, 604, 201, 300)
        else:
            return self._linear_scale(concentration, 605, 1004, 301, 500)

    @staticmethod
    def _linear_scale(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> int:
        """Helper method for linear scaling of values"""
        return int(((value - in_min) * (out_max - out_min) / (in_max - in_min)) + out_min) 