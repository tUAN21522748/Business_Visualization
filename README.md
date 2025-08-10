# 🌦️ Dashboard Phân tích Thời tiết & Khí hậu Việt Nam (Beginner-Friendly)

Chào mừng bạn đến với dự án Dashboard Phân tích Thời tiết! Đây là một ứng dụng web được xây dựng bằng Python và Streamlit, cho phép bạn xem, phân tích và tương tác với dữ liệu thời tiết một cách trực quan.

Tài liệu này sẽ hướng dẫn bạn từ A → Z: cách cài đặt, cách hệ thống hoạt động, và giải thích chi tiết từng phần của mã nguồn.

---

## 🎯 Mục tiêu của dự án

- **Tra cứu thời tiết:** Xem thông tin thời tiết hiện tại, dự báo cho các thành phố ở Việt Nam.
- **Phân tích lịch sử:** Phân tích dữ liệu thời tiết trong quá khứ để tìm ra xu hướng, các điểm bất thường.
- **Trực quan hóa:** Hiển thị dữ liệu qua các biểu đồ (nhiệt độ, mưa, gió) và bản đồ tương tác.
- **Phân tích thông minh:** Tự động tạo cảnh báo (nắng nóng, mưa to) và các chỉ số khí hậu.
- **Tạo báo cáo:** Tự động tạo ra các báo cáo thời tiết hàng tuần, hàng tháng.

---

## 🚀 Hướng dẫn cài đặt và chạy ứng dụng

Để chạy được dự án này trên máy tính của bạn, hãy làm theo các bước sau.

### Bước 1: Chuẩn bị môi trường

Bạn cần có Python trên máy. Sau đó, hãy tạo một "môi trường ảo" (virtual environment). Đây là một không gian riêng biệt để cài đặt các thư viện cho dự án này mà không ảnh hưởng đến các dự án khác.

Mở terminal (dòng lệnh) và chạy các lệnh sau:

```bash
# Tạo môi trường ảo tên là .venv
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows:
.venv\Scripts\activate
# Trên macOS/Linux:
source .venv/bin/activate
```

Sau khi chạy lệnh kích hoạt, bạn sẽ thấy `(.venv)` ở đầu dòng lệnh, báo hiệu bạn đang ở trong môi trường ảo.

### Bước 2: Cài đặt các thư viện cần thiết

Dự án này cần một số thư viện của Python để hoạt động. Danh sách các thư viện này nằm trong file `requirements.txt`.

Chạy lệnh sau để cài đặt tất cả chúng cùng một lúc:

```bash
pip install -r requirements.txt
```

### Bước 3: Chạy ứng dụng!

Sau khi cài đặt xong, bạn có thể khởi động ứng dụng bằng lệnh:

```bash
streamlit run app.py
```

Một trang web sẽ tự động mở ra trong trình duyệt của bạn với địa chỉ `http://localhost:8501`. Đó chính là dashboard của chúng ta!

---

## ⚙️ Hệ thống hoạt động như thế nào?

Hãy tưởng tượng ứng dụng của chúng ta là một nhà hàng. Dưới đây là quy trình hoạt động từ khi bạn "order" (tương tác) cho đến khi "món ăn" (dữ liệu) được phục vụ.

1.  **Giao diện (Frontend - `app.py`)**: Đây là "nhân viên phục vụ" của nhà hàng. Khi bạn chọn một thành phố hay một khoảng thời gian trên giao diện, `app.py` sẽ nhận yêu cầu này.

2.  **Gọi API (API Client - `api_client.py`)**: `app.py` sẽ chuyển yêu cầu của bạn cho `api_client.py`. Anh chàng này giống như "người đi chợ", sẽ chạy ra ngoài (internet) để đến "siêu thị dữ liệu" **Open-Meteo** để lấy về những thông tin thời tiết mà bạn cần.

3.  **Xử lý dữ liệu (Data Handler - `data_handler.py`)**: Dữ liệu lấy về từ Open-Meteo còn khá "thô". `data_handler.py` đóng vai trò là "đầu bếp", sẽ làm sạch, sắp xếp dữ liệu này thành các bảng (DataFrame) gọn gàng, dễ sử dụng. Anh ta cũng rất thông minh, sẽ cất những dữ liệu đã xử lý vào "kho" (`/data` folder) để lần sau bạn hỏi lại thì lấy ra cho nhanh, không cần đi chợ lại.

4.  **Phân tích chuyên sâu (Analysis & Reports - `weather_analysis.py`, `weather_reports.py`)**:

    - `weather_analysis.py`: Đây là "chuyên gia dinh dưỡng". Sau khi có dữ liệu sạch, anh ta sẽ phân tích sâu hơn để tìm ra các thông tin hữu ích như: "Cảnh báo hôm nay có nắng nóng!", "Xu hướng nhiệt độ tuần này đang tăng",...
    - `weather_reports.py`: Đây là "thư ký". Anh ta sẽ tổng hợp tất cả phân tích và viết thành các báo cáo thời tiết hoàn chỉnh.

5.  **Vẽ biểu đồ (Visualization - `charts.py`)**: Đây là "nghệ sĩ trang trí món ăn". Anh ta sẽ dùng dữ liệu đã được xử lý để vẽ ra các biểu đồ, bản đồ đẹp mắt, giúp bạn dễ dàng "thưởng thức" thông tin.

6.  **Hiển thị kết quả (Display)**: Cuối cùng, `app.py` sẽ nhận lại tất cả biểu đồ, phân tích, báo cáo và trình bày chúng một cách đẹp đẽ trên giao diện web cho bạn xem.

Sơ đồ luồng dữ liệu:

```
[Bạn] -> [Giao diện app.py] -> [API Client] -> [Internet (Open-Meteo)]
                                     ^
                                     |
[Biểu đồ & Phân tích] <- [Charts & Analysis] <- [Data Handler] <- [Dữ liệu thô]
```

---

## 📁 Giải thích cấu trúc thư mục và mã nguồn

Dưới đây là ý nghĩa của từng file và thư mục trong dự án.

- `app.py`:

  - **Vai trò**: File chính, "bộ não" của toàn bộ ứng dụng.
  - **Nhiệm vụ**:
    - Tạo ra tất cả các thành phần giao diện mà bạn thấy trên web (thanh sidebar, nút bấm, các tab,...).
    - Điều phối hoạt động của các file khác: gọi `api_client` lấy dữ liệu, dùng `data_handler` xử lý, dùng `charts` vẽ biểu đồ, rồi hiển thị tất cả lên màn hình.

- `src/data_processing/api_client.py`:

  - **Vai trò**: Người giao tiếp với API bên ngoài.
  - **Nhiệm vụ**: Chứa class `OpenMeteoClient` với các hàm để gửi yêu cầu đến API của Open-Meteo và nhận dữ liệu thời tiết trả về. Ví dụ: `get_current_weather()`, `get_forecast()`.

- `src/data_processing/data_handler.py`:

  - **Vai trò**: Người xử lý và dọn dẹp dữ liệu.
  - **Nhiệm vụ**:
    - Nhận dữ liệu thô từ `api_client`.
    - Sử dụng thư viện `pandas` để chuyển dữ liệu thành dạng bảng (DataFrame) cho dễ thao tác.
    - Lưu và tải dữ liệu từ cache (thư mục `/data`) để tăng tốc độ cho những lần truy cập sau.
    - Tính toán các chỉ số thống kê cơ bản.

- `src/utils/helpers.py`:

  - **Vai trò**: Hộp công cụ chứa các hàm nhỏ lẻ, tiện ích.
  - **Nhiệm vụ**: Chứa các hàm nhỏ được sử dụng ở nhiều nơi. Ví dụ: hàm để format nhiệt độ (thêm `°C`), hàm đổi hướng gió từ độ sang chữ (Bắc, Nam, Đông, Tây),...

- `src/utils/weather_analysis.py`:

  - **Vai trò**: Nhà phân tích dữ liệu thông minh.
  - **Nhiệm vụ**: Chứa class `WeatherAnalyzer` với các hàm phân tích nâng cao như:
    - `generate_weather_alerts()`: Tìm kiếm các điều kiện thời tiết nguy hiểm (nắng nóng, mưa to, gió mạnh).
    - `calculate_climate_indices()`: Tính các chỉ số phức tạp hơn như "chỉ số thoải mái".
    - `generate_weather_summary()`: Tự động viết ra một đoạn văn tóm tắt tình hình thời tiết.

- `src/utils/weather_reports.py`:

  - **Vai trò**: Người viết báo cáo.
  - **Nhiệm vụ**: Chứa class `WeatherReportGenerator` để tạo ra các báo cáo thời tiết hoàn chỉnh (dạng Markdown) hàng tuần, hàng tháng hoặc báo cáo khí hậu dài hạn.

- `src/visualization/charts.py`:

  - **Vai trò**: Họa sĩ.
  - **Nhiệm vụ**: Chứa các hàm sử dụng thư viện `Plotly` và `Folium` để vẽ tất cả các biểu đồ và bản đồ bạn thấy trên ứng dụng. Mỗi hàm tương ứng với một loại biểu đồ (ví dụ: `create_temperature_line_chart`).

- `data/`:

  - **Vai trò**: Kho chứa.
  - **Nhiệm vụ**: Thư mục này dùng để lưu các file dữ liệu đã được tải về và xử lý. Điều này giúp ứng dụng chạy nhanh hơn vì không phải tải lại dữ liệu từ internet mỗi lần bạn làm mới trang.

- `requirements.txt`:

  - **Vai trò**: Danh sách mua sắm.
  - **Nhiệm vụ**: Liệt kê tất cả các thư viện Python mà dự án cần. Lệnh `pip install -r requirements.txt` sẽ đọc file này và tự động cài đặt chúng.

- `.gitignore`:
  - **Vai trò**: Danh sách những thứ "riêng tư".
  - **Nhiệm vụ**: Cho Git biết những file/thư mục nào không nên được đưa lên repository công khai (như môi trường ảo `.venv`, thư mục `data`,...).

---

## 💡 Hướng dẫn tùy chỉnh và mở rộng

- **Thêm một thành phố mặc định?**

  - Mở file `src/data_processing/api_client.py`.
  - Tìm biến `self.default_cities`.
  - Thêm một dòng mới với tên thành phố và tọa độ của nó.

- **Thay đổi màu sắc của biểu đồ?**

  - Mở file `src/visualization/charts.py`.
  - Tìm dictionary `COLORS` ở đầu file.
  - Thay đổi mã màu (ví dụ: `temperature` từ `'#ff6b6b'` sang một màu khác).

- **Thay đổi ngưỡng cảnh báo thời tiết?**
  - Mở file `src/utils/weather_analysis.py`.
  - Tìm dictionary `self.alert_thresholds` trong class `WeatherAnalyzer`.
  - Chỉnh sửa các giá trị ngưỡng (ví dụ: `high_heat` từ `35` xuống `34`).

Chúc bạn có những trải nghiệm thú vị khi khám phá và phát triển dự án này!
