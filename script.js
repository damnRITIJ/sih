document.addEventListener("DOMContentLoaded", () => {
    // --- Get all the necessary HTML elements ---
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const signInBtn = document.getElementById("signin-btn"); // The new sign-in button

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
        // In a real app, this would show a secure login form.
        const userId = prompt("Please enter your College ID to sign in for a consultation:");
        
        if (userId && userId.trim() !== "") {
            userState = 'consultancy';
            currentUserId = userId.trim();
            
            // Update the UI to show the user is signed in
            signInBtn.style.display = 'none'; // Hide sign-in button
            alert(`Welcome! You are now in consultancy mode. Your chat history will be saved.`);
            
            // Clear the anonymous chat for a fresh start in the new mode
            chatBox.innerHTML = '';
            addMessage(`Hi ${currentUserId}! You're now in consultancy mode. Your conversations will be remembered. How can I help you today?`, "bot");
        }
    });


    // Function to add a message to the chat box
    function addMessage(message, sender, messageId = null) {
        // ... (this function is perfect as it is)
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", sender + "-message");
        if (messageId) {
            messageElement.id = messageId;
        }
        
        const pElement = document.createElement("p");
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        pElement.innerHTML = message;

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

        userInput.disabled = true;
        sendBtn.disabled = true;
        addMessage("...", "bot", "loading-indicator");

        // --- MODIFIED: Conditional Endpoint and Payload ---
        let endpoint = "http://127.0.0.1:8000/chat/anonymous";
        let payload = {
            message: messageText,
            session_id: sessionId 
        };

        if (userState === 'consultancy') {
            endpoint = "http://127.0.0.1:8000/chat/consultancy";
            payload = {
                message: messageText,
                user_id: currentUserId
            };
        }
        // ---------------------------------------------------

        try {
            const response = await fetch(endpoint, { // The endpoint variable is used here
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload), // The payload variable is used here
            });

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
            const loadingIndicator = document.getElementById("loading-indicator");
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            addMessage("Sorry, something went wrong. Please check the connection and try again.", "bot");
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    // Event listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    userInput.focus();
});
