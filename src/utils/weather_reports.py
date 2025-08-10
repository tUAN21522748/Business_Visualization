"""
Weather Reports - Tạo báo cáo thời tiết tự động
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import io
import base64

class WeatherReportGenerator:
    """Class tạo báo cáo thời tiết"""
    
    def __init__(self):
        self.report_templates = {
            'daily': self._daily_template,
            'weekly': self._weekly_template,
            'monthly': self._monthly_template,
            'climate': self._climate_template
        }
    
    def generate_report(self, df: pd.DataFrame, 
                       city_name: str,
                       report_type: str = 'weekly',
                       include_charts: bool = True) -> str:
        """
        Tạo báo cáo thời tiết
        
        Args:
            df: DataFrame dữ liệu thời tiết
            city_name: Tên thành phố
            report_type: Loại báo cáo ('daily', 'weekly', 'monthly', 'climate')
            include_charts: Có bao gồm mô tả biểu đồ không
            
        Returns:
            String báo cáo HTML/Markdown
        """
        if df.empty:
            return "Không có dữ liệu để tạo báo cáo."
        
        template_func = self.report_templates.get(report_type, self._weekly_template)
        return template_func(df, city_name, include_charts)
    
    def _daily_template(self, df: pd.DataFrame, city_name: str, include_charts: bool) -> str:
        """Template báo cáo hàng ngày"""
        if df.empty:
            return ""
        
        # Lấy ngày gần nhất
        latest_date = df['date'].max() if 'date' in df.columns else datetime.now()
        latest_data = df.tail(1).iloc[0] if not df.empty else {}
        
        temp = latest_data.get('temp_mean', latest_data.get('temperature', 'N/A'))
        precip = latest_data.get('precipitation', 'N/A')
        humidity = latest_data.get('humidity', 'N/A')
        wind = latest_data.get('wind_speed_max', latest_data.get('wind_speed', 'N/A'))
        
        report = f"""
# 🌤️ Báo cáo thời tiết hàng ngày - {city_name}

**Ngày:** {latest_date.strftime('%d/%m/%Y') if hasattr(latest_date, 'strftime') else latest_date}

## 📊 Thông số chính

- **🌡️ Nhiệt độ:** {temp}°C
- **💧 Độ ẩm:** {humidity}%
- **🌧️ Lượng mưa:** {precip}mm
- **💨 Tốc độ gió:** {wind}km/h

## 🔍 Nhận xét

"""
        
        # Thêm nhận xét dựa trên dữ liệu
        if isinstance(temp, (int, float)):
            if temp >= 35:
                report += "⚠️ **Cảnh báo nắng nóng** - Nhiệt độ rất cao, hạn chế ra ngoài vào giữa trưa.\n\n"
            elif temp <= 15:
                report += "❄️ **Thời tiết lạnh** - Nên mặc ấm khi ra ngoài.\n\n"
            else:
                report += "😊 **Thời tiết dễ chịu** - Thích hợp cho các hoạt động ngoài trời.\n\n"
        
        if isinstance(precip, (int, float)) and precip > 10:
            report += "🌧️ **Có mưa** - Nên mang ô khi ra ngoài.\n\n"
        
        report += f"*Báo cáo được tạo tự động lúc {datetime.now().strftime('%H:%M %d/%m/%Y')}*"
        
        return report
    
    def _weekly_template(self, df: pd.DataFrame, city_name: str, include_charts: bool) -> str:
        """Template báo cáo hàng tuần"""
        if df.empty:
            return ""
        
        # Tính toán thống kê tuần
        temp_col = 'temp_mean' if 'temp_mean' in df.columns else 'temperature'
        
        stats = {}
        if temp_col in df.columns:
            temp_data = df[temp_col].dropna()
            stats['temp_avg'] = temp_data.mean()
            stats['temp_min'] = temp_data.min()
            stats['temp_max'] = temp_data.max()
        
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            stats['precip_total'] = precip_data.sum()
            stats['rainy_days'] = len(precip_data[precip_data > 0])
        
        start_date = df['date'].min() if 'date' in df.columns else "N/A"
        end_date = df['date'].max() if 'date' in df.columns else "N/A"
        
        report = f"""
# 📈 Báo cáo thời tiết tuần - {city_name}

**Khoảng thời gian:** {start_date.strftime('%d/%m/%Y') if hasattr(start_date, 'strftime') else start_date} - {end_date.strftime('%d/%m/%Y') if hasattr(end_date, 'strftime') else end_date}

## 📊 Tóm tắt thống kê

### 🌡️ Nhiệt độ
- **Trung bình:** {stats.get('temp_avg', 0):.1f}°C
- **Cao nhất:** {stats.get('temp_max', 0):.1f}°C  
- **Thấp nhất:** {stats.get('temp_min', 0):.1f}°C

### 🌧️ Lượng mưa
- **Tổng lượng mưa:** {stats.get('precip_total', 0):.1f}mm
- **Số ngày mưa:** {stats.get('rainy_days', 0)} ngày

## 🔍 Phân tích xu hướng

"""
        
        # Phân tích xu hướng
        if 'temp_avg' in stats:
            if stats['temp_avg'] > 30:
                report += "🔥 **Tuần nóng** - Nhiệt độ trung bình cao.\n"
            elif stats['temp_avg'] < 20:
                report += "❄️ **Tuần lạnh** - Nhiệt độ trung bình thấp.\n"
            else:
                report += "😊 **Thời tiết ôn hòa** - Nhiệt độ dễ chịu.\n"
        
        if 'precip_total' in stats:
            if stats['precip_total'] > 50:
                report += "🌧️ **Tuần mưa nhiều** - Lượng mưa cao.\n"
            elif stats['precip_total'] == 0:
                report += "☀️ **Tuần khô ráo** - Không có mưa.\n"
        
        if 'temp_max' in stats and 'temp_min' in stats:
            temp_range = stats['temp_max'] - stats['temp_min']
            if temp_range > 15:
                report += "📊 **Dao động nhiệt độ lớn** - Chênh lệch nhiệt độ trong tuần cao.\n"
        
        report += f"\n*Báo cáo được tạo tự động lúc {datetime.now().strftime('%H:%M %d/%m/%Y')}*"
        
        return report
    
    def _monthly_template(self, df: pd.DataFrame, city_name: str, include_charts: bool) -> str:
        """Template báo cáo hàng tháng"""
        if df.empty:
            return ""
        
        # Tính toán thống kê tháng
        temp_col = 'temp_mean' if 'temp_mean' in df.columns else 'temperature'
        
        monthly_stats = {}
        if temp_col in df.columns:
            temp_data = df[temp_col].dropna()
            monthly_stats['temp_avg'] = temp_data.mean()
            monthly_stats['temp_min'] = temp_data.min()
            monthly_stats['temp_max'] = temp_data.max()
            monthly_stats['hot_days'] = len(temp_data[temp_data > 30])
            monthly_stats['cool_days'] = len(temp_data[temp_data < 20])
        
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            monthly_stats['precip_total'] = precip_data.sum()
            monthly_stats['rainy_days'] = len(precip_data[precip_data > 0])
            monthly_stats['max_daily_rain'] = precip_data.max()
        
        start_date = df['date'].min() if 'date' in df.columns else "N/A"
        end_date = df['date'].max() if 'date' in df.columns else "N/A"
        
        report = f"""
# 📅 Báo cáo thời tiết tháng - {city_name}

**Khoảng thời gian:** {start_date.strftime('%d/%m/%Y') if hasattr(start_date, 'strftime') else start_date} - {end_date.strftime('%d/%m/%Y') if hasattr(end_date, 'strftime') else end_date}

## 📊 Thống kê chi tiết

### 🌡️ Nhiệt độ
- **Trung bình tháng:** {monthly_stats.get('temp_avg', 0):.1f}°C
- **Cao nhất:** {monthly_stats.get('temp_max', 0):.1f}°C  
- **Thấp nhất:** {monthly_stats.get('temp_min', 0):.1f}°C
- **Ngày nóng (>30°C):** {monthly_stats.get('hot_days', 0)} ngày
- **Ngày mát (<20°C):** {monthly_stats.get('cool_days', 0)} ngày

### 🌧️ Lượng mưa
- **Tổng lượng mưa:** {monthly_stats.get('precip_total', 0):.1f}mm
- **Số ngày mưa:** {monthly_stats.get('rainy_days', 0)} ngày
- **Mưa nhiều nhất 1 ngày:** {monthly_stats.get('max_daily_rain', 0):.1f}mm

## 🔍 Đánh giá tổng quan

"""
        
        # Đánh giá tháng
        total_days = len(df)
        if 'rainy_days' in monthly_stats and total_days > 0:
            rainy_ratio = monthly_stats['rainy_days'] / total_days
            if rainy_ratio > 0.5:
                report += "🌧️ **Tháng mưa nhiều** - Hơn 50% số ngày có mưa.\n"
            elif rainy_ratio < 0.1:
                report += "☀️ **Tháng khô ráo** - Ít ngày mưa.\n"
        
        if 'temp_avg' in monthly_stats:
            if monthly_stats['temp_avg'] > 28:
                report += "🔥 **Tháng nóng** - Nhiệt độ trung bình cao.\n"
            elif monthly_stats['temp_avg'] < 18:
                report += "❄️ **Tháng lạnh** - Nhiệt độ trung bình thấp.\n"
        
        if 'hot_days' in monthly_stats and monthly_stats['hot_days'] > 10:
            report += "⚠️ **Cảnh báo nắng nóng** - Có nhiều ngày nóng trong tháng.\n"
        
        report += f"\n*Báo cáo được tạo tự động lúc {datetime.now().strftime('%H:%M %d/%m/%Y')}*"
        
        return report
    
    def _climate_template(self, df: pd.DataFrame, city_name: str, include_charts: bool) -> str:
        """Template báo cáo khí hậu"""
        if df.empty:
            return ""
        
        # Phân tích khí hậu dài hạn
        temp_col = 'temp_mean' if 'temp_mean' in df.columns else 'temperature'
        
        climate_stats = {}
        if temp_col in df.columns:
            temp_data = df[temp_col].dropna()
            climate_stats['temp_avg'] = temp_data.mean()
            climate_stats['temp_std'] = temp_data.std()
            climate_stats['extreme_hot'] = len(temp_data[temp_data > 35])
            climate_stats['extreme_cold'] = len(temp_data[temp_data < 10])
        
        if 'precipitation' in df.columns:
            precip_data = df['precipitation'].dropna()
            climate_stats['annual_precip'] = precip_data.sum()
            climate_stats['dry_days'] = len(precip_data[precip_data == 0])
            climate_stats['heavy_rain_days'] = len(precip_data[precip_data > 50])
        
        # Phân tích theo mùa nếu có dữ liệu đủ dài
        seasonal_analysis = ""
        if 'date' in df.columns and len(df) > 90:
            df_copy = df.copy()
            df_copy['month'] = pd.to_datetime(df_copy['date']).dt.month
            
            # Định nghĩa mùa cho VN
            def get_season(month):
                if month in [12, 1, 2]:
                    return 'Mùa đông'
                elif month in [3, 4, 5]:
                    return 'Mùa xuân'
                elif month in [6, 7, 8]:
                    return 'Mùa hè'
                else:
                    return 'Mùa thu'
            
            df_copy['season'] = df_copy['month'].apply(get_season)
            
            if temp_col in df_copy.columns:
                seasonal_temp = df_copy.groupby('season')[temp_col].mean()
                seasonal_analysis = "### 🍂 Phân tích theo mùa\n\n"
                for season, temp in seasonal_temp.items():
                    seasonal_analysis += f"- **{season}:** {temp:.1f}°C\n"
                seasonal_analysis += "\n"
        
        start_date = df['date'].min() if 'date' in df.columns else "N/A"
        end_date = df['date'].max() if 'date' in df.columns else "N/A"
        
        report = f"""
# 🌍 Báo cáo khí hậu dài hạn - {city_name}

**Khoảng thời gian:** {start_date.strftime('%d/%m/%Y') if hasattr(start_date, 'strftime') else start_date} - {end_date.strftime('%d/%m/%Y') if hasattr(end_date, 'strftime') else end_date}

## 📊 Đặc điểm khí hậu

### 🌡️ Nhiệt độ
- **Nhiệt độ trung bình:** {climate_stats.get('temp_avg', 0):.1f}°C
- **Độ biến động:** {climate_stats.get('temp_std', 0):.1f}°C
- **Ngày cực nóng (>35°C):** {climate_stats.get('extreme_hot', 0)} ngày
- **Ngày cực lạnh (<10°C):** {climate_stats.get('extreme_cold', 0)} ngày

### 🌧️ Lượng mưa
- **Tổng lượng mưa:** {climate_stats.get('annual_precip', 0):.0f}mm
- **Ngày khô:** {climate_stats.get('dry_days', 0)} ngày
- **Ngày mưa to (>50mm):** {climate_stats.get('heavy_rain_days', 0)} ngày

{seasonal_analysis}

## 🔍 Đặc điểm khí hậu

"""
        
        # Phân loại khí hậu đơn giản
        if 'temp_avg' in climate_stats and 'annual_precip' in climate_stats:
            temp_avg = climate_stats['temp_avg']
            annual_precip = climate_stats['annual_precip']
            
            if temp_avg > 26 and annual_precip > 1500:
                report += "🏝️ **Khí hậu nhiệt đới ẩm** - Nóng và ẩm quanh năm.\n"
            elif temp_avg > 26 and annual_precip < 1000:
                report += "🌵 **Khí hậu nhiệt đới khô** - Nóng và ít mưa.\n"
            elif 20 < temp_avg <= 26:
                report += "🌸 **Khí hậu cận nhiệt đới** - Ôn hòa với mùa rõ rệt.\n"
            else:
                report += "🍃 **Khí hậu ôn đới** - Mát mẻ với biến động theo mùa.\n"
        
        # Xu hướng biến đổi (nếu có đủ dữ liệu)
        if len(df) > 365 and temp_col in df.columns:
            temp_data = df[temp_col].dropna()
            if len(temp_data) > 100:
                # Tính xu hướng đơn giản
                x = np.arange(len(temp_data))
                slope = np.polyfit(x, temp_data, 1)[0] * 365  # Độ dốc trên năm
                
                if abs(slope) > 0.1:
                    trend_text = "tăng" if slope > 0 else "giảm"
                    report += f"📈 **Xu hướng nhiệt độ:** {trend_text} {abs(slope):.1f}°C/năm.\n"
        
        report += f"\n*Báo cáo được tạo tự động lúc {datetime.now().strftime('%H:%M %d/%m/%Y')}*"
        
        return report
    
    def export_report_to_file(self, report_content: str, filename: str = None) -> str:
        """
        Xuất báo cáo ra file
        
        Args:
            report_content: Nội dung báo cáo
            filename: Tên file (optional)
            
        Returns:
            Đường dẫn file đã tạo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_report_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return filename
        except Exception as e:
            return f"Lỗi khi xuất file: {e}"
    
    def get_download_link(self, report_content: str, filename: str) -> str:
        """
        Tạo link download cho báo cáo
        
        Args:
            report_content: Nội dung báo cáo
            filename: Tên file
            
        Returns:
            HTML link download
        """
        b64 = base64.b64encode(report_content.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Tải xuống báo cáo</a>'
        return href
