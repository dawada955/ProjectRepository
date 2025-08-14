import os
import socket
import subprocess
import sys
import winreg

import psutil


def check_port_advanced(port: int) -> bool:
    """检测端口是否被占用，并返回占用进程信息"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:  # 端口可连接
            # 获取占用进程信息（跨平台）
            if sys.platform.startswith('win'):
                cmd = f"netstat -ano | findstr :{port}"
            else:
                cmd = f"lsof -i :{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(f"端口 {port} 被占用，进程信息:\n{result.stdout}")
            return True
    return False


def find_contiguous_free_ports(start: int, count: int) -> list:
    """找到连续的多个空闲端口"""
    ports = []
    current_port = start
    while len(ports) < count:
        if not check_port_advanced(current_port):
            ports.append(current_port)
            current_port += 1
        else:
            ports.clear()
            current_port += 1
    return ports[:count]


def find_free_port(start_port: int, max_retries: int,) -> int:
    """自动检测并返回可用端口，附带进程清理建议"""
    port = start_port
    while check_port_advanced(port):
        port += 1
        if port == start_port + max_retries:
            return -1
    return port


def is_process_running(name):
    return any(p.name() == name for p in psutil.process_iter())


def resource_path(relative_path):
    """获取资源文件路径，兼容 PyInstaller 打包后"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def enable_auto_start():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    exe_path = sys.executable  # 获取当前Python打包后的exe路径
    winreg.SetValueEx(key, "WeTransferApp", 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)


def disable_auto_start():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "WeTransferApp")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass  # 没有的话直接忽略


def get_preferred_ip():
    wifi_keywords = ['wlan', 'wi-fi', 'wifi']  # 常见WLAN名称关键字
    candidates = []

    addrs = psutil.net_if_addrs()
    for iface_name, iface_addrs in addrs.items():
        for addr in iface_addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                if any(keyword in iface_name.lower() for keyword in wifi_keywords):
                    # 如果是WiFi网卡，优先返回
                    # print(f"Found WiFi IP: {addr.address} on interface {iface_name}")
                    return addr.address
                else:
                    candidates.append((iface_name, addr.address))

    # 如果没有WiFi，退而选其他非回环网卡
    if candidates:
        # print(f"Fallback to {candidates[0][1]} on interface {candidates[0][0]}")
        return candidates[0][1]

    # 如果都没有，返回127.0.0.1
    # print("No valid network interface found, using 127.0.0.1")
    return '127.0.0.1'
