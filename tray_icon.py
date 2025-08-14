from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

from config_manager import config
from fields import PathField


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(QIcon(PathField.icon_app_ico))

        # 创建系统原生菜单
        self.menu = QMenu()
        self.menu.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.menu.setAttribute(Qt.WA_TranslucentBackground)

        # 设置菜单样式表
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #292C32;  /* 背景色 */
                color: white;
                border: 0px solid #444;
                border-radius: 10px;
                padding: 12px 0px;
            }
            QMenu::item {
                padding: 6px 35px 6px 18px;
                margin: 0px;
                fonts-size: 12px;
                color: #CCCCCC;
            }
            QMenu::item:selected {
                background-color: #3A3F45;  /* 选中项背景色 */
            }
            QMenu::item:disabled {
                color: gray;
            }
            QMenu::separator {
                height: 1px;
                background: #444;
                margin: 5px 0;
            }
        """)

        # 添加菜单项
        self.add_action("显示主窗口", self.restore_app)
        self.add_action("退出", self.exit_app)
        self.setContextMenu(self.menu)
        self.setToolTip("微传")
        self.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.restore_app()

    def add_action(self, text, callback):
        action = QAction(text, self)
        action.triggered.connect(callback)
        self.menu.addAction(action)

    def restore_app(self):
        if self.parent().isMinimized() or self.parent().isHidden():
            self.parent().showNormal()
            self.parent().move(config.settings.value("Info/position"))
            self.parent().activateWindow()

    def exit_app(self):
        self.hide()
        if self.parent():
            self.parent().exit_app()
