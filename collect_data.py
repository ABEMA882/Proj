from flask import Flask, request, jsonify
import os
import json
import logging
from flask_cors import CORS
import time
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Логи в консоль
        logging.FileHandler("app.log")  # Логи в файл
    ]
)

app = Flask(__name__)

# Включаем CORS для всех маршрутов
CORS(app)

# Папка для сохранения данных
DATABASE_DIR = "./DataBase"
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

# Проверка прав на запись
if not os.access(DATABASE_DIR, os.W_OK):
    logging.error(f"Нет прав на запись в папку {DATABASE_DIR}")
else:
    logging.info(f"Папка {DATABASE_DIR} доступна для записи")

# Файл для отслеживания времени последнего деплоя
DEPLOY_FILE = 'last_deploy.txt'

# Проверка, был ли деплой недавно
def was_deploy_recent():
    if os.path.exists(DEPLOY_FILE):
        with open(DEPLOY_FILE, 'r') as file:
            last_deploy_time = float(file.read())
            if time.time() - last_deploy_time < 3600:  # За последний час
                logging.info(f"Последний деплой был {last_deploy_time} секунд назад.")
                return True
    return False

# Логирование информации о запуске
@app.route('/')
def home():
    logging.info("Запрос на главную страницу.")
    return """
        <html>
            <head>
                <title>Collect Data</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap');
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    html, body {
                      width: 100%;
                      min-height: 200vh;
                      margin: 0;
                      padding: 0;
                      background-color: #333;
                      scroll-behavior: smooth;
                      overflow-x: hidden;
                    }
                    
                    body {
                        font-family: "Montserrat", sans-serif;
                        color: rgb(255, 255, 255);
                        margin: 0;
                        padding: 0;
                    }
                    
                    .message {
                        transform: translate(-50%,-50%);
                        left: 50%;
                        top: 50%;
                        position: absolute;
                        color: white;
                    }
                </style>
            </head>
            <body>
                <h1 class="message">На легке заскамил.</h1>
                <script>
                    fetch('/collect_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({username: 'TestUser'})
                    })
                    .then(response => response.json())
                    .then(data => console.log(data))
                    .catch(error => console.error('Error:', error));
                </script>
            </body>
        </html>
    """

@app.route('/collect_data', methods=['POST'])
def collect_data():
    start_time = time.time()  # Для отслеживания времени обработки
    logging.info(f"Запрос на сбор данных получен: {request.json}")

    # Проверка формата данных
    if not request.json:
        logging.error("Неверный формат данных. Ожидался JSON.")
        return jsonify({"error": "Invalid data format. Expected JSON."}), 400

    data = request.json
    username = data.get("username")

    # Проверка наличия имени пользователя
    if not username:
        logging.error("Не указан username.")
        return jsonify({"error": "Username is required."}), 400

    # Извлечение реального IP через X-Forwarded-For
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    user_agent = request.headers.get('User-Agent')

    # Безопасное преобразование IP-адреса в имя файла
    safe_user_ip = re.sub(r'[^a-zA-Z0-9]', '_', user_ip)
    timestamp = int(time.time())  # Генерация временной метки
    filename = os.path.join(DATABASE_DIR, f"{safe_user_ip}_{timestamp}.json")

    # Логирование IP-адреса и user-agent
    logging.info(f"Получены данные от пользователя {username} с IP: {user_ip} и User-Agent: {user_agent}")

    # Группируем данные
    user_data = {
        "username": username,
        "user_ip": user_ip,
        "user_agent": user_agent
    }

    # Сохраняем данные в файл
    try:
        with open(filename, 'w') as f:
            json.dump(user_data, f, indent=4)
        logging.info(f"Данные сохранены в файл: {filename}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных в файл {filename}: {e}")

    

    # Логируем данные
    logging.info(f"User Data: {user_data}")

    files = os.listdir(DATABASE_DIR)

    # Отвечаем с данными и списком файлов
    response_data = {
        "message": "Данные успешно собраны",
        "user_data": user_data,
        "files_in_database": files
    }

    logging.info(f"Запрос обработан за {time.time() - start_time:.2f} секунд.")
    return jsonify(response_data), 200

if __name__ == "__main__":
    # Проверка, был ли последний деплой
    if was_deploy_recent():
        logging.warning("Деплой уже был выполнен недавно. Пропуск деплоя.")
    else:
        logging.info("Запуск нового деплоя.")
        # Обновляем файл времени деплоя
        with open(DEPLOY_FILE, 'w') as file:
            file.write(str(time.time()))

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)