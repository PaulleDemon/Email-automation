const configurationAlert = document.getElementById("configuration-alert")
const hostInput = document.getElementById("host-input")
const portInput = document.getElementById("port-input")

const model = document.getElementById("delete-modal")
const modelForm = document.getElementById("modal-btn-delete")
const modelBody = document.getElementById("modal-body")


const form = document.getElementById("configuration-form")

const inputElements = form.querySelectorAll('[name]');

function updatePort(){
    portInput.value = event.target.value
}

function updateHost(){
    hostInput.value = event.target.value
}

function checkSubmition(){

    for (let e of inputElements){

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

function deleteConfiguration(url){
    modelForm.action = url
    modelBody.innerText = `Are you sure you want to delete configuration? This action cannot be undone.`
    // deleteModal.show()
    model.classList.remove("!tw-hidden")
}