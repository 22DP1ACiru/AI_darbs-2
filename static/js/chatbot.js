document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    let chatHistory = [];

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        const icon = className === "outgoing" 
            ? '' 
            : `<img src="/static/images/chatbot-icon.png" alt="Bot" class="bot-icon">`;
        chatLi.innerHTML = `${icon}<p>${message}</p>`;
        return chatLi;
    };

    const generateResponse = (userMessage) => {
        if (!userMessage.trim()) return;

        const thinkingLi = createChatLi("Domā...", "incoming");
        chatbox.appendChild(thinkingLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        fetch("/shop/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage, history: chatHistory })
        })
        .then(res => {
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            thinkingLi.remove();
            const responseLi = createChatLi(data.response, "incoming");
            chatbox.appendChild(responseLi);
            chatHistory.push({ role: "assistant", content: data.response });
        })
        .catch(err => {
            thinkingLi.querySelector("p").textContent = "Kļūda: " + err.message;
            thinkingLi.querySelector("p").classList.add("error");
        })
        .finally(() => {
            chatbox.scrollTo(0, chatbox.scrollHeight);
        });
    };

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        // Показать сообщение пользователя
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatHistory.push({ role: "user", content: userMessage });
        chatInput.value = "";
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // Запустить генерацию ответа
        generateResponse(userMessage);
    };

    // Обработчики
    sendChatBtn.addEventListener("click", handleChat);
    chatInput.addEventListener("keypress", e => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    });
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});