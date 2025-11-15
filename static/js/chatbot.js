const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendBtn = document.querySelector("#send-btn");

let chatHistory = [];

// Add message to chatbox
function addMessage(message, isBot) {
    const li = document.createElement("li");
    li.classList.add("chat", isBot ? "incoming" : "outgoing");

    if (isBot) {
        li.innerHTML = `
            <span class="material-symbols-outlined">smart_toy</span>
            <p>${message}</p>
        `;
    } else {
        li.innerHTML = `<p>${message}</p>`;
    }

    chatbox.appendChild(li);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Send message to backend
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, false);
    chatHistory.push({ role: "user", content: message });
    chatInput.value = "";

    // Temporary loading message
    addMessage("Thinking...", true);
    const loadingMessage = chatbox.lastElementChild;

    try {
        const response = await fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        const data = await response.json();

        // Replace "Thinking..." with bot response
        loadingMessage.querySelector("p").textContent = data.reply;

        chatHistory.push({ role: "assistant", content: data.reply });

    } catch (error) {
        loadingMessage.querySelector("p").textContent =
            "Error: Unable to contact the chatbot.";
    }
}

// Toggle chatbot (IMPORTANT FIX)
chatbotToggler.addEventListener("click", () => {
    document.body.classList.toggle("show-chatbot");
});

closeBtn.addEventListener("click", () => {
    document.body.classList.remove("show-chatbot");
});

// Send message when clicking button
sendBtn.addEventListener("click", sendMessage);

// Send message with Enter
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
