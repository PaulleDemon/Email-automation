const trixEditor = document.querySelector("#trix-editor");
const editorElement = document.querySelector('.editor-container');

const previewContainer = document.getElementById("file-previewContainer");
const fileInput = document.getElementById("file-upload");

const templateAlert = document.getElementById("template-alert")
const alertToast = document.getElementById("error-toast")

const variablesInput = document.getElementById("variables")
const autoCompleteDropdown = document.getElementById('autoCompleteDropDown'); // Create a div for the drop-down container

const strategies = [
    {
      trigger: /\{$/, // Trigger on {
      search: function (term, callback) {
        // Perform an AJAX request to fetch autocomplete results
        // and call the callback with the results
        // Example:
        const results = ['{{', 'name', 'item3'];
        callback(results);
      },
      template: function (result) {
        // Return the HTML for an autocomplete item
        return `<div>${result}</div>`;
      },
      extract: function (item) {
        // Extract the selected item's HTML when selected
        return item.innerHTML;
      },
      replace: function (replacement, position) {
        // Replace the editor content with the selected replacement
        const editor = document.querySelector('.trix-content');
        editor.editor.setSelectedRange([position, position - 1]);
        editor.editor.insertHTML(replacement);
      },
    },
];
  
const autoComplete = new AutoComplete(document.querySelector("trix-editor").editor, editorElement, autoCompleteDropdown, strategies);

// Disable default file attachments
trixEditor.addEventListener("trix-attachment-add", function(event) {
    event.attachment.remove();
});


trixEditor.addEventListener('trix-change', function () {
    const text = trixEditor.innerText;
    const lastCharacter = text.charAt(text.length - 1);

    console.log("Change: ", text, lastCharacter)

    if (lastCharacter === '{') {
        autoComplete.autoCompleteHandler();
    }
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

        const downloadBtn = document.createElement('a')
        downloadBtn.classList.add('bi', 'bi-download', 'tw-text-xl', 'tw-font-semibold')
        downloadBtn.href = file
        downloadBtn.download = file.name

        const removeButton = document.createElement('button');
        removeButton.classList.add('btn', 'btn-close');

        removeButton.addEventListener('click', function () {
            previewContainer.removeChild(filePreview);
        });

        filePreview.appendChild(fileName);
        filePreview.appendChild(downloadBtn);
        filePreview.appendChild(removeButton);
        previewContainer.appendChild(filePreview);
    }
});


document.getElementById('variables-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const reader = new FileReader();

        reader.onload = function(e) {
            const data = e.target.result;

            if (!['csv', 'xlsx', 'xls'].includes(ext)){
                toastAlert(alertToast, "Incorrect file")
                return
            }

            if (ext === 'csv') {
                // Use PapaParse for CSV
                Papa.parse(data, {
                    header: true,
                    complete: function(results) {
                        displayColumnNames(results.meta.fields);
                        variablesInput.value = results.meta.fields.join(", ")
                    }
                });
            } else if (ext === 'xls' || ext === 'xlsx') {
                // Use SheetJS (XLSX) for XLS and XLSX
                const workbook = XLSX.read(data, { type: 'binary' });
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                const header = [];
                for (const key in firstSheet) {
                    if (key[0] === 'A') {
                        header.push(firstSheet[key].v);
                    }
                }
                variablesInput.value = header.join(", ")
            }
        };

        if (ext === 'csv') {
            reader.readAsText(file);
        } else if (ext === 'xls' || ext === 'xlsx') {
            reader.readAsBinaryString(file);
        }
    }
});