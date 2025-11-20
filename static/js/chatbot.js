document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // 1. SOLIS: Izveidot mainīgo sarunas vēstures glabāšanai.
    const conversationHistory = [];

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // 2. SOLIS: Implementēt funkciju, kas sazinās ar serveri.
    const generateResponse = (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");


        // Izveidojiet JSON virknes objektu, kas satur gan pēdējo lietotāja ziņu, gan visu iepriekšējo sarunas vēsturi.
        const lastUserMessage = conversationHistory[conversationHistory.length - 1];
        // TODO: Sagatavot pieprasījuma opcijas (request options)
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: conversationHistory[conversationHistory.length - 1].content,
                history: conversationHistory.slice(0, -1)  // visi iepriekšējie ziņojumi izņemot pēdējo
            })
        };

        // TODO: Izsaukt `fetch()` ar izveidotajām opcijām.
        fetch(API_URL, requestOptions)
            .then(res => res.json())
            .then(data => {
                const botMessage = data.response || "Nav atbildes no servera.";
                messageElement.textContent = botMessage;

                // Pievieno bota atbildi vēsturē
                conversationHistory.push({
                    role: "assistant",
                    content: botMessage
                });

                chatbox.scrollTo(0, chatbox.scrollHeight);
            })
            .catch(() => {
                messageElement.textContent = "Kļūda, sazinoties ar serveri.";
            });
    }

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if(!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `auto`;

        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        
        // 3. SOLIS: Pievienot lietotāja ziņu mainīgajā sarunas vēstures glabāšanai
        // TODO: Pievienojiet ziņu masīvam pareizajā formātā (kā objektu ar "role" un "content").
        conversationHistory.push({
            role: "user",
            content: userMessage
        });
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
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