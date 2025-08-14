import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QLabel, QVBoxLayout, QPushButton

from fields import PathField


class ServiceCardWidget(QWidget):
    def __init__(self, name, url):
        super().__init__()
        # ... 布局与UI...
        self.name = name
        self.url = url
        self.outLayout = QHBoxLayout(self)

        self.wrapper = QWidget(self)
        self.wrapper.setObjectName("ServiceCard")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(78)

        self.layout = QHBoxLayout(self.wrapper)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 18, 0)  # 调整 最右边组件 边距
        self.icon_label = QLabel()
        self.icon_label.setPixmap(
            QPixmap(PathField.icon_responsive_png).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setContentsMargins(15, 0, 12, 0)  # 调整 最左边两个组件 边距

        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(0)
        self.name_label = QLabel(self.name)
        self.name_label.setObjectName("ServiceName")
        self.name_label.setContentsMargins(0, 15, 0, 0)  # 调整上边距
        self.name_label.setFont(QFont("Microsoft YaHei"))

        self.url_label = QLabel(self.url)
        self.url_label.setObjectName("ServiceUrl")
        self.url_label.setContentsMargins(0, 0, 0, 16)  # 调整下边距
        self.info_layout.addWidget(self.name_label)
        self.info_layout.addWidget(self.url_label)

        self.connect_btn = QPushButton("访问")
        self.connect_btn.setObjectName("JoinButton")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(lambda: webbrowser.open(self.url))
        self.connect_btn.setFont(QFont("Microsoft YaHei"))

        self.layout.addWidget(self.icon_label)
        self.layout.addLayout(self.info_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.connect_btn)

        self.outLayout.addWidget(self.wrapper)
        self.outLayout.setContentsMargins(0, 0, 0, 0)
        self.outLayout.setSpacing(0)

    def updateInfo(self, url):
        self.url = url
        self.url_label.setText(self.url)