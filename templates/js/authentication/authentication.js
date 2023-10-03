function checkSignUp(){

    const email = document.getElementById("email")
    const password = document.getElementById("password")

    const termsConditions = document.getElementById("terms-condition")
    const createAccbtn = document.getElementById("create-account-btn")

    const alert = document.getElementById("form-alert")


    if (!isValidEmail(email.value)){
        alertError(alert, "Invalid email")
        disableBtn(createAccbtn)
        return
    }else{
        hideAlertError(alert)
    } 

    if (password.value.trim().length < 6){
        alertError(alert, "Password too short")
        disableBtn(createAccbtn)
        return
    }else{
        hideAlertError(alert)
    }

    if (termsConditions.checked){
        enableBtn(createAccbtn)
    }else{
        disableBtn(createAccbtn)
    }
}


function checkLogin(){

    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    const loginBtn = document.getElementById("login-btn")
    const alert = document.getElementById("login-alert")

    if (!isValidEmail(email)){
        alertError(alert, "Invalid email")
        disableBtn(loginBtn)
        return
    }
    console.log("Password: ", password)
    if (password.length < 6){
        alertError(alert, "Invalid password")
        disableBtn(loginBtn)
        return
    }
    hideAlertError(alert)
    enableBtn(loginBtn)

}


function checkEmailResend(){
    
    email = event.target.value

    const alert = document.getElementById("resend-error")
    const submitBtn = document.getElementById("resend-email-btn")


    if (!isValidEmail(email)){
        alertError(alert, "Invalid email")
        disableBtn(submitBtn)
    }else{
        hideAlertError(alert)
        enableBtn(submitBtn)
    }

}
