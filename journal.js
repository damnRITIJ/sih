document.addEventListener('DOMContentLoaded', () => {
    // Define the key used to check if a user is logged in
    const LOGGED_IN_USER_KEY = 'psycureUserId';

    // Get all the necessary elements from the page
    const lockedView = document.getElementById('locked-view');
    const journalContainer = document.querySelector('.journal-container');
    const newEntryTextarea = document.getElementById('new-entry-textarea');
    const saveEntryBtn = document.getElementById('save-entry-btn');
    const pastEntriesList = document.getElementById('past-entries-list');
    const userIdDisplay = document.getElementById('user-id-display'); // Get the display element

    let currentUserId = null;

    // --- Main function to check the user's login state ---
    function checkLoginState() {
        const loggedInUser = localStorage.getItem(LOGGED_IN_USER_KEY);

        if (loggedInUser) {
            // If the user ID is found, the user is signed in
            currentUserId = loggedInUser;
            
            // Hide the locked message and show the journal
            lockedView.style.display = 'none';
            journalContainer.style.display = 'flex';
            
            // --- THIS IS THE FIX: Display the user's ID ---
            userIdDisplay.textContent = currentUserId;

            loadJournalEntries(); // Load the user's entries
        } else {
            // If no user ID is found, show the locked message and hide the journal
            lockedView.style.display = 'flex';
            journalContainer.style.display = 'none';
        }
    }

    // --- The rest of your script remains the same ---

    function getJournalKey() {
        return `journal_${currentUserId}`;
    }

    function loadJournalEntries() {
        const journalKey = getJournalKey();
        const entries = JSON.parse(localStorage.getItem(journalKey)) || [];
        
        pastEntriesList.innerHTML = ''; 
        
        entries.slice().reverse().forEach((entry, index) => {
            const entryElement = document.createElement('div');
            entryElement.classList.add('entry');
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
        if (content === '') {
            newEntryTextarea.placeholder = "Please write something before saving.";
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

    // --- Initial check when the page loads ---
    checkLoginState();
});
