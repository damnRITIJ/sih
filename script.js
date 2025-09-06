document.addEventListener("DOMContentLoaded", () => {
    // --- Get all the necessary HTML elements ---
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const signInBtn = document.getElementById("signin-btn");
    const journalBtn = document.getElementById("journal-btn");
    const permissionToggle = document.getElementById('permission-toggle');
    const journalPermissionCheckbox = document.getElementById('journal-permission');

    // --- Session & State Management ---
    let sessionId = sessionStorage.getItem("sessionId");
    if (!sessionId) {
        sessionId = Date.now().toString() + Math.random().toString(36).substring(2);
        sessionStorage.setItem("sessionId", sessionId);
    }
    let userState = 'anonymous'; // Can be 'anonymous' or 'consultancy'
    let currentUserId = null;

    // --- Sign-In Button Logic ---
    signInBtn.addEventListener("click", () => {
        const userId = prompt("Please enter your College ID to sign in:");
        
        if (userId && userId.trim() !== "") {
            userState = 'consultancy';
            currentUserId = userId.trim();
            
            localStorage.setItem('psycureUserId', currentUserId); 
            
            // Update the UI to show the user is signed in
            signInBtn.style.display = 'none';
            journalBtn.style.display = 'inline-block';
            permissionToggle.style.display = 'block';

            alert(`Welcome! You are now in consultancy mode. Your chat history and journal will be saved.`);
            
            chatBox.innerHTML = '';
            addMessage(`Hi ${currentUserId}! You're now in consultancy mode. Your conversations will be remembered. How can I help you today?`, "bot");
        }
    });

    // --- Function to add a message to the chat box ---
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

    // --- Function to send message to the backend ---
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === "") return;

        addMessage(messageText, "user");
        userInput.value = "";

        // Disable input and show loading indicator
        userInput.disabled = true;
        sendBtn.disabled = true;
        addMessage("...", "bot", "loading-indicator");

        // Conditional Endpoint and Payload
        let endpoint = "http://127.0.0.1:8000/chat/anonymous";
        let payload = {
            message: messageText,
            session_id: sessionId 
        };

        if (userState === 'consultancy') {
            endpoint = "http://127.0.0.1:8000/chat/consultancy";
            payload = {
                message: messageText,
                user_id: currentUserId,
                journal_entries: [] // Default
            };
            
            if (journalPermissionCheckbox.checked) {
                const journalKey = `journal_${currentUserId}`;
                const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
                payload.journal_entries = entries.slice(-5).map(entry => entry.content);
            }
        }

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const loadingIndicator = document.getElementById("loading-indicator");
            if (loadingIndicator) { loadingIndicator.remove(); }

            if (!response.ok) { throw new Error("Network response was not ok"); }

            const data = await response.json();
            addMessage(data.reply, "bot");

        } catch (error) {
            console.error("Error:", error);
            const loadingIndicator = document.getElementById("loading-indicator");
            if (loadingIndicator) { loadingIndicator.remove(); }
            addMessage("Sorry, something went wrong. Please check the connection and try again.", "bot");
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    // --- Event listeners ---
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    userInput.focus();
});
