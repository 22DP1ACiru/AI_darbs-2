document.addEventListener('DOMContentLoaded', () => {
    // --- 1. SOLIS: Izveidot masīvu čata vēstures glabāšanai ---
    let sarunasVesture = [];

    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // Funkcija jaunas ziņas HTML elementa veidošanai
    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // --- 2. SOLIS: Funkcija, kas sazinās ar serveri ---
    const generateResponse = (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // --- Pieprasījuma parametri ar pēdējo lietotāja ziņu un visu čata vēsturi ---
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: sarunasVesture.length ? sarunasVesture[sarunasVesture.length - 1].content : "",
                history: sarunasVesture
            })
        };

        // Izsaucam fetch uz serveri
        fetch(API_URL, requestOptions)
            .then(res => res.json())
            .then(data => {
                // --- 1. Atjaunojam bota tekstu interfeisā ---
                messageElement.textContent = data.response;
                // --- 2. Pievienojam bota atbildi vēstures masīvam ---
                sarunasVesture.push({ role: "assistant", content: data.response });
            })
            .catch(() => {
                messageElement.textContent = "Neizdevās sazināties ar serveri!";
            });
    }

    // Funkcija, kas apstrādā lietotāja jaunu ziņu
    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatInput.value = "";
        chatInput.style.height = `auto`;

        // Parāda lietotāja ziņu logā
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // --- 3. SOLIS: Lietotāja ziņas pievienošana vēsturei ---
        sarunasVesture.push({ role: "user", content: userMessage });

        setTimeout(() => {
            // Parāda ideju par to, ka bots domā
            const incomingChatLi = createChatLi("Domāju...", "incoming");
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
        if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    sendChatBtn.addEventListener("click", handleChat);
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});
