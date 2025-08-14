import os

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QCheckBox, QPushButton, QWidget, QFrame, QHBoxLayout

import utils
from config_manager import config
from fields import PathField


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__(None)  # <-- 重点：没有 parent 了
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)  # 设置为应用程序模态
        self.setFixedSize(300, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.settings = QSettings("config.ini", QSettings.IniFormat)  # 加载设置配置

        self.wrapper = QWidget()
        self.wrapper.setObjectName("SettingsPanel")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        layout = QVBoxLayout(self.wrapper)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("设置")
        title.setObjectName("SettingsPanelTitle")
        title.setPixmap(
            QPixmap(PathField.icon_settings_png).scaled(17, 17, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title.setContentsMargins(0, 0, 0, 0)

        # --- 分隔线组件 ---
        Separator = QFrame()
        Separator.setFrameShape(QFrame.HLine)
        Separator.setFrameShadow(QFrame.Plain)
        Separator.setLineWidth(1)
        Separator.setStyleSheet("color: #3a3f4b;")

        first_row = QHBoxLayout()
        first_row.setContentsMargins(0, 0, 0, 0)
        first_row.setSpacing(0)

        self.auto_start_checkbox = QCheckBox("开机自启动")
        self.auto_start_checkbox.setObjectName("AutoStartCheckBox")
        self.auto_start_checkbox.toggled.connect(self.switch_auto_start_checkbox)

        self.auto_scan_checkbox = QCheckBox("自动扫描")
        self.auto_scan_checkbox.setObjectName("AutoScan")

        self.auto_open_checkbox = QCheckBox("自动打开网页")
        self.auto_open_checkbox.setObjectName("AutoOpenCheckBox")

        first_row.addWidget(self.auto_start_checkbox, 6)
        first_row.addWidget(self.auto_scan_checkbox, 5)

        layout.addWidget(title)
        layout.addWidget(Separator)
        layout.addLayout(first_row)
        layout.addWidget(self.auto_open_checkbox)

        layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("SettingsPanelCloseBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.on_close_clicked)
        layout.addWidget(close_btn)

        outer_layout.addWidget(self.wrapper)

        self.setStyleSheet("""
            #SettingsPanel {
                background-color: #282c34;
                border-radius: 8px;
                border: 1px solid #282c34;
            }
            #SettingsPanelTitle {
                fonts-size: 17px; fonts-weight: bold; color: #EAEAEA;
            }
            QCheckBox {
                color: #CCCCCC; fonts-size: 13px;
            }
            #SettingsPanelCloseBtn {
                background-color: #3a3f4b;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            #SettingsPanelCloseBtn:hover {
                background-color: #007BFF;
            }
        """)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def switch_auto_start_checkbox(self, checked):
        if checked:
            utils.enable_auto_start()
        else:
            utils.disable_auto_start()

    def get_settings(self):
        return {
            "auto_start": self.auto_start_checkbox.isChecked(),
            "auto_open_web": self.auto_open_checkbox.isChecked(),
            "auto_scan": self.auto_scan_checkbox.isChecked(),
        }

    def on_close_clicked(self):
        self.save_settings()
        self.hide()

    def load_settings(self):
        if os.path.exists("config.ini"):

            auto_start = True if config.settings.value("Setting/AutoStart") == "1" else False
            auto_open = True if config.settings.value("Setting/AutoOpenWeb") == "1" else False
            auto_scan = True if config.settings.value("Setting/AutoScan") == "1" else False
            self.auto_start_checkbox.setChecked(auto_start)
            self.auto_open_checkbox.setChecked(auto_open)
            self.auto_scan_checkbox.setChecked(auto_scan)
        else:
            self.auto_start_checkbox.setChecked(False)
            self.auto_open_checkbox.setChecked(False)
            self.auto_scan_checkbox.setChecked(False)

    def save_settings(self):
        config.settings.setValue("Setting/AutoStart", int(self.auto_start_checkbox.isChecked()))
        config.settings.setValue("Setting/AutoOpenWeb", int(self.auto_open_checkbox.isChecked()))
        config.settings.setValue("Setting/AutoScan", int(self.auto_scan_checkbox.isChecked()))
