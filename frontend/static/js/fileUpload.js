let multiFileUploadButton = document.querySelector('#multi-file-upload');
let clearButtton = document.querySelector('p.clear')


multiFileUploadButton.addEventListener('change', (e) => {
    const files = e.target.files
    const previewContainer = document.getElementById('preview');
    
    // Clear any previous previews
    previewContainer.innerHTML = '';

    // Loop through selected files and display each as an image
    Array.from(files).forEach((file) => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
            clearButtton.classList.remove('hide')
        } else {
            alert("Only image files are allowed!");
        }
    });
});

clearButtton.addEventListener('click', (e) => {
    const previewContainer = document.getElementById('preview');
    previewContainer.innerHTML = '';
    clearButtton.classList.add('hide')
});