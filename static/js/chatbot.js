document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // 1. SOLIS: Sarunas vēsture
    const conversationHistory = [];

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        const chatContent = className === "outgoing"
            ? `<p></p>`
            : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    };

    // 2. SOLIS: Funkcija, kas sazinās ar serveri
    const generateResponse = async (incomingChatLi, userMessage) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: userMessage,          // pēdējā lietotāja ziņa
                history: conversationHistory   // iepriekšējā sarunas vēsture
            })
        };

        try {
            const response = await fetch(API_URL, requestOptions);
            const data = await response.json();

            if (data && data.response) {
                messageElement.textContent = data.response;
                conversationHistory.push({ role: "assistant", content: data.response });
            } else {
                messageElement.textContent = "Nav atbildes no servera.";
            }
        } catch (error) {
            console.error("Server error:", error);
            messageElement.textContent = "Kļūda sazinoties ar serveri.";
        }

        chatbox.scrollTo(0, chatbox.scrollHeight);
    };

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `auto`;

        // Pievieno lietotāja ziņu
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // 3. SOLIS: Saglabā vēsturē
        conversationHistory.push({ role: "user", content: userMessage });

        // 4. SOLIS: Pievieno “Thinking...” un sūta pieprasījumu serverim
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi, userMessage);
        }, 600);
    };

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
