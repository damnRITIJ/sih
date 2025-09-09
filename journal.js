document.addEventListener('DOMContentLoaded', () => {
    // Define the key used to check if a user is logged in
    const LOGGED_IN_USER_KEY = 'psycureUserId';

    // Get all the necessary elements from the page
    const lockedView = document.getElementById('locked-view');
    const journalContainer = document.querySelector('.journal-container');
    const newEntryTextarea = document.getElementById('new-entry-textarea');
    const saveEntryBtn = document.getElementById('save-entry-btn');
    const pastEntriesList = document.getElementById('past-entries-list');
    const userIdDisplay = document.getElementById('user-id-display');

    let currentUserId = null;

    // --- Main function to check the user's login state ---
    function checkLoginState() {
        const loggedInUser = localStorage.getItem(LOGGED_IN_USER_KEY);

        if (loggedInUser) {
            currentUserId = loggedInUser;
            lockedView.style.display = 'none';
            journalContainer.style.display = 'flex';
            userIdDisplay.textContent = currentUserId;
            loadJournalEntries();
        } else {
            currentUserId = null; // Clear the user ID
            lockedView.style.display = 'flex';
            journalContainer.style.display = 'none';
            userIdDisplay.textContent = ''; // Clear the display
        }
    }

    function getJournalKey() {
        return `journal_${currentUserId}`;
    }

    function loadJournalEntries() {
        pastEntriesList.innerHTML = ''; // Clear previous entries
        if (!currentUserId) return; // Don't try to load if no user is logged in

        const journalKey = getJournalKey();
        const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
        
        // Display entries in reverse chronological order (newest first)
        entries.slice().reverse().forEach((entry, index) => {
            const entryElement = document.createElement('div');
            entryElement.classList.add('entry');
            // Calculate the original index for deletion purposes
            const originalIndex = entries.length - 1 - index;
            entryElement.innerHTML = `
                <div class="entry-header">
                    <span class="entry-date">${new Date(entry.date).toLocaleString()}</span>
                    <button class="delete-btn" data-index="${originalIndex}" title="Delete entry">&times;</button>
                </div>
                <p class="entry-content">${entry.content}</p>
            `;
            pastEntriesList.appendChild(entryElement);
        });
    }

    function saveJournalEntry() {
        const content = newEntryTextarea.value.trim();
        if (content === '' || !currentUserId) {
            return;
        }
        const journalKey = getJournalKey();
        const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
        const newEntry = { date: new Date().toISOString(), content: content };
        entries.push(newEntry);
        localStorage.setItem(journalKey, JSON.stringify(entries));
        newEntryTextarea.value = '';
        newEntryTextarea.placeholder = "What's on your mind today?";
        loadJournalEntries();
    }

    function deleteJournalEntry(index) {
        if (!currentUserId) return;
        const journalKey = getJournalKey();
        const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
        entries.splice(index, 1);
        localStorage.setItem(journalKey, JSON.stringify(entries));
        loadJournalEntries();
    }

    // --- Event Listeners ---
    saveEntryBtn.addEventListener('click', saveJournalEntry);

    pastEntriesList.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-btn')) {
            const indexToDelete = parseInt(event.target.getAttribute('data-index'));
            if (confirm('Are you sure you want to permanently delete this entry?')) {
                deleteJournalEntry(indexToDelete);
            }
        }
    });

    // --- Listen for changes from other tabs ---
    // This makes the page reactive if the user logs in/out elsewhere
    window.addEventListener('storage', (event) => {
        if (event.key === LOGGED_IN_USER_KEY) {
            checkLoginState();
        }
    });

    // --- Initial check when the page loads ---
    checkLoginState();
});