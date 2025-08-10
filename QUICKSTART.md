# 🚀 Hướng dẫn chạy nhanh Dashboard Thời tiết

## 1. Cài đặt Dependencies

```bash
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

## 2. Chạy ứng dụng

```bash
# Chạy Streamlit app
streamlit run app.py
```

Ứng dụng sẽ mở trong trình duyệt tại địa chỉ: http://localhost:8501

## 3. Cách sử dụng

### 3.1 Thời tiết hiện tại

- Chọn "Thời tiết hiện tại" từ sidebar
- Chọn thành phố hoặc nhập tọa độ
- Xem thông tin thời tiết realtime

### 3.2 Dự báo thời tiết

- Chọn "Dự báo" từ sidebar
- Chọn số ngày dự báo (1-14 ngày)
- Xem biểu đồ và bảng dự báo

### 3.3 Dữ liệu lịch sử

- Chọn "Dữ liệu lịch sử" từ sidebar
- Chọn khoảng thời gian
- Xem phân tích thống kê và biểu đồ xu hướng
- Xuất dữ liệu CSV/Excel

### 3.4 So sánh đa điểm

- Chọn "So sánh đa điểm" từ sidebar
- Xem thời tiết của tất cả thành phố chính
- So sánh qua bản đồ và biểu đồ

## 4. Tính năng chính

✅ **Thời tiết hiện tại**: Nhiệt độ, độ ẩm, lượng mưa, gió  
✅ **Dự báo**: 1-14 ngày tới  
✅ **Lịch sử**: Dữ liệu các năm trước  
✅ **Bản đồ**: Hiển thị trực quan trên map  
✅ **Biểu đồ**: Line chart, bar chart, heatmap  
✅ **Xuất dữ liệu**: CSV, Excel  
✅ **Cache**: Lưu trữ tự động để tiết kiệm API calls

## 5. Cấu trúc dữ liệu

```
data/
├── historical_*.csv          # Dữ liệu lịch sử cache
├── weather_data_*.csv        # Dữ liệu xuất
└── weather_data_*.xlsx       # Dữ liệu xuất Excel
```

## 6. Troubleshooting

### Lỗi "ModuleNotFoundError"

````bash
# Đảm bảo đã cài đặt đủ dependencies
pip install -r requirements.txt
### Lỗi API timeout

- Kiểm tra kết nối internet
- Thử lại sau vài phút
- Open-Meteo có thể bị giới hạn requests

### Lỗi hiển thị map

- Đảm bảo có folium trong requirements.txt
- Restart ứng dụng

## 7. API được sử dụng

- **Open-Meteo**: Weather API chính (FREE, no API key)
- **Open-Meteo Geocoding**: Tìm kiếm địa điểm

## 8. Giới hạn

- Open-Meteo có rate limit (~10000 requests/day)
- Dữ liệu lịch sử: từ 1940 đến hiện tại
- Dự báo: tối đa 16 ngày

## 9. Mở rộng

Để thêm API khác (OpenWeatherMap, Visual Crossing):

1. Tạo file `.env`:

```env
OPENWEATHERMAP_API_KEY=your_key_here
VISUALCROSSING_API_KEY=your_key_here
```

2. Sửa đổi `api_client.py` để thêm client mới

## 10. Deploy

### Streamlit Cloud

1. Push code lên GitHub
2. Kết nối với streamlit.io
3. Deploy tự động

### Docker (tùy chọn)

```bash
# Build image
docker build -t weather-dashboard .

# Run container
docker run -p 8501:8501 weather-dashboard
```

---

🎉 **Chúc bạn sử dụng thành công!**
````
