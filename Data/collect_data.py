from flask import Flask, request

app = Flask(__name__)

@app.route('/collect_data', methods=['POST'])
def collect_data():
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    data = request.json
    username = data.get("username")

    # Вывод в консоль
    print(f"Пользователь {username} зашел на сайт.")
    print(f"IP: {user_ip}, User-Agent: {user_agent}")

    return "Данные успешно собраны", 200

if __name__ == "__main__":
    app.run(port=5000)