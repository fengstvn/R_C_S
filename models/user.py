class User:
    def __init__(self, user_id, username, password_hash, salt,
                 learning_score=0, created_at=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.learning_score = learning_score
        self.created_at = created_at

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'salt': self.salt,
            'learning_score': self.learning_score,
            'created_at': self.created_at
        }

    def add_score(self, points=1):
        """增加学习积分"""
        self.learning_score += points

    def reduce_score(self, points=1):
        """减少学习积分"""
        if self.learning_score >= points:
            self.learning_score -= points
            return True
        return False