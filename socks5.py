import re
import requests
from bs4 import BeautifulSoup
import time
import random
import socket
import socks
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_socks5_proxy(proxy, test_url="http://httpbin.org/ip", timeout=5):
    """Проверяет работоспособность SOCKS5 прокси"""
    try:
        ip, port = proxy.split(':')
        port = int(port)
        
        # Устанавливаем SOCKS5 прокси для socket
        socks.set_default_proxy(socks.SOCKS5, ip, port)
        socket.socket = socks.socksocket
        
        start_time = time.time()
        response = requests.get(test_url, timeout=timeout)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Восстанавливаем стандартный socket
        socks.set_default_proxy()
        
        if response.status_code == 200:
            print(f"✓ Рабочий прокси: {proxy} (время отклика: {response_time}мс)")
            return proxy
        else:
            print(f"✗ Не рабочий прокси: {proxy} (статус: {response.status_code})")
            return None
            
    except Exception as e:
        # Восстанавливаем стандартный socket в случае ошибки
        socks.set_default_proxy()
        print(f"✗ Ошибка прокси {proxy}: {str(e)[:50]}...")
        return None

def extract_socks5_from_text(text):
    """Извлекает SOCKS5 прокси из текста"""
    socks5_patterns = [
        r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b',
        r'socks5://(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}',
        r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}(?=:[A-Za-z\s]+)',
    ]
    
    proxies = set()
    
    for pattern in socks5_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            proxy = match.replace('socks5://', '')
            proxy = re.sub(r':[^:]+$', '', proxy) if proxy.count(':') > 1 else proxy
            proxies.add(proxy)
    
    return list(proxies)

def scrape_url(url, timeout=10):
    """Скрапит URL и извлекает SOCKS5 прокси"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        if 'text/html' in response.headers.get('content-type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
        else:
            text = response.text
        
        proxies = extract_socks5_from_text(text)
        return proxies
        
    except Exception as e:
        print(f"Ошибка при скрапинге {url}: {e}")
        return []

def read_urls_from_file(filename):
    """Читает URLs из файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return []

def save_proxies_to_file(proxies, filename):
    """Сохраняет прокси в файл"""
    with open(filename, 'w', encoding='utf-8') as file:
        for proxy in sorted(set(proxies)):
            file.write(proxy + '\n')

def check_proxies_parallel(proxies, max_workers=20, output_file='socks5work.txt'):
    """Проверяет прокси в многопоточном режиме и сохраняет результаты по мере нахождения"""
    working_proxies = []
    
    print(f"Начинаем проверку {len(proxies)} прокси...")
    
    # Создаем или очищаем файл для записи
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Рабочие SOCKS5 прокси\n")
        f.write(f"# Обновлено: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def proxy_callback(proxy):
        """Callback функция для сохранения найденного прокси"""
        if proxy:
            working_proxies.append(proxy)
            # Немедленно сохраняем в файл
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(proxy + '\n')
            print(f"✓ Сохранен рабочий прокси: {proxy}")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {
            executor.submit(check_socks5_proxy, proxy): proxy 
            for proxy in proxies
        }
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result:
                proxy_callback(result)
    
    return working_proxies

def collect_proxies_only():
    """Только сбор прокси без проверки"""
    input_file = 'socks5list.txt'
    output_file = 'socks5.txt'
    
    print("Чтение URLs из файла...")
    urls = read_urls_from_file(input_file)
    
    if not urls:
        print("Не найдено URLs для обработки.")
        return
    
    print(f"Найдено {len(urls)} URLs для обработки.")
    
    all_proxies = []
    
    # Сбор прокси
    for i, url in enumerate(urls, 1):
        print(f"Сбор прокси {i}/{len(urls)}: {url}")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        proxies = scrape_url(url)
        
        if proxies:
            print(f"Найдено {len(proxies)} прокси")
            all_proxies.extend(proxies)
        else:
            print("Прокси не найдены")
        
        time.sleep(random.uniform(1, 3))
    
    if not all_proxies:
        print("Не найдено ни одного SOCKS5 прокси")
        return
    
    # Убираем дубликаты
    unique_proxies = list(set(all_proxies))
    print(f"\nНайдено {len(unique_proxies)} уникальных прокси")
    
    # Сохраняем все найденные прокси
    save_proxies_to_file(unique_proxies, output_file)
    print(f"✓ Все найденные прокси сохранены в {output_file}")
    
    # Показываем часть списка
    print("\nПервые 10 найденных прокси:")
    for i, proxy in enumerate(unique_proxies[:10], 1):
        print(f"  {i:2d}. {proxy}")
    if len(unique_proxies) > 10:
        print(f"  ... и еще {len(unique_proxies) - 10} прокси")

def collect_and_check_proxies():
    """Сбор и проверка прокси"""
    input_file = 'socks5list.txt'
    output_file = 'socks5work.txt'
    
    print("Чтение URLs из файла...")
    urls = read_urls_from_file(input_file)
    
    if not urls:
        print("Не найдено URLs для обработки.")
        return
    
    print(f"Найдено {len(urls)} URLs для обработки.")
    
    all_proxies = []
    
    # Этап 1: Сбор прокси
    for i, url in enumerate(urls, 1):
        print(f"Сбор прокси {i}/{len(urls)}: {url}")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        proxies = scrape_url(url)
        
        if proxies:
            print(f"Найдено {len(proxies)} прокси")
            all_proxies.extend(proxies)
        else:
            print("Прокси не найдены")
        
        time.sleep(random.uniform(1, 3))
    
    if not all_proxies:
        print("Не найдено ни одного SOCKS5 прокси")
        return
    
    # Убираем дубликаты
    unique_proxies = list(set(all_proxies))
    print(f"\nНайдено {len(unique_proxies)} уникальных прокси")
    
    # Этап 2: Проверка работоспособности с автоматическим сохранением
    print("\nНачинаем проверку работоспособности прокси...")
    print(f"Результаты будут сохраняться в реальном времени в {output_file}")
    
    working_proxies = check_proxies_parallel(unique_proxies, output_file=output_file)
    
    # Финальная статистика
    if working_proxies:
        print(f"\n✓ Проверка завершена! Найдено {len(working_proxies)} рабочих SOCKS5 прокси")
        print(f"Все результаты сохранены в {output_file}")
        
        print("\nИтоговый список рабочих прокси:")
        for i, proxy in enumerate(working_proxies, 1):
            print(f"  {i:2d}. {proxy}")
    else:
        print("✗ Не найдено рабочих SOCKS5 прокси")
        # Создаем пустой файл с комментарием
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Не найдено рабочих SOCKS5 прокси\n")
            f.write(f"# Проверка выполнена: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def show_menu():
    """Показывает меню выбора"""
    print("\n" + "="*50)
    print("          SOCKS5 ПРОКСИ СБОРЩИК")
    print("="*50)
    print("1. Только собрать прокси (без проверки)")
    print("2. Собрать и проверить прокси на доступность")
    print("3. Выход")
    print("="*50)
    
    while True:
        choice = input("\nВыберите действие (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Неверный выбор! Пожалуйста, введите 1, 2 или 3.")

def main():
    """Основная функция с меню выбора"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            print("\nЗапуск сбора прокси...")
            collect_proxies_only()
            
        elif choice == '2':
            print("\nЗапуск сбора и проверки прокси...")
            collect_and_check_proxies()
            
        elif choice == '3':
            print("Выход из программы.")
            break
        
        # Спрашиваем, хочет ли пользователь продолжить
        continue_choice = input("\nХотите выполнить другую операцию? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes', 'д', 'да']:
            print("Выход из программы.")
            break

if __name__ == "__main__":
    main()