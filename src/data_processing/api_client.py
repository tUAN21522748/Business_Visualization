"""
API Client cho Open-Meteo Weather API
Lấy dữ liệu thời tiết hiện tại, forecast và lịch sử
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenMeteoClient:
    """Client để gọi API Open-Meteo"""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self):
        self.session = requests.Session()
        # Các thành phố mặc định ở Việt Nam
        self.default_cities = {
            "Hà Nội": {"lat": 21.0278, "lon": 105.8342},
            "TP.HCM": {"lat": 10.8231, "lon": 106.6297},
            "Đà Nẵng": {"lat": 16.0471, "lon": 108.2068},
            "Huế": {"lat": 16.4637, "lon": 107.5909},
            "Cần Thơ": {"lat": 10.0452, "lon": 105.7469}
        }
    
    def get_current_weather(self, lat: float, lon: float, city_name: str = None) -> Dict:
        """
        Lấy dữ liệu thời tiết hiện tại
        
        Args:
            lat: Latitude
            lon: Longitude  
            city_name: Tên thành phố (optional)
            
        Returns:
            Dict chứa dữ liệu thời tiết hiện tại
        """
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m", 
                    "precipitation",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "pressure_msl"
                ],
                "timezone": "Asia/Ho_Chi_Minh",
                "forecast_days": 1
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            # Format dữ liệu
            result = {
                "city_name": city_name or f"Lat:{lat}, Lon:{lon}",
                "latitude": lat,
                "longitude": lon,
                "timestamp": current.get("time"),
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "pressure": current.get("pressure_msl"),
                "units": data.get("current_units", {})
            }
            
            logger.info(f"Lấy dữ liệu thành công cho {result['city_name']}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gọi API: {e}")
            return {}
        except Exception as e:
            logger.error(f"Lỗi không xác định: {e}")
            return {}
    
    def get_forecast(self, lat: float, lon: float, days: int = 7, city_name: str = None) -> pd.DataFrame:
        """
        Lấy dữ liệu dự báo thời tiết
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Số ngày dự báo (1-16)
            city_name: Tên thành phố
            
        Returns:
            DataFrame chứa dữ liệu dự báo
        """
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min", 
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "wind_direction_10m_dominant"
                ],
                "timezone": "Asia/Ho_Chi_Minh",
                "forecast_days": min(days, 16)
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            daily = data.get("daily", {})
            
            # Tạo DataFrame
            df = pd.DataFrame({
                "date": pd.to_datetime(daily.get("time", [])),
                "temp_max": daily.get("temperature_2m_max", []),
                "temp_min": daily.get("temperature_2m_min", []),
                "precipitation": daily.get("precipitation_sum", []),
                "wind_speed_max": daily.get("wind_speed_10m_max", []),
                "wind_direction": daily.get("wind_direction_10m_dominant", [])
            })
            
            # Thêm metadata
            df["city_name"] = city_name or f"Lat:{lat}, Lon:{lon}"
            df["latitude"] = lat
            df["longitude"] = lon
            
            logger.info(f"Lấy dự báo {len(df)} ngày cho {city_name or 'Unknown'}")
            return df
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy dự báo: {e}")
            return pd.DataFrame()
    
    def get_historical_data(self, lat: float, lon: float, 
                          start_date: str, end_date: str, 
                          city_name: str = None) -> pd.DataFrame:
        """
        Lấy dữ liệu lịch sử thời tiết
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            city_name: Tên thành phố
            
        Returns:
            DataFrame chứa dữ liệu lịch sử
        """
        try:
            url = f"{self.BASE_URL}/historical-weather"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "precipitation_sum", 
                    "wind_speed_10m_max"
                ],
                "timezone": "Asia/Ho_Chi_Minh"
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            daily = data.get("daily", {})
            
            # Tạo DataFrame
            df = pd.DataFrame({
                "date": pd.to_datetime(daily.get("time", [])),
                "temp_max": daily.get("temperature_2m_max", []),
                "temp_min": daily.get("temperature_2m_min", []),
                "temp_mean": daily.get("temperature_2m_mean", []),
                "precipitation": daily.get("precipitation_sum", []),
                "wind_speed_max": daily.get("wind_speed_10m_max", [])
            })
            
            # Thêm metadata
            df["city_name"] = city_name or f"Lat:{lat}, Lon:{lon}"
            df["latitude"] = lat
            df["longitude"] = lon
            
            logger.info(f"Lấy dữ liệu lịch sử {len(df)} ngày cho {city_name or 'Unknown'}")
            return df
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu lịch sử: {e}")
            return pd.DataFrame()
    
    def get_multiple_cities_current(self, cities: Dict[str, Dict] = None) -> List[Dict]:
        """
        Lấy dữ liệu thời tiết hiện tại cho nhiều thành phố
        
        Args:
            cities: Dict chứa tên thành phố và tọa độ
                   Format: {"Tên": {"lat": float, "lon": float}}
                   
        Returns:
            List các dict chứa dữ liệu thời tiết
        """
        if cities is None:
            cities = self.default_cities
            
        results = []
        for city_name, coords in cities.items():
            current_data = self.get_current_weather(
                coords["lat"], coords["lon"], city_name
            )
            if current_data:
                results.append(current_data)
                
        return results
    
    def search_location(self, query: str) -> List[Dict]:
        """
        Tìm kiếm tọa độ của địa điểm
        
        Args:
            query: Tên địa điểm cần tìm
            
        Returns:
            List các kết quả tìm kiếm
        """
        try:
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {
                "name": query,
                "count": 10,
                "language": "vi",
                "format": "json"
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "name": result.get("name"),
                    "country": result.get("country"),
                    "admin1": result.get("admin1"),
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "timezone": result.get("timezone")
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm địa điểm: {e}")
            return []


# Utility functions
def get_date_range(days_back: int = 30) -> Tuple[str, str]:
    """
    Tạo khoảng thời gian từ days_back ngày trước đến hôm nay
    
    Args:
        days_back: Số ngày trở về trước
        
    Returns:
        Tuple (start_date, end_date) định dạng YYYY-MM-DD
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")