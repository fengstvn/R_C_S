import re
from datetime import datetime

def validate_username(username: str) -> bool:
    """验证用户名（3-20个字符，字母数字下划线）"""
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))

def validate_password(password: str) -> bool:
    """验证密码（至少6位）"""
    return len(password) >= 6

def format_datetime(dt_str: str) -> str:
    """格式化时间"""
    if not dt_str:
        return ''
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str[:16]

def truncate_text(text: str, max_len: int = 50) -> str:
    """截断文本"""
    if not text:
        return ''
    if len(text) <= max_len:
        return text
    return text[:max_len] + '...'