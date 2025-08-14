from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget, QVBoxLayout

from config_manager import config
from fields import PathField


class TitleBarWidget(QWidget):
    minimized = pyqtSignal()
    closed = pyqtSignal()
    showSetting = pyqtSignal()
    dragStart = None

    def __init__(self):
        super().__init__()
        # ...布局与按钮初始化...
        self.outLayout = QHBoxLayout(self)
        self.outLayout.setContentsMargins(0, 0, 0, 0)
        self.outLayout.setSpacing(0)

        self.wrapper = QWidget()  # 自定义组件要加上包裹组件，才能被ID选择器识别
        self.wrapper.setObjectName("TitleBar")

        self.title_bar_layout = QVBoxLayout(self.wrapper)
        self.title_bar_layout.setSpacing(0)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)

        # self.title_label = QLabel("发现群聊")
        # self.title_label.setObjectName("TitleLabel")
        # self.title_label.setContentsMargins(0, 3, 0, 0)

        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.setIcon(
            QIcon(QPixmap(PathField.icon_settings_png).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.settings_btn.setFixedHeight(35)

        self.min_btn = QPushButton()
        self.min_btn.setObjectName("MinimizeButton")
        self.min_btn.setIcon(
            QIcon(QPixmap(PathField.icon_minimize_png).scaled(12, 12, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.min_btn.setFixedHeight(35)

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setIcon(
            QIcon(QPixmap(PathField.icon_close_png).scaled(12, 12, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.close_btn.setFixedHeight(35)

        # spacer = QWidget()  # 拉伸空间，用于撑起布局
        # spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.title_button_bar = QWidget()
        self.title_button_layout = QHBoxLayout(self.title_button_bar)
        self.title_button_layout.setSpacing(0)
        self.title_button_layout.setContentsMargins(0, 0, 0, 0)
        # self.title_bar_layout.addWidget(self.title_label)

        # self.title_bar_layout.addWidget(spacer)
        self.title_button_layout.addWidget(self.settings_btn)
        self.title_button_layout.addWidget(self.min_btn)
        self.title_button_layout.addWidget(self.close_btn)

        self.title_panel_bar = QWidget()
        self.title_panel_bar.setObjectName("TitlePanel")
        self.title_panel_layout = QHBoxLayout(self.title_panel_bar)
        self.title_panel_layout.setSpacing(0)
        self.title_panel_layout.setContentsMargins(0, 12, 0, 10)

        self.title_bar_layout.addWidget(self.title_button_bar)
        self.title_bar_layout.addWidget(self.title_panel_bar)

        self.settings_btn.clicked.connect(self.showSetting.emit)
        self.min_btn.clicked.connect(self.minimized.emit)
        self.close_btn.clicked.connect(self.closed.emit)

        self.outLayout.addWidget(self.wrapper)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            self.dragStart = event.globalPos()
            return True
        elif event.type() == event.MouseMove and event.buttons() == Qt.LeftButton and self.dragStart:
            diff = event.globalPos() - self.dragStart
            self.window().move(self.window().pos() + diff)
            self.dragStart = event.globalPos()
            return True
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.dragStart = None
            config.settings.setValue("Info/position", self.window().pos())
            return True
        return super().eventFilter(source, event)
