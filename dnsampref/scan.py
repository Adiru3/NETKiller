#!/usr/bin/env python3
"""
REAL DNS Amplification Vulnerability Scanner
Проверяет реальный коэффициент усиления для ANY, DNSKEY, TXT запросов
Сохраняет IP отдельно от детальной информации
"""

import subprocess
import ipaddress
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import time
import threading
import csv
import json
import struct
import random

def is_ipv4(ip_str):
    """Проверяет, является ли строка IPv4 адресом"""
    try:
        ipaddress.IPv4Address(ip_str.strip())
        return True
    except ipaddress.AddressValueError:
        return False

def create_dns_query(domain, query_type):
    """
    Создает DNS запрос для указанного типа
    query_type: 'ANY', 'DNSKEY', 'TXT'
    """
    query = bytearray()
    # DNS header - случайный ID для отслеживания
    query_id = random.randint(0, 65535)
    query.extend(struct.pack('>H', query_id))
    query.extend(b'\x01\x00')  # Flags: стандартный запрос
    query.extend(b'\x00\x01')  # 1 вопрос
    query.extend(b'\x00\x00')  # 0 ответов
    query.extend(b'\x00\x00')  # 0 authoritative
    query.extend(b'\x00\x00')  # 0 additional
    
    # Question section
    domains = domain.split('.')
    for domain_part in domains:
        query.append(len(domain_part))
        query.extend(domain_part.encode())
    query.extend(b'\x00')  # конец домена
    
    # TYPE в зависимости от запроса
    if query_type == 'ANY':
        query.extend(b'\x00\xff')  # TYPE = ANY (255)
    elif query_type == 'DNSKEY':
        query.extend(b'\x00\x30')  # TYPE = DNSKEY (48)
    elif query_type == 'TXT':
        query.extend(b'\x00\x10')  # TYPE = TXT (16)
    
    query.extend(b'\x00\x01')  # CLASS = IN (1)
    
    return query, query_id

def test_reflection_vulnerability(ip, spoofed_ip, test_domain="isc.org", query_type='ANY'):
    """
    Тестирует возможность reflection атаки
    Отправляет запрос с подмененным IP и проверяет, принимается ли он
    """
    try:
        # Создаем RAW socket для отправки спуфленного пакета
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        
        # Создаем IP заголовок с подмененным source IP
        ip_header = create_ip_header(spoofed_ip, ip)
        
        # Создаем DNS запрос
        dns_query, query_id = create_dns_query(test_domain, query_type)
        
        # Создаем UDP заголовок
        udp_header = create_udp_header(53, 53, ip_header + dns_query)
        
        # Полный пакет
        packet = ip_header + udp_header + dns_query
        
        # Создаем сокет для прослушивания ответов
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.settimeout(3.0)
        listen_sock.bind(('0.0.0.0', 53535))  # случайный порт для прослушивания
        
        # Отправляем спуфленный пакет
        sock.sendto(packet, (ip, 0))
        
        # Пытаемся получить ответ
        start_time = time.time()
        try:
            response, addr = listen_sock.recvfrom(8192)
            response_time = time.time() - start_time
            
            # Проверяем, соответствует ли ID ответа нашему запросу
            if len(response) >= 2:
                response_id = struct.unpack('>H', response[:2])[0]
                if response_id == query_id:
                    return {
                        'reflection_success': True,
                        'response_time': response_time,
                        'response_size': len(response),
                        'error': None
                    }
        
        except socket.timeout:
            pass
            
        sock.close()
        listen_sock.close()
        
        return {
            'reflection_success': False,
            'response_time': 0,
            'response_size': 0,
            'error': 'no_response'
        }
        
    except Exception as e:
        return {
            'reflection_success': False,
            'response_time': 0,
            'response_size': 0,
            'error': str(e)
        }

def create_ip_header(source_ip, dest_ip):
    """Создает IP заголовок для RAW socket"""
    # Упрощенный IP заголовок
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 0  # заполнится ядром
    ip_id = random.randint(0, 65535)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_UDP
    ip_check = 0
    ip_saddr = socket.inet_aton(source_ip)
    ip_daddr = socket.inet_aton(dest_ip)
    
    ip_ihl_ver = (ip_ver << 4) + ip_ihl
    
    # Упаковываем заголовок
    ip_header = struct.pack('!BBHHHBBH4s4s',
                           ip_ihl_ver, ip_tos, ip_tot_len,
                           ip_id, ip_frag_off, ip_ttl,
                           ip_proto, ip_check, ip_saddr, ip_daddr)
    return ip_header

def create_udp_header(src_port, dest_port, data):
    """Создает UDP заголовок"""
    length = 8 + len(data)
    checksum = 0
    
    udp_header = struct.pack('!HHHH', src_port, dest_port, length, checksum)
    return udp_header

def test_dns_amplification_full(ip, test_domain="isc.org"):
    """
    Тестирует реальный коэффициент усиления DNS для всех типов запросов
    Возвращает словарь с результатами для каждого типа
    """
    results = {}
    query_types = ['ANY', 'DNSKEY', 'TXT']
    
    for qtype in query_types:
        try:
            # Создаем DNS запрос
            query, query_id = create_dns_query(test_domain, qtype)
            
            # Отправляем запрос
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)
            
            request_size = len(query)
            start_time = time.time()
            sock.sendto(query, (ip, 53))
            response, addr = sock.recvfrom(8192)
            response_time = time.time() - start_time
            sock.close()
            
            response_size = len(response)
            
            # Рассчитываем коэффициент усиления
            amplification_factor = 0
            if request_size > 0 and response_size > request_size:
                amplification_factor = response_size / request_size
                
            results[qtype] = {
                'amplification': amplification_factor,
                'response_time': response_time,
                'response_size': response_size,
                'request_size': request_size,
                'success': True
            }
            
        except socket.timeout:
            results[qtype] = {
                'amplification': 0,
                'response_time': 0,
                'response_size': 0,
                'request_size': 0,
                'success': False,
                'error': 'timeout'
            }
        except Exception as e:
            results[qtype] = {
                'amplification': 0,
                'response_time': 0,
                'response_size': 0,
                'request_size': 0,
                'success': False,
                'error': str(e)
            }
    
    return results

def test_combined_vulnerability(ip, spoofed_ip="8.8.8.8"):
    """
    Комплексная проверка amplification + reflection
    """
    # Тестируем amplification
    amp_results = test_dns_amplification_full(ip)
    
    # Тестируем reflection для лучшего типа запроса
    best_amp, best_type = get_best_amplification(amp_results)
    
    reflection_results = {}
    if best_amp > 0:
        reflection_results = test_reflection_vulnerability(ip, spoofed_ip, query_type=best_type)
    else:
        reflection_results = {'reflection_success': False, 'error': 'no_amplification'}
    
    return {
        'amplification': amp_results,
        'reflection': reflection_results,
        'best_amplification': best_amp,
        'best_type': best_type
    }

def get_best_amplification(results):
    """Возвращает лучший коэффициент усиления из всех типов запросов"""
    best_amp = 0
    best_type = None
    
    for qtype, data in results.items():
        if data['success'] and data['amplification'] > best_amp:
            best_amp = data['amplification']
            best_type = qtype
    
    return best_amp, best_type

def is_vulnerable(results, min_amplification=5):
    """Определяет, является ли сервер уязвимым"""
    amp_vulnerable = results['best_amplification'] >= min_amplification
    reflection_vulnerable = results['reflection']['reflection_success']
    
    return {
        'vulnerable': amp_vulnerable and reflection_vulnerable,
        'amplification_only': amp_vulnerable and not reflection_vulnerable,
        'reflection_only': not amp_vulnerable and reflection_vulnerable,
        'risk_level': 'HIGH' if (amp_vulnerable and reflection_vulnerable) else 
                     'MEDIUM' if amp_vulnerable else 
                     'LOW' if reflection_vulnerable else 'NONE'
    }

def save_results(ip_file, details_file, ip, results, min_amplification=5):
    """Сохраняет результаты в два файла (потокобезопасно)"""
    try:
        with threading.Lock():
            vulnerability = is_vulnerable(results, min_amplification)
            amp_results = results['amplification']
            
            # Сохраняем IP только если есть полная уязвимость
            if vulnerability['vulnerable']:
                ip_exists = os.path.exists(ip_file)
                with open(ip_file, 'a', encoding='utf-8') as f:
                    if not ip_exists or os.path.getsize(ip_file) == 0:
                        f.write("# Уязвимые DNS серверы (amplification + reflection)\n")
                    f.write(f"{ip} # {results['best_amplification']:.1f}x {vulnerability['risk_level']}\n")
            
            # Сохраняем детальную информацию в CSV для всех IP
            details_exists = os.path.exists(details_file)
            with open(details_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if not details_exists or os.path.getsize(details_file) == 0:
                    writer.writerow([
                        'IP', 'Risk_Level', 'Vulnerable', 'Amp_Only', 'Refl_Only',
                        'Best_Amplification', 'Best_Type', 'Reflection_Success',
                        'ANY_Amplification', 'ANY_Size', 'ANY_Time',
                        'DNSKEY_Amplification', 'DNSKEY_Size', 'DNSKEY_Time', 
                        'TXT_Amplification', 'TXT_Size', 'TXT_Time',
                        'Reflection_Time', 'Reflection_Size', 'Timestamp'
                    ])
                
                writer.writerow([
                    ip, 
                    vulnerability['risk_level'],
                    vulnerability['vulnerable'],
                    vulnerability['amplification_only'],
                    vulnerability['reflection_only'],
                    f"{results['best_amplification']:.2f}", 
                    results['best_type'],
                    results['reflection']['reflection_success'],
                    f"{amp_results['ANY']['amplification']:.2f}",
                    amp_results['ANY']['response_size'],
                    f"{amp_results['ANY']['response_time']:.3f}",
                    f"{amp_results['DNSKEY']['amplification']:.2f}",
                    amp_results['DNSKEY']['response_size'],
                    f"{amp_results['DNSKEY']['response_time']:.3f}",
                    f"{amp_results['TXT']['amplification']:.2f}",
                    amp_results['TXT']['response_size'],
                    f"{amp_results['TXT']['response_time']:.3f}",
                    f"{results['reflection']['response_time']:.3f}",
                    results['reflection']['response_size'],
                    time.strftime('%Y-%m-%d %H:%M:%S')
                ])
                
    except Exception as e:
        print(f"Ошибка сохранения IP {ip}: {e}")

def scan_dns_amplification(input_file, output_ip_file, output_details_file, min_amplification=5, max_workers=20):
    """Сканирует на реальную amplification уязвимость для всех типов запросов"""
    
    print("=== REAL DNS Amplification Scanner ===")
    print("Проверяет типы запросов: ANY, DNSKEY, TXT")
    print(f"Минимальный коэффициент усиления: {min_amplification}x")
    print(f"Файл с IP: {output_ip_file}")
    print(f"Файл с деталями: {output_details_file}")
    print(f"Результаты сохраняются сразу при обнаружении")
    print("-" * 60)
    
    # Читаем IP адреса
    with open(input_file, 'r') as f:
        ip_list = [line.strip() for line in f if line.strip() and is_ipv4(line.strip())]
    
    print(f"Начинаем сканирование {len(ip_list)} серверов...")
    
    # Создаем/очищаем файлы результатов
    open(output_ip_file, 'w').close()
    open(output_details_file, 'w').close()
    
    vulnerable_ips = []
    scanned_count = 0
    start_time = time.time()
    
    def process_result(ip, results):
        nonlocal scanned_count, vulnerable_ips
        
        scanned_count += 1
        elapsed_time = time.time() - start_time
        ips_per_second = scanned_count / elapsed_time if elapsed_time > 0 else 0
        
        best_amp, best_type = get_best_amplification(results)
        
        if best_amp >= min_amplification:
            vulnerable_ips.append((ip, best_amp, best_type, results))
            
            # Сохраняем сразу при обнаружении в оба файла
            save_results(output_ip_file, output_details_file, ip, results, min_amplification)
            
            # В функции process_result замените вывод:
            print(f"🚨 УЯЗВИМ: {ip} | Усиление: {best_amp:.1f}x ({best_type}) | "
                  f"Reflection: {'YES' if results['reflection']['reflection_success'] else 'NO'} | "
                  f"ANY: {results['amplification']['ANY']['amplification']:.1f}x | "
                  f"DNSKEY: {results['amplification']['DNSKEY']['amplification']:.1f}x | "
                  f"TXT: {results['amplification']['TXT']['amplification']:.1f}x")
        else:
            # Прогресс каждые 25 сканов или каждые 5 секунд
            if scanned_count % 25 == 0 or elapsed_time % 5 < 0.1:
                print(f"📊 Прогресс: {scanned_count}/{len(ip_list)} | "
                      f"Уязвимых: {len(vulnerable_ips)} | "
                      f"Скорость: {ips_per_second:.1f} IP/сек")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_combined_vulnerability, ip): ip for ip in ip_list}
        
        for future in as_completed(futures):
            ip = futures[future]
            results = future.result()
            process_result(ip, results)
    
    # Финальная статистика
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("СКАНИРОВАНИЕ ЗАВЕРШЕНО!")
    print(f"Всего просканировано: {scanned_count} IP")
    print(f"Найдено уязвимых: {len(vulnerable_ips)}")
    print(f"Общее время: {total_time:.1f} секунд")
    print(f"Средняя скорость: {scanned_count/total_time:.1f} IP/сек")
    print(f"IP адреса сохранены в: {output_ip_file}")
    print(f"Детальная информация в: {output_details_file}")
    
    if vulnerable_ips:
        # Анализ эффективности типов запросов
        type_stats = {'ANY': 0, 'DNSKEY': 0, 'TXT': 0}
        for ip, amp, best_type, results in vulnerable_ips:
            type_stats[best_type] += 1
        
        print(f"\n📈 Эффективность типов запросов:")
        for qtype, count in type_stats.items():
            percentage = (count / len(vulnerable_ips)) * 100
            print(f"  {qtype}: {count} серверов ({percentage:.1f}%)")
        
        # Сортируем для красивого вывода топа
        vulnerable_ips.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🎯 Топ-5 самых опасных серверов:")
        for i, (ip, amp, best_type, results) in enumerate(vulnerable_ips[:5], 1):
            print(f"  {i}. {ip} - {amp:.1f}x ({best_type}) | "
                f"ANY:{results['amplification']['ANY']['amplification']:.1f}x "
                f"DNSKEY:{results['amplification']['DNSKEY']['amplification']:.1f}x "
                f"TXT:{results['amplification']['TXT']['amplification']:.1f}x")

        # Создаем отсортированный файл с IP
        sorted_ip_file = output_ip_file.replace('.txt', '_sorted.txt')
        with open(sorted_ip_file, 'w', encoding='utf-8') as f:
            f.write("# Уязвимые DNS серверы (отсортировано по коэффициенту усиления)\n")
            for ip, amp, best_type, _ in vulnerable_ips:
                f.write(f"{ip} # {amp:.1f}x ({best_type})\n")
        print(f"📁 Отсортированные IP также в: {sorted_ip_file}")
    else:
        print("\n❌ Уязвимых серверов не найдено")

def main():
    print("=== DNS Amplification & Reflection Vulnerability Scanner ===")
    print("⚠️  ВНИМАНИЕ: Используйте только для тестирования собственных сетей!")
    print("⚠️  Сканирование чужих сетей без разрешения может быть незаконно!")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("Использование: python dns_amp_refl_scanner.py <input_file> <output_ip_file> [min_amplification]")
        print("Пример: python dns_amp_refl_scanner.py dns_servers.txt vulnerable_ips.txt")
        print("\nПроверяет:")
        print("  • Amplification: ANY, DNSKEY, TXT запросы")
        print("  • Reflection: возможность спуфинга source IP")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_ip_file = sys.argv[2]
    
    # Генерируем имя для файла с деталями на основе основного файла
    if output_ip_file.endswith('.txt'):
        output_details_file = output_ip_file.replace('.txt', '_details.csv')
    else:
        output_details_file = output_ip_file + '_details.csv'
    
    # Опциональный параметр - минимальный коэффициент усиления
    min_amplification = 2
    if len(sys.argv) > 3:
        try:
            min_amplification = float(sys.argv[3])
            print(f"Установлен минимальный коэффициент усиления: {min_amplification}x")
        except ValueError:
            print(f"Ошибка: {sys.argv[3]} не является числом, используем по умолчанию 2x")
    
    if not os.path.exists(input_file):
        print(f"Ошибка: Файл {input_file} не найден!")
        sys.exit(1)
    
    try:
        scan_dns_amplification(
            input_file=input_file,
            output_ip_file=output_ip_file,
            output_details_file=output_details_file,
            min_amplification=min_amplification,
            max_workers=50
        )
    except KeyboardInterrupt:
        print("\n⏹️ Сканирование прервано пользователем")
        print("Частичные результаты сохранены в файлы:")
        print(f"  IP: {output_ip_file}")
        print(f"  Детали: {output_details_file}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()