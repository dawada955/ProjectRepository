from PyQt5.QtCore import QSettings


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化 QSettings（使用 INI 文件）
            cls._instance.settings = QSettings("config.ini", QSettings.IniFormat)
        return cls._instance


# 全局实例
config = ConfigManager()
