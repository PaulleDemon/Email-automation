function checkSignUp(){

    const email = document.getElementById("email")
    const password = document.getElementById("password")

    const termsConditions = document.getElementById("terms-condition")
    const createAccbtn = document.getElementById("create-account-btn")

    const alert = document.getElementById("form-alert")


    if (!isValidEmail(email.value)){
        formError(alert, "Invalid email")
        disableBtn(createAccbtn)
        return
    }else{
        hideError(alert)
    } 

    if (password.value.trim().length < 6){
        formError(alert, "Password too short")
        disableBtn(createAccbtn)
        return
    }else{
        hideError(alert)
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
        formError(alert, "Invalid email")
        disableBtn(loginBtn)
        return
    }
    console.log("Password: ", password)
    if (password.length < 6){
        formError(alert, "Invalid password")
        disableBtn(loginBtn)
        return
    }
    hideError(alert)
    enableBtn(loginBtn)

}


function checkEmailResend(){
    
    email = event.target.value

    const alert = document.getElementById("resend-error")
    const submitBtn = document.getElementById("resend-email-btn")


    if (!isValidEmail(email)){
        formError(alert, "Invalid email")
        disableBtn(submitBtn)
    }else{
        hideError(alert)
        enableBtn(submitBtn)
    }

}
