"""
Weather Analysis - Phân tích thời tiết nâng cao
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class WeatherAnalyzer:
    """Class phân tích thời tiết nâng cao"""
    
    def __init__(self):
        # Ngưỡng cảnh báo thời tiết
        self.alert_thresholds = {
            'extreme_heat': 38,      # Nắng nóng cực đoan
            'high_heat': 35,         # Nắng nóng
            'cold': 15,              # Lạnh
            'extreme_cold': 5,       # Lạnh cực đoan
            'heavy_rain': 50,        # Mưa to
            'very_heavy_rain': 100,  # Mưa rất to
            'strong_wind': 25,       # Gió mạnh
            'very_strong_wind': 40   # Gió rất mạnh
        }
    
    def generate_weather_alerts(self, df: pd.DataFrame) -> List[Dict]:
        """
        Tạo cảnh báo thời tiết
        
        Args:
            df: DataFrame chứa dữ liệu thời tiết
            
        Returns:
            List các cảnh báo
        """
        alerts = []
        
        if df.empty:
            return alerts
        
        # Kiểm tra nhiệt độ
        temp_cols = ['temp_max', 'temp_mean', 'temperature']
        temp_col = None
        for col in temp_cols:
            if col in df.columns:
                temp_col = col
                break
        
        if temp_col:
            # Nắng nóng cực đoan
            extreme_hot = df[df[temp_col] >= self.alert_thresholds['extreme_heat']]
            if not extreme_hot.empty:
                alerts.append({
                    'type': 'danger',
                    'title': '🔥 Cảnh báo nắng nóng cực đoan',
                    'message': f'Có {len(extreme_hot)} ngày nhiệt độ ≥ {self.alert_thresholds["extreme_heat"]}°C',
                    'count': len(extreme_hot),
                    'max_temp': extreme_hot[temp_col].max()
                })
            
            # Nắng nóng
            elif len(df[df[temp_col] >= self.alert_thresholds['high_heat']]) > 0:
                hot_days = df[df[temp_col] >= self.alert_thresholds['high_heat']]
                alerts.append({
                    'type': 'warning',
                    'title': '🌡️ Cảnh báo nắng nóng',
                    'message': f'Có {len(hot_days)} ngày nhiệt độ ≥ {self.alert_thresholds["high_heat"]}°C',
                    'count': len(hot_days),
                    'max_temp': hot_days[temp_col].max()
                })
            
            # Lạnh
            cold_days = df[df[temp_col] <= self.alert_thresholds['cold']]
            if not cold_days.empty:
                alert_type = 'danger' if cold_days[temp_col].min() <= self.alert_thresholds['extreme_cold'] else 'info'
                alerts.append({
                    'type': alert_type,
                    'title': '❄️ Cảnh báo thời tiết lạnh',
                    'message': f'Có {len(cold_days)} ngày nhiệt độ ≤ {self.alert_thresholds["cold"]}°C',
                    'count': len(cold_days),
                    'min_temp': cold_days[temp_col].min()
                })
        
        # Kiểm tra mưa
        if 'precipitation' in df.columns:
            # Mưa to
            heavy_rain = df[df['precipitation'] >= self.alert_thresholds['heavy_rain']]
            if not heavy_rain.empty:
                alert_type = 'danger' if heavy_rain['precipitation'].max() >= self.alert_thresholds['very_heavy_rain'] else 'warning'
                alerts.append({
                    'type': alert_type,
                    'title': '🌧️ Cảnh báo mưa to',
                    'message': f'Có {len(heavy_rain)} ngày mưa ≥ {self.alert_thresholds["heavy_rain"]}mm',
                    'count': len(heavy_rain),
                    'max_rain': heavy_rain['precipitation'].max()
                })
        
        # Kiểm tra gió
        wind_cols = ['wind_speed_max', 'wind_speed']
        wind_col = None
        for col in wind_cols:
            if col in df.columns:
                wind_col = col
                break
        
        if wind_col:
            strong_wind = df[df[wind_col] >= self.alert_thresholds['strong_wind']]
            if not strong_wind.empty:
                alert_type = 'danger' if strong_wind[wind_col].max() >= self.alert_thresholds['very_strong_wind'] else 'warning'
                alerts.append({
                    'type': alert_type,
                    'title': '💨 Cảnh báo gió mạnh',
                    'message': f'Có {len(strong_wind)} ngày gió ≥ {self.alert_thresholds["strong_wind"]}km/h',
                    'count': len(strong_wind),
                    'max_wind': strong_wind[wind_col].max()
                })
        
        return alerts
    
    def calculate_climate_indices(self, df: pd.DataFrame) -> Dict:
        """
        Tính toán các chỉ số khí hậu
        
        Args:
            df: DataFrame chứa dữ liệu
            
        Returns:
            Dict chứa các chỉ số khí hậu
        """
        indices = {}
        
        if df.empty or 'date' not in df.columns:
            return indices
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Chỉ số nhiệt độ
        temp_cols = ['temp_max', 'temp_mean', 'temperature']
        temp_col = None
        for col in temp_cols:
            if col in df.columns:
                temp_col = col
                break
        
        if temp_col:
            temp_data = df[temp_col].dropna()
            if not temp_data.empty:
                indices['temperature_indices'] = {
                    'mean_temp': round(temp_data.mean(), 1),
                    'temp_range': round(temp_data.max() - temp_data.min(), 1),
                    'hot_days': len(temp_data[temp_data > 30]),
                    'cool_days': len(temp_data[temp_data < 20]),
                    'temp_variability': round(temp_data.std(), 1)
                }
        
        # Chỉ số mưa
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            if not precip_data.empty:
                rainy_days = len(precip_data[precip_data > 0])
                dry_days = len(precip_data[precip_data == 0])
                
                indices['precipitation_indices'] = {
                    'total_precipitation': round(precip_data.sum(), 1),
                    'rainy_days': rainy_days,
                    'dry_days': dry_days,
                    'average_rain_per_rainy_day': round(precip_data[precip_data > 0].mean(), 1) if rainy_days > 0 else 0,
                    'max_daily_rain': round(precip_data.max(), 1),
                    'precipitation_intensity': 'Cao' if precip_data.mean() > 5 else 'Thấp'
                }
        
        # Comfort Index (dựa trên nhiệt độ và độ ẩm)
        if temp_col and 'humidity' in df.columns:
            temp_data = df[temp_col].dropna()
            humidity_data = df['humidity'].dropna()
            
            if not temp_data.empty and not humidity_data.empty:
                # Heat Index đơn giản
                comfort_scores = []
                for temp, humidity in zip(temp_data, humidity_data):
                    if 18 <= temp <= 26 and 40 <= humidity <= 60:
                        comfort_scores.append(100)  # Thoải mái
                    elif 15 <= temp <= 30 and 30 <= humidity <= 70:
                        comfort_scores.append(75)   # Khá thoải mái
                    else:
                        comfort_scores.append(50)   # Không thoải mái
                
                if comfort_scores:
                    avg_comfort = np.mean(comfort_scores)
                    indices['comfort_index'] = {
                        'comfort_score': round(avg_comfort, 1),
                        'comfort_level': self._get_comfort_level(avg_comfort),
                        'comfortable_days': len([s for s in comfort_scores if s == 100])
                    }
        
        return indices
    
    def _get_comfort_level(self, score: float) -> str:
        """Chuyển đổi điểm comfort thành mức độ"""
        if score >= 90:
            return "Rất thoải mái"
        elif score >= 75:
            return "Thoải mái"
        elif score >= 60:
            return "Khá thoải mái"
        elif score >= 40:
            return "Không thoải mái"
        else:
            return "Rất không thoải mái"
    
    def detect_weather_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Phát hiện các pattern thời tiết
        
        Args:
            df: DataFrame chứa dữ liệu
            
        Returns:
            Dict chứa các pattern
        """
        patterns = {}
        
        if df.empty or len(df) < 7:
            return patterns
        
        df = df.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        # Pattern nhiệt độ
        temp_cols = ['temp_max', 'temp_mean', 'temperature']
        temp_col = None
        for col in temp_cols:
            if col in df.columns:
                temp_col = col
                break
        
        if temp_col:
            temp_data = df[temp_col].dropna()
            if len(temp_data) >= 7:
                # Tính xu hướng
                x = np.arange(len(temp_data))
                slope = np.polyfit(x, temp_data, 1)[0]
                
                if slope > 0.2:
                    temp_trend = "Tăng"
                elif slope < -0.2:
                    temp_trend = "Giảm"
                else:
                    temp_trend = "Ổn định"
                
                # Phát hiện heat waves (3+ ngày liên tiếp > 35°C)
                heat_wave_days = 0
                current_streak = 0
                for temp in temp_data:
                    if temp > 35:
                        current_streak += 1
                        if current_streak >= 3:
                            heat_wave_days += 1
                    else:
                        current_streak = 0
                
                patterns['temperature_patterns'] = {
                    'trend': temp_trend,
                    'trend_slope': round(slope, 3),
                    'heat_wave_days': heat_wave_days,
                    'temperature_volatility': 'Cao' if temp_data.std() > 5 else 'Thấp'
                }
        
        # Pattern mưa
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            if len(precip_data) >= 7:
                # Phát hiện dry/wet spells
                dry_spell_days = 0
                wet_spell_days = 0
                current_dry_streak = 0
                current_wet_streak = 0
                
                for precip in precip_data:
                    if precip == 0:
                        current_dry_streak += 1
                        current_wet_streak = 0
                        if current_dry_streak >= 5:  # 5+ ngày không mưa
                            dry_spell_days += 1
                    else:
                        current_wet_streak += 1
                        current_dry_streak = 0
                        if current_wet_streak >= 3:  # 3+ ngày mưa liên tiếp
                            wet_spell_days += 1
                
                patterns['precipitation_patterns'] = {
                    'dry_spell_days': dry_spell_days,
                    'wet_spell_days': wet_spell_days,
                    'rain_consistency': 'Đều' if precip_data.std() < 10 else 'Không đều'
                }
        
        return patterns
    
    def generate_weather_summary(self, df: pd.DataFrame, city_name: str = None) -> str:
        """
        Tạo tóm tắt thời tiết tự động
        
        Args:
            df: DataFrame chứa dữ liệu
            city_name: Tên thành phố
            
        Returns:
            String tóm tắt
        """
        if df.empty:
            return "Không có dữ liệu để phân tích."
        
        city = city_name or "khu vực này"
        summary_parts = []
        
        # Phân tích cơ bản
        alerts = self.generate_weather_alerts(df)
        indices = self.calculate_climate_indices(df)
        patterns = self.detect_weather_patterns(df)
        
        # Tóm tắt nhiệt độ
        if 'temperature_indices' in indices:
            temp_idx = indices['temperature_indices']
            summary_parts.append(
                f"Nhiệt độ trung bình tại {city} là {temp_idx['mean_temp']}°C, "
                f"với biên độ dao động {temp_idx['temp_range']}°C."
            )
            
            if temp_idx['hot_days'] > 0:
                summary_parts.append(f"Có {temp_idx['hot_days']} ngày nóng (>30°C).")
        
        # Tóm tắt mưa
        if 'precipitation_indices' in indices:
            precip_idx = indices['precipitation_indices']
            summary_parts.append(
                f"Tổng lượng mưa là {precip_idx['total_precipitation']}mm "
                f"trong {precip_idx['rainy_days']} ngày mưa."
            )
        
        # Cảnh báo quan trọng
        danger_alerts = [a for a in alerts if a['type'] == 'danger']
        if danger_alerts:
            summary_parts.append("⚠️ Cần chú ý: " + ", ".join([a['title'] for a in danger_alerts]))
        
        # Comfort index
        if 'comfort_index' in indices:
            comfort = indices['comfort_index']
            summary_parts.append(f"Mức độ thoải mái: {comfort['comfort_level']} ({comfort['comfort_score']}/100).")
        
        return " ".join(summary_parts)
    
    def compare_periods(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                       period1_name: str, period2_name: str) -> Dict:
        """
        So sánh hai khoảng thời gian
        
        Args:
            df1: DataFrame khoảng thời gian 1
            df2: DataFrame khoảng thời gian 2
            period1_name: Tên khoảng thời gian 1
            period2_name: Tên khoảng thời gian 2
            
        Returns:
            Dict chứa kết quả so sánh
        """
        comparison = {
            'period1': period1_name,
            'period2': period2_name,
            'differences': {}
        }
        
        # So sánh nhiệt độ
        temp_cols = ['temp_max', 'temp_mean', 'temperature']
        temp_col = None
        for col in temp_cols:
            if col in df1.columns and col in df2.columns:
                temp_col = col
                break
        
        if temp_col:
            temp1 = df1[temp_col].mean()
            temp2 = df2[temp_col].mean()
            diff = temp2 - temp1
            
            comparison['differences']['temperature'] = {
                'period1_avg': round(temp1, 1),
                'period2_avg': round(temp2, 1),
                'difference': round(diff, 1),
                'change_description': f"{'Tăng' if diff > 0 else 'Giảm'} {abs(diff):.1f}°C"
            }
        
        # So sánh mưa
        if 'precipitation' in df1.columns and 'precipitation' in df2.columns:
            precip1 = df1['precipitation'].sum()
            precip2 = df2['precipitation'].sum()
            diff = precip2 - precip1
            
            comparison['differences']['precipitation'] = {
                'period1_total': round(precip1, 1),
                'period2_total': round(precip2, 1),
                'difference': round(diff, 1),
                'change_description': f"{'Tăng' if diff > 0 else 'Giảm'} {abs(diff):.1f}mm"
            }
        
        return comparison
