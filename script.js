document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // --- Session ID Management ---
    let sessionId = sessionStorage.getItem("sessionId");
    if (!sessionId) {
        sessionId = Date.now().toString() + Math.random().toString(36).substring(2);
        sessionStorage.setItem("sessionId", sessionId);
    }

    // --- MODIFIED: Function to add a message now supports basic markdown and a unique ID ---
    function addMessage(message, sender, messageId = null) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender + "-message");
        if (messageId) {
            messageElement.id = messageId;
        }
        
        const pElement = document.createElement("p");
        
        // Basic markdown for bold text (**text**)
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        pElement.innerHTML = message; // Use innerHTML to render the <strong> tag

        messageElement.appendChild(pElement);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to send message to the backend
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === "") return;

        addMessage(messageText, "user");
        userInput.value = "";

        // --- NEW: Disable input and show loading indicator ---
        userInput.disabled = true;
        sendBtn.disabled = true;
        addMessage("...", "bot", "loading-indicator");

        try {
            const response = await fetch("http://127.0.0.1:8000/chat/anonymous", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    message: messageText,
                    session_id: sessionId 
                }),
            });

            // --- NEW: Remove the loading indicator ---
            const loadingIndicator = document.getElementById("loading-indicator");
            if (loadingIndicator) {
                loadingIndicator.remove();
            }

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            const botReply = data.reply;

            addMessage(botReply, "bot");

        } catch (error) {
            console.error("Error:", error);
            // Ensure loading indicator is removed on error as well
            const loadingIndicator = document.getElementById("loading-indicator");
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            addMessage("Sorry, something went wrong. Please check the connection and try again.", "bot");
        } finally {
            // --- NEW: Re-enable input ---
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus(); // Set focus back to the input field
        }
    }

    // Event listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Set initial focus on the input field
    userInput.focus();
});