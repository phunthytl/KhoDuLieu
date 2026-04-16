-- =======================================================
-- System Metadata (ETL Log)
-- Chức năng: Lưu trữ toàn bộ nhật ký khi đổ mới (hoặc update)
-- từ kho Database chính diện vào Data Warehouse này. 
-- Đáp ứng yêu cầu: "Tạo Metadata quản lý Hệ Thống"
-- =======================================================

USE DoanhThuBanHang; -- Thay đổi tên DB gốc theo ngữ cảnh
GO

IF OBJECT_ID('dbo.Log_ETL_Metadata', 'U') IS NOT NULL
	DROP TABLE dbo.Log_ETL_Metadata;
GO

CREATE TABLE dbo.Log_ETL_Metadata (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    TableName NVARCHAR(100) NOT NULL, -- Tên Bảng (Ex: Fact_BanHang, Dim_ViTri)
    ActionType NVARCHAR(50) NOT NULL, -- Insert, Update, Full Load
    RowsAffected INT NOT NULL,        -- Số lượng bản ghi được tác động
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NULL,
    Status NVARCHAR(50) DEFAULT 'Running', -- Success, Failed...
    ErrorMessage NVARCHAR(MAX) NULL,
    ExecutedBy NVARCHAR(100) DEFAULT SUSER_SNAME()
);
GO

-- Example: Cách ghi log Siêu Dữ Liệu 
-- INSERT INTO dbo.Log_ETL_Metadata (TableName, ActionType, RowsAffected, StartTime, Status)
-- VALUES ('Fact_BanHang', 'Full Load', 99999, GETDATE(), 'Success');
