// Sample compliance tasks data
let complianceTasks = [
    {
        id: 1,
        title: "GDPR Data Protection Impact Assessment",
        description: "Conduct DPIA for new customer data processing activities",
        dueDate: new Date(new Date().setDate(new Date().getDate() + 3)),
        priority: "high",
        regulation: "gdpr",
        tags: ["audit", "data-protection", "assessment"],
        completed: false
    },
    {
        id: 2,
        title: "HIPAA Security Rule Compliance Review",
        description: "Annual review of security measures for protected health information",
        dueDate: new Date(new Date().setDate(new Date().getDate() + 7)),
        priority: "high",
        regulation: "hipaa",
        tags: ["security", "review", "annual"],
        completed: false
    },
    {
        id: 3,
        title: "SOX Internal Control Testing",
        description: "Quarterly testing of financial reporting controls",
        dueDate: new Date(new Date().setDate(new Date().getDate() + 10)),
        priority: "medium",
        regulation: "sox",
        tags: ["financial", "testing", "quarterly"],
        completed: false
    },
    {
        id: 4,
        title: "PCI DSS Security Scan",
        description: "Quarterly external vulnerability scan",
        dueDate: new Date(new Date().setDate(new Date().getDate() - 2)),
        priority: "medium",
        regulation: "pci",
        tags: ["security", "scan", "quarterly"],
        completed: false
    },
    {
        id: 5,
        title: "ISO 27001 Internal Audit",
        description: "Semi-annual internal audit of ISMS",
        dueDate: new Date(new Date().setDate(new Date().getDate() + 14)),
        priority: "medium",
        regulation: "iso",
        tags: ["audit", "security", "isms"],
        completed: false
    },
    {
        id: 6,
        title: "Data Retention Policy Update",
        description: "Review and update data retention policies",
        dueDate: new Date(new Date().setDate(new Date().getDate() + 5)),
        priority: "low",
        regulation: "gdpr",
        tags: ["policy", "update", "review"],
        completed: false
    }
];

let currentDate = new Date();
let currentFilter = 'all';
let currentPriorityFilter = 'all';
let currentView = 'month';

// Initialize the calendar
document.addEventListener('DOMContentLoaded', function() {
    loadFromLocalStorage();
    initializeCalendar();
    renderTasks();
    updateStats();
    
    // Initialize date picker
    flatpickr("#dueDate", {
        dateFormat: "Y-m-d",
        minDate: "today",
        defaultDate: new Date()
    });
    
    // Setup form submission
    document.getElementById('taskForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addNewTask();
    });
    
    // Theme toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    themeBtn.addEventListener('click', toggleTheme);
    
    // Check for overdue tasks
    checkOverdueTasks();
});

// Initialize calendar
function initializeCalendar() {
    renderMonthView();
}

// Render month view
function renderMonthView() {
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();
    
    document.getElementById('currentMonth').textContent = 
        `${monthNames[currentMonth]} ${currentYear}`;
    
    // Get first day of month
    const firstDay = new Date(currentYear, currentMonth, 1);
    // Get last day of month
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    // Get number of days in month
    const daysInMonth = lastDay.getDate();
    // Get day of week for first day (0 = Sunday, 6 = Saturday)
    const firstDayIndex = firstDay.getDay();
    
    // Create calendar grid
    let calendarHTML = '<div class="calendar-grid">';
    
    // Add day headers
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(day => {
        calendarHTML += `<div class="day-header">${day}</div>`;
    });
    
    // Add empty cells for days before first day of month
    for (let i = 0; i < firstDayIndex; i++) {
        calendarHTML += `<div class="calendar-day"></div>`;
    }
    
    // Add days of month
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dayDate = new Date(currentYear, currentMonth, day);
        const isToday = dayDate.getTime() === today.getTime();
        const isWeekend = dayDate.getDay() === 0 || dayDate.getDay() === 6;
        
        // Count tasks for this day
        const dayTasks = complianceTasks.filter(task => {
            const taskDate = new Date(task.dueDate);
            return taskDate.getDate() === day &&
                   taskDate.getMonth() === currentMonth &&
                   taskDate.getFullYear() === currentYear;
        });
        
        let dayClass = 'calendar-day';
        if (isToday) dayClass += ' today';
        if (isWeekend) dayClass += ' weekend';
        
        calendarHTML += `
            <div class="${dayClass}" onclick="showDayTasks(${day}, ${currentMonth}, ${currentYear})">
                <div class="day-number">${day}</div>
                <div class="event-dots">
                    ${dayTasks.filter(t => t.priority === 'high').map(() => 
                        `<div class="event-dot" style="background: #e74c3c;"></div>`
                    ).join('')}
                    ${dayTasks.filter(t => t.priority === 'medium').map(() => 
                        `<div class="event-dot" style="background: #f39c12;"></div>`
                    ).join('')}
                    ${dayTasks.filter(t => t.priority === 'low').map(() => 
                        `<div class="event-dot" style="background: #17a2b8;"></div>`
                    ).join('')}
                </div>
                <div class="event-count">${dayTasks.length} tasks</div>
            </div>
        `;
    }
    
    calendarHTML += '</div>';
    document.getElementById('calendarView').innerHTML = calendarHTML;
}

// Change month
function changeMonth(direction) {
    currentDate.setMonth(currentDate.getMonth() + direction);
    if (currentView === 'month') {
        renderMonthView();
    }
    renderTasks();
}

// Change view
function changeView(view) {
    currentView = view;
    
    // Update active tab
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide views
    if (view === 'month') {
        document.getElementById('calendarView').style.display = 'block';
        document.getElementById('listView').style.display = 'none';
        renderMonthView();
    } else if (view === 'list') {
        document.getElementById('calendarView').style.display = 'none';
        document.getElementById('listView').style.display = 'block';
        renderListView();
    }
}

// Render list view
function renderListView() {
    let listHTML = '';
    const sortedTasks = [...complianceTasks].sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
    
    sortedTasks.forEach(task => {
        if (currentFilter !== 'all' && task.regulation !== currentFilter) return;
        if (currentPriorityFilter !== 'all' && task.priority !== currentPriorityFilter) return;
        
        const dueDate = new Date(task.dueDate);
        const now = new Date();
        const isOverdue = dueDate < now && !task.completed;
        
        listHTML += `
            <div class="task-item ${task.priority} ${isOverdue ? 'overdue' : ''}" onclick="toggleTask(${task.id})">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-duedate ${isOverdue ? 'text-danger' : ''}">
                        ${isOverdue ? '<i class="fas fa-exclamation-circle"></i> ' : ''}
                        ${formatDate(dueDate)}
                    </div>
                </div>
                <div class="task-description">${task.description}</div>
                <div class="task-tags">
                    <span class="task-tag">${task.regulation.toUpperCase()}</span>
                    <span class="task-tag">${task.priority}</span>
                    ${task.tags.map(tag => `<span class="task-tag">${tag}</span>`).join('')}
                </div>
            </div>
        `;
    });
    
    document.getElementById('upcomingList').innerHTML = listHTML;
}

// Render tasks in sidebar
function renderTasks() {
    let upcomingHTML = '';
    const now = new Date();
    const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    // Sort tasks by due date
    const sortedTasks = [...complianceTasks]
        .filter(task => !task.completed)
        .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
    
    // Filter tasks
    const filteredTasks = sortedTasks.filter(task => {
        if (currentFilter !== 'all' && task.regulation !== currentFilter) return false;
        if (currentPriorityFilter !== 'all' && task.priority !== currentPriorityFilter) return false;
        return true;
    });
    
    // Display up to 5 tasks
    filteredTasks.slice(0, 5).forEach(task => {
        const dueDate = new Date(task.dueDate);
        const isOverdue = dueDate < now;
        const isThisWeek = dueDate <= nextWeek && dueDate >= now;
        
        upcomingHTML += `
            <div class="task-item ${task.priority} ${isOverdue ? 'overdue' : ''}" onclick="toggleTask(${task.id})">
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-duedate ${isOverdue ? 'text-danger' : ''}">
                        ${isOverdue ? '<i class="fas fa-exclamation-circle"></i> ' : ''}
                        ${formatDate(dueDate)}
                    </div>
                </div>
                <div class="task-description">${task.description}</div>
                <div class="task-tags">
                    <span class="task-tag">${task.regulation.toUpperCase()}</span>
                    <span class="task-tag">${task.priority}</span>
                </div>
            </div>
        `;
    });
    
    document.getElementById('upcomingTasks').innerHTML = upcomingHTML;
    updateStats();
}

// Update statistics
function updateStats() {
    const now = new Date();
    const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    const totalTasks = complianceTasks.length;
    const completedTasks = complianceTasks.filter(task => task.completed).length;
    const dueThisWeek = complianceTasks.filter(task => {
        const dueDate = new Date(task.dueDate);
        return !task.completed && dueDate <= nextWeek && dueDate >= now;
    }).length;
    const pendingTasks = complianceTasks.filter(task => !task.completed).length;
    const overdueTasks = complianceTasks.filter(task => {
        const dueDate = new Date(task.dueDate);
        return !task.completed && dueDate < now;
    }).length;
    
    document.getElementById('totalTasks').textContent = totalTasks;
    document.getElementById('completedTasks').textContent = completedTasks;
    document.getElementById('dueThisWeek').textContent = dueThisWeek;
    document.getElementById('pendingTasks').textContent = pendingTasks;
    document.getElementById('overdueTasks').textContent = overdueTasks;
}

// Filter tasks by regulation
function filterTasks(regulation) {
    currentFilter = regulation;
    
    // Update active filter button
    document.querySelectorAll('.filter-buttons .filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderTasks();
    if (currentView === 'list') {
        renderListView();
    }
}

// Filter by priority
function filterPriority(priority) {
    currentPriorityFilter = priority;
    
    // Update active filter button
    const parent = event.target.parentElement;
    parent.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderTasks();
    if (currentView === 'list') {
        renderListView();
    }
}

// Toggle task completion
function toggleTask(id) {
    const task = complianceTasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        renderTasks();
        if (currentView === 'list') {
            renderListView();
        }
        updateStats();
        saveToLocalStorage();
    }
}

// Open task modal
function openTaskModal() {
    document.getElementById('taskModal').style.display = 'flex';
}

// Close task modal
function closeTaskModal() {
    document.getElementById('taskModal').style.display = 'none';
    document.getElementById('taskForm').reset();
    document.getElementById('priority').value = 'medium';
    // Reset priority buttons
    document.querySelectorAll('.priority-btn').forEach(btn => {
        btn.classList.remove('active');
    });
}

// Set priority
function setPriority(priority) {
    document.getElementById('priority').value = priority;
    
    // Update button styles
    document.querySelectorAll('.priority-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Add new task
function addNewTask() {
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const dueDate = document.getElementById('dueDate').value;
    const priority = document.getElementById('priority').value;
    const regulation = document.getElementById('regulation').value;
    const tags = document.getElementById('tags').value.split(',').map(tag => tag.trim()).filter(tag => tag);
    
    const newTask = {
        id: complianceTasks.length + 1,
        title,
        description,
        dueDate: new Date(dueDate),
        priority,
        regulation,
        tags,
        completed: false
    };
    
    complianceTasks.push(newTask);
    renderTasks();
    if (currentView === 'list') {
        renderListView();
    }
    if (currentView === 'month') {
        renderMonthView();
    }
    updateStats();
    closeTaskModal();
    saveToLocalStorage();
    
    // Show success message
    showNotification('Task added successfully!', 'success');
}

// Show tasks for a specific day
function showDayTasks(day, month, year) {
    const dayTasks = complianceTasks.filter(task => {
        const taskDate = new Date(task.dueDate);
        return taskDate.getDate() === day &&
               taskDate.getMonth() === month &&
               taskDate.getFullYear() === year;
    });
    
    if (dayTasks.length === 0) {
        showNotification(`No tasks scheduled for ${month + 1}/${day}/${year}`, 'info');
        return;
    }
    
    let message = `Tasks for ${month + 1}/${day}/${year}:\n\n`;
    dayTasks.forEach((task, index) => {
        const status = task.completed ? '✓ Completed' : '○ Pending';
        message += `${index + 1}. ${status} - ${task.title} (${task.priority})\n`;
    });
    
    alert(message);
}

// Format date
function formatDate(date) {
    const now = new Date();
    const taskDate = new Date(date);
    
    // If today
    if (taskDate.toDateString() === now.toDateString()) {
        return 'Today';
    }
    
    // If tomorrow
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    if (taskDate.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    }
    
    // If yesterday
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (taskDate.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    }
    
    // Otherwise format as date
    return taskDate.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

// Check for overdue tasks
function checkOverdueTasks() {
    const now = new Date();
    const overdueTasks = complianceTasks.filter(task => {
        const dueDate = new Date(task.dueDate);
        return !task.completed && dueDate < now;
    });
    
    if (overdueTasks.length > 0) {
        showNotification(`You have ${overdueTasks.length} overdue tasks!`, 'warning');
    }
}

// Toggle theme
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const themeIcon = document.querySelector('#themeToggleBtn i');
    themeIcon.className = document.body.classList.contains('dark-theme') ? 'fas fa-sun' : 'fas fa-moon';
    saveToLocalStorage();
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Set icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : type === 'warning' ? '#f39c12' : '#3498db'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Add animation styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Save to localStorage
function saveToLocalStorage() {
    const data = {
        tasks: complianceTasks,
        theme: document.body.classList.contains('dark-theme') ? 'dark' : 'light',
        currentDate: currentDate.toISOString()
    };
    localStorage.setItem('complianceCalendar', JSON.stringify(data));
}

// Load from localStorage
function loadFromLocalStorage() {
    const saved = localStorage.getItem('complianceCalendar');
    if (saved) {
        const data = JSON.parse(saved);
        complianceTasks = data.tasks || complianceTasks;
        
        if (data.theme === 'dark') {
            document.body.classList.add('dark-theme');
            const themeIcon = document.querySelector('#themeToggleBtn i');
            if (themeIcon) themeIcon.className = 'fas fa-sun';
        }
        
        if (data.currentDate) {
            currentDate = new Date(data.currentDate);
        }
    }
}