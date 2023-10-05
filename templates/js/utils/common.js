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
}

/**
 * 
 * @param {HTMLElement} toast 
 * @param {string} text 
 */
function toastAlert(toast, text=""){

    const toastBody = Array.from(toast.getElementsByClassName('toast-body'))
    toastBody.at(-1).innerText = text

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