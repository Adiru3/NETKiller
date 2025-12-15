#!/usr/bin/env python3

import socket
import struct
import random
import threading
import time
from hashlib import sha1
import binascii
from collections import OrderedDict
import os
import ipaddress

class DHTScanner:
    def __init__(self):
        self.nodes = set()
        self.scanned_nodes = set()
        self.dht_port = 6881
        self.scanning = True
        self.lock = threading.Lock()
        self.nodes_file = "dht_nodes.txt"
        
        self.load_existing_nodes()

        self.stats = {
            'scanned': 0,
            'active': 0,
            'errors': 0,
            'neighbors_found': 0,
            'duplicates_skipped': 0,
            'existing_loaded': len(self.nodes),
            'phase': 'BOOTSTRAP'
        }
        
        self.bootstrap_nodes = self.get_working_bootstrap_nodes()
    
    def get_working_bootstrap_nodes(self):
        """Проверенные рабочие bootstrap ноды"""
        return [
            # Основные DHT bootstrap ноды
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("router.utorrent.com", 6881),
            ("dht.aelitis.com", 6881),
            
            # Проверенные публичные трекеры с DHT
            ("tracker.opentrackr.org", 1337),
            ("open.demonii.com", 1337),
            ("tracker.openbittorrent.com", 80),
            ("tracker.coppersurfer.tk", 6969),
            
            # Известные рабочие ноды
            ("67.215.246.10", 6881),  # opentracker
            ("87.98.162.88", 6881),   # В Европе
            ("212.129.33.50", 6881),
            ("195.154.177.123", 6881),
            ("54.37.135.31", 6881),
            
            # Дополнительные проверенные ноды
            ("91.121.59.153", 6881),
            ("188.165.225.183", 6881),
            ("62.138.0.158", 6881),
            ("208.83.20.20", 6881),
            ("74.208.149.119", 6881),
        ]
    
    def load_existing_nodes(self):
        """Загружаем существующие ноды из файла"""
        if os.path.exists(self.nodes_file):
            try:
                with open(self.nodes_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            ip, port = line.split(':', 1)
                            ip = ip.strip()
                            try:
                                port = int(port.strip())
                                node_key = f"{ip}:{port}"
                                self.nodes.add(node_key)
                            except ValueError:
                                continue
                print(f"✓ Loaded {len(self.nodes)} existing nodes from {self.nodes_file}")
            except Exception as e:
                print(f"✗ Error loading existing nodes: {e}")
        else:
            print("ℹ No existing nodes file found, starting fresh")
    
    def is_scanned(self, ip, port):
        """Проверяем, сканировали ли ноду"""
        node_key = f"{ip}:{port}"
        with self.lock:
            return node_key in self.scanned_nodes
    
    def mark_as_scanned(self, ip, port):
        """Помечаем ноду как проверенную"""
        node_key = f"{ip}:{port}"
        with self.lock:
            self.scanned_nodes.add(node_key)
    
    def is_duplicate_node(self, ip, port):
        """Проверяем дубликат ноды"""
        node_key = f"{ip}:{port}"
        with self.lock:
            return node_key in self.nodes
    
    def add_node(self, ip, port):
        """Добавляем ноду"""
        node_key = f"{ip}:{port}"
        with self.lock:
            if node_key in self.nodes:
                return False
            self.nodes.add(node_key)
            return True
    
    def save_node_immediately(self, ip, port):
        """Сохраняем ноду в файл"""
        try:
            if self.is_duplicate_node(ip, port):
                with self.lock:
                    self.stats['duplicates_skipped'] += 1
                return False
            
            if self.add_node(ip, port):
                with open(self.nodes_file, "a") as f:
                    f.write(f"{ip}:{port}\n")
                    f.flush()
                return True
            return False
        except Exception as e:
            return False

    def print_stats(self):
        phase_icons = {
            'BOOTSTRAP': '🎯',
            'NEIGHBORS_1': '🔍', 
            'NEIGHBORS_2': '🌐',
            'NEIGHBORS_3': '🚀'
        }
        icon = phase_icons.get(self.stats['phase'], '⚡')
        print(f"\r{icon} {self.stats['phase']} | Scanned: {self.stats['scanned']} | "
              f"Active: {self.stats['active']} | Neighbors: {self.stats['neighbors_found']} | "
              f"Errors: {self.stats['errors']} | Nodes: {len(self.nodes)}", end="")

    def create_node_id(self):
        """Создание случайного Node ID"""
        return os.urandom(20)
    
    def decode_nodes(self, nodes_data):
        """Декодирование списка нод из компактного формата"""
        nodes = []
        try:
            for i in range(0, len(nodes_data), 26):
                if i + 26 <= len(nodes_data):
                    node_info = nodes_data[i:i+26]
                    node_id = node_info[:20]
                    ip = socket.inet_ntoa(node_info[20:24])
                    port = struct.unpack("!H", node_info[24:26])[0]
                    nodes.append((ip, port))
        except:
            pass
        return nodes

    def send_dht_request(self, sock, ip, port, query):
        """Отправка DHT запроса с обработкой ошибок"""
        try:
            sock.sendto(query, (ip, port))
            response, addr = sock.recvfrom(2048)
            return response, addr
        except socket.timeout:
            return None, None
        except Exception as e:
            return None, None
    
    def create_ping_query(self):
        """Создание ping запроса"""
        transaction_id = os.urandom(2)
        query = {
            b"t": transaction_id,
            b"y": b"q",
            b"q": b"ping",
            b"a": {b"id": self.create_node_id()}
        }
        return self.bencode(query), transaction_id
    
    def create_find_node_query(self, target=None):
        """Создание find_node запроса"""
        if target is None:
            target = self.create_node_id()
        transaction_id = os.urandom(2)
        query = {
            b"t": transaction_id,
            b"y": b"q",
            b"q": b"find_node",
            b"a": {
                b"id": self.create_node_id(),
                b"target": target
            }
        }
        return self.bencode(query), transaction_id
    
    def bencode(self, data):
        """Кодирование в Bencode"""
        if isinstance(data, bytes):
            return str(len(data)).encode() + b':' + data
        elif isinstance(data, str):
            return self.bencode(data.encode())
        elif isinstance(data, int):
            return b'i' + str(data).encode() + b'e'
        elif isinstance(data, list):
            return b'l' + b''.join(self.bencode(item) for item in data) + b'e'
        elif isinstance(data, dict):
            result = b'd'
            for key in sorted(data.keys()):
                result += self.bencode(key) + self.bencode(data[key])
            return result + b'e'
        else:
            raise TypeError(f"Unsupported type: {type(data)}")
    
    def bdecode(self, data):
        """Декодирование Bencode"""
        try:
            def decode(data, index=0):
                if index >= len(data):
                    return None, index
                    
                if data[index:index+1] == b'i':
                    end_pos = data.find(b'e', index + 1)
                    number = int(data[index+1:end_pos])
                    return number, end_pos + 1
                    
                elif data[index:index+1] == b'l':
                    index += 1
                    result = []
                    while data[index:index+1] != b'e':
                        item, index = decode(data, index)
                        result.append(item)
                    return result, index + 1
                    
                elif data[index:index+1] == b'd':
                    index += 1
                    result = {}
                    while data[index:index+1] != b'e':
                        key, index = decode(data, index)
                        value, index = decode(data, index)
                        result[key] = value
                    return result, index + 1
                    
                elif data[index:index+1].isdigit():
                    colon_pos = data.find(b':', index)
                    length = int(data[index:colon_pos])
                    start_pos = colon_pos + 1
                    end_pos = start_pos + length
                    string_data = data[start_pos:end_pos]
                    return string_data, end_pos
                else:
                    raise ValueError("Unknown token")
            
            return decode(data)[0]
        except:
            return None

    def is_valid_dht_ip(self, ip):
        """Проверка валидности IP для DHT"""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            
            # Исключаем приватные и специальные сети
            if (ip_obj.is_private or 
                ip_obj.is_multicast or 
                ip_obj.is_loopback or
                ip_obj.is_link_local):
                return False
                
            # Исключаем зарезервированные диапазоны
            first_octet = int(ip.split('.')[0])
            if first_octet in (0, 10, 127, 169, 172, 192, 224, 240):
                return False
                
            return True
        except:
            return False

    def scan_single_node(self, ip, port, timeout=4, find_neighbors=True):
        """Сканирование одной ноды"""
        if self.is_scanned(ip, port):
            return []
            
        try:
            with self.lock:
                self.stats['scanned'] += 1
            
            self.mark_as_scanned(ip, port)
            
            if not self.is_valid_dht_ip(ip):
                return []
                
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            neighbors = []
            
            # Пинг ноды
            ping_query, ping_tid = self.create_ping_query()
            response, addr = self.send_dht_request(sock, ip, port, ping_query)
            
            if response:
                decoded = self.bdecode(response)
                if (decoded and 
                    decoded.get(b'y') == b'r' and 
                    decoded.get(b't') == ping_tid):
                    
                    print(f"✅ Active: {addr[0]}:{addr[1]}")
                    
                    with self.lock:
                        self.stats['active'] += 1
                    
                    self.save_node_immediately(addr[0], addr[1])
                    
                    # Запрос соседей
                    if find_neighbors:
                        find_query, find_tid = self.create_find_node_query()
                        response, _ = self.send_dht_request(sock, addr[0], addr[1], find_query)
                        
                        if response:
                            decoded = self.bdecode(response)
                            if (decoded and 
                                decoded.get(b'y') == b'r' and 
                                decoded.get(b't') == find_tid and
                                b'r' in decoded):
                                
                                nodes_data = decoded[b'r'].get(b'nodes', b'')
                                neighbors = self.decode_nodes(nodes_data)
                                
                                with self.lock:
                                    self.stats['neighbors_found'] += len(neighbors)
            
            return neighbors
            
        except Exception as e:
            with self.lock:
                self.stats['errors'] += 1
            return []
        finally:
            try:
                sock.close()
            except:
                pass

    def phase_bootstrap(self):
        """ФАЗА 1: Bootstrap ноды"""
        self.stats['phase'] = 'BOOTSTRAP'
        print(f"\n🎯 PHASE 1: BOOTSTRAP NODES ({len(self.bootstrap_nodes)} nodes)")
        
        active_count = 0
        all_neighbors = []
        
        for i, (ip, port) in enumerate(self.bootstrap_nodes):
            if not self.scanning:
                break
                
            print(f"  Scanning {i+1}/{len(self.bootstrap_nodes)}: {ip}:{port}")
            neighbors = self.scan_single_node(ip, port, timeout=5, find_neighbors=True)
            
            if neighbors:
                active_count += 1
                all_neighbors.extend(neighbors)
            
            self.print_stats()
        
        print(f"\n✅ Bootstrap completed: {active_count}/{len(self.bootstrap_nodes)} active, found {len(all_neighbors)} neighbors")
        return all_neighbors

    def phase_neighbors_level_1(self, neighbors_list):
        """ФАЗА 2: Соседи 1-го уровня"""
        self.stats['phase'] = 'NEIGHBORS_1'
        print(f"\n🔍 PHASE 2: LEVEL 1 NEIGHBORS ({len(neighbors_list)} nodes)")
        
        level_1_neighbors = []
        scanned_count = 0
        
        for i, (ip, port) in enumerate(neighbors_list):
            if not self.scanning:
                break
                
            if scanned_count >= 200:  # Ограничиваем количество сканирований
                break
                
            neighbors = self.scan_single_node(ip, port, timeout=3, find_neighbors=True)
            
            if neighbors:
                level_1_neighbors.extend(neighbors)
            
            scanned_count += 1
            
            if scanned_count % 20 == 0:
                print(f"  Scanned {scanned_count}/{min(200, len(neighbors_list))} neighbors...")
                self.print_stats()
        
        print(f"\n✅ Level 1 neighbors completed: {scanned_count} scanned, found {len(level_1_neighbors)} new neighbors")
        return level_1_neighbors

    def phase_neighbors_level_2(self, neighbors_list):
        """ФАЗА 3: Соседи 2-го уровня"""
        self.stats['phase'] = 'NEIGHBORS_2'
        print(f"\n🌐 PHASE 3: LEVEL 2 NEIGHBORS ({len(neighbors_list)} nodes)")
        
        level_2_neighbors = []
        scanned_count = 0
        
        for i, (ip, port) in enumerate(neighbors_list):
            if not self.scanning:
                break
                
            if scanned_count >= 300:  # Ограничиваем количество сканирований
                break
                
            neighbors = self.scan_single_node(ip, port, timeout=2, find_neighbors=True)
            
            if neighbors:
                level_2_neighbors.extend(neighbors)
            
            scanned_count += 1
            
            if scanned_count % 30 == 0:
                print(f"  Scanned {scanned_count}/{min(300, len(neighbors_list))} neighbors...")
                self.print_stats()
        
        print(f"\n✅ Level 2 neighbors completed: {scanned_count} scanned, found {len(level_2_neighbors)} new neighbors")
        return level_2_neighbors

    def phase_neighbors_level_3(self, neighbors_list):
        """ФАЗА 4: Соседи 3-го уровня"""
        self.stats['phase'] = 'NEIGHBORS_3'
        print(f"\n🚀 PHASE 4: LEVEL 3 NEIGHBORS ({len(neighbors_list)} nodes)")
        
        scanned_count = 0
        
        for i, (ip, port) in enumerate(neighbors_list):
            if not self.scanning:
                break
                
            if scanned_count >= 400:  # Ограничиваем количество сканирований
                break
                
            # На последнем уровне только пинг, без запроса соседей
            self.scan_single_node(ip, port, timeout=1, find_neighbors=False)
            scanned_count += 1
            
            if scanned_count % 40 == 0:
                print(f"  Scanned {scanned_count}/{min(400, len(neighbors_list))} neighbors...")
                self.print_stats()
        
        print(f"\n✅ Level 3 neighbors completed: {scanned_count} neighbors scanned")

    def start_scan(self):
        """Запуск сканирования с выбором источника"""
        print("🚀 Starting DHT Node Web Builder")
        print("Press Ctrl+C to stop\n")
        
        # Выбор режима сканирования
        print("🔍 Select scan mode:")
        print("1. Bootstrap nodes only")
        print("2. Existing nodes from file only") 
        print("3. Both (bootstrap + existing nodes)")
        
        try:
            choice = input("Enter choice (1-3, default 3): ").strip()
            if choice == "1":
                scan_mode = "bootstrap"
            elif choice == "2":
                scan_mode = "existing"
            else:
                scan_mode = "both"
        except:
            scan_mode = "both"
        
        print(f"\n🎯 Selected mode: {scan_mode.upper()}")
        
        start_time = time.time()
        self.scanning = True
        
        # Очередь для сканирования соседей
        neighbors_queue = []
        current_level = 0
        max_nodes_per_level = 500
        
        try:
            # Фаза 1: Начальные ноды в зависимости от выбора
            if scan_mode in ["bootstrap", "both"]:
                print(f"\n🎯 LEVEL {current_level}: BOOTSTRAP NODES ({len(self.bootstrap_nodes)} nodes)")
                bootstrap_neighbors = []
                
                for i, (ip, port) in enumerate(self.bootstrap_nodes):
                    if not self.scanning:
                        break
                        
                    print(f"  Scanning {i+1}/{len(self.bootstrap_nodes)}: {ip}:{port}")
                    neighbors = self.scan_single_node(ip, port, timeout=5, find_neighbors=True)
                    
                    if neighbors:
                        bootstrap_neighbors.extend(neighbors)
                    
                    self.print_stats()
                
                # Добавляем найденных соседей в очередь (без дубликатов)
                for neighbor in bootstrap_neighbors:
                    if not self.is_node_in_queue(neighbors_queue, neighbor):
                        neighbors_queue.append(neighbor)
                
                print(f"✅ Bootstrap: found {len(bootstrap_neighbors)} neighbors, queue: {len(neighbors_queue)}")
            
            if scan_mode in ["existing", "both"] and self.nodes:
                print(f"\n📁 LEVEL {current_level}: EXISTING NODES ({len(self.nodes)} nodes)")
                print(f"🔍 Checking ALL {len(self.nodes)} existing nodes for activity...")
                
                existing_neighbors = []
                # УБРАЛ РАНДОМИЗАЦИЮ - сканируем по порядку
                existing_nodes_list = list(self.nodes)
                
                checked_count = 0
                active_count = 0
                
                for node_str in existing_nodes_list:
                    if not self.scanning:
                        break
                        
                    ip, port_str = node_str.split(':')
                    port = int(port_str)
                    
                    # Пропускаем если уже сканировали в этой сессии
                    if self.is_scanned(ip, port):
                        continue
                        
                    if checked_count % 20 == 0:  # Показываем прогресс каждые 20 нод
                        print(f"  Progress: {checked_count}/{len(self.nodes)} nodes checked, {active_count} active")
                    
                    neighbors = self.scan_single_node(ip, port, timeout=3, find_neighbors=True)
                    
                    if neighbors:
                        existing_neighbors.extend(neighbors)
                        active_count += 1
                    
                    checked_count += 1
                    
                    if checked_count % 50 == 0:
                        self.print_stats()
                
                # Добавляем найденных соседей в очередь (без дубликатов)
                for neighbor in existing_neighbors:
                    if not self.is_node_in_queue(neighbors_queue, neighbor):
                        neighbors_queue.append(neighbor)
                
                print(f"✅ Existing nodes: checked ALL {checked_count} nodes, found {active_count} active, {len(existing_neighbors)} neighbors, queue: {len(neighbors_queue)}")
            
            current_level += 1
            
            if not neighbors_queue:
                print("❌ No active nodes found. Check network connection.")
                return list(self.nodes)
            
            print(f"\n✅ Initial scan completed: {len(neighbors_queue)} neighbors in queue")
            
            # БЕСКОНЕЧНЫЙ ЦИКЛ сканирования соседей
            while self.scanning and neighbors_queue and current_level <= 50:
                print(f"\n🔍 LEVEL {current_level}: NEIGHBORS (queue: {len(neighbors_queue)} nodes)")
                
                # Берем ноды из очереди для текущего уровня (ПО ПОРЯДКУ)
                current_level_nodes = []
                nodes_to_process = min(len(neighbors_queue), max_nodes_per_level)
                
                for i in range(nodes_to_process):
                    if neighbors_queue:
                        node = neighbors_queue.pop(0)
                        current_level_nodes.append(node)
                
                print(f"  Processing {len(current_level_nodes)} nodes at level {current_level}...")
                
                level_neighbors = []
                scanned_count = 0
                
                # Сканируем ноды текущего уровня ПО ПОРЯДКУ
                for ip, port in current_level_nodes:
                    if not self.scanning:
                        break
                    
                    if self.is_scanned(ip, port):
                        continue
                    
                    neighbors = self.scan_single_node(ip, port, timeout=3, find_neighbors=True)
                    
                    if neighbors:
                        for neighbor_ip, neighbor_port in neighbors:
                            if (self.is_valid_dht_ip(neighbor_ip) and 
                                not self.is_scanned(neighbor_ip, neighbor_port) and
                                not self.is_duplicate_node(neighbor_ip, neighbor_port) and
                                not self.is_node_in_queue(neighbors_queue, (neighbor_ip, neighbor_port)) and
                                not self.is_node_in_list(level_neighbors, (neighbor_ip, neighbor_port))):
                                
                                neighbors_queue.append((neighbor_ip, neighbor_port))
                                level_neighbors.append((neighbor_ip, neighbor_port))
                    
                    scanned_count += 1
                    
                    if scanned_count % 25 == 0:
                        print(f"    Scanned {scanned_count}/{len(current_level_nodes)} nodes, queue: {len(neighbors_queue)}")
                        self.print_stats()
                
                print(f"✅ Level {current_level} completed: scanned {scanned_count}, found {len(level_neighbors)} new neighbors, total queue: {len(neighbors_queue)}")
                
                # Если очередь пустая, пытаемся найти больше нод
                if len(neighbors_queue) < 100 and len(self.nodes) > 10:
                    print("🔄 Queue low - exploring existing nodes for more neighbors...")
                    self.explore_existing_nodes_for_neighbors(neighbors_queue)
                
                current_level += 1
                
                if self.scanning and neighbors_queue:
                    print("⏳ Preparing next level...")
                    time.sleep(2)
            
            if current_level > 5000000000:
                print("\n📈 Reached maximum level limit (5000000000). Scan completed.")
            
        except KeyboardInterrupt:
            print("\n⏹️ Scan stopped by user")
            self.scanning = False
        
        # Результаты
        elapsed_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"🎉 DHT Node WEB Builder")
        print(f"⏰ Time: {elapsed_time:.1f}s")
        print(f"📊 Total levels scanned: {current_level}")
        print(f"🏠 Total nodes found: {len(self.nodes)}")
        print(f"✅ Active responses: {self.stats['active']}")
        print(f"🔍 Neighbors discovered: {self.stats['neighbors_found']}")
        print(f"📋 Queue remaining: {len(neighbors_queue)}")
        print(f"{'='*60}")
        
        return list(self.nodes)

    def is_node_in_queue(self, queue, node):
        """Проверяет, есть ли нода в очереди"""
        ip, port = node
        for q_ip, q_port in queue:
            if q_ip == ip and q_port == port:
                return True
        return False

    def is_node_in_list(self, node_list, node):
        """Проверяет, есть ли нода в списке"""
        ip, port = node
        for n_ip, n_port in node_list:
            if n_ip == ip and n_port == port:
                return True
        return False

    def explore_existing_nodes_for_neighbors(self, neighbors_queue):
        """Исследуем существующие ноды для поиска новых соседей"""
        print("  Searching existing nodes for new neighbors...")
        
        existing_nodes = list(self.nodes)
        # УБРАЛ РАНДОМИЗАЦИЮ - проверяем по порядку
        
        explored_count = 0
        new_neighbors_found = 0
        
        for node_str in existing_nodes[:50]:  # Проверяем первые 50 нод
            if not self.scanning:
                break
                
            if explored_count >= 20:  # Ограничиваем количество проверок
                break
                
            ip, port_str = node_str.split(':')
            port = int(port_str)
            
            # Пропускаем если недавно сканировали
            if self.is_scanned(ip, port):
                continue
            
            neighbors = self.scan_single_node(ip, port, timeout=2, find_neighbors=True)
            
            if neighbors:
                for neighbor_ip, neighbor_port in neighbors:
                    if (self.is_valid_dht_ip(neighbor_ip) and 
                        not self.is_scanned(neighbor_ip, neighbor_port) and
                        not self.is_duplicate_node(neighbor_ip, neighbor_port) and
                        not self.is_node_in_queue(neighbors_queue, (neighbor_ip, neighbor_port))):
                        
                        neighbors_queue.append((neighbor_ip, neighbor_port))
                        new_neighbors_found += 1
            
            explored_count += 1
        
        if new_neighbors_found > 0:
            print(f"  ✅ Found {new_neighbors_found} new neighbors from existing nodes")


def main():
    scanner = DHTScanner()
    
    try:
        nodes = scanner.start_scan()
        
        # Сохраняем финальную статистику
        if nodes:
            print(f"\n💾 Results saved to {scanner.nodes_file}")
            print(f"📋 Total unique DHT nodes: {len(nodes)}")
            
            # Показываем топ 10 нод
            print(f"\n🏆 Top 10 active nodes:")
            nodes_list = list(nodes)[:10]
            for i, node in enumerate(nodes_list, 1):
                print(f"  {i}. {node}")
        else:
            print("\n❌ No DHT nodes found. Possible issues:")
            print("   - No internet connection")
            print("   - Firewall blocking UDP packets")
            print("   - Network restrictions")
            print("   - Bootstrap nodes temporarily unavailable")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scan stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()