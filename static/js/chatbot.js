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
    const generateResponse = (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // TODO: Sagatavot pieprasījuma opcijas (request options)
        // Izveidojiet JSON virknes objektu, kas satur gan pēdējo lietotāja ziņu, gan visu iepriekšējo sarunas vēsturi.
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: chatHistory[chatHistory.length - 1].content, // pēdējā lietotāja ziņa
                chat_history: chatHistory.slice(0, -1)                // visa iepriekšējā vēsture bez pēdējās ziņas
            })
        };

        // TODO: Izsaukt `fetch()` ar izveidotajām opcijām.
        // Pēc atbildes saņemšanas:
        // 1. Atjaunojiet `messageElement` saturu ar saņemto atbildi.
        // 2. Pievienojiet bota atbildi mainīgajā sarunas vēstures glabāšanai.
        fetch(API_URL, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // vai atbilde ir veiksmīga
                if (data.status === "success") {
                    messageElement.textContent = data.response;
                    // pievienot bota atbildi sarunas vēsturei
                    chatHistory.push({
                        role: "assistant",
                        content: data.response
                    });
                    // saglabāt sarunu localStorage
                    saveChatToLocalStorage();
                } else {
                    messageElement.textContent = "Sorry, I encountered an error. Please try again.";
                }
                chatbox.scrollTo(0, chatbox.scrollHeight);
            })
            .catch(error => {
                console.error('Error:', error);
                messageElement.textContent = "Sorry, I'm having connection issues. Please try again later.";
                chatbox.scrollTo(0, chatbox.scrollHeight);
            });
    }

    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if(!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `auto`;

        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
        // 3. SOLIS: Pievienot lietotāja ziņu mainīgajā sarunas vēstures glabāšanai
        // TODO: Pievienojiet ziņu masīvam pareizajā formātā (kā objektu ar "role" un "content").
        chatHistory.push({
            role: "user",
            content: userMessage
        });
        // saglabāt sarunu localStorage
        saveChatToLocalStorage();
        
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    // papildus funkcija sarunas saglabāšanai localStorage
    const saveChatToLocalStorage = () => {
        localStorage.setItem('eshop_chat_history', JSON.stringify(chatHistory));
    }
    // papildus funkcija sarunas ielādei no localStorage
    const loadChatFromLocalStorage = () => {
        const savedChat = localStorage.getItem('eshop_chat_history');
        if (savedChat) {
            try {
                chatHistory = JSON.parse(savedChat);
                // notīrīt esošo chatbox izņemot sākotnējo ziņu
                const initialMessage = chatbox.querySelector('.chat.incoming');
                if (initialMessage && chatHistory.length > 0) {
                    initialMessage.remove();
                }
                // atjaunot sarunu no vēstures
                chatHistory.forEach(message => {
                    const className = message.role === 'user' ? 'outgoing' : 'incoming';
                    chatbox.appendChild(createChatLi(message.content, className));
                });
                
                chatbox.scrollTo(0, chatbox.scrollHeight);
            } catch (error) {
                console.error('Error loading chat history:', error);
                localStorage.removeItem('eshop_chat_history');
            }
        }
    }
    // ielādēt sarunu, kad lapa ielādējas
    loadChatFromLocalStorage();

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
