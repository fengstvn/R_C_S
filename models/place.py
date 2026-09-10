class Place:
    def __init__(self, place_id, name, location, description='',
                 image_path='', is_hot=False, checkin_count=0, created_at=None):
        self.place_id = place_id
        self.name = name
        self.location = location
        self.description = description
        self.image_path = image_path
        self.is_hot = is_hot
        self.checkin_count = checkin_count
        self.created_at = created_at

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.place_id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'image_path': self.image_path,
            'is_hot': self.is_hot,
            'checkin_count': self.checkin_count,
            'created_at': self.created_at
        }

    def increment_checkin(self):
        """增加打卡次数"""
        self.checkin_count += 1
        if self.checkin_count >= 10:
            self.is_hot = True

    def is_hot_place(self):
        """判断是否为热门景点"""
        return self.checkin_count >= 10