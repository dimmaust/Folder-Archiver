# backup File&Folder  

**File&FolderArchiver** – это программа для резервного копирования файлов и папок с возможностью настройки параметров архивации через графический интерфейс.  

## Возможности  
- Выбор исходной папки для архивации  
- Выбор папки назначения для сохранения архивов  
- Архивация в формат `.7z` (необходимо, чтобы **7-Zip** был установлен в стандартную папку `C:\Program Files\7-Zip\7z.exe`)  
- Настройка глубины архивации (удаление старых архивов)  
- Отправка уведомлений в **Telegram** с произвольным текстом  
- Автоматический запуск через **планировщик задач** (при наличии конфигурационного файла ждет **15 секунд**, затем начинает архивацию)  

## Как использовать  
1. Запустите программу `archiver.py`.  
2. Введите путь к папке, которую нужно архивировать.  
3. Укажите папку для сохранения архива.  
4. Настройте глубину архивации (в днях).  
5. (Опционально) Укажите **Token** и **Chat ID** Telegram-бота, если хотите получать уведомления.  
6. (Опционально) Добавьте дополнительный текст для Telegram-сообщения.  
7. Нажмите **"Сохранить"**, чтобы сохранить настройки.  
8. Нажмите **"Архивировать"**, чтобы создать архив вручную, или запустите программу через планировщик задач.  

## Настройка автоматического запуска  
- При первом запуске программа ожидает ввода данных.  
- Если **конфигурационный файл найден**, программа ждет **15 секунд** и запускает архивацию автоматически (подходит для планировщика задач Windows).  

## Как создать Telegram-бота  
1. Откройте Telegram и найдите `@BotFather`.  
2. Отправьте команду `/newbot` и следуйте инструкциям.  
3. Скопируйте полученный **Token**.  
4. Добавьте бота в чат (группу) и получите `Chat ID` через `@userinfobot` или `https://api.telegram.org/bot<TOKEN>/getUpdates`.  
5. Введите эти данные в программе.  

## Пример использования в планировщике задач Windows  
1. Откройте **Планировщик заданий** (`taskschd.msc`).  
2. Создайте новую задачу и укажите путь к `python.exe` в разделе **Программа/скрипт**.  
3. В поле **Аргументы** укажите путь к `archiver.py`.  
4. Настройте расписание запуска.  

### Логи  
- Программа ведет логирование в `archiver.log` (кодировка UTF-8).  
- Ошибки и успешные операции записываются в файл.  

## Требования  
- Windows  
- Python 3  
- 7-Zip (`C:\Program Files\7-Zip\7z.exe`)  
- Библиотеки: `requests`, `tkinter`, `json`, `logging`, `subprocess`  

---

Если через долгое время ты забудешь, зачем ждет 15 секунд — это сделано для совместимости с **планировщиком задач**, чтобы избежать проблем с задержкой запуска. 😊
