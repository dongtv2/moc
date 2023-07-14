import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('user_management.db')
c = conn.cursor()

# Tạo bảng users
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        group_name TEXT
    )
''')

# Thêm người dùng mẫu
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('admin', 'admin123', 'admin', NULL)
''')
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('moderator', 'mod123', 'mod', NULL)
''')
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('user1', 'pass1', 'user', 'techsupport')
''')
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('user2', 'pass2', 'user', 'dutymanager')
''')
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('user3', 'pass3', 'user', 'readiness')
''')
c.execute('''
    INSERT INTO users (username, password, role, group_name)
    VALUES ('user4', 'pass4', 'user', 'coordinator')
''')

# Lưu thay đổi và đóng kết nối cơ sở dữ liệu
conn.commit()
conn.close()
