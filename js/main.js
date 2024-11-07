document.getElementById("dataForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Останавливаем стандартную отправку формы

    const username = document.getElementById("username").value;  // Получаем имя пользователя

    if (!username) {
        console.error("Username is required.");
        return;
    }

    const data = { username: username };

    // Отправляем данные на сервер с помощью fetch
    fetch('/collect_data', {
        method: 'POST',  // Отправка POST-запроса
        headers: {
            'Content-Type': 'application/json',  // Указываем тип данных
        },
        body: JSON.stringify(data),  // Преобразуем данные в JSON и отправляем
    })
    .then(response => response.json())  // Ожидаем JSON-ответ
    .then(data => {
        console.log("Response:", data);  // Выводим успешный ответ
    })
    .catch(error => {
        console.error("Error:", error);  // Выводим ошибку, если запрос не удался
    });
});