class Notice:
    def __init__(self, notice_id, title, content, remark='', created_at=None):
        self.notice_id = notice_id
        self.title = title
        self.content = content
        self.remark = remark
        self.created_at = created_at

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.notice_id,
            'title': self.title,
            'content': self.content,
            'remark': self.remark,
            'created_at': self.created_at
        }