ADMIN_ID = 0
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123123'


def get_admin_user() -> dict:
    """返回管理员用户字典（登录成功后使用）"""
    return {
        'id': ADMIN_ID,
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'role': 'admin',
        'learning_score': 0
    }


def is_admin(username: str, password: str) -> bool:
    """校验是否为管理员账号"""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD
