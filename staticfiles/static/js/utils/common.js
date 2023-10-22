/**
 * commonnly used functions
 */


/**
 * 
 * @param {HTMLElement} alert 
 */
function hideAlertError(alert){
    alert.classList.add("tw-hidden")
    alert.innerText = ""
}

/**
 * @param {HTMLElement} alert 
 * @param {string} text 
 */
function alertError(alert, text=""){
    alert.innerText = text
    alert.classList.remove("tw-hidden")
    alert.classList.remove("!tw-hidden")
}

/**
 * 
 * @param {HTMLElement | null} toast 
 * @param {"normal" | "danger"} text 
 */
function toastAlert(toast, text="", type="normal"){

    if (toast == null){
        toast = defaultToast
    }

    if (type === "danger"){
        toast.classList.add("bg-danger")
        toast.classList.remove("bg-dark")
    }else{
        toast.classList.remove("bg-danger")
        toast.classList.add("bg-dark")
    }

    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast)
    const toastBody = Array.from(toast.getElementsByClassName('toast-body'))
    toastBody.at(-1).innerText = text
    
    toastBootstrap.show()
}

/**
 * 
 * @param {HTMLElement} toast 
 * @param {string} text 
 */
function resetToast(toast){

    const toastBody = Array.from(toast.getElementsByClassName('toast-body'))
    toastBody.at(-1).innerText = ""

}

/**
 * @param {HTMLElement} btn 
 */
function disableBtn(btn){
    btn.disabled = true
}

/**
 * @param {HTMLElement} btn 
 */
function enableBtn(btn){
    btn.disabled = false
}

function isValidEmail(email){
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function isValidDomain(domain) {
    // Regular expression pattern to match a valid domain, including subdomains
    const domainPattern = /^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/i;

    return domainPattern.test(domain);
}
 

/**
 * 
 * @param {File} file 
 * @param {'MB'|'KB'} unit 
 * @returns 
 */
function getFileSize(file, unit='MB') {
    // Check if the input is a valid File object
    if (file instanceof File) {
        const fileSizeInBytes = file.size;

        if (unit === 'KB') {
            // Calculate the file size in kilobytes
            const fileSizeInKB = fileSizeInBytes / 1024;
            return fileSizeInKB.toFixed(2) // Round to 2 decimal places and add the unit
        } else if (unit === 'MB') {
            // Calculate the file size in megabytes
            const fileSizeInMB = fileSizeInBytes / (1024 * 1024);
            return fileSizeInMB.toFixed(2) // Round to 2 decimal places and add the unit
        }
    } else {
        return null; // Invalid input, return null
    }
}

function generateUUID() {
    let d = new Date().getTime();
    if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
      d += performance.now(); // Use high-precision timer if available
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
}

/**
 * returns the current time + additional_time
 * @param {HTMLElement|null} datetimeElement 
 * @param {number} datetimeElement // used to add or subtract to the current time in ms
 */
function setDatetimeToLocal(datetimeElement, additonal_time=0){
    const currentDate = new Date();
    
    // Calculate the datetime 10 minutes from now
    const minDate = new Date(currentDate.getTime() + additonal_time);
    
    // Format the minDate as a string for the input field
    const minDateString = minDate.toISOString().slice(0, 16);
    // const minDateString = minDate.toUTCString();
    datetimeElement?.setAttribute('min', minDateString);

    return minDate
}

/**
 * 
 * @param {Date} datetime 
 * @returns 
 */
function toLocalTime(datetime){

    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        timeZoneName: 'short',
        hour12: true,
    };

    return datetime.toLocaleString('en-US', options);

}

/**
 * Makes the string input value format usable
 */
function UTCToUTCInputString(utcDateString){

    const utcDate = new Date(utcDateString)

    const year = utcDate.getUTCFullYear()
    const month = (utcDate.getUTCMonth() + 1).toString().padStart(2, '0')
    const day = utcDate.getUTCDate().toString().padStart(2, '0')
    const hours = utcDate.getUTCHours().toString().padStart(2, '0')
    const minutes = utcDate.getUTCMinutes().toString().padStart(2, '0')

    // Create a string in the format expected by the input element
    return `${year}-${month}-${day}T${hours}:${minutes}`

}  

function stringifyOnlyObjects(key, value) {
    if (typeof value === 'object' && value !== null) {
        return value; // Include only objects
    }
    return undefined; // Exclude all other types
}

function isValidVariableFormat(inputString){
    try {
        JSON5.parse(inputString);
        return true
    } catch (error) {
        return false
    }
    
}

/**
 * 
 * @param {string} template 
 * @param {{}} context 
 * @returns 
 */
function renderTemplate(template, context){
    const copyContext = JSON5.parse(context || '{}');
    
    copyContext['from_email'] = copyContext['from_email'] || "paul@mail.com";
    copyContext['from_name'] = copyContext['from_name'] || "Paul";
    copyContext['from_signature'] = copyContext['from_signature'] || "Best regards, Paul";

    return nunjucks.renderString(template, copyContext)
}

function parseTemplateModalVariables(){
    const alertWarning = document.getElementById("templateModalAlert")
    const testVariables = document.getElementById("templateModal-variables")

    if(!isValidVariableFormat(testVariables.value)){
        alertError(alertWarning, "Cannot parse variables, Please use JS object model eg: {name: 'hellp', id: 2}")
    }else{
        hideAlertError(alertWarning)
    }

}

async function viewTemplate(id){

    const templateModalTitle = document.getElementById("templateViewModelLabel")
    const templateModalSubject = document.getElementById("templateModalSubject")
    
    const templateModalBody = document.getElementById("templateViewModel-body")
    const templateModalLoader = document.getElementById("templateViewModel-loader")
    const testVariables = document.getElementById("templateModal-variables")
    const editButton = document.getElementById("templateModalEdit")
    
    const alertWarning = document.getElementById("templateModalAlert")


    // fetches the full template.
    templateModalLoader?.classList.remove("!tw-hidden")
    
    const res = await fetch(`/email/${id}/view-mail/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": Cookies.get('csrftoken'),
            // 'Content-Type': 'application/json'
            }, 
    })

    let data = undefined
    try {
        if (res.headers.get('content-type') === 'application/json') {
            data = await res.json();
            responseBody = JSON.stringify(data); // Store the JSON response body
        } else {
            data = await res.text();
            responseBody = data; // Store the text response body
        }
    } catch (e) {
        data = await res;
        return
    }
    templateModalLoader?.classList.add("!tw-hidden")

    if (res.status == 400){
        alertError(alertWarning, "Something went wrong")
    }

    if (res.status == 429){
        toastAlert(null, "Too many requests please wait", "danger")
        alertError(alertWarning, "Too many requst please close this modal and wait")

    }

    if (res.status == 200){
        templateModalTitle.innerText = data.name
        templateModalSubject.innerText = data.subject
        templateModalBody.innerText = data.body
        
        editButton.setAttribute("href", data.edit_url)

        try{
            testVariables.value = data.variables// JSON.stringify(JSON.parse(data.variables), null, 4) || JSON.stringify({})
        } catch(error){
            alertError(alertWarning, "Cannot parse variables, please add your own")
        }
    }

}


function templateModalRenderPreview(){
    const templateModalSubject = document.getElementById("templateModalSubject")
    const templateModalBody = document.getElementById("templateViewModel-body")
    const testVariables = document.getElementById("templateModal-variables")

    const alertWarning = document.getElementById("templateModalAlert")

    try{
        templateModalBody.innerHTML = renderTemplate(templateModalBody.innerText, testVariables.value)
        templateModalSubject.innerHTML = renderTemplate(templateModalSubject.innerText, testVariables.value)
        hideAlertError(alertWarning)
    }catch(e){
        alertError(alertWarning, "error with the template or variables.")
        // console.log("Error :", e)
    }
}


// function templateModalClosed(){
//     const templateModalSubject = document.getElementById("templateViewModelLabel")
//     const templateModalBody = document.getElementById("templateViewModel-body")
//     const templateModalLoader = document.getElementById("templateViewModel-loader")

//     templateModalLoader.classList.remove("!tw-hidden")
//     templateModalSubject.innerText = ""
//     templateModalBody.innerHTML = ""
// }