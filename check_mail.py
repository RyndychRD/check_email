import imaplib
import time
import os
import sys
import json
import platform

# Путь к файлу конфигурации
CONFIG_FILE = 'config.json'

def show_error(message):
    """Показывает ошибку с использованием стандартных средств ОС."""
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, "Ошибка", 0x10)
    elif platform.system() == 'Darwin':  # macOS
        os.system(f'osascript -e \'display dialog "{message}" with title "Ошибка" with icon stop\'')
    else:  # Linux и другие
        os.system(f'notify-send "Ошибка" "{message}" --urgency=critical')
    sys.exit(1)

def load_config():
    """Загружает конфигурацию из файла config.json."""
    if not os.path.exists(CONFIG_FILE):
        show_error(f"Файл конфигурации '{CONFIG_FILE}' не найден.")

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        show_error(f"Файл '{CONFIG_FILE}' содержит некорректный JSON.")

    # Проверка наличия всех необходимых ключей
    required_keys = ['IMAP_SERVER', 'EMAIL', 'PASSWORD', 'CHECK_INTERVAL']
    for key in required_keys:
        if key not in config:
            show_error(f"В файле '{CONFIG_FILE}' отсутствует ключ '{key}'.")

    return config

def check_new_emails(config):
    """Проверяет новые письма на IMAP-сервере."""
    try:
        # Подключение к IMAP-серверу
        mail = imaplib.IMAP4_SSL(config['IMAP_SERVER'])
        mail.login(config['EMAIL'], config['PASSWORD'])
        mail.select('inbox')

        # Поиск непрочитанных писем
        status, messages = mail.search(None, 'UNSEEN')
        if status == 'OK':
            new_emails = len(messages[0].split())
            if new_emails > 0:
                message = f"У вас {new_emails} новое(ых) письмо(а)!"
                if platform.system() == 'Windows':
                    import ctypes
                    ctypes.windll.user32.MessageBoxW(0, message, "Новая почта", 0x40)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'osascript -e \'display notification "{message}" with title "Новая почта"\'')
                else:  # Linux и другие
                    os.system(f'notify-send "Новая почта" "{message}"')

        mail.logout()
    except Exception as e:
        show_error(f"Ошибка при проверке почты: {e}")

if __name__ == '__main__':
    # Загрузка конфигурации
    config = load_config()

    print("Запуск проверки новых писем...")
    while True:
        check_new_emails(config)
        time.sleep(config['CHECK_INTERVAL'])
