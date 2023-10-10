const campaign = document.getElementById("campaign")

const fileInput = document.getElementById("file-upload");
const selectedFileName = document.getElementById("selected-file-name");

const followUpBtn = document.getElementById("followup-btn")
const followUpSection = document.getElementById("followup-section")

const followUpElement = document.querySelector("[title='follow-up']");

const templates = JSON.parse(document.getElementById('templates')?.textContent || '[]')
const rules = JSON.parse(document.getElementById('rules')?.textContent || '[]')

const campaignSchedule = document.getElementById("schedule_time")
const localTime = document.getElementById("local-time")

const templateViewBtn = document.getElementById("template-view")


const datetime = setDatetimeToLocal(campaignSchedule, 10 * 60 * 1000)

if (!campaignSchedule.value){
    campaignSchedule.value = datetime.toISOString().slice(0, 16)
}

localTime.innerText = toLocalTime(datetime)

followUpBtn.onclick = createFollowup

function updateLocalTime(){
    // triggered when the campaign schedule is changed, updates the localtime and sets
    // min datetime for all the follow ups
    const datetime = new Date(event.target.value)

    localTime.innerText = toLocalTime(datetime)

    setMinFollowUpDatetime()
}

function setMinFollowUpDatetime(){

    const followUp = Array.from(document.querySelectorAll("[title='followup-schedule']")|| [])

    const datetime = new Date(campaignSchedule.value)

    const minDatetime = new Date(datetime.getTime() + 20 * 60 *1000)

    console.log("Datetime: ", minDatetime.toISOString().slice(0, 16))

    followUp.forEach(e => {
        // set min datetime for each follow up
        console.log("YAA: ",  minDatetime.toISOString().slice(0, 16))
        e.setAttribute("min", minDatetime.toISOString().slice(0, 16))
    })
    console.log("followup: ", )
    followUp.forEach(e => console.log("Stay: ", e))

    return minDatetime
}

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


function viewTemplate(){
 
    if (event.target.value){
        const url = templateViewBtn.getAttribute("url") + `?edit=${event.target.value}`
        templateViewBtn.setAttribute("href", url) 
    }else{
        templateViewBtn.removeAttribute("href")
    }
}


function createFollowup(){

    const uuid = generateUUID()

    const FOLLOW_UP = `
    
                    <div class="tw-min-h-[150px] tw-min-w-[200px] tw-shadow-lg tw-rounded-lg tw-mt-[2%] tw-p-4
                        tw-flex tw-flex-col tw-gap-2" id="${uuid}" name='follow-up'>
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
                                        `<option value=${r[0]}>${r[1]}</option>`
                                    )
                                })
                            }
                        </select>

                        <div class="input-group mb-3">
                            <span class="input-group-text" id="">Schedule</span>
                            <input type="datetime-local" class="form-control" name="email_lookup" id="basic-url" autofocus 
                                    value="" 
                                    title='followup-schedule'
                                    placeholder="default email address column">
                        </div>  

                        <div class="form-check !tw-w-full tw-mt-2 tw-text-lg !tw-place-items-center !tw-flex">
                            <button class="btn" onclick="deleteFollowup('${uuid}')">
                                <i class="tw-text-red-600 bi bi-trash"></i>
                            </button>
                            <input class="form-check-input !tw-ml-auto" onchange="" type="checkbox" value="" >
                            <label class="form-check-label tw-m-1" for="schedule">
                                Schedule
                            </label>
                        </div>

                    </div>
                    `

    
    followUpSection.innerHTML += FOLLOW_UP
    setMinFollowUpDatetime()
}   

function deleteFollowup(id){
    document.getElementById(id).remove()
}


function checkFields(){

    const inputFields = campaign.querySelectorAll("[name]")

    for(let x of inputFields){
    
        if (x.name === "name" && x.value.trim().length < 3){
            toastAlert(null, "Please give a proper campaign name")
            return false
        }

        if (x.name === "email_lookup" && x.value.trim().length === 0){
            toastAlert(null, "Please fill default email column")
            return false
        }
        
        if (x.name === "from_email" && !x.value){
            toastAlert(null, "Please select the from email")
            return false
        }

        if (x.name === "file" && !x.value){
            toastAlert(null, "Please upload your excel file")
            return false
        }


        if (x.name === "template" && !x.value){
            toastAlert(null, "Please select the template")
            return false
        }

        if (x.name === "template" && !x.value){
            toastAlert(null, "Please select the template")
            return false
        }

        if (x.name === "schedule" && (!x.value || new Date(x.value) < new Date())){
            toastAlert(null, "scheduled time must be greater than now!")
            return false
        }

    }
    console.log("false")
    return true
}