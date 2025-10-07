import re
from typing import List


def is_valid_email_strict(email: str) -> bool:
    """
    Строгая проверка валидности email адреса.
    
    Args:
        email (str): Email адрес для проверки
        
    Returns:
        bool: True если email валиден, False в противном случае
    """
    # Более строгое регулярное выражение
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
    
    if not re.match(pattern, email):
        return False
    
    # Дополнительные проверки
    if len(email) > 254:  # Максимальная длина email
        return False
    
    local_part, domain = email.split('@', 1)
    
    if len(local_part) > 64:  # Максимальная длина локальной части
        return False
    
    return True