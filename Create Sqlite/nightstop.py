import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('allocate_nightstop.db')
c = conn.cursor()

# Tạo bảng dữ liệu
c.execute('''
    CREATE TABLE IF NOT EXISTS data (
        REG TEXT,
        ARR TEXT,
        STA TEXT,
        Route TEXT,
        NightStop TEXT,
        GroundTime TEXT
    )
''')

# Lưu thay đổi và đóng kết nối cơ sở dữ liệu
conn.commit()
conn.close()

