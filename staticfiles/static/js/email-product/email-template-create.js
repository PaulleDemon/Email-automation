const form = document.getElementById("template-create")

const trixEditor = document.querySelector("#trix-editor");
const editorElement = document.querySelector('.editor-container');

const testMailBtn = document.getElementById("test-mail-btn")

const previewContainer = document.getElementById("file-previewContainer");
const fileInput = document.getElementById("file-upload");

const templateAlert = document.getElementById("template-alert")
const alertToast = document.getElementById("error-toast")

const variablesInput = document.getElementById("variables")
const variableUpload = document.getElementById('variables-upload')

const autoCompleteDropdown = document.getElementById('autoCompleteDropDown'); // Create a div for the drop-down container

testMailBtn.onclick = sendTestMail


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

    // console.log("Change: ", text, lastCharacter)

    if (lastCharacter === '{') {
        autoComplete.autoCompleteHandler();
    }
});


fileInput.addEventListener('change', function () {
    previewContainer.innerHTML = ''; // Clear previous previews

    let fileSize = 0 // 0 MB

    for (const file of fileInput.files) {
        fileSize += getFileSize(file, "MB")
    }

    if (fileSize > TEMPLATE.attachment_size){
        toastAlert(alertToast, `Files cannot be larger than ${TEMPLATE.attachment_size} MB`)
        fileInput.value = null
        return 
    }

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


function removeFileAttachment(id){
    previewContainer.removeChild(previewContainer.querySelector(`#${id}`))
}


variableUpload.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const reader = new FileReader();

        if (getFileSize(file, "KB") > EMAIL_CAMPAIGN.upload_size){
            variableUpload.value = null
            toastAlert(alertToast, "File too large")
            return
        }

        reader.onload = function(e) {
            const data = e.target.result;

            if (!['csv', 'xlsx', 'xls'].includes(ext)){
                toastAlert(alertToast, "Incorrect file")
                variableUpload.value = null
                return
            }

            if (ext === 'csv') {
                // Use PapaParse for CSV
                Papa.parse(data, {
                    header: true,
                    complete: function(results) {
                        // Extract column names
                        const columnNames = results.meta.fields;
                        displayColumnNames(columnNames);
                        
                        // Extract the first row values
                        const firstRowValues = results.data[0];

                        // Create key-value pairs
                        const keyValues = {};
                        columnNames.forEach((columnName, index) => {
                            keyValues[columnName] = firstRowValues[index];
                        });

                        // Set the key-value pairs as an object
                        variablesInput.value = JSON.stringify(keyValues);

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

                // Extract the first row values
                const firstRowValues = [];
                for (const key in firstSheet) {
                    if (key[0] === 'B') {
                        firstRowValues.push(firstSheet[key].v);
                    }
                }

                // Create key-value pairs
                const keyValues = {};
                header.forEach((columnName, index) => {
                    keyValues[columnName] = firstRowValues[index];
                });

                // Set the key-value pairs as an object
                variablesInput.value = JSON.stringify(keyValues, null, 4);
            }
        };

        if (ext === 'csv') {
            reader.readAsText(file);
        } else if (ext === 'xls' || ext === 'xlsx') {
            reader.readAsBinaryString(file);
        }
    }
})

/**
 * given a csv or xls file returns the header 
 * @param {File} file 
 */
function getHeaderFromFile(file){

    const ext = file.name.split('.').pop().toLowerCase();
    const reader = new FileReader();

    reader.onload = function(e) {
        const data = e.target.result;

        if (!['csv', 'xlsx', 'xls'].includes(ext)){
            toastAlert(alertToast, "Incorrect file")
            variableUpload.value = null
            return
        }

        if (ext === 'csv') {
            // Use PapaParse for CSV
            Papa.parse(data, {
                header: true,
                complete: function(results) {
                    displayColumnNames(results.meta.fields);
                    return results.meta.fields.join(", ")
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
            return header.join(", ")
        }
    };

    if (ext === 'csv') {
        reader.readAsText(file);
    } else if (ext === 'xls' || ext === 'xlsx') {
        reader.readAsBinaryString(file);
    }

}


function warnUserOnPublic(){
    // show warning when the user make the template public
    if (event.target.checked){
        templateAlert.innerText = "Warning: Upon submission this tempate is made public, including the file attachments."
        templateAlert.classList.remove('tw-hidden', 'alert-danger')
        templateAlert.classList.add('alert-warning')
    }else{
        templateAlert.classList.add('tw-hidden')
    }

}

function validateVariables(){
    const value = variablesInput.value
    if (isValidVariableFormat(value)){
        hideAlertError(templateAlert)
    }else{
        alertError(templateAlert, "template variables are in incorrect format. Please use the format specified.")
    }
}


function validateTemplate(){

    const elements = form.querySelectorAll("[name]")

    for (let x of elements){

        if (x.name == "name" && x.value.trim().length < 3){
            toastAlert(null, "Please provide a proper template name")
            return false
        }

        if (x.name == "subject" && x.value.trim().length < 5){
            toastAlert(null, "Please provide a proper subject")
            return false
        }

        if (x.name == "body" && trixEditor.innerText.trim().length < 10){
            toastAlert(null, "Please provide a proper body")
            return false
        }

        if (x.name == "body" || x.name == "subject"){

            try{
                const value = x.value
                renderTemplate(value, variablesInput.value)
                hideAlertError(templateAlert)
            }catch(e){
                alertError(templateAlert, `Error in template ${e}`)
                return false
            }
        }
        
    }
    
    return true
}

async function sendTestMail(){

    if (!validateTemplate())
        return

    testMailBtn.disabled = true
    testMailBtn.classList.add("spinner-border", "text-light")

    const elements = form.querySelectorAll("[name]")

    let data = new FormData()
    
    if (fileInput.files) {
        for (let i = 0; i < fileInput.files.length; i++) {
            data.append('attachments', fileInput.files[i]);
        }
    }
    
    for (let x of elements){
        data.append(x.name, x.value)
    }

    const res = await fetch("/email/send-test-mail/", {
        method: "POST",
        headers: {
            "X-CSRFToken": Cookies.get('csrftoken'),
            // "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryABC123"
            }, 
        body: data
    })

    let res_data = {}

    try {
        if (res.headers.get('content-type') === 'application/json') {
            res_data = await res.json();
            responseBody = JSON.stringify(data); // Store the JSON response body
        } else {
            res_data = await res.text();
            responseBody = data; // Store the text response body
        }
    } catch (e) {
        // console.log("response: ", res);
        data = await res;
        return
    }

    if (res.status == 400){
        if (res_data.json){
            toastAlert(null, "Please check your variable structure", "danger")
        }
        if (res_data.file){
            toastAlert(null, "File too large", "danger")
        }
        if (res_data.error){
            toastAlert(null, res_data.error, "danger")

        }
    }

    if (res.status == 200){
        toastAlert(null, "Email has been sent successfully. If you cannot find it please check spam.")
    }

    if (res.status == 429){
        toastAlert(null, "Too many requests please wait")
    }

    if (res.staus == 302){
        window.location = res.redirect
    }
    
    testMailBtn.disabled = false
    testMailBtn.classList.remove("spinner-border", "text-light")

}


function templateRenderPreview(){

    const elements = form.querySelectorAll("[name]")
    const data = {}
    for (let x of elements){

        data[x.name] = x.value
    }

    const templateModalSubject = document.getElementById("templateModalSubject")
    
    const templateModalBody = document.getElementById("templateViewModel-body")
    const templateModalLoader = document.getElementById("templateViewModel-loader")
    const testVariables = document.getElementById("templateModal-variables")

    templateModalLoader?.classList.add("!tw-hidden")

    const alertWarning = document.getElementById("templateModalAlert")

    try{
        testVariables.innerText = variablesInput.value

        const body = renderTemplate(data.body, variablesInput.value)
        const subject = renderTemplate(data.subject, variablesInput.value)

        templateModalBody.innerHTML =`<b>subject: </b>${subject} <br/><br/>${body}`
        templateModalSubject.innerText = data.name
        hideAlertError(alertWarning)
    }catch(e){
        alertError(alertWarning, "error with the template or variables.")
        // console.log("Error :", e)
    }
}