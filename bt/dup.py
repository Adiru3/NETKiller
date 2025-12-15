#!/usr/bin/env python3
"""
DHT Nodes Duplicate Cleaner
Удаляет дубликаты из файла dht_nodes.txt
"""

import os
import sys
from collections import OrderedDict

def remove_duplicates(input_file="dht_nodes.txt", output_file=None, backup=True):
    """
    Удаляет дубликаты из файла с DHT нодами
    
    Args:
        input_file: входной файл с нодами
        output_file: выходной файл (по умолчанию перезаписывает входной)
        backup: создавать ли резервную копию
    """
    
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден!")
        return False
    
    if output_file is None:
        output_file = input_file
    
    # Читаем исходный файл
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False
    
    original_count = len(lines)
    print(f"📊 Прочитано {original_count} строк из {input_file}")
    
    # Убираем дубликаты с сохранением порядка
    unique_nodes = OrderedDict()
    duplicates_count = 0
    invalid_lines = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Пропускаем пустые строки
        if not line:
            continue
            
        # Пропускаем комментарии
        if line.startswith('#'):
            unique_nodes[line] = True
            continue
            
        # Проверяем формат "ip:port"
        if ':' not in line:
            print(f"⚠️  Строка {line_num}: неверный формат - '{line}'")
            invalid_lines += 1
            continue
            
        # Нормализуем (убираем лишние пробелы)
        parts = line.split(':', 1)
        ip = parts[0].strip()
        port = parts[1].strip()
        
        # Создаем нормализованную версию
        normalized_line = f"{ip}:{port}"
        
        # Проверяем дубликат
        if normalized_line in unique_nodes:
            print(f"🔍 Найден дубликат: {normalized_line}")
            duplicates_count += 1
        else:
            unique_nodes[normalized_line] = True
    
    # Создаем резервную копию
    if backup and input_file == output_file:
        backup_file = f"{input_file}.backup"
        try:
            import shutil
            shutil.copy2(input_file, backup_file)
            print(f"💾 Создана резервная копия: {backup_file}")
        except Exception as e:
            print(f"⚠️  Не удалось создать резервную копию: {e}")
    
    # Записываем результат
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for node in unique_nodes.keys():
                f.write(node + '\n')
        
        new_count = len(unique_nodes)
        print(f"✅ Успешно обработано!")
        print(f"📈 Статистика:")
        print(f"   Исходное количество строк: {original_count}")
        print(f"   Найдено дубликатов: {duplicates_count}")
        print(f"   Неверных строк: {invalid_lines}")
        print(f"   Уникальных нод: {new_count}")
        print(f"   Удалено строк: {original_count - new_count}")
        print(f"💾 Результат сохранен в: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка записи файла: {e}")
        return False

def validate_nodes_file(filename="dht_nodes.txt"):
    """
    Проверяет валидность нод в файле
    """
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return
    
    valid_nodes = 0
    invalid_nodes = 0
    
    print(f"🔍 Проверка валидности нод в {filename}:")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
            
        if ':' not in line:
            print(f"   ❌ Строка {line_num}: неверный формат - '{line}'")
            invalid_nodes += 1
            continue
            
        parts = line.split(':', 1)
        ip = parts[0].strip()
        port_str = parts[1].strip()
        
        # Проверяем порт
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                print(f"   ❌ Строка {line_num}: неверный порт - {port}")
                invalid_nodes += 1
                continue
        except ValueError:
            print(f"   ❌ Строка {line_num}: порт не число - '{port_str}'")
            invalid_nodes += 1
            continue
        
        valid_nodes += 1
    
    print(f"📊 Результат проверки:")
    print(f"   ✅ Валидных нод: {valid_nodes}")
    print(f"   ❌ Невалидных нод: {invalid_nodes}")
    print(f"   📝 Всего строк: {len(lines)}")

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='DHT Nodes Duplicate Cleaner - Удаляет дубликаты из файла с DHT нодами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры использования:
  %(prog)s                          # Удалить дубликаты из dht_nodes.txt
  %(prog)s --input nodes.txt        # Указать входной файл
  %(prog)s --output clean.txt       # Сохранить в новый файл
  %(prog)s --no-backup             # Не создавать резервную копию
  %(prog)s --validate              # Только проверить файл
  %(prog)s --stats                 # Показать статистику файла
        '''
    )
    
    parser.add_argument('--input', '-i', default='dht_nodes.txt',
                       help='Входной файл с DHT нодами (по умолчанию: dht_nodes.txt)')
    parser.add_argument('--output', '-o', 
                       help='Выходной файл (по умолчанию перезаписывает входной)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Не создавать резервную копию')
    parser.add_argument('--validate', action='store_true',
                       help='Проверить валидность нод в файле')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику файла')
    
    args = parser.parse_args()
    
    print("🔄 DHT Nodes Duplicate Cleaner")
    print("=" * 50)
    
    if args.validate:
        validate_nodes_file(args.input)
        return
    
    if args.stats:
        if not os.path.exists(args.input):
            print(f"❌ Файл {args.input} не найден!")
            return
        
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        unique_nodes = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and ':' in line:
                unique_nodes.add(line)
        
        print(f"📊 Статистика файла {args.input}:")
        print(f"   📝 Всего строк: {len(lines)}")
        print(f"   🔗 Уникальных нод: {len(unique_nodes)}")
        print(f"   📋 Дубликатов: {len(lines) - len(unique_nodes)}")
        return
    
    # Основная функция удаления дубликатов
    success = remove_duplicates(
        input_file=args.input,
        output_file=args.output,
        backup=not args.no_backup
    )
    
    if success:
        print("\n🎉 Очистка завершена успешно!")
    else:
        print("\n💥 Очистка завершена с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    main()