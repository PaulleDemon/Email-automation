const model = document.getElementById("delete-modal")
const modelForm = document.getElementById("modal-btn-delete")
const modelBody = document.getElementById("modal-body")

const deleteModal = new window.bootstrap.Modal(document.getElementById('myModal'))

console.log("delete modal", deleteModal)

function onDeleteTemplate(url, name){
    modelForm.action = url
    modelBody.innerText = `Are you sure you want to delete template ${name}? This action cannot be undone.`
    // deleteModal.show()
    model.classList.remove("!tw-hidden")
}