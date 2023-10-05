const configurationAlert = document.getElementById("configuration-alert")
const hostInput = document.getElementById("host-input")
const portInput = document.getElementById("port-input")

const form = document.getElementById("configuration-form")

const inputElements = form.querySelectorAll('[name]');

function updatePort(){
    portInput.value = event.target.value
}

function updateHost(){
    hostInput.value = event.target.value
}

console.log("input: ", inputElements)

function checkSubmition(){

    for (let e of inputElements){
        console.log("Value: ", e.name, e.value)

        if (e.name == 'email' && !isValidEmail(e.value)){
            alertError(configurationAlert, "Invalid email")
            return false
        }
        
        if (e.name == 'password' && e.value.length < 1){
            alertError(configurationAlert, "Invalid Password")
            return false
        }

        if (e.name == 'host' && !isValidDomain(e.value)){
            alertError(configurationAlert, "Invalid host")
            return false
        }


        if (e.name == 'port' && e.value === ''){
            alertError(configurationAlert, "Invalid port")
            return false
        }

    }

    return true

}