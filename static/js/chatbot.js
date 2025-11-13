document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // SOLIS 1: Izveidot mainīgo sarunas vēstures glabāšanai
    // Šis masīvs glabā visu sarunu vēsturi ar struktūru: [{role: "user/assistant", content: "ziņa"}]
    let chatHistory = [];

    /**
     * Izveido čata ziņas elementu (li)
     * @param {string} message - Ziņas teksts
     * @param {string} className - CSS klase (outgoing vai incoming)
     * @returns {HTMLElement} - Izveidotais li elements
     */
    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent = className === "outgoing" 
            ? `<p></p>` 
            : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // SOLIS 2: Implementēt funkciju, kas sazinās ar serveri
    /**
     * Ģenerē čatbota atbildi, sazināties ar serveri
     * @param {HTMLElement} incomingChatLi - Ienākošās ziņas elements
     */
    const generateResponse = (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // Sagatavot pieprasījuma opcijas
        // Izveidojam JSON objektu ar lietotāja ziņu un sarunas vēsturi
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: chatHistory[chatHistory.length - 1].content, // Pēdējā lietotāja ziņa
                chat_history: chatHistory.slice(0, -1) // Visa iepriekšējā vēsture (bez pēdējās ziņas)
            })
        };

        // Izsaukt fetch() ar izveidotajām opcijām
        fetch(API_URL, requestOptions)
            .then(response => {
                // Pārbauda, vai atbilde ir veiksmīga
                if (!response.ok) {
                    throw new Error(`HTTP kļūda! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // 1. Atjaunojam messageElement saturu ar saņemto atbildi
                if (data.response) {
                    messageElement.textContent = data.response;
                    
                    // 2. Pievienojam bota atbildi sarunas vēsturei
                    chatHistory.push({
                        role: "assistant",
                        content: data.response
                    });
                } else {
                    // Ja nav atbildes, parādam kļūdas ziņojumu
                    messageElement.textContent = "Atvainojiet, nevarēju iegūt atbildi.";
                    messageElement.classList.add("error");
                }
            })
            .catch(error => {
                // Kļūdas apstrāde
                console.error("Kļūda, sazināties ar čatbotu:", error);
                messageElement.textContent = "Atvainojiet, notika kļūda. Lūdzu, mēģiniet vēlreiz.";
                messageElement.classList.add("error");
            })
            .finally(() => {
                // Noņem "Thinking..." animāciju
                chatbox.scrollTo(0, chatbox.scrollHeight);
            });
    }

    /**
     * Apstrādā lietotāja ziņas nosūtīšanu
     */
    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        
        // Pārbauda, vai ziņa nav tukša
        if (!userMessage) return;

        // Iztīra input lauku
        chatInput.value = "";
        chatInput.style.height = `auto`;

        // Pievieno lietotāja ziņu čatam
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        
        // SOLIS 3: Pievienot lietotāja ziņu sarunas vēsturei
        // Pievienojam ziņu masīvam pareizajā formātā
        chatHistory.push({
            role: "user",
            content: userMessage
        });
        
        // Pēc nelielas pauzes parāda bota atbildi
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    /**
     * Notīra čata vēsturi (opcija - var pievienot pogu)
     */
    const clearChatHistory = () => {
        chatHistory = [];
        chatbox.innerHTML = "";
    }

    // Event listeners

    // Automātiski pielāgo textarea augstumu
    chatInput.addEventListener("input", () => {
        chatInput.style.height = `auto`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    // Nosūta ziņu, nospiežot Enter (bez Shift)
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    // Nosūta ziņu, noklikšķinot uz pogas
    sendChatBtn.addEventListener("click", handleChat);
    
    // Aizver čatbotu
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    
    // Atver/aizver čatbotu
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});