import psycopg2 

try:
    # Thông tin kết nối
    conn = psycopg2.connect(
        dbname='dbcrawlerxemay',  # Tên cơ sở dữ liệu
        user='postgres',           # Tên người dùng
        password='123456',         # Mật khẩu
        host='localhost',          # Host (thay đổi thành 'host.docker.internal' nếu cần)
        port='5432'                # Cổng
    )

    # Tạo một đối tượng cursor
    cur = conn.cursor()

    # Thực hiện một truy vấn đơn giản (ví dụ: lấy danh sách bảng)
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = cur.fetchall()

    print("Danh sách bảng trong cơ sở dữ liệu:")
    for table in tables:
        print(table)

except psycopg2.Error as e:
    print("Lỗi kết nối:", e)

finally:
    # Đóng cursor và kết nối
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
