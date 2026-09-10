"""
打卡记录模型类
"""
from datetime import datetime


class Record:
    def __init__(self, record_id, user_id, place_id,
                 checkin_time=None, experience=''):
        self.record_id = record_id
        self.user_id = user_id
        self.place_id = place_id
        self.checkin_time = checkin_time or datetime.now()
        self.experience = experience

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.record_id,
            'user_id': self.user_id,
            'place_id': self.place_id,
            'checkin_time': self.checkin_time,
            'experience': self.experience
        }

    def format_time(self):
        """格式化时间"""
        if isinstance(self.checkin_time, str):
            return self.checkin_time
        return self.checkin_time.strftime('%Y-%m-%d %H:%M:%S')