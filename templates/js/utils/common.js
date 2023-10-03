/**
 * commonnly used functions
 */

/**
 * 
 * @param {HTMLElement} alert 
 */
function hideError(alert){
    alert.classList.add("tw-hidden")
    alert.innerText = ""
}

/**
 * @param {HTMLElement} alert 
 * @param {string} text 
 */
function formError(alert, text=""){
    alert.innerText = text
    alert.classList.remove("tw-hidden")
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