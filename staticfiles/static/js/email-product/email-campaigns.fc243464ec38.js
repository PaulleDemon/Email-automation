const model = document.getElementById("delete-modal")
const modelForm = document.getElementById("modal-btn-delete")
const modelBody = document.getElementById("modal-body")

const deleteModal = new window.bootstrap.Modal(document.getElementById('myModal'))


function onDeleteCampaign(url, name){
    modelForm.action = url
    modelBody.innerText = `Are you sure you want to delete campaign "${name}"? This action cannot be undone.`
    // deleteModal.show()
    model.classList.remove("!tw-hidden")
}