from zeroconf import Zeroconf, ServiceInfo
import socket

from fields import heart_beat_sign
from utils import get_preferred_ip


class ZeroconfServer:
    def __init__(self, port, service_name="_pcservicewt._tcp.local."):
        self.zeroconf = Zeroconf()
        ip = get_preferred_ip()  # 获取优先的WiFi IP
        hostname = socket.gethostname()

        self.info = ServiceInfo(
            service_name,
            f"{hostname}.{service_name}",
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={"heart_beat_sign": heart_beat_sign},
            server=f"{hostname}.local.",
        )

    def start(self):
        self.zeroconf.register_service(self.info)

    def stop(self):
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

