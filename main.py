import ctypes
import sys
import threading
import time
import webbrowser

from PyQt5.QtCore import Qt, QSize, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie, QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, QDesktopWidget)

from config_manager import config
from fields import PathField
from service_card import ServiceCardWidget
from title_bar import TitleBarWidget
from tray_icon import TrayIcon
from udp_heartbeat_listener import UdpHeartbeatListener
from utils import is_process_running
from zeroconf_server import ZeroconfServer


# UdpHeartBeatPort = find_free_port(8100, 1)  # 太慢


# --- Main Application Window ---
class ScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._init_stylesheet()
        self._restore_window_position()
        self._init_threads()
        self._load_settings_panel()

    def _init_ui(self):
        self.setWindowTitle("微传-发现")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(380, 380)
        self.settings = QSettings("config.ini", QSettings.IniFormat)  # 加载设置配置
        self.setWindowIcon(QIcon(PathField.icon_app_ico))
        self.service_cards = {}
        self.setup_tray_icon()

        self.container = QWidget()
        self.container.setObjectName("Container")
        self.setCentralWidget(self.container)

        self.outer_layout = QVBoxLayout(self.container)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # --- 标题栏组件 ---
        self.title_bar = TitleBarWidget()

        self.title_bar.minimized.connect(self.minimize_to_task_bar)
        self.title_bar.closed.connect(self.close)
        self.title_bar.showSetting.connect(self.show_settings_panel)

        self._init_content_area()

        self.outer_layout.addWidget(self.title_bar)
        self.outer_layout.addWidget(self.content_widget)

        self.installEventFilter(self)

    def _init_content_area(self):
        # --- 扫描控制组件（按钮+状态） ---
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 3, 15, 16)
        self.content_layout.setSpacing(0)

        scan_control_layout = QHBoxLayout()
        scan_control_layout.setContentsMargins(0, 8, 3, 15)

        self.spinner = QLabel()
        self.movie = QMovie(PathField.icon_spinner_gif)  # 替换为你的GIF路径
        self.movie.setCacheMode(QMovie.CacheAll)  # 启用缓存
        self.movie.setScaledSize(QSize(30, 30))
        self.spinner.setMovie(self.movie)
        self.spinner.setContentsMargins(0, 3, 5, 0)
        self.spinner.setVisible(False)
        self.movie.start()

        self.status_label = QLabel(" 准备扫描。")
        self.status_label.setFont(QFont("Microsoft YaHei"))

        self.scan_button = QPushButton("启动扫描")
        self.scan_button.setCursor(Qt.PointingHandCursor)
        self.scan_button.setObjectName("ScanButton")
        self.scan_button.setFont(QFont("Microsoft YaHei"))
        self.scan_button.clicked.connect(self.toggle_scan)

        scan_control_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        scan_control_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        scan_control_layout.addStretch()
        scan_control_layout.addWidget(self.scan_button, alignment=Qt.AlignCenter)

        # --- 服务卡片组件 ---
        self.services_widget = QWidget()
        self.services_layout = QVBoxLayout()
        self.services_layout = QVBoxLayout(self.services_widget)
        self.services_layout.setContentsMargins(0, 8, 0, 0)
        self.services_layout.setSpacing(9)
        self.services_layout.setAlignment(Qt.AlignTop)
        self.services_layout.addWidget(self.services_widget)
        self.services_layout.addStretch()

        # --- 滚动框架组件 ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("DeviceScrollArea")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.services_widget)
        self.scroll_area.setViewportMargins(0, 0, 0, 0)

        # 占位组件
        self._init_placeholder()

        # 内容区装配
        self.content_layout.addLayout(scan_control_layout)
        self.content_layout.addWidget(self.scroll_area)  # Add ScrollArea to main layout
        self.content_layout.addWidget(self.placeholder_widget)

    def _init_stylesheet(self):
        with open(PathField.style_scroll_area, "r", encoding="utf-8") as f:
            self.scroll_area.setStyleSheet(f.read())
        with open(PathField.style_app_qss, "r", encoding="utf-8") as f:  # 最高层级qss，最后装配
            self.setStyleSheet(f.read())

    def _init_placeholder(self):
        # --- 占位图标组件 ---
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        placeholder_layout.setContentsMargins(0, 0, 0, 75)
        placeholder_layout.setSpacing(10)

        self.placeholder_icon = QLabel()
        self.placeholder_icon.setPixmap(
            QPixmap(PathField.icon_empty_png).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.placeholder_text = QLabel("暂无可用设备")
        self.placeholder_text.setStyleSheet("color: #666; fonts-size: 15px;")

        placeholder_layout.addWidget(self.placeholder_icon, alignment=Qt.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_text, alignment=Qt.AlignCenter)

    def _load_settings_panel(self):
        # --- 加载设置面板 ---
        if not hasattr(self, 'settings_panel'):
            from setting_panel import SettingsPanel
            self.settings_panel = SettingsPanel()
            self.settings_panel.load_settings()
            if self.settings_panel.auto_scan_checkbox.checkState():  # 自动切换扫描状态
                self.toggle_scan()

    def _init_threads(self):
        self.setup_scanner_thread()
        self.listManagerThread = DeviceListManagerThread()
        self.listManagerThread.update_list_signal.connect(self.fresh_service_list)
        self.listManagerThread.start()

    def _restore_window_position(self):
        # --- 加载窗口位置 ---
        if config.settings.contains("Info/position"):
            self.move(config.settings.value("Info/position"))
        else:
            screen = QDesktopWidget().screenGeometry()  # 获取屏幕尺寸
            size = self.geometry()  # 获取窗口尺寸
            # 计算居中坐标
            self.move((screen.width() - size.width()) // 2 + 100,
                      (screen.height() - size.height()) // 2)
            config.settings.setValue("Info/position", self.window().pos())

    def setup_scanner_thread(self):

        UdpHeartBeatPort = 8100
        self.zeroconfServer = ZeroconfServer(UdpHeartBeatPort)
        self.zeroconfServer.start()  # 把IP，端口 实时广播给局域网内所有服务器

        self.heartbeat_listener = UdpHeartbeatListener(UdpHeartBeatPort)
        self.heartbeat_listener.device_online.connect(self.add_service_card)
        self.heartbeat_listener.device_offline.connect(self.remove_service_card)
        self.heartbeat_listener.start()
        self.scanning = False

    def toggle_scan(self):
        if not self.scanning:
            self.scanning = True
            self.clear_service_list()
            self.status_label.setText("扫描中。。。")
            self.spinner.setVisible(True)
            self.scan_button.setText("停止扫描")
            self.listManagerThread.pause = False
        else:
            self.scanning = False
            self.scan_button.setText("启动扫描")
            self.spinner.setVisible(False)
            self.status_label.setText("扫描已停止。")
            self.listManagerThread.pause = True

    def clear_service_list(self):
        for card in self.service_cards.values():
            self.services_layout.removeWidget(card)
            card.deleteLater()
        self.service_cards.clear()

    def fresh_service_list(self):
        for name, ip, port in self.heartbeat_listener.get_current_devices():
            self.add_service_card(name, f"http://{ip}:{port}")

    def add_service_card(self, name, url):
        if not self.scanning:
            return
        if name in self.service_cards:
            self.service_cards[name].updateInfo(url)
            return
        self.placeholder_widget.hide()  # 隐藏站位图标

        card = ServiceCardWidget(name, url)
        self.services_layout.insertWidget(0, card)
        self.service_cards[name] = card

        self.status_label.setText(f"发现 {len(self.service_cards)} 个聊天室。。。")

        # 自动打开网页
        if self.settings_panel.auto_open_checkbox.checkState():
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    def remove_service_card(self, name):
        if not self.scanning:
            return
        if name in self.service_cards:
            card = self.service_cards.pop(name)
            self.services_layout.removeWidget(card)
            card.deleteLater()
            self.status_label.setText(f"发现 {len(self.service_cards)} 个聊天室。。。")

    def show_settings_panel(self):
        # 居中到主窗口
        parent_geometry = self.geometry()
        settings_geometry = self.settings_panel.frameGeometry()
        center_point = parent_geometry.center()
        settings_geometry.moveCenter(center_point)
        self.settings_panel.move(settings_geometry.topLeft())

        self.settings_panel.show()
        self.settings_panel.raise_()

    def closeEvent(self, event):
        event.ignore()  # 拦截默认关闭事件
        self.hide()  # 隐藏窗口

    def exit_app(self):
        self.hide()
        self.listManagerThread.stop()
        self.heartbeat_listener.stop()
        self.zeroconfServer.stop()
        QApplication.quit()

    def minimize_to_task_bar(self):
        self.showMinimized()

    def minimize_to_tray(self):
        self.hide()  # 隐藏主窗口

    def setup_tray_icon(self):
        tray_icon = TrayIcon(self)
        tray_icon.show()  # 显示托盘图标


class DeviceListManagerThread(QThread):
    update_list_signal = pyqtSignal()  # 信号：传递更新后的列表

    def __init__(self):
        super().__init__()
        self.running = True
        self.pause = True  # 外部控制是否开关

    def run(self):
        while self.running:
            if not self.pause:
                # 模拟列表更新逻辑（如从网络/文件读取数据）
                self.update_list_signal.emit()  # 发送副本避免引用问题

            self.msleep(1000)  # 间隔1秒更新一次

    def stop(self):
        self.running = False
        self.wait()


def set_app_user_model_id(app_id):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


if __name__ == '__main__':
    if is_process_running("微传-发现"):
        sys.exit(0)
    set_app_user_model_id("com.wetransfer.client.uniqueid")

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(PathField.icon_app_ico))

    window = ScannerApp()

    # window.show()

    sys.exit(app.exec_())
