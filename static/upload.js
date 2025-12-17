// upload.js - Handles drag & drop, file selection, and UI for upload page

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const processingStatus = document.getElementById('processingStatus');
    const uploadForm = document.getElementById('uploadForm');

    // Enable upload button when a file is selected
    fileInput.addEventListener('change', function() {
        uploadBtn.disabled = !fileInput.files.length;
    });

    // Drag & drop events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            uploadBtn.disabled = false;
        }
    });

    // Show processing status on submit
    uploadForm.addEventListener('submit', function() {
        processingStatus.style.display = 'block';
    });
});
