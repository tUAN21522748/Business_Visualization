"""
Charts - Tạo các biểu đồ thời tiết
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import folium
from folium.plugins import HeatMap
import streamlit as st

# Cấu hình màu sắc
COLORS = {
    'temperature': '#ff6b6b',
    'precipitation': '#4ecdc4', 
    'humidity': '#45b7d1',
    'wind': '#96ceb4',
    'pressure': '#feca57'
}

def create_temperature_line_chart(df: pd.DataFrame, 
                                city_name: str = None,
                                show_range: bool = True) -> go.Figure:
    """
    Tạo biểu đồ đường nhiệt độ
    
    Args:
        df: DataFrame chứa dữ liệu
        city_name: Tên thành phố
        show_range: Hiển thị khoảng min-max
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if df.empty:
        return fig
    
    # Đảm bảo có cột date
    if 'date' not in df.columns:
        return fig
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Nhiệt độ trung bình
    if 'temp_mean' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['temp_mean'],
            mode='lines+markers',
            name='Nhiệt độ TB',
            line=dict(color=COLORS['temperature'], width=3),
            marker=dict(size=6)
        ))
    
    # Khoảng nhiệt độ min-max
    if show_range and 'temp_max' in df.columns and 'temp_min' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['temp_max'],
            mode='lines',
            name='Nhiệt độ cao nhất',
            line=dict(color='rgba(255,107,107,0.3)', width=1),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['temp_min'],
            mode='lines',
            name='Nhiệt độ thấp nhất',
            line=dict(color='rgba(255,107,107,0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(255,107,107,0.1)',
            showlegend=False
        ))
    
    # Cấu hình layout
    title = f"Biến động nhiệt độ - {city_name}" if city_name else "Biến động nhiệt độ"
    fig.update_layout(
        title=title,
        xaxis_title="Ngày",
        yaxis_title="Nhiệt độ (°C)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_precipitation_bar_chart(df: pd.DataFrame, 
                                 city_name: str = None,
                                 aggregate: str = 'daily') -> go.Figure:
    """
    Tạo biểu đồ cột lượng mưa
    
    Args:
        df: DataFrame chứa dữ liệu
        city_name: Tên thành phố
        aggregate: Mức độ tổng hợp ('daily', 'monthly')
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if df.empty or 'precipitation' not in df.columns:
        return fig
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    if aggregate == 'monthly':
        # Tổng hợp theo tháng
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_precip = df.groupby('year_month')['precipitation'].sum().reset_index()
        monthly_precip['year_month_str'] = monthly_precip['year_month'].astype(str)
        
        fig.add_trace(go.Bar(
            x=monthly_precip['year_month_str'],
            y=monthly_precip['precipitation'],
            name='Lượng mưa tháng',
            marker_color=COLORS['precipitation']
        ))
        
        x_title = "Tháng"
        y_title = "Tổng lượng mưa (mm)"
        
    else:
        # Hiển thị theo ngày
        df = df.sort_values('date')
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['precipitation'],
            name='Lượng mưa ngày',
            marker_color=COLORS['precipitation']
        ))
        
        x_title = "Ngày"
        y_title = "Lượng mưa (mm)"
    
    title = f"Lượng mưa - {city_name}" if city_name else "Lượng mưa"
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template='plotly_white',
        height=400
    )
    
    return fig

def create_wind_polar_chart(df: pd.DataFrame, city_name: str = None) -> go.Figure:
    """
    Tạo biểu đồ hướng gió dạng polar
    
    Args:
        df: DataFrame chứa dữ liệu
        city_name: Tên thành phố
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if df.empty:
        return fig
    
    # Kiểm tra cột cần thiết
    wind_dir_col = None
    wind_speed_col = None
    
    for col in ['wind_direction', 'wind_direction_10m_dominant']:
        if col in df.columns:
            wind_dir_col = col
            break
    
    for col in ['wind_speed_max', 'wind_speed']:
        if col in df.columns:
            wind_speed_col = col
            break
    
    if not wind_dir_col or not wind_speed_col:
        return fig
    
    # Lọc dữ liệu hợp lệ
    valid_data = df.dropna(subset=[wind_dir_col, wind_speed_col])
    
    if valid_data.empty:
        return fig
    
    fig.add_trace(go.Scatterpolar(
        r=valid_data[wind_speed_col],
        theta=valid_data[wind_dir_col],
        mode='markers',
        marker=dict(
            color=valid_data[wind_speed_col],
            colorscale='Viridis',
            size=8,
            colorbar=dict(title="Tốc độ gió (km/h)")
        ),
        name='Hướng gió'
    ))
    
    title = f"Phân bố hướng gió - {city_name}" if city_name else "Phân bố hướng gió"
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, valid_data[wind_speed_col].max() * 1.1]
            )
        ),
        height=500
    )
    
    return fig

def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Tạo heatmap tương quan giữa các biến thời tiết
    
    Args:
        df: DataFrame chứa dữ liệu
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # Chọn các cột số
    numeric_cols = []
    possible_cols = [
        'temp_mean', 'temp_max', 'temp_min', 'temperature',
        'precipitation', 'humidity', 'wind_speed_max', 'wind_speed',
        'pressure'
    ]
    
    for col in possible_cols:
        if col in df.columns:
            numeric_cols.append(col)
    
    if len(numeric_cols) < 2:
        return fig
    
    # Tính ma trận tương quan
    corr_matrix = df[numeric_cols].corr()
    
    # Tạo heatmap
    fig.add_trace(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Hệ số tương quan")
    ))
    
    fig.update_layout(
        title="Ma trận tương quan các yếu tố thời tiết",
        height=500,
        template='plotly_white'
    )
    
    return fig

def create_weather_map(weather_data: List[Dict], zoom: int = 6) -> folium.Map:
    """
    Tạo bản đồ thời tiết
    
    Args:
        weather_data: List dữ liệu thời tiết các địa điểm
        zoom: Mức zoom bản đồ
        
    Returns:
        Folium Map
    """
    if not weather_data:
        # Bản đồ mặc định trung tâm Việt Nam
        center_map = folium.Map(
            location=[16.0, 107.0],
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        return center_map
    
    # Tính toán trung tâm bản đồ
    lats = [data.get('latitude', 0) for data in weather_data if data.get('latitude')]
    lons = [data.get('longitude', 0) for data in weather_data if data.get('longitude')]
    
    if not lats or not lons:
        center_lat, center_lon = 16.0, 107.0
    else:
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    
    # Tạo bản đồ
    weather_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # Thêm markers cho từng địa điểm
    for data in weather_data:
        if not data.get('latitude') or not data.get('longitude'):
            continue
            
        temp = data.get('temperature', 'N/A')
        humidity = data.get('humidity', 'N/A')
        precip = data.get('precipitation', 'N/A')
        city = data.get('city_name', 'Unknown')
        
        # Màu marker dựa trên nhiệt độ
        if isinstance(temp, (int, float)):
            if temp < 15:
                color = 'blue'
            elif temp < 25:
                color = 'green'
            elif temp < 30:
                color = 'orange'
            else:
                color = 'red'
        else:
            color = 'gray'
        
        # Popup content
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>{city}</b><br>
            🌡️ Nhiệt độ: {temp}°C<br>
            💧 Độ ẩm: {humidity}%<br>
            🌧️ Lượng mưa: {precip}mm
        </div>
        """
        
        folium.Marker(
            location=[data['latitude'], data['longitude']],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{city}: {temp}°C",
            icon=folium.Icon(color=color, icon='cloud')
        ).add_to(weather_map)
    
    return weather_map

def create_seasonal_comparison(df: pd.DataFrame, 
                             city_name: str = None) -> go.Figure:
    """
    Tạo biểu đồ so sánh theo mùa
    
    Args:
        df: DataFrame chứa dữ liệu
        city_name: Tên thành phố
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    if df.empty or 'date' not in df.columns:
        return fig
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Định nghĩa mùa
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Mùa đông'
        elif month in [3, 4, 5]:
            return 'Mùa xuân'
        elif month in [6, 7, 8]:
            return 'Mùa hè'
        else:
            return 'Mùa thu'
    
    df['season'] = df['date'].dt.month.apply(get_season)
    
    # Tổng hợp theo mùa
    if 'temp_mean' in df.columns:
        seasonal_temp = df.groupby('season')['temp_mean'].agg(['mean', 'min', 'max']).reset_index()
        
        fig.add_trace(go.Bar(
            x=seasonal_temp['season'],
            y=seasonal_temp['mean'],
            name='Nhiệt độ TB',
            marker_color=COLORS['temperature'],
            error_y=dict(
                type='data',
                symmetric=False,
                array=seasonal_temp['max'] - seasonal_temp['mean'],
                arrayminus=seasonal_temp['mean'] - seasonal_temp['min']
            )
        ))
    
    title = f"So sánh theo mùa - {city_name}" if city_name else "So sánh theo mùa"
    fig.update_layout(
        title=title,
        xaxis_title="Mùa",
        yaxis_title="Nhiệt độ (°C)",
        template='plotly_white',
        height=400
    )
    
    return fig

def create_multi_metric_chart(df: pd.DataFrame, 
                            metrics: List[str] = None,
                            city_name: str = None) -> go.Figure:
    """
    Tạo biểu đồ đa chỉ số
    
    Args:
        df: DataFrame chứa dữ liệu
        metrics: List các chỉ số cần hiển thị
        city_name: Tên thành phố
        
    Returns:
        Plotly Figure
    """
    if metrics is None:
        metrics = ['temp_mean', 'precipitation', 'humidity']
    
    # Lọc metrics có trong DataFrame
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics or df.empty:
        return go.Figure()
    
    # Tạo subplot
    fig = make_subplots(
        rows=len(available_metrics),
        cols=1,
        shared_xaxes=True,
        subplot_titles=available_metrics,
        vertical_spacing=0.08
    )
    
    df = df.copy()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        x_data = df['date']
    else:
        x_data = range(len(df))
    
    # Thêm từng metric
    for i, metric in enumerate(available_metrics, 1):
        color = COLORS.get(metric.split('_')[0], '#1f77b4')
        
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=df[metric],
                mode='lines+markers',
                name=metric,
                line=dict(color=color),
                marker=dict(size=4)
            ),
            row=i, col=1
        )
    
    title = f"Đa chỉ số thời tiết - {city_name}" if city_name else "Đa chỉ số thời tiết"
    fig.update_layout(
        title=title,
        height=150 * len(available_metrics) + 100,
        template='plotly_white',
        showlegend=False
    )
    
    return fig