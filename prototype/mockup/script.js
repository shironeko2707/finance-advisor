// Global Variables
let currentUser = null;
let uploadedFiles = [];
let isGenerating = false;
let users = [];

// Sample Users Data
const sampleUsers = [
    {
        id: 1,
        username: 'admin',
        password: 'admin123',
        firstName: 'System',
        lastName: 'Administrator',
        email: 'admin@kheng-leong.com',
        role: 'admin',
        status: 'active',
        lastLogin: new Date('2025-08-21T10:30:00'),
        createdAt: new Date('2025-01-01')
    },
    {
        id: 2,
        username: 'hoangpt',
        password: 'password',
        firstName: 'Hoang',
        lastName: 'Pham',
        email: 'hoangpt@kheng-leong.com',
        role: 'user',
        status: 'active',
        lastLogin: new Date('2025-08-21T09:15:00'),
        createdAt: new Date('2025-02-15')
    },
    {
        id: 3,
        username: 'jason.derulo',
        password: 'manager123',
        firstName: 'Jason',
        lastName: 'Derulo',
        email: 'jason.derulo@kheng-leong.com',
        role: 'manager',
        status: 'active',
        lastLogin: new Date('2025-08-21T08:45:00'),
        createdAt: new Date('2025-01-15')
    },
    {
        id: 4,
        username: 'mike.wilson',
        password: 'user123',
        firstName: 'Mike',
        lastName: 'Wilson',
        email: 'mike.wilson@kheng-leong.com',
        role: 'user',
        status: 'inactive',
        lastLogin: new Date('2025-08-18T16:20:00'),
        createdAt: new Date('2025-03-01')
    },
    {
        id: 5,
        username: 'sarah.chen',
        password: 'user123',
        firstName: 'Sarah',
        lastName: 'Chen',
        email: 'sarah.chen@kheng-leong.com',
        role: 'manager',
        status: 'active',
        lastLogin: new Date('2025-08-20T14:30:00'),
        createdAt: new Date('2025-02-28')
    }
];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Load saved data
    loadSavedData();
    
    // Check for saved login
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showMainApp();
    } else {
        showLoginScreen();
    }
    
    setupEventListeners();
    updateFileDisplays();
    startClock();
}

function loadSavedData() {
    // Load users from localStorage or use sample data
    const savedUsers = localStorage.getItem('users');
    users = savedUsers ? JSON.parse(savedUsers) : [...sampleUsers];
    saveUsers();
}

function saveUsers() {
    localStorage.setItem('users', JSON.stringify(users));
}

function setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // File upload events
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.querySelector('.browse-btn');
    const generateBtn = document.getElementById('generateBtn');

    // Browse button click
    browseBtn?.addEventListener('click', () => {
        fileInput.click();
    });

    // Dropzone click
    dropzone?.addEventListener('click', (e) => {
        if (e.target === dropzone || e.target.closest('.upload-content')) {
            fileInput.click();
        }
    });

    // File input change
    fileInput?.addEventListener('change', handleFileSelect);

    // Drag and drop events
    dropzone?.addEventListener('dragover', handleDragOver);
    dropzone?.addEventListener('dragleave', handleDragLeave);
    dropzone?.addEventListener('drop', handleDrop);

    // Generate report button
    generateBtn?.addEventListener('click', handleGenerateReport);

    // Delete file events (using event delegation)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-icon')) {
            const fileName = e.target.closest('.file-item').querySelector('.file-name').textContent;
            deleteFile(fileName);
        }
    });

    // User search and filter
    const userSearch = document.getElementById('userSearch');
    const roleFilter = document.getElementById('roleFilter');
    
    userSearch?.addEventListener('input', filterUsers);