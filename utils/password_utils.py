import hashlib
import os
import base64


class PasswordUtils:
    """密码加密工具类"""

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """生成随机盐"""
        salt = os.urandom(length)
        return base64.b64encode(salt).decode('utf-8')

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """使用盐对密码进行哈希"""
        salted = password + salt
        hash_obj = hashlib.sha256(salted.encode('utf-8'))
        return hash_obj.hexdigest()

    @staticmethod
    def verify_password(password: str, salt: str, password_hash: str) -> bool:
        """验证密码是否正确"""
        computed_hash = PasswordUtils.hash_password(password, salt)
        return computed_hash == password_hash

    @staticmethod
    def encrypt_password(password: str) -> tuple:
        """生成盐和密码哈希"""
        salt = PasswordUtils.generate_salt()
        password_hash = PasswordUtils.hash_password(password, salt)
        return salt, password_hash