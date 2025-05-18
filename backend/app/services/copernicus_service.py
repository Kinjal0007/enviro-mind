import requests
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CopernicusService:
    def __init__(self):
        self.base_url = "https://ads.atmosphere.copernicus.eu/api/v2"
        self.api_key = os.getenv("COPERNICUS_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_air_quality_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch air quality data from Copernicus Atmosphere Monitoring Service (CAMS)
        """
        try:
            # Get current date and time
            now = datetime.utcnow()
            
            # Parameters for air quality data
            params = {
                "lat": latitude,
                "lon": longitude,
                "time": now.isoformat(),
                "variables": [
                    "pm2p5",  # PM2.5
                    "pm10",   # PM10
                    "co",     # Carbon Monoxide
                    "no2",    # Nitrogen Dioxide
                    "o3",     # Ozone
                    "so2"     # Sulfur Dioxide
                ]
            }

            response = requests.get(
                f"{self.base_url}/products/cams-global-atmospheric-composition-forecasts",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching air quality data: {str(e)}")
            raise

    async def get_weather_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch weather data from Copernicus Climate Data Store (CDS)
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "time": datetime.utcnow().isoformat(),
                "variables": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "uv_index",
                    "precipitation"
                ]
            }

            response = requests.get(
                f"{self.base_url}/products/reanalysis-era5-single-levels",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            raise

    def calculate_aqi(self, air_quality_data: Dict) -> Dict:
        """
        Calculate Air Quality Index based on various pollutants
        """
        try:
            # Extract pollutant concentrations
            pm2p5 = air_quality_data.get("pm2p5", 0)
            pm10 = air_quality_data.get("pm10", 0)
            co = air_quality_data.get("co", 0)
            no2 = air_quality_data.get("no2", 0)
            o3 = air_quality_data.get("o3", 0)
            so2 = air_quality_data.get("so2", 0)

            # Calculate individual AQI components
            aqi_components = {
                "pm2p5": self._calculate_pm2p5_aqi(pm2p5),
                "pm10": self._calculate_pm10_aqi(pm10),
                "co": self._calculate_co_aqi(co),
                "no2": self._calculate_no2_aqi(no2),
                "o3": self._calculate_o3_aqi(o3),
                "so2": self._calculate_so2_aqi(so2)
            }

            # Overall AQI is the maximum of all components
            overall_aqi = max(aqi_components.values())

            return {
                "overall_aqi": overall_aqi,
                "components": aqi_components,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating AQI: {str(e)}")
            raise

    def calculate_weather_warnings(self, weather_data: Dict) -> List[Dict]:
        """
        Calculate weather warnings based on temperature and UV index
        """
        warnings = []
        try:
            temp = float(weather_data.get("temperature_2m", 0).values[0] - 273.15)
            uv_index = weather_data.get("uv_index", 0)
            precipitation = weather_data.get("precipitation", 0)

            # Heat wave warning
            if temp > float(os.getenv("HEAT_WAVE_TEMP_THRESHOLD", 35)):
                warnings.append({
                    "type": "heat_wave",
                    "severity": "high",
                    "message": "Heat wave warning: High temperatures expected"
                })

            # Cold weather warning
            if temp < float(os.getenv("COLD_WAVE_TEMP_THRESHOLD", 0)):
                warnings.append({
                    "type": "cold_wave",
                    "severity": "high",
                    "message": "Cold weather warning: Low temperatures expected"
                })

            # UV index warning
            if uv_index > float(os.getenv("UV_INDEX_HIGH_THRESHOLD", 6)):
                warnings.append({
                    "type": "uv_warning",
                    "severity": "moderate",
                    "message": f"High UV index warning: {uv_index}"
                })

            # Snowstorm warning (temperature below 0 and precipitation)
            if temp < 0 and precipitation > 0:
                warnings.append({
                    "type": "snowstorm",
                    "severity": "high",
                    "message": "Snowstorm warning: Snow expected"
                })

            return warnings
        except Exception as e:
            logger.error(f"Error calculating weather warnings: {str(e)}")
            raise

    # Helper methods for AQI calculations
    def _calculate_pm2p5_aqi(self, concentration: float) -> int:
        # EPA PM2.5 AQI calculation
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
        # EPA PM10 AQI calculation
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
        # EPA CO AQI calculation (8-hour average)
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
        # EPA NO2 AQI calculation (1-hour average)
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
        # EPA O3 AQI calculation (8-hour average)
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
        # EPA SO2 AQI calculation (1-hour average)
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