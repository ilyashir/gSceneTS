"""
Файл конфигурации приложения.
Хранит настройки и константы, которые могут быть изменены пользователем.
"""
import json
import os
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class Config:
    """
    Класс для работы с конфигурацией приложения.
    Позволяет загружать, сохранять и получать доступ к настройкам.
    """
    # Путь к файлу конфигурации (относительно корня проекта)
    CONFIG_FILE = "app_config.json"
    
    # Параметры по умолчанию
    DEFAULT_CONFIG = {
        "app": {
            "name": "TS Scene Generator",
            "version": "1.0.0"
        },
        "appearance": {
            "theme": "dark",  # 'dark' или 'light'
            "theme_name": "Темный стиль"
        },
        "language": {
            "current": "ru",  # 'ru' или 'en'
            "name": "Русский"
        },
        "grid": {
            "size": 50,
            "snap_to_grid": True
        },
        "scene": {
            "default_width": 1300,
            "default_height": 1000
        }
    }
    
    _instance = None
    
    def __new__(cls):
        """Реализация паттерна Singleton для Config"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._config = cls.DEFAULT_CONFIG.copy()
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Загружает конфигурацию из файла или создает новый файл с настройками по умолчанию"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Обновляем конфигурацию, но сохраняем структуру по умолчанию
                    self._merge_configs(self._config, loaded_config)
                    logger.info("Конфигурация успешно загружена из файла")
            else:
                # Файл не существует, сохраняем настройки по умолчанию
                self._save_config()
                logger.info("Создан новый файл конфигурации с настройками по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {e}")
    
    def _merge_configs(self, default, loaded):
        """Рекурсивно объединяет загруженную конфигурацию с конфигурацией по умолчанию"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_configs(default[key], value)
                else:
                    default[key] = value
    
    def _save_config(self):
        """Сохраняет текущую конфигурацию в файл"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info("Конфигурация успешно сохранена в файл")
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {e}")
    
    def get(self, section, key=None):
        """
        Получает значение настройки.
        
        Args:
            section (str): Раздел настроек (например, 'appearance')
            key (str, optional): Ключ внутри раздела. Если None, возвращает весь раздел.
        
        Returns:
            Значение настройки или словарь с настройками раздела.
        """
        if section not in self._config:
            return None
        
        if key is None:
            return self._config[section]
        
        if key not in self._config[section]:
            return None
        
        return self._config[section][key]
    
    def set(self, section, key, value):
        """
        Устанавливает значение настройки и сохраняет конфигурацию.
        
        Args:
            section (str): Раздел настроек
            key (str): Ключ внутри раздела
            value: Новое значение
            
        Returns:
            bool: True, если значение успешно установлено
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
        self._save_config()
        return True
    
    def get_all(self):
        """Возвращает полную копию конфигурации"""
        return self._config.copy()


# Создаем глобальный экземпляр конфигурации для использования в приложении
config = Config() 