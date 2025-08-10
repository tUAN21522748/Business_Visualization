"""
Helper functions - Các hàm tiện ích cho ứng dụng thời tiết
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re

def format_temperature(temp: float, unit: str = "°C") -> str:
    """
    Format nhiệt độ với đơn vị
    
    Args:
        temp: Giá trị nhiệt độ
        unit: Đơn vị nhiệt độ
        
    Returns:
        String đã format
    """
    if pd.isna(temp):
        return "N/A"
    return f"{temp:.1f}{unit}"

def format_precipitation(precip: float, unit: str = "mm") -> str:
    """
    Format lượng mưa với đơn vị
    
    Args:
        precip: Giá trị lượng mưa
        unit: Đơn vị
        
    Returns:
        String đã format
    """
    if pd.isna(precip) or precip == 0:
        return "0mm"
    return f"{precip:.1f}{unit}"

def format_wind_speed(speed: float, unit: str = "km/h") -> str:
    """
    Format tốc độ gió với đơn vị
    
    Args:
        speed: Tốc độ gió
        unit: Đơn vị
        
    Returns:
        String đã format
    """
    if pd.isna(speed):
        return "N/A"
    return f"{speed:.1f}{unit}"

def get_wind_direction_text(degree: float) -> str:
    """
    Chuyển đổi góc gió thành text mô tả
    
    Args:
        degree: Góc gió (độ)
        
    Returns:
        Mô tả hướng gió
    """
    if pd.isna(degree):
        return "N/A"
    
    directions = [
        "Bắc", "Bắc Đông Bắc", "Đông Bắc", "Đông Đông Bắc",
        "Đông", "Đông Đông Nam", "Đông Nam", "Nam Đông Nam", 
        "Nam", "Nam Tây Nam", "Tây Nam", "Tây Tây Nam",
        "Tây", "Tây Tây Bắc", "Tây Bắc", "Bắc Tây Bắc"
    ]
    
    index = round(degree / 22.5) % 16
    return directions[int(index)]

def get_weather_description(temp: float, precip: float = 0, 
                          wind_speed: float = 0) -> str:
    """
    Tạo mô tả thời tiết dựa trên các chỉ số
    
    Args:
        temp: Nhiệt độ
        precip: Lượng mưa
        wind_speed: Tốc độ gió
        
    Returns:
        Mô tả thời tiết
    """
    descriptions = []
    
    # Mô tả nhiệt độ
    if temp < 15:
        descriptions.append("lạnh")
    elif temp < 25:
        descriptions.append("mát mẻ")
    elif temp < 30:
        descriptions.append("ấm áp")
    elif temp < 35:
        descriptions.append("nóng")
    else:
        descriptions.append("rất nóng")
    
    # Mô tả mưa
    if precip > 50:
        descriptions.append("mưa to")
    elif precip > 10:
        descriptions.append("mưa vừa")
    elif precip > 0:
        descriptions.append("mưa nhẹ")
    
    # Mô tả gió
    if wind_speed > 25:
        descriptions.append("gió mạnh")
    elif wind_speed > 15:
        descriptions.append("gió vừa")
    
    return ", ".join(descriptions).capitalize()

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Kiểm tra tọa độ có hợp lệ không
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True nếu hợp lệ
    """
    return (-90 <= lat <= 90) and (-180 <= lon <= 180)

def parse_date_input(date_str: str) -> Optional[datetime]:
    """
    Parse string ngày tháng thành datetime
    
    Args:
        date_str: String ngày tháng
        
    Returns:
        Datetime object hoặc None
    """
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y", 
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def get_date_range_options() -> Dict[str, Tuple[datetime, datetime]]:
    """
    Tạo các tùy chọn khoảng thời gian mặc định
    
    Returns:
        Dict chứa các tùy chọn thời gian
    """
    today = datetime.now()
    # Đảm bảo end_date không vượt quá hôm nay
    yesterday = today - timedelta(days=1)
    
    return {
        "7 ngày qua": (yesterday - timedelta(days=6), yesterday),
        "30 ngày qua": (yesterday - timedelta(days=29), yesterday),
        "3 tháng qua": (yesterday - timedelta(days=89), yesterday),
        "6 tháng qua": (yesterday - timedelta(days=179), yesterday),
        "1 năm qua": (yesterday - timedelta(days=364), yesterday)
    }

def create_color_scale(values: List[float], colormap: str = "RdYlBu_r") -> List[str]:
    """
    Tạo color scale cho dữ liệu
    
    Args:
        values: List giá trị
        colormap: Tên colormap
        
    Returns:
        List màu hex
    """
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    
    if not values:
        return []
    
    # Normalize values
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        return ["#1f77b4"] * len(values)
    
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(colormap)
    
    colors = []
    for val in values:
        rgba = cmap(norm(val))
        hex_color = mcolors.to_hex(rgba)
        colors.append(hex_color)
    
    return colors

def filter_dataframe_by_date(df: pd.DataFrame, 
                           start_date: datetime, 
                           end_date: datetime,
                           date_column: str = "date") -> pd.DataFrame:
    """
    Filter DataFrame theo khoảng thời gian
    
    Args:
        df: DataFrame cần filter
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        date_column: Tên cột chứa ngày
        
    Returns:
        DataFrame đã được filter
    """
    if df.empty or date_column not in df.columns:
        return df
    
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df[mask]

def create_summary_cards_data(weather_data: Dict) -> List[Dict]:
    """
    Tạo dữ liệu cho các KPI cards
    
    Args:
        weather_data: Dict chứa dữ liệu thời tiết
        
    Returns:
        List dict cho các cards
    """
    cards = []
    
    if "temperature" in weather_data:
        cards.append({
            "title": "Nhiệt độ",
            "value": format_temperature(weather_data["temperature"]),
            "delta": None,
            "help": "Nhiệt độ hiện tại"
        })
    
    if "humidity" in weather_data:
        cards.append({
            "title": "Độ ẩm", 
            "value": f"{weather_data['humidity']:.0f}%",
            "delta": None,
            "help": "Độ ẩm tương đối"
        })
    
    if "precipitation" in weather_data:
        cards.append({
            "title": "Lượng mưa",
            "value": format_precipitation(weather_data["precipitation"]),
            "delta": None,
            "help": "Lượng mưa hiện tại"
        })
    
    if "wind_speed" in weather_data:
        cards.append({
            "title": "Tốc độ gió",
            "value": format_wind_speed(weather_data["wind_speed"]),
            "delta": None,
            "help": "Tốc độ gió hiện tại"
        })
    
    return cards

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Phép chia an toàn, tránh chia cho 0
    
    Args:
        a: Số bị chia
        b: Số chia
        default: Giá trị mặc định nếu b = 0
        
    Returns:
        Kết quả phép chia
    """
    return a / b if b != 0 else default

def clean_city_name(city_name: str) -> str:
    """
    Làm sạch tên thành phố
    
    Args:
        city_name: Tên thành phố gốc
        
    Returns:
        Tên thành phố đã làm sạch
    """
    if not city_name:
        return "Unknown"
    
    # Loại bỏ các ký tự đặc biệt
    cleaned = re.sub(r'[^\w\s\-\.]', '', city_name)
    # Loại bỏ khoảng trắng thừa
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()

def format_number(number: float, decimals: int = 1) -> str:
    """
    Format số với số chữ số thập phân
    
    Args:
        number: Số cần format
        decimals: Số chữ số thập phân
        
    Returns:
        String đã format
    """
    if pd.isna(number):
        return "N/A"
    
    format_str = f"{{:.{decimals}f}}"
    return format_str.format(number)

@st.cache_data(ttl=3600)  # Cache 1 giờ
def cached_api_call(func, *args, **kwargs):
    """
    Wrapper để cache các API calls
    
    Args:
        func: Function cần cache
        args: Arguments
        kwargs: Keyword arguments
        
    Returns:
        Kết quả function
    """
    return func(*args, **kwargs)

def display_error_message(message: str, error_type: str = "error"):
    """
    Hiển thị thông báo lỗi trong Streamlit
    
    Args:
        message: Nội dung thông báo
        error_type: Loại thông báo (error, warning, info)
    """
    if error_type == "error":
        st.error(f"❌ {message}")
    elif error_type == "warning":
        st.warning(f"⚠️ {message}")
    elif error_type == "info":
        st.info(f"ℹ️ {message}")
    else:
        st.write(message)

def display_success_message(message: str):
    """
    Hiển thị thông báo thành công
    
    Args:
        message: Nội dung thông báo
    """
    st.success(f"✅ {message}")

def get_vietnamese_month_name(month_num: int) -> str:
    """
    Chuyển đổi số tháng thành tên tháng tiếng Việt
    
    Args:
        month_num: Số tháng (1-12)
        
    Returns:
        Tên tháng tiếng Việt
    """
    months = {
        1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
        5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8", 
        9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12"
    }
    return months.get(month_num, f"Tháng {month_num}")