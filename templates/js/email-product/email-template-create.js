const trixEditor = document.querySelector("#trix-editor");
const previewContainer = document.getElementById('file-previewContainer');
const fileInput = document.getElementById('file-upload');


console.log("trix: ", trixEditor.editor)
// Disable default file attachments
trixEditor.addEventListener("trix-attachment-add", function(event) {
    event.attachment.remove();
});


fileInput.addEventListener('change', function () {
    previewContainer.innerHTML = ''; // Clear previous previews

    for (const file of fileInput.files) {
        const filePreview = document.createElement('div');
        filePreview.classList.add('tw-shadow-lg', 'tw-p-1', '!tw-w-fit', 'tw-border-solid',
                                'tw-border-[0.2px]', 'tw-border-gray-700', 'tw-max-w-[150px]', 
                                'tw-flex', 'tw-gap-2', 'tw-place-items-center');
        const fileName = document.createElement('span');
        fileName.textContent = file.name;
        const removeButton = document.createElement('button');
        removeButton.classList.add('btn', 'btn-close');
        removeButton.addEventListener('click', function () {
            previewContainer.removeChild(filePreview);
        });

        filePreview.appendChild(fileName);
        filePreview.appendChild(removeButton);
        previewContainer.appendChild(filePreview);
    }
});
