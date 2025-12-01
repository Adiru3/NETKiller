import requests
import json

def check_ip_services(domain):
    """
    Использование публичных сервисов для проверки реального IP
    """
    services = [
        f"https://api.hackertarget.com/hostsearch/?q={domain}",
        f"https://api.viewdns.info/iphistory/?domain={domain}&apikey=8dd524dabd81fd111c1c6b87e73e5a1037851d37",
        f"https://www.whoisxmlapi.com/whoisserver/WhoisService?domainName={domain}&outputFormat=JSON"
    ]
    
    found_ips = []
    
    for service in services:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                # Парсим ответ в зависимости от сервиса
                if 'hackertarget' in service:
                    data = response.text
                    for line in data.split('\n'):
                        if domain in line:
                            ip = line.split(',')[1].strip()
                            found_ips.append(ip)
        except Exception as e:
            print(f"Service error: {e}")
    
    return list(set(found_ips))

# Использование
domain = "gua.pub"
ips = check_ip_services(domain)
print(f"IP из сервисов: {ips}")