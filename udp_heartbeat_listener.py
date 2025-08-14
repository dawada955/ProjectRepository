from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import socket
import time

from fields import heart_beat_sign


class UdpHeartbeatListener(QObject):
    device_online = pyqtSignal(str, str)
    device_offline = pyqtSignal(str)

    def __init__(self, port, timeout=2):
        super().__init__()
        self.port = port
        self.timeout = timeout
        self.devices = {}

        self.is_running = False
        self.listener_thread = QThread()
        self.check_timer = QTimer()
        self.check_timer.setInterval(1000)
        self.check_timer.timeout.connect(self.check_device_timeouts)

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.listen_udp)
        self.listener_thread.start()
        self.check_timer.start()

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self.listener_thread.quit()
        self.listener_thread.wait()
        self.check_timer.stop()
        #print("Heartbeat listener stopped.")

    def listen_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('', self.port))
        udp_socket.settimeout(1)  # 每1秒timeout检查退出标志

        #print(f"Listening UDP heartbeats on port {self.port}")

        while self.is_running:
            try:
                data, addr = udp_socket.recvfrom(1024)
                message = data.decode()
                #print(message)
                if message.startswith(heart_beat_sign + "|"):
                    info = message.split("|")
                    device_name = info[1]
                    ip = info[2]
                    port = info[3]
                    self.devices[device_name] = (ip, port, time.time())
            except socket.timeout:
                continue
            except Exception as e:
                print(f"UDP Error: {e}")
                break

        udp_socket.close()
        #print("UDP socket closed.")

    def get_current_devices(self):
        # 返回当前在线的设备列表 [(device_name, ip), ...]
        #print(self.devices)
        return [(name, ip_port[0], ip_port[1]) for name, ip_port in self.devices.items()]

    def check_device_timeouts(self):
        current_time = time.time()
        to_remove = []
        for device_name, (ip, port, last_time) in self.devices.items():
            if current_time - last_time > self.timeout:
                to_remove.append(device_name)

        for device_name in to_remove:
            del self.devices[device_name]
            self.device_offline.emit(device_name)
