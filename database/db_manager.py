import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from utils.password_utils import PasswordUtils


class DatabaseManager:
    def __init__(self, db_path='red_culture.db'):
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

            # 1. users表（普通用户，不保存管理员）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    learning_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. places表（景点）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS places (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    image_path TEXT,
                    is_hot BOOLEAN DEFAULT 0,
                    checkin_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 3. records表（用户和景点的多对多关联）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    place_id INTEGER NOT NULL,
                    checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    experience TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
                    UNIQUE(user_id, place_id)
                )
            ''')

            # 4. notices表（公告，独立）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    remark TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_user ON records(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_records_place ON records(place_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_hot ON places(is_hot)')

            # 插入示例景点数据
            cursor.execute('''
                INSERT OR IGNORE INTO places (name, location, description) 
                VALUES 
                ('井冈山革命博物馆', '江西省吉安市', '中国第一个农村革命根据地，被誉为"中国革命的摇篮"'),
                ('延安革命纪念馆', '陕西省延安市', '中国革命圣地，党中央和毛主席在此生活战斗了13年'),
                ('西柏坡纪念馆', '河北省石家庄市', '解放战争时期中共中央所在地，新中国从这里走来'),
                ('韶山毛泽东故居', '湖南省湘潭市', '伟大领袖毛泽东同志的故乡，全国爱国主义教育示范基地'),
                ('瑞金共和国摇篮景区', '江西省赣州市', '中华苏维埃共和国临时中央政府所在地')
            ''')

            # 插入示例公告数据
            cursor.execute('''
                INSERT OR IGNORE INTO notices (title, content, remark) 
                VALUES 
                ('系统上线通知', '红色文化学习打卡系统正式上线，欢迎广大师生使用！通过打卡学习红色文化，传承革命精神。', '重要通知'),
                ('学习积分规则说明', '每次打卡可获得1个学习积分，打卡次数达到10次可解锁"红色达人"称号。', '使用说明'),
                ('新增景点推荐', '系统已添加5个红色文化景点，欢迎前往学习打卡！', '系统更新')
            ''')

        def create_user(self, username: str, password: str) -> int:
            """创建用户，返回用户ID（密码使用加盐哈希）"""
            salt, password_hash = PasswordUtils.encrypt_password(password)

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                    (username, password_hash, salt)
                )
                return cursor.lastrowid

        def get_user_by_username(self, username: str) -> Optional[Dict]:
            """根据用户名获取用户信息"""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM users WHERE username = ?',
                    (username,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

        def get_user_by_id(self, user_id: int) -> Optional[Dict]:
            """根据用户ID获取用户信息"""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM users WHERE id = ?',
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

        def verify_user_password(self, username: str, password: str) -> Optional[Dict]:
            """验证用户密码，成功返回用户信息，失败返回None"""
            user = self.get_user_by_username(username)
            if not user:
                return None

            if PasswordUtils.verify_password(password, user['salt'], user['password_hash']):
                return user
            return None

        def update_user_score(self, user_id: int, delta: int):
            """更新用户积分"""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET learning_score = learning_score + ? WHERE id = ?',
                    (delta, user_id)
                )

            def create_notice(self, title: str, content: str, remark: str = '') -> int:
                """发布公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO notices (title, content, remark) VALUES (?, ?, ?)',
                        (title, content, remark)
                    )
                    return cursor.lastrowid

            def get_all_notices(self) -> List[Dict]:
                """获取所有公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM notices ORDER BY created_at DESC')
                    return [dict(row) for row in cursor.fetchall()]

            def get_notice_by_id(self, notice_id: int) -> Optional[Dict]:
                """根据ID获取公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM notices WHERE id = ?', (notice_id,))
                    row = cursor.fetchone()
                    return dict(row) if row else None

            def search_notices_by_title(self, keyword: str) -> List[Dict]:
                """按标题搜索公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'SELECT * FROM notices WHERE title LIKE ?',
                        (f'%{keyword}%',)
                    )
                    return [dict(row) for row in cursor.fetchall()]

            def update_notice(self, notice_id: int, **kwargs):
                """修改公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    fields = []
                    values = []
                    for key, value in kwargs.items():
                        if key in ['title', 'content', 'remark']:
                            fields.append(f'{key} = ?')
                            values.append(value)
                    if fields:
                        sql = f'UPDATE notices SET {", ".join(fields)} WHERE id = ?'
                        values.append(notice_id)
                        cursor.execute(sql, values)

            def delete_notice(self, notice_id: int):
                """删除公告"""
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM notices WHERE id = ?', (notice_id,))