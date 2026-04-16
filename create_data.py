import pandas as pd
import numpy as np
import sqlalchemy as sa
import urllib
import random

# 1. KẾT NỐI
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=NGP\\KHODULIEU;"
    "DATABASE=DW;"
    "Trusted_Connection=yes;"
)
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

@sa.event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if executemany:
        cursor.fast_executemany = True

print("Đang sinh dữ liệu Dimension ...")

# 2. SINH DỮ LIỆU DIMENSION
data_mien = {
    'Bac': ['Ha Noi', 'Hai Phong', 'Bac Ninh', 'Hung Yen', 'Quang Ninh', 'Lang Son', 'Lao Cai', 'Lai Chau', 
            'Dien Bien', 'Son La', 'Cao Bang', 'Tuyen Quang', 'Thai Nguyen', 'Phu Tho', 'Ninh Binh'],
    'Trung': ['Thanh Hoa', 'Nghe An', 'Ha Tinh', 'Thua Thien Hue', 'Quang Tri', 'Da Nang', 
              'Quang Ngai', 'Khanh Hoa', 'Gia Lai', 'Lam Dong', 'Dak Lak'],
    'Nam': ['TP Ho Chi Minh', 'Dong Nai', 'Tay Ninh', 'Vinh Long', 'Dong Thap', 'Ca Mau', 'An Giang', 'Can Tho']
}

vpdd_list = []
id_tp = 1
for mien, tinh_thanh in data_mien.items():
    for tp in tinh_thanh:
        vpdd_list.append({'MaThanhPho': f'TP{id_tp:03}', 
                          'TenThanhPho': tp, 
                          'Bang': mien})
        id_tp += 1
df_vpdd = pd.DataFrame(vpdd_list)

# Dim_KhachHang
ho = ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Phan', 'Vu', 'Dang', 'Bui', 'Do']
ten_dem = ['Van', 'Thi', 'Duc', 'Ngoc', 'Huu', 'Minh', 'Quoc', 'Thanh']
ten = ['Anh', 'Binh', 'Chau', 'Dung', 'Giang', 'Hanh', 'Khanh', 'Linh', 'Nam', 'Phuong', 'Trang']

def random_name():
    return f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"

df_khachhang = pd.DataFrame({
    'MaKhachHang': [f'KH{i:04}' for i in range(1, 2001)],
    'TenKhachHang': [random_name() for _ in range(2000)],
    'LoaiKhachHang': [random.choice(['Buu Dien', 'Du Lich']) for _ in range(2000)]
})

# Dim_MatHang
product_names = [
    "Ao Thun Tron","Ao Thun In Hinh","Ao Thun Basic","Ao Thun Oversize","Ao Thun Co Tron",
    "Ao Polo Classic","Ao Polo The Thao","Ao Polo Cao Cap",
    "Ao So Mi Trang","Ao So Mi Den","Ao So Mi Ke Soc","Ao So Mi Tay Dai","Ao So Mi Tay Ngan",
    "Ao So Mi Slim Fit","Ao So Mi Form Rong",
    "Ao Khoac Jean","Ao Khoac Gio","Ao Khoac Bomber","Ao Khoac Hoodie","Ao Khoac The Thao",
    "Ao Khoac Ni","Ao Len Mong","Ao Len Day","Ao Len Co Lo","Ao Len Co Tim",
    "Ao Tank Top","Ao Ba Lo","Ao The Thao Ngan Tay","Ao The Thao Dai Tay","Ao Croptop",
    "Quan Jean Skinny","Quan Jean Slim Fit","Quan Jean Regular","Quan Jean Ong Rong","Quan Jean Rach",
    "Quan Jean Den","Quan Jean Xanh",
    "Quan Tay Cong So","Quan Tay Slim Fit","Quan Tay Ong Dung","Quan Tay Mau Den","Quan Tay Mau Xam",
    "Quan Kaki Dai","Quan Kaki Ngan","Quan Kaki Mau Be",
    "Quan Short Jean","Quan Short Kaki","Quan Short The Thao","Quan Short Lung","Quan Short Nam",
    "Vay Cong So","Vay Maxi","Vay Ngan","Vay Body","Vay Xoe","Vay Hoa","Vay Du Tiec","Vay Tay Dai",
    "Vay Tay Ngan","Vay Co Vuong",
    "Bo The Thao Nam","Bo The Thao Nu","Bo Do Mac Nha","Bo Do Thu Dong","Bo Do He",
    "Ao Vest Nam","Ao Vest Nu","Ao Blazer","Ao Mang To","Ao Da",
    "Quan Jogger","Quan Legging","Quan The Thao Dai","Quan The Thao Ngan","Quan Ong Rong",
    "Dam Maxi","Dam Body","Dam Cong So","Dam Du Tiec","Dam Hoa",
    "Ao So Mi Denim","Ao So Mi Lua","Ao So Mi Cotton","Ao Polo Ke Soc","Ao Polo Tron",
    "Quan Jean Wax","Quan Jean Baggy","Quan Jean Lung","Quan Tay Lung","Quan Kaki Slim Fit",
    "Ao Hoodie Zip","Ao Hoodie Khong Mu","Ao Khoac Dai","Ao Khoac Ngan","Ao Khoac Co Long"
]

sizes = ['S', 'M', 'L', 'XL', 'XXL']
mathang_list = []
id_mh = 1

for name in product_names:
    for size in sizes:
        mathang_list.append({
            'MaMatHang': f'MH{id_mh:04}',
            'MoTa': name,
            'KichCo': size
        })
        id_mh += 1

df_mathang = pd.DataFrame(mathang_list)

# Dim_ThoiGian
dates = pd.date_range(start='2022-01-01', end='2026-03-01', freq='MS')

df_thoigian = pd.DataFrame({
    'MaThoiGian': dates.strftime('%Y%m'),
    'Thang': dates.month,
    'Quy': (dates.month - 1)//3 + 1,
    'Nam': dates.year
})

# --- 3. SINH DỮ LIỆU FACT_BANHANG ---
print("🚀 Sinh Fact_BanHang...")

num_records = 1200000

# GÁN THÀNH PHỐ CHO KHÁCH
df_khachhang['MaThanhPho'] = np.random.choice(
    df_vpdd['MaThanhPho'].values,
    len(df_khachhang)
)

# CHỌN KHÁCH
df_fact = pd.DataFrame({
    'MaKhachHang': np.random.choice(
        df_khachhang['MaKhachHang'].values,
        num_records
    )
})

# MAP THÀNH PHỐ THEO KHÁCH
df_fact = df_fact.merge(
    df_khachhang[['MaKhachHang', 'MaThanhPho']],
    on='MaKhachHang',
    how='left'
)

# THÊM 10% KHÁCH HÀNG MUA Ở THÀNH PHỐ KHÁC
mask = np.random.rand(num_records) < 0.1
df_fact.loc[mask, 'MaThanhPho'] = np.random.choice(
    df_vpdd['MaThanhPho'].values,
    mask.sum()
)

# RANDOM CÁC DIM KHÁC
df_fact['MaMatHang'] = np.random.choice(
    df_mathang['MaMatHang'].values,
    num_records
)

df_fact['MaThoiGian'] = np.random.choice(
    df_thoigian['MaThoiGian'].values,
    num_records
)

# SỐ LƯỢNG
df_fact['TongSoLuongHang'] = np.random.choice(
    [1,2,3,5,10],
    size=num_records,
    p=[0.4,0.3,0.2,0.08,0.02]
)

# MAP GIÁ
def get_price_range(mota):
    if 'Ao Thun' in mota:
        return (80000, 200000)
    elif 'Ao So Mi' in mota:
        return (150000, 400000)
    elif 'Quan Jean' in mota:
        return (300000, 800000)
    elif 'Quan Tay' in mota or 'Kaki' in mota:
        return (250000, 600000)
    elif 'Ao Khoac' in mota or 'Hoodie' in mota:
        return (400000, 1000000)
    elif 'Vay' in mota or 'Dam' in mota:
        return (250000, 900000)
    else:
        return (100000, 300000)

price_map = {}
for _, row in df_mathang.iterrows():
    min_p, max_p = get_price_range(row['MoTa'])
    price_map[row['MaMatHang']] = random.randint(min_p, max_p)

df_fact['DonGia'] = df_fact['MaMatHang'].map(price_map)

# TÍNH TIỀN
df_fact['TongTien'] = df_fact['DonGia'] * df_fact['TongSoLuongHang']

# DROP DUPLICATE + LẤY 1 TRIỆU BẢN GHI
df_fact = df_fact.drop_duplicates(
    subset=['MaKhachHang','MaMatHang','MaThanhPho','MaThoiGian']
)

df_fact = df_fact.sample(
    min(1000000, len(df_fact))
)

# 4. NẠP DỮ LIỆU VÀO SQL SERVER
try:
    print("--- Đang dọn dẹp dữ liệu cũ để tránh lỗi PK ---")
    with engine.connect() as connection:
        connection.execute(sa.text("DELETE FROM Fact_BanHang"))
        connection.execute(sa.text("DELETE FROM Dim_VPDD"))
        connection.execute(sa.text("DELETE FROM Dim_KhachHang"))
        connection.execute(sa.text("DELETE FROM Dim_MatHang"))
        connection.execute(sa.text("DELETE FROM Dim_ThoiGian"))
        connection.commit()
    
    print("Đang nạp lại các bảng Dimension...")
    df_vpdd.to_sql('Dim_VPDD', engine, if_exists='append', index=False)
    df_khachhang.drop(columns=['MaThanhPho']).to_sql(
        'Dim_KhachHang',
        engine,
        if_exists='append',
        index=False
    )
    df_mathang.to_sql('Dim_MatHang', engine, if_exists='append', index=False)
    df_thoigian.to_sql('Dim_ThoiGian', engine, if_exists='append', index=False)
    
    print(f"Đang nạp {len(df_fact)} dòng vào Fact_BanHang...")
    df_fact.drop(columns=['DonGia']).to_sql(
        'Fact_BanHang',
        engine,
        if_exists='append',
        index=False,
        chunksize=10000
    )
    
    print("Hoàn thành! Dữ liệu mới đã được nạp.")
except Exception as e:
    print(f"Lỗi: {e}")