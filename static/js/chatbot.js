document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // 1. SOLIS: Izveidot mainīgo sarunas vēstures glabāšanai.
    // chatHistory stores objects like { role: 'user'|'assistant', content: '...' }
    const chatHistory = [];

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // 2. SOLIS: Implementēt funkciju, kas sazinās ar serveri.
    const generateResponse = async (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // Build request payload: include last user message and full history
        // chatHistory is maintained in the page and will be sent as-is
        const lastUserMessage = chatHistory.length ? chatHistory[chatHistory.length - 1].content : "";
        const payload = {
            message: lastUserMessage,
            history: chatHistory
        };

        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        };

        try {
            const res = await fetch(API_URL, requestOptions);
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                messageElement.textContent = err.error || `Error: ${res.status}`;
                return;
            }
            const data = await res.json();
            const botReply = data.response || data.reply || "(no response)";

            // Update incoming bubble with actual reply
            messageElement.textContent = botReply;

            // Append assistant reply to history
            chatHistory.push({ role: 'assistant', content: botReply });
        } catch (e) {
            messageElement.textContent = 'Network error';
            console.error('chatbot fetch error', e);
        }
    }

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if(!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `auto`;

        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
    // 3. SOLIS: Pievienot lietotāja ziņu mainīgajā sarunas vēstures glabāšanai
    // Push the user's message into chatHistory as a {role, content} object
    chatHistory.push({ role: 'user', content: userMessage });
        
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    chatInput.addEventListener("input", () => {
        chatInput.style.height = `auto`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    chatInput.addEventListener("keydown", (e) => {
        if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    sendChatBtn.addEventListener("click", handleChat);
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});