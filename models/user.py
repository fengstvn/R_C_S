class User:
    def __init__(self, user_id, username, password, learning_score=0, role='user', created_at=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.learning_score = learning_score
        self.role = role
        self.created_at = created_at

    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'learning_score': self.learning_score,
            'role': self.role,
            'created_at': self.created_at
        }

    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin'

    def add_score(self, points=1):
        """增加学习积分"""
        self.learning_score += points

    def reduce_score(self, points=1):
        """减少学习积分"""
        if self.learning_score >= points:
            self.learning_score -= points
            return True
        return False