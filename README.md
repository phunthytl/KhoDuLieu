# Bài tập lớn Kho dữ liệu

# 1. Cài Đặt Khởi Tạo
Cài đặt các thư viện Python cần thiết:
```bash
pip install -r requirements.txt
```

# 2. SSAS
Cài đặt SSAS:
    Data Source=localhost\\KDL;
    Initial Catalog=DW;
Kết nối tới SSAS máy đang có dữ liệu hoặc restore file abf ()

## 3. Chạy web
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
