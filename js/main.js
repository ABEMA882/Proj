const express = require("express");
app.use(express.static("public"));
const fs = require("fs");
const path = require("path");

const app = express();
const port = 3000;
const databaseDir = path.join(__dirname, "DataBase");

// Убедимся, что папка DataBase существует
if (!fs.existsSync(databaseDir)) {
    fs.mkdirSync(databaseDir);
}

// Middleware для обработки данных формы
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static("public"));

// Функция для создания нового аккаунта
function createAccount(username, password) {
    const filePath = path.join(databaseDir, `${username}.json`);

    if (fs.existsSync(filePath)) {
        return false; // Аккаунт уже существует
    }

    const data = { username, password };
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    return true;
}

// Функция для проверки данных аккаунта
function checkAccount(username, password) {
    const filePath = path.join(databaseDir, `${username}.json`);

    if (!fs.existsSync(filePath)) {
        return false; // Аккаунт не найден
    }

    const content = fs.readFileSync(filePath, "utf-8");
    const accountData = JSON.parse(content);
    return accountData.password === password;
}

// Маршрут для регистрации
const axios = require("axios");

// Добавьте это в обработчик регистрации
app.post("/register", async (req, res) => {
    const { username, password } = req.body;
    if (createAccount(username, password)) {
        // Отправляем данные на Python-сервер для сбора дополнительной информации
        try {
            await axios.post("http://localhost:5000/collect_data", {
                username: username
            }, {
                headers: { "Content-Type": "application/json" }
            });
            res.send("Регистрация прошла успешно, данные собраны!");
        } catch (error) {
            res.send("Регистрация успешна, но произошла ошибка при сборе данных.");
        }
    } else {
        res.send("Аккаунт с таким именем уже существует.");
    }
});

// Маршрут для входа
app.post("/login", (req, res) => {
    const { username, password } = req.body;
    if (checkAccount(username, password)) {
        res.send("Вход успешен!");
    } else {
        res.send("Неправильное имя пользователя или пароль.");
    }
});

app.listen(port, () => {
    console.log(`Сервер запущен на http://localhost:${port}`);
});