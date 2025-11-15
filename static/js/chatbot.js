document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements for chatbot controls and UI
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");

    // Initialize chat history with a greeting from the assistant
    let chatHistory = [
        { role: "assistant", content: "Hi there! How can I help you today?" }
    ];

    // Create a chat list item for user or bot messages
    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", className);
        // Add bot icon for incoming messages, plain for outgoing
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").textContent = message;
        return chatLi;
    }

    // Send user message and chat history to backend, handle bot response
    const generateResponse = (incomingChatLi) => {
        const API_URL = "/chatbot";
        const messageElement = incomingChatLi.querySelector("p");

        // Get the last user message from chat history
        const lastUserMessage = chatHistory.filter(m => m.role === "user").slice(-1)[0]?.content || "";
        // Prepare request options for fetch
        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: lastUserMessage,
                history: chatHistory
            })
        };

        // Send request to backend and update UI with bot reply
        fetch(API_URL, requestOptions)
            .then(res => res.json())
            .then(data => {
                const botReply = data.response || "Sorry, I couldn't get a response.";
                messageElement.textContent = botReply;
                chatHistory.push({ role: "assistant", content: botReply });
            })
            .catch(() => {
                messageElement.textContent = "Error: Unable to reach chatbot.";
            });
    }

    // Handle sending a user message
    const handleChat = () => {
        const userMessage = chatInput.value.trim();
        if(!userMessage) return; // Ignore empty messages

        chatInput.value = "";
        chatInput.style.height = `auto`;

        // Add user message to chatbox UI
        chatbox.appendChild(createChatLi(userMessage, "outgoing"));
        chatbox.scrollTo(0, chatbox.scrollHeight);

        // Add user message to chat history
        chatHistory.push({ role: "user", content: userMessage });

        // Show "Thinking..." message and get bot response
        setTimeout(() => {
            const incomingChatLi = createChatLi("Thinking...", "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            generateResponse(incomingChatLi);
        }, 600);
    }

    // Auto-resize textarea as user types
    chatInput.addEventListener("input", () => {
        chatInput.style.height = `auto`;
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    // Send message on Enter (without Shift) if screen is wide enough
    chatInput.addEventListener("keydown", (e) => {
        if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
            e.preventDefault();
            handleChat();
        }
    });

    // Send message on button click
    sendChatBtn.addEventListener("click", handleChat);

    // Close chatbot window
    closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));

    // Toggle chatbot window visibility
    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
});