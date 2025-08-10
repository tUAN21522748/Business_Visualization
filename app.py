"""
Dashboard Phân tích Khí hậu & Thời tiết
Ứng dụng Streamlit để hiển thị và phân tích dữ liệu thời tiết
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Thêm src vào Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processing.api_client import OpenMeteoClient
from data_processing.data_handler import WeatherDataHandler
from utils.helpers import *
from utils.weather_analysis import WeatherAnalyzer
from utils.weather_reports import WeatherReportGenerator
from visualization.charts import *

# Cấu hình trang
st.set_page_config(
    page_title="Dashboard Thời tiết Việt Nam",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo clients
@st.cache_resource
def init_clients():
    """Khởi tạo các client và handler"""
    api_client = OpenMeteoClient()
    data_handler = WeatherDataHandler()
    weather_analyzer = WeatherAnalyzer()
    report_generator = WeatherReportGenerator()
    return api_client, data_handler, weather_analyzer, report_generator

# Khởi tạo session state
def init_session_state():
    """Khởi tạo session state"""
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = []
    if 'historical_data' not in st.session_state:
        st.session_state.historical_data = pd.DataFrame()
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = "Hà Nội"

def main():
    """Hàm chính của ứng dụng"""
    init_session_state()
    api_client, data_handler, weather_analyzer, report_generator = init_clients()
    
    # Header
    st.title("🌤️ Dashboard Thời tiết & Khí hậu Việt Nam")
    st.markdown("### Phân tích dữ liệu thời tiết theo thời gian thực")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        
        # Chọn chế độ
        mode = st.selectbox(
            "Chế độ hiển thị:",
            ["Thời tiết hiện tại", "Dự báo", "Dữ liệu lịch sử", "So sánh đa điểm"]
        )
        
        st.divider()
        
        # Chọn địa điểm
        location_method = st.radio(
            "Cách chọn địa điểm:",
            ["Thành phố có sẵn", "Tìm kiếm", "Tọa độ thủ công"]
        )
        
        # Xử lý input địa điểm
        city_coords = None
        city_name = None
        
        if location_method == "Thành phố có sẵn":
            default_cities = api_client.default_cities
            city_name = st.selectbox(
                "Chọn thành phố:",
                list(default_cities.keys()),
                index=list(default_cities.keys()).index(st.session_state.selected_city) 
                if st.session_state.selected_city in default_cities else 0
            )
            city_coords = default_cities[city_name]
            st.session_state.selected_city = city_name
            
        elif location_method == "Tìm kiếm":
            search_query = st.text_input("Tìm kiếm địa điểm:", "")
            if search_query:
                with st.spinner("Đang tìm kiếm..."):
                    search_results = api_client.search_location(search_query)
                
                if search_results:
                    # Hiển thị kết quả tìm kiếm
                    options = []
                    for result in search_results[:5]:  # Giới hạn 5 kết quả đầu
                        name = result.get('name', 'Unknown')
                        country = result.get('country', '')
                        admin1 = result.get('admin1', '')
                        display_name = f"{name}"
                        if admin1:
                            display_name += f", {admin1}"
                        if country:
                            display_name += f", {country}"
                        options.append((display_name, result))
                    
                    if options:
                        selected_idx = st.selectbox(
                            "Chọn từ kết quả:",
                            range(len(options)),
                            format_func=lambda x: options[x][0]
                        )
                        selected_result = options[selected_idx][1]
                        city_name = selected_result['name']
                        city_coords = {
                            'lat': selected_result['latitude'],
                            'lon': selected_result['longitude']
                        }
                else:
                    st.warning("Không tìm thấy kết quả nào")
        
        else:  # Tọa độ thủ công
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude:", value=21.0278, format="%.4f")
            with col2:
                lon = st.number_input("Longitude:", value=105.8342, format="%.4f")
            
            if validate_coordinates(lat, lon):
                city_coords = {'lat': lat, 'lon': lon}
                city_name = f"Lat:{lat:.2f}, Lon:{lon:.2f}"
            else:
                st.error("Tọa độ không hợp lệ!")
        
        # Cấu hình thời gian cho dữ liệu lịch sử
        if mode == "Dữ liệu lịch sử":
            st.divider()
            st.subheader("⏰ Khoảng thời gian")
            
            date_range_options = get_date_range_options()
            selected_range = st.selectbox(
                "Chọn khoảng thời gian:",
                list(date_range_options.keys())
            )
            
            start_date, end_date = date_range_options[selected_range]
            
            # Tùy chọn thời gian tùy chỉnh
            if st.checkbox("Tùy chỉnh thời gian"):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Từ ngày:", start_date.date(), max_value=datetime.now().date())
                with col2:
                    end_date = st.date_input("Đến ngày:", end_date.date(), max_value=datetime.now().date())
                
                # Validation
                if start_date > end_date:
                    st.error("❌ Ngày bắt đầu phải nhỏ hơn ngày kết thúc!")
                elif end_date > datetime.now().date():
                    st.error("❌ Ngày kết thúc không thể trong tương lai!")
                elif (end_date - start_date).days > 365:
                    st.warning("⚠️ Khoảng thời gian quá dài, có thể mất nhiều thời gian để tải dữ liệu!")
        
        # Nút refresh dữ liệu
        st.divider()
        if st.button("🔄 Làm mới dữ liệu", type="primary"):
            # Clear cache
            st.cache_data.clear()
            st.rerun()
    
    # Main content
    if not city_coords or not city_name:
        st.info("👆 Vui lòng chọn địa điểm từ sidebar để xem dữ liệu thời tiết")
        return
    
    lat, lon = city_coords['lat'], city_coords['lon']
    
        # Hiển thị dữ liệu theo mode
    if mode == "Thời tiết hiện tại":
        show_current_weather(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name)
        
    elif mode == "Dự báo":
        show_forecast(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name)
        
    elif mode == "Dữ liệu lịch sử":
        show_historical_data(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name, 
                           start_date, end_date)
        
    elif mode == "So sánh đa điểm":
        show_multi_city_comparison(api_client, data_handler, weather_analyzer, report_generator)

def show_current_weather(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name):
    """Hiển thị thời tiết hiện tại"""
    st.header(f"🌡️ Thời tiết hiện tại - {city_name}")
    
    with st.spinner("Đang tải dữ liệu thời tiết hiện tại..."):
        current_data = api_client.get_current_weather(lat, lon, city_name)
    
    if not current_data:
        st.error("Không thể lấy dữ liệu thời tiết hiện tại")
        return
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = current_data.get('temperature', 'N/A')
        st.metric("🌡️ Nhiệt độ", format_temperature(temp) if temp != 'N/A' else 'N/A')
    
    with col2:
        humidity = current_data.get('humidity', 'N/A')
        st.metric("💧 Độ ẩm", f"{humidity}%" if humidity != 'N/A' else 'N/A')
    
    with col3:
        precip = current_data.get('precipitation', 'N/A')
        st.metric("🌧️ Lượng mưa", format_precipitation(precip) if precip != 'N/A' else 'N/A')
    
    with col4:
        wind = current_data.get('wind_speed', 'N/A')
        st.metric("💨 Tốc độ gió", format_wind_speed(wind) if wind != 'N/A' else 'N/A')
    
    # Chi tiết thông tin
    st.subheader("📊 Thông tin chi tiết")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📍 Vị trí:** {city_name}  
        **🗓️ Thời gian:** {current_data.get('timestamp', 'N/A')}  
        **🧭 Hướng gió:** {get_wind_direction_text(current_data.get('wind_direction', 0))}  
        **🌀 Áp suất:** {current_data.get('pressure', 'N/A')} hPa
        """)
    
    with col2:
        # Mô tả thời tiết
        temp_val = current_data.get('temperature', 0)
        precip_val = current_data.get('precipitation', 0)
        wind_val = current_data.get('wind_speed', 0)
        
        if all(isinstance(x, (int, float)) for x in [temp_val, precip_val, wind_val]):
            description = get_weather_description(temp_val, precip_val, wind_val)
            st.success(f"🌤️ **Mô tả thời tiết:** {description}")
        
        # Bản đồ
        weather_map = create_weather_map([current_data])
        st.components.v1.html(weather_map._repr_html_(), height=300)
    
    # Weather Alerts dựa trên dữ liệu hiện tại
    temp_val = current_data.get('temperature')
    wind_val = current_data.get('wind_speed')
    
    alerts = []
    if isinstance(temp_val, (int, float)):
        if temp_val >= 38:
            alerts.append(("danger", "🔥 Cảnh báo nắng nóng cực đoan!", f"Nhiệt độ {temp_val}°C rất nguy hiểm"))
        elif temp_val >= 35:
            alerts.append(("warning", "🌡️ Cảnh báo nắng nóng", f"Nhiệt độ {temp_val}°C, cần chú ý"))
        elif temp_val <= 10:
            alerts.append(("info", "❄️ Thời tiết lạnh", f"Nhiệt độ {temp_val}°C, hãy giữ ấm"))
    
    if isinstance(wind_val, (int, float)) and wind_val >= 25:
        alerts.append(("warning", "💨 Cảnh báo gió mạnh", f"Tốc độ gió {wind_val}km/h"))
    
    if alerts:
        st.subheader("⚠️ Cảnh báo thời tiết")
        for alert_type, title, message in alerts:
            if alert_type == "danger":
                st.error(f"{title}\n{message}")
            elif alert_type == "warning":
                st.warning(f"{title}\n{message}")
            else:
                st.info(f"{title}\n{message}")

def show_forecast(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name):
    """Hiển thị dự báo thời tiết"""
    st.header(f"📅 Dự báo thời tiết - {city_name}")
    
    # Tùy chọn số ngày dự báo
    forecast_days = st.select_slider(
        "Số ngày dự báo:",
        options=[1, 3, 5, 7, 10, 14],
        value=7
    )
    
    with st.spinner(f"Đang tải dự báo {forecast_days} ngày..."):
        forecast_df = api_client.get_forecast(lat, lon, forecast_days, city_name)
    
    if forecast_df.empty:
        st.error("Không thể lấy dữ liệu dự báo")
        return
    
    # Hiển thị bảng dự báo
    st.subheader("📋 Bảng dự báo")
    
    # Format dữ liệu cho hiển thị - optimize performance
    display_df = forecast_df.copy()
    display_df['Ngày'] = display_df['date'].dt.strftime('%d/%m/%Y')
    display_df['Nhiệt độ cao nhất (°C)'] = display_df['temp_max'].round(1)
    display_df['Nhiệt độ thấp nhất (°C)'] = display_df['temp_min'].round(1)
    display_df['Lượng mưa (mm)'] = display_df['precipitation'].round(1)
    display_df['Gió (km/h)'] = display_df['wind_speed_max'].round(1)
    
    # Optimize table rendering
    table_cols = ['Ngày', 'Nhiệt độ cao nhất (°C)', 'Nhiệt độ thấp nhất (°C)', 
                  'Lượng mưa (mm)', 'Gió (km/h)']
    
    st.dataframe(
        display_df[table_cols],
        use_container_width=True,
        height=min(400, len(display_df) * 35 + 50),  # Dynamic height
        column_config={
            "Ngày": st.column_config.TextColumn("Ngày", width="medium"),
            "Nhiệt độ cao nhất (°C)": st.column_config.NumberColumn("Nhiệt độ cao nhất", format="%.1f°C"),
            "Nhiệt độ thấp nhất (°C)": st.column_config.NumberColumn("Nhiệt độ thấp nhất", format="%.1f°C"),
            "Lượng mưa (mm)": st.column_config.NumberColumn("Lượng mưa", format="%.1fmm"),
            "Gió (km/h)": st.column_config.NumberColumn("Gió", format="%.1fkm/h")
        }
    )
    
    # Biểu đồ dự báo
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌡️ Dự báo nhiệt độ")
        temp_chart = create_temperature_line_chart(forecast_df, city_name)
        st.plotly_chart(temp_chart, use_container_width=True)
    
    with col2:
        st.subheader("🌧️ Dự báo lượng mưa")
        precip_chart = create_precipitation_bar_chart(forecast_df, city_name)
        st.plotly_chart(precip_chart, use_container_width=True)
    
    # Weather Alerts cho dự báo
    st.subheader("⚠️ Cảnh báo trong dự báo")
    alerts = weather_analyzer.generate_weather_alerts(forecast_df)
    
    if alerts:
        for alert in alerts:
            if alert['type'] == 'danger':
                st.error(f"{alert['title']}: {alert['message']}")
            elif alert['type'] == 'warning':
                st.warning(f"{alert['title']}: {alert['message']}")
            else:
                st.info(f"{alert['title']}: {alert['message']}")
    else:
        st.success("✅ Không có cảnh báo thời tiết đặc biệt trong dự báo")

def show_historical_data(api_client, data_handler, weather_analyzer, report_generator, lat, lon, city_name, start_date, end_date):
    """Hiển thị dữ liệu lịch sử"""
    st.header(f"📈 Dữ liệu lịch sử - {city_name}")
    
    # Chuyển đổi date thành string
    start_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
    end_str = end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date)
    
    st.info(f"📅 Khoảng thời gian: {start_str} đến {end_str}")
    
    # Load từ cache hoặc tải mới
    cache_filename = f"historical_{city_name}_{start_str}_{end_str}".replace(" ", "_").replace(",", "")
    historical_df = data_handler.load_from_cache(cache_filename)
    
    if historical_df is None or st.button("🔄 Tải lại dữ liệu"):
        with st.spinner("Đang tải dữ liệu lịch sử..."):
            historical_df = api_client.get_historical_data(lat, lon, start_str, end_str, city_name)
            
            if not historical_df.empty:
                data_handler.save_to_cache(historical_df, cache_filename)
    
    if historical_df.empty:
        st.error("Không thể lấy dữ liệu lịch sử")
        return
    
    # Thống kê tổng quan
    st.subheader("📊 Thống kê tổng quan")
    stats = data_handler.calculate_statistics(historical_df)
    
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'temperature' in stats:
                temp_stats = stats['temperature']
                st.metric("🌡️ Nhiệt độ TB", f"{temp_stats['mean']:.1f}°C")
                st.metric("🔥 Nhiệt độ cao nhất", f"{temp_stats['max']:.1f}°C")
                st.metric("❄️ Nhiệt độ thấp nhất", f"{temp_stats['min']:.1f}°C")
        
        with col2:
            if 'precipitation' in stats:
                precip_stats = stats['precipitation']
                st.metric("🌧️ Tổng lượng mưa", f"{precip_stats['total']:.1f}mm")
                st.metric("☔ Số ngày mưa", f"{precip_stats['rainy_days']} ngày")
        
        with col3:
            if 'wind' in stats:
                wind_stats = stats['wind']
                st.metric("💨 Gió TB", f"{wind_stats['mean']:.1f}km/h")
                st.metric("🌪️ Gió mạnh nhất", f"{wind_stats['max']:.1f}km/h")
    
    # Phân tích nâng cao
    st.subheader("🧠 Phân tích thông minh")
    
    # Weather alerts
    alerts = weather_analyzer.generate_weather_alerts(historical_df)
    if alerts:
        st.subheader("⚠️ Cảnh báo và điểm bất thường")
        alert_cols = st.columns(len(alerts) if len(alerts) <= 3 else 3)
        for i, alert in enumerate(alerts[:3]):  # Hiển thị tối đa 3 alerts
            with alert_cols[i]:
                if alert['type'] == 'danger':
                    st.error(f"**{alert['title']}**\n\n{alert['message']}")
                elif alert['type'] == 'warning':
                    st.warning(f"**{alert['title']}**\n\n{alert['message']}")
                else:
                    st.info(f"**{alert['title']}**\n\n{alert['message']}")
    
    # Climate indices
    indices = weather_analyzer.calculate_climate_indices(historical_df)
    if indices:
        st.subheader("📊 Chỉ số khí hậu")
        
        if 'comfort_index' in indices:
            comfort = indices['comfort_index']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏠 Chỉ số thoải mái", f"{comfort['comfort_score']}/100", help="Dựa trên nhiệt độ và độ ẩm")
            with col2:
                st.metric("😊 Mức độ thoải mái", comfort['comfort_level'])
            with col3:
                st.metric("🌞 Ngày thoải mái", f"{comfort['comfortable_days']} ngày")
    
    # Weather patterns
    patterns = weather_analyzer.detect_weather_patterns(historical_df)
    if patterns:
        st.subheader("🔍 Phát hiện xu hướng")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'temperature_patterns' in patterns:
                temp_patterns = patterns['temperature_patterns']
                st.info(f"""
                **🌡️ Xu hướng nhiệt độ:**
                - Xu hướng: {temp_patterns['trend']}
                - Độ biến động: {temp_patterns['temperature_volatility']}
                - Ngày nắng nóng: {temp_patterns.get('heat_wave_days', 0)}
                """)
        
        with col2:
            if 'precipitation_patterns' in patterns:
                precip_patterns = patterns['precipitation_patterns']
                st.info(f"""
                **🌧️ Xu hướng mưa:**
                - Ngày khô hạn: {precip_patterns['dry_spell_days']}
                - Ngày mưa liên tục: {precip_patterns['wet_spell_days']}
                - Tính đều đặn: {precip_patterns['rain_consistency']}
                """)
    
    # AI Summary
    summary = weather_analyzer.generate_weather_summary(historical_df, city_name)
    if summary:
        st.subheader("🤖 Tóm tắt AI")
        st.markdown(f"💬 **{summary}**")
    
    # Biểu đồ phân tích
    st.subheader("📈 Biểu đồ phân tích")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Nhiệt độ", "Lượng mưa", "Tương quan", "Xu hướng", "So sánh theo mùa"])
    
    with tab1:
        temp_chart = create_temperature_line_chart(historical_df, city_name)
        st.plotly_chart(temp_chart, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            precip_daily = create_precipitation_bar_chart(historical_df, city_name, 'daily')
            st.plotly_chart(precip_daily, use_container_width=True)
        
        with col2:
            precip_monthly = create_precipitation_bar_chart(historical_df, city_name, 'monthly')
            st.plotly_chart(precip_monthly, use_container_width=True)
    
    with tab3:
        corr_chart = create_correlation_heatmap(historical_df)
        st.plotly_chart(corr_chart, use_container_width=True)
    
    with tab4:
        # Thêm biểu đồ multi-metric
        multi_chart = create_multi_metric_chart(historical_df, 
                                              ['temp_mean', 'precipitation'], 
                                              city_name)
        st.plotly_chart(multi_chart, use_container_width=True)
    
    with tab5:
        seasonal_chart = create_seasonal_comparison(historical_df, city_name)
        st.plotly_chart(seasonal_chart, use_container_width=True)
    
    # Xuất dữ liệu và báo cáo
    st.subheader("💾 Xuất dữ liệu & Báo cáo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Xuất CSV"):
            filename = f"weather_data_{city_name}_{start_str}_{end_str}.csv"
            filepath = data_handler.export_data(historical_df, filename, 'csv')
            if filepath:
                st.success(f"Đã xuất file: {filename}")
    
    with col2:
        if st.button("📊 Xuất Excel"):
            filename = f"weather_data_{city_name}_{start_str}_{end_str}.xlsx"
            filepath = data_handler.export_data(historical_df, filename, 'excel')
            if filepath:
                st.success(f"Đã xuất file: {filename}")
    
    with col3:
        if st.button("📝 Tạo báo cáo tuần"):
            report = report_generator.generate_report(historical_df, city_name, 'weekly')
            st.markdown("### 📋 Báo cáo tuần")
            st.markdown(report)
    
    with col4:
        if st.button("📈 Tạo báo cáo khí hậu"):
            report = report_generator.generate_report(historical_df, city_name, 'climate')
            st.markdown("### 🌍 Báo cáo khí hậu")
            st.markdown(report)

def show_multi_city_comparison(api_client, data_handler, weather_analyzer, report_generator):
    """So sánh đa điểm"""
    st.header("🏙️ So sánh thời tiết đa điểm")
    
    with st.spinner("Đang tải dữ liệu cho tất cả thành phố..."):
        multi_city_data = api_client.get_multiple_cities_current()
    
    if not multi_city_data:
        st.error("Không thể lấy dữ liệu thời tiết")
        return
    
    # Bảng so sánh
    st.subheader("📋 Bảng so sánh")
    
    comparison_df = pd.DataFrame(multi_city_data)
    
    if not comparison_df.empty:
        display_cols = ['city_name', 'temperature', 'humidity', 'precipitation', 'wind_speed']
        available_cols = [col for col in display_cols if col in comparison_df.columns]
        
        if available_cols:
            display_df = comparison_df[available_cols].copy()
            
            # Format dữ liệu
            if 'temperature' in display_df.columns:
                display_df['temperature'] = display_df['temperature'].round(1)
            if 'humidity' in display_df.columns:
                display_df['humidity'] = display_df['humidity'].round(1)
            if 'precipitation' in display_df.columns:
                display_df['precipitation'] = display_df['precipitation'].round(1)
            if 'wind_speed' in display_df.columns:
                display_df['wind_speed'] = display_df['wind_speed'].round(1)
            
            # Đổi tên cột
            column_names = {
                'city_name': 'Thành phố',
                'temperature': 'Nhiệt độ (°C)',
                'humidity': 'Độ ẩm (%)',
                'precipitation': 'Lượng mưa (mm)',
                'wind_speed': 'Gió (km/h)'
            }
            
            display_df = display_df.rename(columns=column_names)
            st.dataframe(display_df, use_container_width=True)
    
    # Bản đồ so sánh
    st.subheader("🗺️ Bản đồ thời tiết")
    weather_map = create_weather_map(multi_city_data, zoom=5)
    st.components.v1.html(weather_map._repr_html_(), height=500)
    
    # Biểu đồ so sánh
    if not comparison_df.empty and 'temperature' in comparison_df.columns:
        st.subheader("📊 Biểu đồ so sánh nhiệt độ")
        
        fig = px.bar(
            comparison_df,
            x='city_name',
            y='temperature',
            title="So sánh nhiệt độ các thành phố",
            color='temperature',
            color_continuous_scale='RdYlBu_r'
        )
        
        fig.update_layout(
            xaxis_title="Thành phố",
            yaxis_title="Nhiệt độ (°C)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
