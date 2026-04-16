# KhoDuLieu - 4D OLAP Pivot Analyzer

Dự án Kho Dữ Liệu (Data Warehouse) hoàn chỉnh bao gồm mã nguồn khởi tạo DWH giả lập, kết nối tới SQL Server Analysis Services (SSAS), và cung cấp một giao diện Web cho phép phân tích động đa chiều (Pivot 4D) mạnh mẽ.

## Tính Năng Nổi Bật
- **4D Pivot Dynamic Engine:** Khả năng tự do xây dựng bản phân tích với Trục X, Nhóm màu (Legend) và Đo lường (Measure) bất kỳ.
- **Slice & Dice / Khoan Sâu (Drill-down):** Tương tác Click trực tiếp trên biểu đồ phân tích để liên tục đào sâu vào các cấp bậc dữ liệu.
- **Tối Ưu Ngầm Định:** Tự động sinh truy vấn MDX siêu giới hạn bằng Cascading Subselects bảo vệ RAM máy chủ.
- **Tài liệu Academic:** Cung cấp đầy đủ Metadata và SQL Scripts chuẩn điểm đồ án ở trong thư mục `database_docs`.

## 1. Yêu Cầu Hệ Thống
* Microsoft SQL Server (có kèm công cụ SQL Server Management Studio).
* Microsoft SQL Server Analysis Services (SSAS) cài đặt chế độ Multidimensional.
* Python 3.9 trở lên.

## 2. Cài Đặt Khởi Tạo
Mở Terminal tại thư mục này và cài đặt các thư viện Python cần thiết:
```bash
pip install -r requirements.txt
```
*(Yêu cầu Windows OS vì thư viện kết nối `pywin32` và `adodbapi` phụ thuộc vào ADO/OLE DB Provider của Microsoft).*

## 3. Tạo Dữ Liệu Demo (ETL & DWH)
Nếu bạn chưa có CSDL `DoanhThuBanHang` trong SQL Server, bạn có thể khởi chạy mã giả lập:
```bash
python create_data.py
```
*Script này sẽ vào SQL Server thông qua Windows Authentication, tự cài các bảng Dimension và Fact, rồi sinh dữ liệu giả ngẫu nhiên.*
> **Sau khi có dữ liệu:** Đừng quên mở ứng dụng Visual Studio Data Tools (SSDT) để Deploy 1 Cube mới lấy tên là `DoanhThuBanHang`.

## 4. Chạy Ứng Dụng Dashboard Phân Tích
```bash
python app.py
```
Truy cập vào [http://localhost:5000](http://localhost:5000) trên trình duyệt để sử dụng.

---

## Tham Khảo Cấu Trúc
* `app.py`: Điều hướng Flask Router REST API.
* `cube_service.py`: Cầu nối Backend qua Windows ADO Connection để giao tiếp với Analysis Services MDX Engine.
* `mdx_builder.py`: Trái tim sinh truy vấn MDX động với logic Cascading Subselects tiên tiến.
* `/templates/dashboard.html`: Toàn bộ logic giao diện Pivot, UI Cắt lớp đa chiều và vẽ biểu đồ Plotly.
* `/database_docs`: Thư mục lưu trữ Siêu dữ liệu (Metadata) và file SQL tối ưu hóa Cube theo chuẩn Kho dữ liệu Đại Học.
