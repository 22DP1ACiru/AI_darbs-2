document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // 1. SOLIS: Izveidot mainīgo sarunas vēstures glabāšanai.
    let chatHistory = [];

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // 2. SOLIS: Implementēt funkciju, kas sazinās ar serveri.
    const generateResponse = (incomingChatLi, userMessage) => {  // Pass userMessage as param
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // TODO: Sagatavot pieprasījuma opcijas (request options)
        // Izveidojiet JSON virknes objektu, kas satur gan pēdējo lietotāja ziņu, gan visu iepriekšējo sarunas vēsturi.
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userMessage,  // Use the captured message
                chat_history: chatHistory
            })
        };

        // TODO: Izsaukt `fetch()` ar izveidotajām opcijām.
        // Pēc atbildes saņemšanas:
        // 1. Atjaunojiet `messageElement` saturu ar saņemto atbildi.
        // 2. Pievienojiet bota atbildi mainīgajā sarunas vēstures glabāšanai.
        fetch(API_URL, requestOptions)
            .then(res => res.json())
            .then(data => {
                if (data.response) {
                    messageElement.textContent = data.response;
                    chatHistory.push({"role": "assistant", "content": data.response});
                } else {
                    messageElement.textContent = data.error || "Sorry, something went wrong. Try again!";
                }
            })
            .catch(err => {
                console.error("Chatbot error:", err);
                messageElement.textContent = "Sorry, I couldn't connect. Please check your internet and try again.";
            })
            .finally(() => {
                chatbox.scrollTo(0, chatbox.scrollHeight);
            });
    }

    const handleChat = () => {
        let userMessage = chatInput.value.trim();  // Capture message FIRST
        if (!userMessage) return;

        // Now clear the input
        chatInput.value = "";
        chatInput.style.height = `auto`;

        // Add user message to UI and history
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
        // 3. SOLIS: Pievienot lietotāja ziņu mainīgajā sarunas vēstures glabāšanai
        // TODO: Pievienojiet ziņu masīvam pareizajā formātā (kā objektu ar "role" un "content").
        chatHistory.push({"role": "user", "content": userMessage});
        
        // Generate response, passing the captured message
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi, userMessage);  // Pass it here
        }, 600);
    }

    chatInput.addEventListener("input", () => {
        chatInput.style.height = `auto`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    sendChatBtn.addEventListener("click", handleChat);
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});