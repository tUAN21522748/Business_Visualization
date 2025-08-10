"""
Data Handler - Xử lý và phân tích dữ liệu thời tiết
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class WeatherDataHandler:
    """Class xử lý dữ liệu thời tiết"""
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Đảm bảo thư mục cache tồn tại"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def save_to_cache(self, data: pd.DataFrame, filename: str):
        """
        Lưu DataFrame vào cache
        
        Args:
            data: DataFrame cần lưu
            filename: Tên file (không bao gồm extension)
        """
        try:
            filepath = os.path.join(self.cache_dir, f"{filename}.csv")
            data.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Đã lưu dữ liệu vào {filepath}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu cache: {e}")
    
    def load_from_cache(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Tải DataFrame từ cache
        
        Args:
            filename: Tên file (không bao gồm extension)
            
        Returns:
            DataFrame hoặc None nếu không tìm thấy
        """
        try:
            filepath = os.path.join(self.cache_dir, f"{filename}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, encoding='utf-8')
                # Convert date column nếu có
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                logger.info(f"Đã tải dữ liệu từ {filepath}")
                return df
            return None
        except Exception as e:
            logger.error(f"Lỗi khi tải cache: {e}")
            return None
    
    def process_current_weather(self, weather_data: List[Dict]) -> pd.DataFrame:
        """
        Xử lý dữ liệu thời tiết hiện tại thành DataFrame
        
        Args:
            weather_data: List các dict chứa dữ liệu thời tiết
            
        Returns:
            DataFrame đã được xử lý
        """
        if not weather_data:
            return pd.DataFrame()
        
        # Chuyển đổi thành DataFrame
        df = pd.DataFrame(weather_data)
        
        # Xử lý timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date
        
        # Làm tròn số liệu
        numeric_columns = ['temperature', 'humidity', 'precipitation', 
                          'wind_speed', 'pressure']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
        
        return df
    
    def calculate_statistics(self, df: pd.DataFrame, 
                           temp_col: str = 'temp_mean') -> Dict:
        """
        Tính toán các thống kê cơ bản
        
        Args:
            df: DataFrame chứa dữ liệu
            temp_col: Tên cột nhiệt độ
            
        Returns:
            Dict chứa các thống kê
        """
        if df.empty:
            return {}
        
        stats = {}
        
        # Thống kê nhiệt độ
        if temp_col in df.columns:
            temp_data = df[temp_col].dropna()
            if not temp_data.empty:
                stats['temperature'] = {
                    'mean': round(temp_data.mean(), 1),
                    'min': round(temp_data.min(), 1),
                    'max': round(temp_data.max(), 1),
                    'std': round(temp_data.std(), 1)
                }
        
        # Thống kê lượng mưa
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            if not precip_data.empty:
                stats['precipitation'] = {
                    'total': round(precip_data.sum(), 1),
                    'mean': round(precip_data.mean(), 1),
                    'max': round(precip_data.max(), 1),
                    'rainy_days': len(precip_data[precip_data > 0])
                }
        
        # Thống kê gió
        if 'wind_speed_max' in df.columns:
            wind_data = df['wind_speed_max'].dropna()
            if not wind_data.empty:
                stats['wind'] = {
                    'mean': round(wind_data.mean(), 1),
                    'max': round(wind_data.max(), 1)
                }
        
        return stats
    
    def calculate_monthly_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán dữ liệu tổng hợp theo tháng
        
        Args:
            df: DataFrame chứa dữ liệu hàng ngày
            
        Returns:
            DataFrame tổng hợp theo tháng
        """
        if df.empty or 'date' not in df.columns:
            return pd.DataFrame()
        
        # Đảm bảo date column là datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        
        # Tổng hợp theo tháng
        monthly_agg = {}
        
        # Nhiệt độ trung bình
        if 'temp_mean' in df.columns:
            monthly_agg['temp_mean'] = df.groupby('year_month')['temp_mean'].mean()
        elif 'temp_max' in df.columns and 'temp_min' in df.columns:
            df['temp_mean'] = (df['temp_max'] + df['temp_min']) / 2
            monthly_agg['temp_mean'] = df.groupby('year_month')['temp_mean'].mean()
        
        # Nhiệt độ cao nhất và thấp nhất
        if 'temp_max' in df.columns:
            monthly_agg['temp_max'] = df.groupby('year_month')['temp_max'].max()
        if 'temp_min' in df.columns:
            monthly_agg['temp_min'] = df.groupby('year_month')['temp_min'].min()
        
        # Tổng lượng mưa
        if 'precipitation' in df.columns:
            monthly_agg['precipitation_sum'] = df.groupby('year_month')['precipitation'].sum()
            monthly_agg['rainy_days'] = df.groupby('year_month')['precipitation'].apply(
                lambda x: (x > 0).sum()
            )
        
        # Gió trung bình
        if 'wind_speed_max' in df.columns:
            monthly_agg['wind_speed_mean'] = df.groupby('year_month')['wind_speed_max'].mean()
        
        # Tạo DataFrame kết quả
        if monthly_agg:
            result_df = pd.DataFrame(monthly_agg)
            result_df.index.name = 'month'
            result_df = result_df.reset_index()
            result_df['month_str'] = result_df['month'].astype(str)
            
            # Làm tròn
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns
            result_df[numeric_cols] = result_df[numeric_cols].round(1)
            
            return result_df
        
        return pd.DataFrame()
    
    def detect_anomalies(self, df: pd.DataFrame, 
                        column: str = 'temp_mean',
                        threshold: float = 2.0) -> pd.DataFrame:
        """
        Phát hiện dị thường trong dữ liệu
        
        Args:
            df: DataFrame chứa dữ liệu
            column: Tên cột cần phân tích
            threshold: Ngưỡng độ lệch chuẩn
            
        Returns:
            DataFrame chứa các điểm dị thường
        """
        if df.empty or column not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        data = df[column].dropna()
        
        if len(data) < 10:  # Cần ít nhất 10 điểm dữ liệu
            return pd.DataFrame()
        
        # Tính z-score
        mean_val = data.mean()
        std_val = data.std()
        
        df['z_score'] = np.abs((df[column] - mean_val) / std_val)
        df['is_anomaly'] = df['z_score'] > threshold
        
        # Trả về chỉ các điểm dị thường
        anomalies = df[df['is_anomaly']].copy()
        
        if not anomalies.empty:
            logger.info(f"Tìm thấy {len(anomalies)} điểm dị thường trong {column}")
        
        return anomalies
    
    def calculate_trends(self, df: pd.DataFrame,
                        column: str = 'temp_mean',
                        window: int = 7) -> pd.DataFrame:
        """
        Tính toán xu hướng và moving average
        
        Args:
            df: DataFrame chứa dữ liệu
            column: Tên cột cần phân tích
            window: Cửa sổ trung bình động
            
        Returns:
            DataFrame với các cột xu hướng bổ sung
        """
        if df.empty or column not in df.columns:
            return df
        
        df = df.copy()
        
        # Sắp xếp theo ngày
        if 'date' in df.columns:
            df = df.sort_values('date')
            df = df.reset_index(drop=True)
        
        # Moving average
        df[f'{column}_ma{window}'] = df[column].rolling(window=window, center=True).mean()
        
        # Tính độ dốc (slope) đơn giản
        if len(df) > 1:
            df[f'{column}_slope'] = df[column].diff()
        
        # Phân loại xu hướng
        if f'{column}_slope' in df.columns:
            conditions = [
                df[f'{column}_slope'] > 0.5,
                df[f'{column}_slope'] < -0.5
            ]
            choices = ['Tăng', 'Giảm']
            df[f'{column}_trend'] = np.select(conditions, choices, default='Ổn định')
        
        return df
    
    def get_weather_summary(self, df: pd.DataFrame, city_name: str = None) -> Dict:
        """
        Tạo tóm tắt thời tiết tổng quan
        
        Args:
            df: DataFrame chứa dữ liệu
            city_name: Tên thành phố
            
        Returns:
            Dict chứa tóm tắt
        """
        if df.empty:
            return {"error": "Không có dữ liệu"}
        
        summary = {
            "city": city_name or "Unknown",
            "period": {
                "start": None,
                "end": None,
                "total_days": len(df)
            },
            "statistics": self.calculate_statistics(df)
        }
        
        # Thời gian
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            summary["period"]["start"] = dates.min().strftime("%Y-%m-%d")
            summary["period"]["end"] = dates.max().strftime("%Y-%m-%d")
        
        # Thêm thông tin đặc biệt
        stats = summary["statistics"]
        
        if "temperature" in stats:
            temp_stats = stats["temperature"]
            summary["highlights"] = []
            
            if temp_stats["max"] > 35:
                summary["highlights"].append(f"Có ngày nóng cực đại {temp_stats['max']}°C")
            if temp_stats["min"] < 15:
                summary["highlights"].append(f"Có ngày lạnh tối thiểu {temp_stats['min']}°C")
        
        if "precipitation" in stats:
            precip_stats = stats["precipitation"]
            if precip_stats["total"] > 100:
                summary["highlights"] = summary.get("highlights", [])
                summary["highlights"].append(
                    f"Tổng lượng mưa {precip_stats['total']}mm trong {precip_stats['rainy_days']} ngày"
                )
        
        return summary
    
    def export_data(self, df: pd.DataFrame, filename: str, format: str = 'csv'):
        """
        Xuất dữ liệu ra file
        
        Args:
            df: DataFrame cần xuất
            filename: Tên file
            format: Định dạng file ('csv', 'excel')
        """
        try:
            filepath = os.path.join(self.cache_dir, filename)
            
            if format.lower() == 'csv':
                df.to_csv(filepath, index=False, encoding='utf-8')
            elif format.lower() in ['excel', 'xlsx']:
                df.to_excel(filepath, index=False)
            else:
                raise ValueError(f"Định dạng {format} không được hỗ trợ")
            
            logger.info(f"Đã xuất dữ liệu ra {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Lỗi khi xuất dữ liệu: {e}")
            return None