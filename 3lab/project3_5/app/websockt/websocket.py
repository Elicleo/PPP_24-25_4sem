import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from fastapi import WebSocket
from serv.image_bin import all_the_bradley
from api.endpoints import (
    get_all_students,
    logged,
    sign_up,
    login,
    delete_user,
    update_user_info
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Image Binarization Service</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }

            .task-card {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .task-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                align-items: center;
            }

            .task-title {
                font-weight: bold;
                font-size: 1.1em;
                color: #333;
            }

            .task-status {
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.9em;
                font-weight: bold;
            }

            .status-started {
                background-color: #fff3cd;
                color: #856404;
            }

            .status-progress {
                background-color: #cce5ff;
                color: #004085;
            }

            .status-completed {
                background-color: #d4edda;
                color: #155724;
            }

            .status-failed {
                background-color: #f8d7da;
                color: #721c24;
            }

            .progress-container {
                margin: 10px 0;
            }

            progress {
                width: 100%;
                height: 20px;
                border-radius: 4px;
            }

            .result-image {
                max-width: 100%;
                margin-top: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }

            .base64-result {
                width: 100%;
                margin-top: 10px;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-family: monospace;
                word-break: break-all;
                max-height: 150px;
                overflow-y: auto;
                font-size: 0.8em;
                line-height: 1.4;
            }

            .command-form {
                margin: 20px 0;
                display: flex;
                gap: 10px;
            }

            #commandInput {
                flex-grow: 1;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }

            button {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                transition: background-color 0.3s;
            }

            button:hover {
                background-color: #45a049;
            }

            #imageUpload {
                margin: 15px 0;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            #previewImage {
                max-width: 300px;
                display: block;
                margin: 10px 0;
                border-radius: 4px;
            }

            #messages {
                list-style-type: none;
                padding: 0;
                max-height: 300px;
                overflow-y: auto;
                background-color: white;
                border-radius: 4px;
                padding: 10px;
                border: 1px solid #ddd;
            }

            .message {
                padding: 8px;
                margin: 5px 0;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 0.9em;
            }

            .message.error {
                background-color: #f8d7da;
                color: #721c24;
            }

            .message.success {
                background-color: #d4edda;
                color: #155724;
            }

            .copy-btn {
                margin-top: 5px;
                padding: 5px 10px;
                background-color: #2196F3;
                font-size: 0.8em;
            }

            .copy-btn:hover {
                background-color: #0b7dda;
            }

            .copy-notification {
                margin-left: 10px;
                color: green;
                display: none;
                font-size: 0.8em;
            }

            h1, h2, h3 {
                color: #333;
            }

            .section {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <h1>Image Binarization Service</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>

        <div class="section">
            <h3>Image Processing</h3>
            <div id="imageUpload">
                <input type="file" id="imageInput" accept="image/*">
                <button onclick="processImage()">Process Image</button>
                <div id="imagePreview">
                    <img id="previewImage" style="display: none;">
                </div>
            </div>

            <div id="taskContainer"></div>
        </div>

        <div class="section">
            <h3>Command Console</h3>
            <form class="command-form" onsubmit="sendCommand(event)">
                <input type="text" id="commandInput" placeholder="Enter command (e.g. /get_all_students)" autocomplete="off">
                <button type="submit">Send</button>
            </form>
        </div>

        <div class="section">
            <h3>Activity Log</h3>
            <ul id="messages"></ul>
        </div>

        <script>
            // Инициализация WebSocket соединения
            const clientId = Date.now();
            document.getElementById('ws-id').textContent = clientId;
            const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

            // Элементы DOM
            const taskContainer = document.getElementById('taskContainer');
            const messagesList = document.getElementById('messages');
            const imageInput = document.getElementById('imageInput');
            const previewImage = document.getElementById('previewImage');

            // Обработчик сообщений от сервера
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message:', data);

                    // Обработка разных типов сообщений
                    switch(data.status) {
                        case 'STARTED':
                            createTaskCard(data);
                            addMessage(`Task started (ID: ${data.task_id}, Algorithm: ${data.algorithm || 'unknown'})`, 'success');
                            break;

                        case 'PROGRESS':
                            updateTaskProgress(data);
                            addMessage(`Progress update: ${data.progress}% (Task ID: ${data.task_id})`);
                            break;

                        case 'COMPLETED':
                            completeTask(data);
                            if (data.binarized_image) {
                                addMessage(`Image processing completed (Task ID: ${data.task_id})`, 'success');
                            } else {
                                addMessage(`Command completed: ${JSON.stringify(data.result)}`, 'success');
                            }
                            break;

                        case 'FAILED':
                            failTask(data);
                            addMessage(`Task failed: ${data.message}`, 'error');
                            break;

                        default:
                            // Обычные сообщения чата
                            addMessage(event.data);
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                    addMessage(event.data);
                }
            };

            // Функция для обработки изображения
            function processImage() {
                const file = imageInput.files[0];
                if (!file) {
                    addMessage('Please select an image first', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    // Показываем превью изображения
                    previewImage.src = e.target.result;
                    previewImage.style.display = 'block';

                    // Отправляем данные на сервер
                    const base64Data = e.target.result.split(',')[1];
                    ws.send(`/binary_image ${base64Data}`);

                    addMessage('Image sent for processing...');
                };
                reader.readAsDataURL(file);
            }

            // Функция для отправки команд
            function sendCommand(event) {
                event.preventDefault();
                const commandInput = document.getElementById('commandInput');
                const command = commandInput.value.trim();

                if (!command) {
                    addMessage('Please enter a command', 'error');
                    return;
                }

                ws.send(command);
                commandInput.value = '';
                addMessage(`Command sent: ${command}`);
            }

            // Создание карточки задачи
            function createTaskCard(data) {
                const taskCard = document.createElement('div');
                taskCard.className = 'task-card';
                taskCard.id = `task-${data.task_id}`;

                taskCard.innerHTML = `
                    <div class="task-header">
                        <div class="task-title">Task ID: ${data.task_id}</div>
                        <div class="task-status status-started">STARTED</div>
                    </div>
                    <div class="task-message">
                        Algorithm: <strong>${data.algorithm || 'unknown'}</strong>
                    </div>
                    <div class="progress-container">
                        <progress id="progress-${data.task_id}" value="0" max="100"></progress>
                    </div>
                    <div class="task-result" id="result-${data.task_id}"></div>
                `;

                taskContainer.prepend(taskCard);
            }

            // Обновление прогресса задачи
            function updateTaskProgress(data) {
                const taskCard = document.getElementById(`task-${data.task_id}`);
                if (!taskCard) return;

                const progressBar = document.getElementById(`progress-${data.task_id}`);
                if (progressBar) {
                    progressBar.value = data.progress;
                }

                const statusDiv = taskCard.querySelector('.task-status');
                if (statusDiv) {
                    statusDiv.className = 'task-status status-progress';
                    statusDiv.textContent = `PROGRESS (${data.progress}%)`;
                }
            }

            // Завершение задачи
            function completeTask(data) {
                const taskCard = document.getElementById(`task-${data.task_id}`);
                if (!taskCard) return;

                const statusDiv = taskCard.querySelector('.task-status');
                if (statusDiv) {
                    statusDiv.className = 'task-status status-completed';
                    statusDiv.textContent = 'COMPLETED';
                }

                const resultDiv = taskCard.querySelector('.task-result');
                if (resultDiv) {
                    if (data.binarized_image) {
                        resultDiv.innerHTML = `
                            <p><strong>Binarization Result:</strong></p>
                            <img src="data:image/png;base64,${data.binarized_image}" class="result-image">
                            <p><strong>Base64 Result (first 100 chars):</strong></p>
                            <div class="base64-result" id="base64-${data.task_id}">
                                ${data.binarized_image.substring(0, 100)}...
                            </div>
                            <button class="copy-btn" onclick="copyBase64('${data.binarized_image}', '${data.task_id}')">
                                Copy Full Base64
                            </button>
                            <span class="copy-notification" id="copy-notification-${data.task_id}">Copied!</span>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <p><strong>Command Result:</strong></p>
                            <pre>${JSON.stringify(data.result, null, 2)}</pre>
                        `;
                    }
                }
            }

            // Ошибка задачи
            function failTask(data) {
                const taskCard = document.getElementById(`task-${data.task_id}`);
                if (!taskCard) return;

                const statusDiv = taskCard.querySelector('.task-status');
                if (statusDiv) {
                    statusDiv.className = 'task-status status-failed';
                    statusDiv.textContent = 'FAILED';
                }

                const resultDiv = taskCard.querySelector('.task-result');
                if (resultDiv) {
                    resultDiv.innerHTML = `<p class="error"><strong>Error:</strong> ${data.message}</p>`;
                }
            }

            // Функция для копирования base64 в буфер обмена
            function copyBase64(base64, taskId) {
                navigator.clipboard.writeText(base64).then(() => {
                    const notification = document.getElementById(`copy-notification-${taskId}`);
                    notification.style.display = 'inline';
                    setTimeout(() => {
                        notification.style.display = 'none';
                    }, 2000);
                });
            }

            // Добавление сообщения в лог
            function addMessage(text, type = '') {
                const messageItem = document.createElement('li');
                messageItem.className = `message ${type}`;
                messageItem.textContent = text;
                messagesList.appendChild(messageItem);
                messagesList.scrollTop = messagesList.scrollHeight;
            }

            // Обработчик ошибок WebSocket
            ws.onerror = function(error) {
                addMessage(`WebSocket Error: ${error.message}`, 'error');
            };

            // Обработчик закрытия соединения
            ws.onclose = function() {
                addMessage('Disconnected from server', 'error');
            };

            // Обработчик открытия соединения
            ws.onopen = function() {
                addMessage('Connected to server', 'success');
            };

            // Обработчик нажатия Enter в поле команды
            document.getElementById('commandInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendCommand(e);
                }
            });
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # client_id: WebSocket

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        websocket.client_id = client_id
        self.active_connections[client_id] = websocket
        print(f"Client connected: {client_id}")

    def disconnect(self, websocket: WebSocket):
        if hasattr(websocket, 'client_id'):
            client_id = websocket.client_id
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                print(f"Client disconnected: {client_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def notify_client(self, client_id: str, message: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to client {client_id}: {e}")


async def execute_command(command: str, args: list):
    try:
        cmd = command

        if cmd == "get_all_students":
            result = await get_all_students()
            return {"status": "success", "command": cmd, "result": [user.to_dict() for user in result]}

        elif cmd == "logged":
            result = await logged()
            return {"status": "success", "command": cmd, "result": result}

        elif cmd == "login":
            if len(args) < 2:
                return {"status": "error", "message": "Usage: /login email password"}
            email, password = args[0], args[1]
            result = await login(email, password)
            return {"status": "success", "command": cmd, "result": result}

        elif cmd == "sign_up":
            if len(args) < 3:
                return {"status": "error", "message": "Usage: /sign_up email username password"}
            email, username, password = args[0], args[1], args[2]
            result = await sign_up(email, username, password)
            return {"status": "success", "command": cmd, "result": result}

        elif cmd == "delete_user":
            if len(args) < 1:
                return {"status": "error", "message": "Usage: /delete_user email"}
            email = args[0]
            result = await delete_user(email)
            return {"status": "success", "command": cmd, "result": result}

        elif cmd == "update_user":
            if len(args) < 5:
                return {"status": "error",
                        "message": "Usage: /update_user email new_email username old_password new_password"}
            email, new_email, username, old_pass, new_pass = args[0], args[1], args[2], args[3], args[4]
            result = await update_user_info(email, new_email, username, old_pass, new_pass)
            return {"status": "success", "command": cmd, "result": result}

        elif cmd == "binary_image":
            if not args:
                return {"status": "error", "message": "No image data provided"}
            result = all_the_bradley(args[0])
            return {"status": "success", "result": result}

        else:
            return {"status": "error", "message": f"Unknown command: {cmd}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


manager = ConnectionManager()
