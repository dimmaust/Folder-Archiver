import os
import subprocess
import time
import datetime
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import json
import sys
import requests

# Настройка логирования с явной поддержкой UTF-8
logging.basicConfig(
    filename='archiver.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True,
    encoding='utf-8'
)

class ArchiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Archiver")
        self.config_file = "archiver_config.json"
        self.config = self.load_config()
        self.auto_archive = False
        
        logging.info(f"Инициализация: self.config = {self.config}")
        self.create_widgets()
        
        if not self.config:
            logging.info("Первый запуск, ожидание ввода данных")
            self.wait_for_input()
        else:
            logging.info("Конфигурация найдена, запуск автоматической архивации через 15 секунд")
            self.root.after(15000, self.start_auto_archive)

    def create_widgets(self):
        tk.Label(self.root, text="Исходная папка:").grid(row=0, column=0, padx=5, pady=5)
        self.source_entry = tk.Entry(self.root, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Выбрать", command=self.select_source).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Папка назначения:").grid(row=1, column=0, padx=5, pady=5)
        self.dest_entry = tk.Entry(self.root, width=50)
        self.dest_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Выбрать", command=self.select_dest).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Глубина архива (дни):").grid(row=2, column=0, padx=5, pady=5)
        self.depth_entry = tk.Entry(self.root, width=50)
        self.depth_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Telegram Bot Token (опционально):").grid(row=3, column=0, padx=5, pady=5)
        self.token_entry = tk.Entry(self.root, width=50)
        self.token_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Telegram Chat ID (опционально):").grid(row=4, column=0, padx=5, pady=5)
        self.chat_id_entry = tk.Entry(self.root, width=50)
        self.chat_id_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Дополнительный текст для Telegram:").grid(row=5, column=0, padx=5, pady=5)
        self.custom_text_entry = tk.Entry(self.root, width=50)
        self.custom_text_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Сохранить", command=self.save_config).grid(row=6, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Сбросить", command=self.reset_fields).grid(row=6, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Архивировать", command=self.start_archive).grid(row=6, column=2, padx=5, pady=5)

        if self.config:
            self.source_entry.insert(0, self.config.get('source_path', ''))
            self.dest_entry.insert(0, self.config.get('dest_path', ''))
            self.depth_entry.insert(0, self.config.get('archive_depth', ''))
            self.token_entry.insert(0, self.config.get('telegram_token', ''))
            self.chat_id_entry.insert(0, self.config.get('chat_id', ''))
            self.custom_text_entry.insert(0, self.config.get('custom_text', ''))

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.info(f"Конфигурация загружена: {config}")
                return config
        except FileNotFoundError:
            logging.info("Конфигурационный файл не найден")
            return {}
        except Exception as e:
            logging.error(f"Ошибка загрузки конфигурации: {str(e)}")
            return {}

    def save_config(self):
        config = {
            'source_path': self.source_entry.get(),
            'dest_path': self.dest_entry.get(),
            'archive_depth': self.depth_entry.get(),
            'telegram_token': self.token_entry.get(),
            'chat_id': self.chat_id_entry.get(),
            'custom_text': self.custom_text_entry.get()
        }
        
        required_fields = ['source_path', 'dest_path', 'archive_depth']
        if not all(config[field] for field in required_fields):
            messagebox.showerror("Ошибка", "Все обязательные поля должны быть заполнены!")
            return
        
        try:
            depth = int(config['archive_depth'])
            if depth <= 0:
                raise ValueError("Глубина архива должна быть положительным числом")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
        self.config = config
        logging.info(f"Конфигурация сохранена: {config}")
        messagebox.showinfo("Успех", "Конфигурация сохранена!")

    def reset_fields(self):
        self.source_entry.delete(0, tk.END)
        self.dest_entry.delete(0, tk.END)
        self.depth_entry.delete(0, tk.END)
        self.token_entry.delete(0, tk.END)
        self.chat_id_entry.delete(0, tk.END)
        self.custom_text_entry.delete(0, tk.END)
        self.config = {}
        try:
            os.remove(self.config_file)
            logging.info("Конфигурационный файл удален")
        except FileNotFoundError:
            pass

    def select_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)

    def select_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)

    def send_telegram_message(self, message):
        self.config = self.load_config()
        logging.info(f"send_telegram_message: текущая конфигурация = {self.config}")
        
        token = self.config.get('telegram_token', '')
        chat_id = self.config.get('chat_id', '')
        
        if not token or not chat_id:
            logging.info("Отправка в Telegram пропущена: токен или chat_id не указаны")
            return
        
        custom_text = self.config.get('custom_text', '')
        full_message = f"{message}\n{custom_text}" if custom_text else message
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': full_message
        }
        
        logging.info(f"Попытка отправки в Telegram: url={url}, chat_id={chat_id}, message={full_message}")
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get('ok'):
                logging.info(f"Уведомление в Telegram успешно отправлено: {full_message}")
            else:
                logging.error(f"Ошибка Telegram API: {result}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка отправки в Telegram: {str(e)}")

    def archive_folder(self):
        if not self.config:
            logging.info("Архивация пропущена: конфигурация не загружена")
            return

        source_path = self.config['source_path']
        dest_path = self.config['dest_path']
        depth = int(self.config['archive_depth'])
        seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
        
        try:
            if not os.path.exists(seven_zip_path):
                raise FileNotFoundError("7-Zip не найден по указанному пути")

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"archive_{timestamp}.7z"
            archive_path = os.path.join(dest_path, archive_name)

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
                logging.info(f"Создана папка назначения: {dest_path}")

            # Используем cp866 для вывода 7-Zip в Windows (консольная кодировка)
            cmd = [seven_zip_path, 'a', '-t7z', archive_path, source_path, '-r']
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='cp866')
            
            # Логируем полный вывод для диагностики
            logging.info(f"7-Zip stdout: {result.stdout}")
            if result.stderr:
                logging.warning(f"7-Zip stderr: {result.stderr}")

            # Проверяем, создан ли архив, даже если есть предупреждения
            if result.returncode != 0 and not os.path.exists(archive_path):
                error_msg = result.stderr or result.stdout
                raise Exception(f"Ошибка 7-Zip: {error_msg}")
            
            logging.info(f"Архивация успешно завершена: {archive_name}")

            # Ротация только архивов программы (archive_*.7z)
            current_time = time.time()
            for file in os.listdir(dest_path):
                file_path = os.path.join(dest_path, file)
                if file.endswith('.7z') and file.startswith('archive_') and os.path.isfile(file_path):
                    creation_time = os.path.getctime(file_path)
                    age_in_seconds = current_time - creation_time
                    age_in_days = age_in_seconds / (24 * 3600)
                    if age_in_days > depth:
                        try:
                            os.remove(file_path)
                            logging.info(f"Удален старый архив: {file_path} (возраст: {age_in_days:.2f} дней)")
                        except Exception as remove_error:
                            logging.error(f"Ошибка удаления старого архива {file_path}: {str(remove_error)}")

            self.send_telegram_message(f"Архивация успешно завершена: {archive_name}")

        except Exception as e:
            error_msg = f"Ошибка архивации: {str(e)}"
            logging.error(error_msg)
            self.send_telegram_message(error_msg)
        
        finally:
            logging.info("Завершение работы программы")
            self.root.after(1000, self.root.destroy)

    def start_archive(self):
        if not self.config:
            messagebox.showerror("Ошибка", "Сначала сохраните конфигурацию!")
            return
        Thread(target=self.archive_folder).start()

    def start_auto_archive(self):
        if not self.auto_archive:
            self.auto_archive = True
            self.start_archive()

    def wait_for_input(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArchiverApp(root)
    root.mainloop()