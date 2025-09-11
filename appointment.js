document.addEventListener('DOMContentLoaded', () => {
    // State management
    const selection = {
        counselor: null,
        date: null,
        time: null,
    };

    // DOM Elements
    const counselorCards = document.querySelectorAll('.counselor-card');
    const calendarDaysContainer = document.getElementById('calendar-days');
    const monthYearDisplay = document.getElementById('month-year');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const confirmationDetails = document.getElementById('confirmation-details');
    const bookAppointmentBtn = document.getElementById('book-appointment-btn');

    let currentDate = new Date(2024, 10, 1); // Start at Nov 2024

    // --- COUNSELOR SELECTION ---
    counselorCards.forEach(card => {
        card.addEventListener('click', () => {
            counselorCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selection.counselor = {
                id: card.dataset.counselorId,
                name: card.dataset.counselorName,
            };
            updateConfirmation();
        });
    });

    // --- CALENDAR LOGIC ---
    function renderCalendar() {
        calendarDaysContainer.innerHTML = '';
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        monthYearDisplay.textContent = `${currentDate.toLocaleString('default', { month: 'short' }).toUpperCase()} ${year}`;

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const dayNames = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];

        dayNames.forEach(name => {
            const dayNameEl = document.createElement('div');
            dayNameEl.classList.add('day-name');
            dayNameEl.textContent = name;
            calendarDaysContainer.appendChild(dayNameEl);
        });

        for (let i = 1; i < firstDay; i++) {
            const emptyEl = document.createElement('div');
            calendarDaysContainer.appendChild(emptyEl);
        }

        for (let i = 1; i <= daysInMonth; i++) {
            const dayEl = document.createElement('div');
            dayEl.classList.add('day');
            dayEl.textContent = i;
            dayEl.dataset.day = i;
            
            if (selection.date && selection.date.getDate() === i && selection.date.getMonth() === month) {
                dayEl.classList.add('selected');
            }

            dayEl.addEventListener('click', () => {
                selection.date = new Date(year, month, i);
                document.querySelectorAll('.day.selected').forEach(d => d.classList.remove('selected'));
                dayEl.classList.add('selected');
                renderTimeSlots();
                updateConfirmation();
            });
            calendarDaysContainer.appendChild(dayEl);
        }
    }

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // --- TIME SLOT LOGIC ---
    function renderTimeSlots() {
        timeSlotsContainer.innerHTML = '';
        const availableTimes = ["10:00 AM", "11:30 AM", "02:00 PM", "03:30 PM", "05:00 PM"];
        
        availableTimes.forEach(time => {
            const timeSlotEl = document.createElement('div');
            timeSlotEl.classList.add('time-slot');
            timeSlotEl.innerHTML = `<span>${time}</span> <span>&gt;</span>`;
            timeSlotEl.dataset.time = time;
            
            if (selection.time === time) {
                timeSlotEl.classList.add('selected');
            }

            timeSlotEl.addEventListener('click', () => {
                selection.time = time;
                document.querySelectorAll('.time-slot.selected').forEach(t => t.classList.remove('selected'));
                timeSlotEl.classList.add('selected');
                updateConfirmation();
            });
            timeSlotsContainer.appendChild(timeSlotEl);
        });
    }

    // --- CONFIRMATION LOGIC ---
    function updateConfirmation() {
        if (selection.counselor && selection.date && selection.time) {
            confirmationDetails.innerHTML = `
                <div>
                    <strong>COUNSELOR</strong>
                    <span>${selection.counselor.name}</span>
                </div>
                <div>
                    <strong>DATE</strong>
                    <span>${selection.date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                </div>
                <div>
                    <strong>TIME</strong>
                    <span>${selection.time}</span>
                </div>
            `;
            bookAppointmentBtn.disabled = false;
        } else {
            confirmationDetails.innerHTML = '<p class="placeholder">Please select a counselor, date, and time.</p>';
            bookAppointmentBtn.disabled = true;
        }
    }

    bookAppointmentBtn.addEventListener('click', () => {
        if (selection.counselor && selection.date && selection.time) {
            alert(`Appointment Booked!\n\nCounselor: ${selection.counselor.name}\nDate: ${selection.date.toLocaleDateString()}\nTime: ${selection.time}`);
        }
    });

    // Initial render
    renderCalendar();
    renderTimeSlots(); // Show initial time slots
});