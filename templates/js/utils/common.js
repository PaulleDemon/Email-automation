/**
 * commonnly used functions
 */

const defaultToast = document.getElementById("error-toast")

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
}

/**
 * 
 * @param {HTMLElement | null} toast 
 * @param {string} text 
 */
function toastAlert(toast, text=""){

    if (toast === null){
        toast = defaultToast
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
    // Regular expression pattern to match a valid domain
    const domainPattern = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/
  
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
            return fileSizeInKB.toFixed(2) + ' KB'; // Round to 2 decimal places and add the unit
        } else if (unit === 'MB') {
            // Calculate the file size in megabytes
            const fileSizeInMB = fileSizeInBytes / (1024 * 1024);
            return fileSizeInMB.toFixed(2) + ' MB'; // Round to 2 decimal places and add the unit
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
    console.log("mon date: ", minDateString)
    datetimeElement?.setAttribute('min', minDateString);

    return minDateString
}