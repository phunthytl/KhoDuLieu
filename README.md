# Bài tập lớn Kho dữ liệu

# 1. Cài Đặt Khởi Tạo
Cài đặt các thư viện Python cần thiết:
```bash
pip install -r requirements.txt
```
*(Yêu cầu Windows OS vì thư viện kết nối `pywin32` và `adodbapi` phụ thuộc vào ADO/OLE DB Provider của Microsoft).*

# 2. Tạo Dữ Liệu Demo
Tạo CSDL với các bảng Dim, Fact
Sửa server và database rồi chạy:
```bash
python create_data.py
```
để sinh dữ liệu

# 3. Tạo cube và dimension
Sử dụng Visual Studio để cài đặt khối `DoanhThuBanHang` và 4 bảng Dimensions tương ứng.
Sau khi cài đặt xong Deploy lên SQL server

## 4. Chạy Ứng Dụng Dashboard Phân Tích
```bash
python app.py
```
Truy cập vào [http://localhost:5000](http://localhost:5000) trên trình duyệt để sử dụng.

---

## Cấu Trúc
* `app.py`: Điều hướng Flask Router REST API.
* `cube_service.py`: Cầu nối Backend qua Windows ADO Connection để giao tiếp với Analysis Services MDX Engine.
* `mdx_builder.py`: Trái tim sinh truy vấn MDX động với logic Cascading Subselects tiên tiến.
* `/templates/dashboard.html`: Toàn bộ logic giao diện Pivot, UI Cắt lớp đa chiều và vẽ biểu đồ Plotly.
* `/database_docs`: Thư mục lưu trữ Siêu dữ liệu (Metadata) và file SQL tối ưu hóa Cube
