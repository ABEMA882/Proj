from flask import Flask, request, jsonify
import os
import json
import logging
from flask_cors import CORS
import time
import re


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
DATABASE_DIR = "DataBase"
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

@app.route('/')
def home():
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

    if not request.json:
        return jsonify({"error": "Invalid data format. Expected JSON."}), 400

    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required."}), 400

    # Попробуем извлечь реальный IP через X-Forwarded-For
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    user_agent = request.headers.get('User-Agent')

    safe_user_ip = re.sub(r'[^a-zA-Z0-9]', '_', user_ip)
    filename = os.path.join(DATABASE_DIR, f"{safe_user_ip}.json")
    # Группируем данные
    user_data = {
        "username": username,
        "user_ip": user_ip,
        "user_agent": user_agent
    }

    timestamp = int(time.time())  # Генерация временной метки
    filename = os.path.join(DATABASE_DIR, f"{safe_user_ip}_{timestamp}.json")
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=4)

    # Логируем данные
    logging.info(f"User Data: {user_data}")
    
    files = os.listdir(DATABASE_DIR)
    
    # Отвечаем с данными и списком файлов
    response_data = {
        "message": "Данные успешно собраны",
        "user_data": user_data,
        "files_in_database": files
    }

    logging.info(f"Request processed in {time.time() - start_time:.2f} seconds.")
    return jsonify(response_data), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)