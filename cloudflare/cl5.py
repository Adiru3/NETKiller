import socket
import requests
import dns.resolver
from urllib.parse import urlparse

def comprehensive_ip_finder(domain):
    """
    Комплексный поиск реального IP адреса
    """
    print(f"Поиск реального IP для: {domain}")
    print("=" * 50)
    
    # 1. Стандартный DNS lookup
    try:
        standard_ip = socket.gethostbyname(domain)
        print(f"Стандартный DNS: {standard_ip}")
        
        # Проверяем, является ли IP Cloudflare
        if is_cloudflare_ip(standard_ip):
            print("⚠️  Вероятно Cloudflare IP")
        else:
            print("✅ Возможно реальный IP")
    except Exception as e:
        print(f"Ошибка DNS lookup: {e}")
    
    # 2. Проверка MX записей (часто указывают на реальный сервер)
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        print(f"MX записи: {[str(r.exchange) for r in mx_records]}")
    except:
        print("MX записи не найдены")
    
    # 3. Проверка TXT записей
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        print(f"TXT записи: {[str(r) for r in txt_records]}")
    except:
        print("TXT записи не найдены")

def is_cloudflare_ip(ip):
    """
    Проверка, принадлежит ли IP диапазону Cloudflare
    """
    cloudflare_ranges = [
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
        "162.158.0.0/15",
        "104.16.0.0/13",
        "104.24.0.0/14",
        "172.64.0.0/13",
        "131.0.72.0/22"
    ]
    
    from ipaddress import ip_address, ip_network
    ip_addr = ip_address(ip)
    
    for range_ip in cloudflare_ranges:
        if ip_addr in ip_network(range_ip):
            return True
    return False

# Основная функция
if __name__ == "__main__":
    domain = input("Введите домен для анализа: ").strip()
    comprehensive_ip_finder(domain)