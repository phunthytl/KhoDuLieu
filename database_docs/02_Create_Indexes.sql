-- =======================================================
-- SQL Data Warehouse Index Optimization Script
-- Chức năng: Tối ưu trực tiếp cho 4 chiều CUBE
-- Tác dụng: Cực kỳ giúp ích đẩy nhanh tốc độ Phân cấp
-- và Roll-Up khi Cube chạy theo cơ chế ROLAP/MOLAP.
-- =======================================================

USE DoanhThuBanHang;
GO

-- ==========================================
-- 1. INDEX CHO CHIỀU (DIMENSION TABLES)
-- Lợi ích: Tăng tốc cực đỉnh khi người dùng Drill-Down (khoan nhánh)
-- do Index giúp SQL engine gộp các bản ghi cùng cấp bậc tức thì.
-- ==========================================

-- Cấp bậc Dim_KhachHang: LoaiKhachHang > TenKhachHang
CREATE NONCLUSTERED INDEX NCIX_DimKhachHang_Levels 
ON Dim_KhachHang (LoaiKhachHang, TenKhachHang);
GO

-- Cấp bậc Dim_MatHang: MoTa > KichCo
CREATE NONCLUSTERED INDEX NCIX_DimMatHang_Levels 
ON Dim_MatHang (MoTa, KichCo);
GO

-- Cấp bậc Dim_VPDD: Bang > TenThanhPho
CREATE NONCLUSTERED INDEX NCIX_DimVPDD_Levels 
ON Dim_VPDD (Bang, TenThanhPho);
GO

-- Cấp bậc Dim_ThoiGian: Nam > Quy > Thang
CREATE NONCLUSTERED INDEX NCIX_DimThoiGian_Levels 
ON Dim_ThoiGian (Nam, Quy, Thang);
GO


-- ==========================================
-- 2. INDEX CHO SỰ KIỆN (FACT TABLE)
-- Lợi ích: Khi gom nhóm (Measure/TongTien) SSAS phải Join Fact với Dim.
-- Khóa ngoại có sẵn Index giúp hệ thống Join thẳng vào Subcube siêu tốc.
-- ==========================================

-- Theo tiêu chuẩn của DWH hiện đại, Fact table nên được bọc bởi Clustered Columnstore.
-- Đoạn mã dưới dùng thiết kế phổ thông phòng trường hợp server bản cũ:
IF NOT EXISTS (SELECT name FROM sys.indexes WHERE name = 'NCIX_Fact_FK_Optimization')
BEGIN
    CREATE NONCLUSTERED INDEX NCIX_Fact_FK_Optimization 
    ON Fact_BanHang (MaThanhPho, MaMatHang, MaKhachHang, MaThoiGian)
    INCLUDE (TongSoLuongHang, TongTien);
END
GO
