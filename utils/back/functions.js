// Función para alternar la visibilidad del chat
document.getElementById('toggle-chat-btn').addEventListener('click', function() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer.style.display === 'none' || chatContainer.style.display === '') {
        chatContainer.style.display = 'block';
    } else {
        chatContainer.style.display = 'none';
    }
});

// Función para enviar mensajes al hacer clic en "Enviar"
document.getElementById('send-button').addEventListener('click', sendMessage);

// Función para enviar mensajes al presionar "Enter"
document.getElementById('input-field').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Función que maneja el envío de mensajes
function sendMessage() {
    const userMessage = document.getElementById('input-field').value;
    if (userMessage.trim()) {
        addMessageToChat(userMessage, 'user-message');
        fetch('http://127.0.0.1:8000/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChat(data.response, 'ai-message');
        });
    }
}

// Función para agregar mensajes al chat
function addMessageToChat(message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + className;
    messageDiv.textContent = message;
    const chatWindow = document.getElementById('chat-window');
    chatWindow.appendChild(messageDiv);
    document.getElementById('input-field').value = '';

    setTimeout(() => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }, 0);
}

// Funcionalidad de maximización
document.getElementById('toggle-button').addEventListener('click', function() {
    const chatContainer = document.getElementById('chat-container');

    // Alternar la clase "maximized" en el contenedor del chat
    chatContainer.classList.toggle('maximized');

    // Cambiar el ícono según el estado
    if (chatContainer.classList.contains('maximized')) {
        this.innerHTML = '<i class="fa-solid fa-down-left-and-up-right-to-center"></i>'; // Ícono para minimizar
    } else {
        this.innerHTML = '<i class="fa-solid fa-up-right-and-down-left-from-center"></i>'; // Ícono para maximizar
    }
});