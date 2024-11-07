from flask import Flask, request, jsonify
import os
import json
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

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
    # Проверка наличия данных в запросе
    if not request.json:
        return jsonify({"error": "Invalid data format. Expected JSON."}), 400

    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required."}), 400

    # Попробуем извлечь реальный IP через X-Forwarded-For
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]  # Получаем реальный IP
    user_agent = request.headers.get('User-Agent')

    # Группируем данные
    user_data = {
        "username": username,
        "user_ip": user_ip,
        "user_agent": user_agent
    }

    # Сохраняем данные в файл
    filename = os.path.join(DATABASE_DIR, f"{user_ip}.json")
    with open(filename, 'w') as f:
        json.dump(user_data, f, indent=4)

    # Выводим данные в консоль в отформатированном виде
    print("\n--- Полученные данные ---")
    logging.info(f"Username: {user_data['username']}")
    logging.info(f"User IP: {user_data['user_ip']}")
    logging.info(f"User Agent: {user_data['user_agent']}")
    print(f"--- Конец данных ---\n")

    files = os.listdir(DATABASE_DIR)

    # Формируем ответ с данными и списком файлов
    response_data = {
        "message": "Данные успешно собраны",
        "user_data": user_data,
        "files_in_database": files
    }

    return jsonify(response_data), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)