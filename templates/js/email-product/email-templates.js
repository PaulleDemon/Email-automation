const model = document.getElementById("delete-modal")
const modelForm = document.getElementById("modal-btn-delete")
const modelBody = document.getElementById("modal-body")

const deleteModal = new window.bootstrap.Modal(document.getElementById('myModal'))

function onDeleteTemplate(url, name){
    modelForm.action = url
    modelBody.innerText = `Are you sure you want to delete template ${name}? This action cannot be undone.`
    // deleteModal.show()
    model.classList.remove("!tw-hidden")
}


async function viewTmplate(id){
    // fetches the full template.

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
        console.log("response: ", res);
        data = await res;
        return
    }

    if (res.status == 400){
        return
    }

    if (res.status == 200){

        data

    }

}