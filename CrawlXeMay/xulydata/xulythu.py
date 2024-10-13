import pymongo  # Thư viện để kết nối và tương tác với MongoDB
import pandas as pd  # Thư viện để xử lý dữ liệu
from sqlalchemy import create_engine, text  # Thư viện giúp kết nối và tương tác với cơ sở dữ liệu SQL
import psycopg2  # Thư viện để kết nối PostgreSQL

# Bước 1: Kết nối tới MongoDB
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/') #Tạo một kết nối đến MongoDB đang chạy trên localhost và cổng 27017.
mongo_db = mongo_client['dbmycrawler']  # Tên cơ sở dữ liệu
collection = mongo_db['tbXemay']  # Tên collection

# Bước 2: Lấy dữ liệu từ MongoDB
data = list(collection.find({}))  # Lấy tất cả dữ liệu trong collection

# Bước 3: Chuyển đổi dữ liệu sang DataFrame của Pandas
df = pd.DataFrame(data)

# Bước 4: Lựa chọn các cột cần thiết
lay_cot = ['Gia', 'TenSP', 'ThuongHieu', 'Loai', 'SmartKey', 'MaSanPham', 'NamDangKy', 'DungTich', 'MauSac', 'TinhTrang', 'ThongTinSanPham']
xemay_df = df[lay_cot]  # Lựa chọn các cột cần thiết

# Bước 5: Loại bỏ các hàng có giá trị rỗng hoặc chuỗi rỗng
xemay_df = xemay_df.fillna('')  # Thay thế giá trị NaN bằng chuỗi rỗng
xemay_df = xemay_df[xemay_df.apply(lambda x: x.str.strip() != '').all(axis=1)]  # Loại bỏ hàng có giá trị rỗng

# Bước 6: Tạo bảng Loại (Categories) với khóa chính
categories_df = xemay_df[['Loai']].drop_duplicates().reset_index(drop=True)#.drop_duplicates(): Loại bỏ các giá trị trùng lặp trong cột Loai, đảm bảo rằng mỗi loại sản phẩm chỉ xuất hiện một lần.
categories_df['LoaiID'] = categories_df.index + 1  # Thêm khóa chính tự động
categories_df = categories_df[['LoaiID', 'Loai']]  # Đưa khóa chính lên đầu

# Bước 7: Tạo bảng Sản Phẩm (Products) với khóa chính và khóa ngoại
xemay_df = xemay_df.merge(categories_df[['LoaiID', 'Loai']], on='Loai', how='left')
products_df = xemay_df[['MaSanPham', 'TenSP', 'Gia', 'NamDangKy', 'DungTich', 'MauSac', 'TinhTrang', 'SmartKey', 'ThongTinSanPham', 'LoaiID']]

# Hiển thị các DataFrame kết quả
print("Bảng Sản Phẩm (Products):")
print(products_df)

print("\nBảng Loại (Categories):")
print(categories_df)

# đẩy kết quả lên postgre
def create_database(db_name):
    # Kết nối tới PostgreSQL với database mặc định
    conn = psycopg2.connect(
        dbname='dbcrawlerxemay',  # Kết nối tới database mặc định
        user='postgres',
        password='123456',  # Mật khẩu của PostgreSQL
        host='localhost',
        port='5432'
    )
    # Để thực hiện các lệnh CREATE DATABASE
    conn.autocommit = True  
    cursor = conn.cursor()

    # Tạo database nếu chưa tồn tại
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"Cơ sở dữ liệu '{db_name}' đã được tạo.")
    else:
        print(f"Cơ sở dữ liệu '{db_name}' đã tồn tại.")

    # Đóng kết nối
    cursor.close()
    conn.close()

# Tạo cơ sở dữ liệu
db_name = 'dbcrawlerxemay'
create_database(db_name)


# Bước 9: Kết nối tới cơ sở dữ liệu mới
engine = create_engine(f'postgresql://postgres:123456@localhost:5432/{db_name}')
# Bước 10: Đẩy dữ liệu lên PostgreSQL
categories_df.to_sql('categories', engine, index=False, if_exists='replace')  # Đẩy bảng categories lên
products_df.to_sql('products', engine, index=False, if_exists='replace')  # Đẩy bảng products lên
print("Dữ liệu đã được xử lý và đẩy lên PostgreSQL thành công!")