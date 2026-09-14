import unittest
import os
from database.db_manager import DatabaseManager


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager('test.db')
        self.test_user_id = self.db.create_user('testuser', 'test123')
        self.test_place_id = self.db.create_place('测试景点', '测试地点', '测试描述')

    def tearDown(self):
        os.remove('test.db')

    def test_create_user(self):
        user = self.db.get_user_by_username('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')

    def test_verify_password(self):
        user = self.db.verify_user_password('testuser', 'test123')
        self.assertIsNotNone(user)

        user2 = self.db.verify_user_password('testuser', 'wrong')
        self.assertIsNone(user2)

    def test_create_record(self):
        record_id = self.db.create_record(self.test_user_id, self.test_place_id, '测试心得')
        self.assertIsNotNone(record_id)

        records = self.db.get_records_by_user(self.test_user_id)
        self.assertEqual(len(records), 1)


if __name__ == '__main__':
    unittest.main()