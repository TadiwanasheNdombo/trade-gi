document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadForm = document.getElementById('uploadForm');
    const processingStatus = document.getElementById('processingStatus');
    
    // Elements to update in the drop zone
    const icon = dropZone.querySelector('.upload-icon i');
    const mainText = dropZone.querySelector('h3');
    const subText = dropZone.querySelector('.upload-hint');

    // 1. Handle Click to Open File Dialog
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // 2. Handle File Selection via Click
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    // 3. Handle Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files; // Assign dropped files to the hidden input
            handleFile(files[0]);
        }
    }

    function handleFile(file) {
        // Validate PDF
        if (file.type !== 'application/pdf') {
            alert('Only PDF files are allowed.');
            fileInput.value = ''; // Reset selection
            resetUI();
            return;
        }

        // Update UI to show selected file
        icon.className = 'fas fa-file-pdf';
        icon.style.color = '#28a745';
        mainText.textContent = file.name;
        subText.textContent = formatBytes(file.size);
        
        dropZone.style.borderColor = '#28a745';
        dropZone.style.backgroundColor = '#f0fff4';

        // Enable Upload Button
        uploadBtn.disabled = false;
    }

    function resetUI() {
        icon.className = 'fas fa-cloud-upload-alt';
        icon.style.color = ''; // Reset to CSS default
        mainText.textContent = 'Drag & Drop PDF Here';
        subText.textContent = 'Or click to browse files';
        
        dropZone.style.borderColor = '';
        dropZone.style.backgroundColor = '';
        
        uploadBtn.disabled = true;
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // 4. Handle Form Submission (Visual Feedback)
    uploadForm.addEventListener('submit', function(e) {
        if (fileInput.files.length > 0) {
            // Hide upload area and show processing status
            document.querySelector('.upload-steps').style.display = 'none';
            dropZone.style.display = 'none';
            document.querySelector('.upload-actions').style.display = 'none';
            processingStatus.style.display = 'block';
            
            // Animate progress bar (simulated visual feedback)
            const fill = document.getElementById('progressFill');
            setTimeout(() => { fill.style.width = '30%'; }, 100);
            setTimeout(() => { fill.style.width = '60%'; }, 1500);
            setTimeout(() => { fill.style.width = '90%'; }, 3000);
        }
    });
});