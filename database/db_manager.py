import sqlite3
from contextlib import contextmanager


class DatabaseManager:
    def __init__(self, db_path='RC.db'):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    learning_score INTEGER DEFAULT 0,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. 景点表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attractions (
                    attraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    image_path TEXT,
                    is_hot BOOLEAN DEFAULT 0,
                    checkin_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 3. 公告表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcements (
                    announcement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    remark TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 4. 打卡记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkins (
                    checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    attraction_id INTEGER NOT NULL,
                    checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    experience TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (attraction_id) REFERENCES attractions(attraction_id) ON DELETE CASCADE
                )
            ''')

            # 5. 创建管理员账号
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role) 
                VALUES ('admin', 'admin123', 'admin')
            ''')

            # 6. 插入示例数据
            cursor.execute('''
                INSERT OR IGNORE INTO attractions (name, location, description) 
                VALUES 
                ('中国人民革命军事博物馆', '北京市海淀区', '中国第一个综合类军事博物馆、展示人民军队光辉历程的重要窗口'),
                ('南昌八一起义纪念馆', '江西省南昌市', '中国共产党武装反抗国民党反动派的第一枪所在地'),
                ('瑞金中央革命根据地纪念馆', '江西省赣州市', '中华苏维埃共和国临时中央政府诞生地')
            ''')

            cursor.execute('''
                INSERT OR IGNORE INTO announcements (title, content, remark) 
                VALUES 
                ('系统上线通知', '红色文化学习打卡系统正式上线，欢迎使用！', '重要'),
                ('学习积分规则', '每次打卡获得1积分，坚持学习红色文化！', '提示')
            ''')