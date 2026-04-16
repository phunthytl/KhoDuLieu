# Data Dictionary - Siêu Dữ Liệu Nghiệp Vụ
**Kho Dữ Liệu:** DoanhThuBanHang

Tài liệu này cung cấp Metadata (Siêu dữ liệu) mô tả chi tiết danh mục cấu trúc các bảng và ý nghĩa nghiệp vụ của Khối OLAP.

## 1. Bảng Sự Kiện (Fact Table)
**Tên bảng:** `Fact_BanHang`
**Mô tả:** Bảng lưu trữ giao dịch trung tâm chứa các chỉ số đo lường (Measures) phân chia theo 4 góc nhìn đa chiều.

| Tên Cột | Kiểu Dữ Liệu | Khóa | Phân loại | Mô tả |
|---------|--------------|------|-----------|-------|
| `MaKhachHang` | INT | FK | Dimension Key | FK liên kết tới Dim_KhachHang |
| `MaMatHang` | INT | FK | Dimension Key | FK liên kết tới Dim_MatHang |
| `MaThanhPho` | INT | FK | Dimension Key | FK liên kết tới Dim_VPDD |
| `MaThoiGian` | INT | FK | Dimension Key | FK liên kết tới Dim_ThoiGian |
| `TongSoLuongHang` | INT | - | Measure | Tổng số lượng sản phẩm bán ra theo từng giao dịch |
| `TongTien` | DECIMAL | - | Measure | Tổng mức doanh thu bán hàng mang về (VNĐ) |

---

## 2. Các Bảng Chiều (Dimension Tables)

### 2.1 Chiều Nhóm Khách Hàng (Dim_KhachHang)
**Mô tả:** Chiều phân tích dữ liệu dựa vào phân loại và danh tính của người mua (Ví dụ: Du lịch, Bưu Điện).
* `MaKhachHang` (PK): Mã dịnh danh hệ thống.
* `LoaiKhachHang` (Attribute/Level 0): Kiểu đối tác khách hàng (Du Lich, Buu Dien).
* `TenKhachHang` (Attribute/Level 1): Tên riêng của từng cá nhân / tập thể mua.

### 2.2 Chiều Sản Phẩm (Dim_MatHang)
**Mô tả:** Chiều phân tích số liệu theo đặc tính của hiện vật được bán.
* `MaMatHang` (PK): Mã định danh mặt hàng.
* `MoTa` (Attribute/Level 0): Phân loại chủng loại / mô tả thuộc tính chính (Áo, Quần...).
* `KichCo` (Attribute/Level 1): Các size sản phẩm (M, L, XL...).

### 2.3 Chiều Vị Trí (Dim_VPDD)
**Mô tả:** Chiều phân chia giao dịch theo địa dư hành chính nhà kho / chi nhánh bán.
* `MaThanhPho` (PK): Mã định danh vị trí.
* `Bang` (Attribute/Level 0): Vùng miền (Bắc, Trung, Nam) hoặc tên Bang.
* `TenThanhPho` (Attribute/Level 1): Tên thành phố chứa chi nhánh.

### 2.4 Chiều Thời Gian (Dim_ThoiGian)
**Mô tả:** Cấu trúc phân cấp chuẩn của trục dọc thời gian sự kiện.
* `MaThoiGian` (PK): Khóa nguyên bản liên kết.
* `Nam` (Attribute/Level 0): Năm giao dịch.
* `Quy` (Attribute/Level 1): Quý trong năm.
* `Thang` (Attribute/Level 2): Tháng cụ thể của sự kiện.
