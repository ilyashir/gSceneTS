"""
Общие утилиты для приложения.

Включает в себя:
- Работу с сигналами
- Работу с типами данных
- Логирование
- Исключения
- Работу с UI
"""

from utils.signal_utils import SignalBlock, safe_emit, safe_connect, safe_disconnect
from utils.logging_utils import setup_logger, log_exception, log_value_change
from utils.exceptions import (
    ApplicationError, ValidationError, ResourceError, 
    ConfigError, EventError, handle_application_error
)
from utils.type_utils import (
    safe_cast, is_numeric, is_string, is_dict, is_list, 
    get_nested_value, set_nested_value
)

"""
Утилиты для gSceneTS
""" 