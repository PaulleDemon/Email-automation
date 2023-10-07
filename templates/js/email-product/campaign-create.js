const fileInput = document.getElementById("file-upload");
const selectedFileName = document.getElementById("selected-file-name");

const followUpBtn = document.getElementById("followup-btn")
const followUpSection = document.getElementById("followup-section")

const followUpElement = document.querySelector("[title='follow-up']");

const templates = JSON.parse(document.getElementById('templates').textContent) || []
const rules = JSON.parse(document.getElementById('rules').textContent) || []

const campaignSchedule = document.getElementById("schedule_time")


const datetime = setDatetimeToLocal(campaignSchedule, 10 * 60 * 1000)
campaignSchedule.value = datetime

console.log("Follow up", followUpElement, fileInput)

followUpBtn.onclick = createFollowup

fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {

        const file = fileInput.files[0]
        const file_extension = file.name.split('.').at(-1)
        console.log("extension: ", file_extension)
        if (!['xlsx', 'xls', 'csv'].includes(file_extension)){
            toastAlert(null, `Invalid file`)
            fileInput.value = ''
            return
        }
        
        if (getFileSize(file, 'KB') > EMAIL_CAMPAIGN.upload_size){
            fileInput.value = ''
            toastAlert(null, `File too large, please upload file under 300 kb ${EMAIL_CAMPAIGN.upload_size}`)
            return
        }
        
        selectedFileName.textContent = file.name;
    } else {
        selectedFileName.textContent = "No file selected";
    }
});


function createFollowup(){

    const uuid = generateUUID()

    const FOLLOW_UP = `
    
                    <div class="tw-min-h-[150px] tw-min-w-[200px] tw-shadow-lg tw-rounded-lg tw-mt-[2%] tw-p-4
                        tw-flex tw-flex-col tw-gap-2" id="${uuid}">
                        <select class="form-select">
                            <option selected>Choose Template</option>
                            ${
                                templates.map(t => {
                                    return (
                                        `<option value=${t.i}>${t.name} #${t.id}</option>`
                                    )
                                })
                            }
                        </select>

                        <select class="form-select">
                            <option selected>Select rule</option>
                            ${
                                rules.map(r => {
                                    return (
                                        `<option value=${r.i}>${r.name}</option>`
                                    )
                                })
                            }
                        </select>

                        <div class="input-group mb-3">
                            <span class="input-group-text" id="">Schedule</span>
                            <input type="datetime-local" class="form-control" name="email_lookup" id="basic-url" autofocus 
                                    value="{% if campaign.email_lookup %}{{campaign.email_lookup}}{% else %}Email{% endif %}" 
                                    placeholder="default email address column">
                        </div>  

                        <div class="form-check !tw-w-full tw-mt-2 tw-text-lg !tw-place-items-center !tw-flex">
                            <button class="btn" onclick="deleteFollowup('${uuid}')">
                                <i class="tw-text-red-600 bi bi-trash"></i>
                            </button>
                            <input class="form-check-input !tw-ml-auto" onchange="" type="checkbox" value="" id="schedule">
                            <label class="form-check-label tw-m-1" for="schedule">
                                Schedule
                            </label>
                        </div>

                    </div>
                    `

    
    followUpSection.innerHTML += FOLLOW_UP
}

function deleteFollowup(id){
    document.getElementById(id).remove()
}