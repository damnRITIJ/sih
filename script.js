document.addEventListener("DOMContentLoaded", () => {
    // --- Get all the necessary HTML elements ---
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const signInBtn = document.getElementById("signin-btn");
    const signOutBtn = document.getElementById("signout-btn");
    const journalBtn = document.getElementById("journal-btn");
    const permissionToggle = document.getElementById('permission-toggle');
    const journalPermissionCheckbox = document.getElementById('journal-permission');

    // --- State Management ---
    const USER_ID_KEY = 'psycureUserId'; // Use a constant for the key name
    let sessionId = sessionStorage.getItem("sessionId");
    if (!sessionId) {
        sessionId = Date.now().toString() + Math.random().toString(36).substring(2);
        sessionStorage.setItem("sessionId", sessionId);
    }
    let userState = 'anonymous'; 
    let currentUserId = null;

    // --- UI Update Functions ---
    function showLoggedInView(userId) {
        userState = 'consultancy';
        currentUserId = userId;
        signInBtn.style.display = 'none';
        signOutBtn.style.display = 'inline-block';
        journalBtn.style.display = 'inline-block';
        permissionToggle.style.display = 'block';
    }

    function showLoggedOutView() {
        userState = 'anonymous';
        currentUserId = null;
        signInBtn.style.display = 'inline-block';
        signOutBtn.style.display = 'none';
        journalBtn.style.display = 'none';
        permissionToggle.style.display = 'none';
    }

    // --- Sign-In and Sign-Out Logic ---
    function signIn() {
        const userId = prompt("Please enter your College ID to sign in:");
        if (userId && userId.trim() !== "") {
            const trimmedUserId = userId.trim();
            localStorage.setItem(USER_ID_KEY, trimmedUserId); 
            showLoggedInView(trimmedUserId);
            chatBox.innerHTML = '';
            addMessage(`Hi ${trimmedUserId}! You're now in consultancy mode. How can I help?`, "bot");
        }
    }

    function signOut() {
        localStorage.removeItem(USER_ID_KEY); 
        showLoggedOutView();
        chatBox.innerHTML = '';
        addMessage("You have been signed out. Your session is now anonymous.", "bot");
    }

    // --- Check initial state when the page loads ---
    function checkInitialState() {
        const loggedInUser = localStorage.getItem(USER_ID_KEY);
        if (loggedInUser) {
            showLoggedInView(loggedInUser);
            addMessage(`Welcome back, ${loggedInUser}! Your conversation is being continued.`, "bot");
        } else {
            showLoggedOutView();
            addMessage("Welcome! You are in anonymous mode. Your chat will not be saved. Sign in to get personalized help.", "bot");
        }
    }

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
        pElement.innerHTML = message;
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
        userInput.disabled = true;
        sendBtn.disabled = true;
        addMessage("...", "bot", "loading-indicator");

        let endpoint, payload;

        if (userState === 'consultancy') {
            endpoint = "http://127.0.0.1:8000/chat/consultancy";
            payload = {
                user_message: messageText,
                user_id: currentUserId,
                session_id: sessionId, // Pass session_id for test state management
                journal_entries: []
            };
            if (journalPermissionCheckbox.checked) {
                const journalKey = `journal_${currentUserId}`;
                const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
                // Send the full entry object, not just the content
                payload.journal_entries = entries.slice(-5);
            }
        } else {
            endpoint = "http://127.0.0.1:8000/chat/anonymous";
            payload = {
                user_message: messageText,
                session_id: sessionId 
            };
        }

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            document.getElementById("loading-indicator")?.remove();
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            addMessage(data.reply, "bot");
        } catch (error) {
            console.error("Error:", error);
            document.getElementById("loading-indicator")?.remove();
            addMessage("Sorry, something went wrong. Please try again.", "bot");
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    // --- Event listeners ---
    signInBtn.addEventListener("click", signIn);
    signOutBtn.addEventListener("click", signOut);
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    // --- Initialize the chat when the page loads ---
    checkInitialState();
    userInput.focus();
});