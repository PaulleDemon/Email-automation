const campaign = document.getElementById("campaign")

const fileInput = document.getElementById("file-upload");
const selectedFileName = document.getElementById("selected-file-name");

const hiddenFollowup = document.getElementById("hidden-followups") //used in form submition
const followUpBtn = document.getElementById("followup-btn")
const followUpSection = document.getElementById("followup-section")

const followUpElement = document.querySelector("[title='follow-up']");

const templates = JSON.parse(document.getElementById('templates')?.textContent || '[]')
const rules = JSON.parse(document.getElementById('rules')?.textContent || '[]')

const campaignSchedule = document.getElementById("schedule_time")
const localTime = document.getElementById("local-time")

const templateViewBtn = document.getElementById("template-view")


const datetime = setDatetimeToLocal(campaignSchedule, 10 * 60 * 1000) // add 10 minutes to the current time


if (!campaignSchedule.value){
    new Date().toLocaleString()
    console.log("DATetime: ", datetime.toLocaleString())
    campaignSchedule.value = `${datetime.getFullYear()}-${(datetime.getMonth() + 1).toString().padStart(2, '0')}-${datetime.getDate().toString().padStart(2, '0')}T${datetime.getHours().toString().padStart(2, '0')}:${datetime.getMinutes().toString().padStart(2, '0')}`;

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


if (fileInput.value){
    fileInput.value = fileInput.value
    console.log("FILE: ", fileInput.value)
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


function templatePreview(){
 
    if (event.target.value){
        // const url = templateViewBtn.getAttribute("url") + `?edit=${event.target.value}`
        // templateViewBtn.setAttribute("href", url)
        templateViewBtn.setAttribute("onclick", `viewTemplate(${event.target.value})`)
        // viewTemplate(event.target.value) 

    }else{
        templateViewBtn.removeAttribute("onclick")
    }
}


function followUpTemplate(uuid) {

    const followUpcontainer = document.createElement('div')
    followUpcontainer.setAttribute("id", uuid)
    followUpcontainer.setAttribute("title", "follow-up")
    followUpcontainer.setAttribute("class", `tw-min-h-[150px] tw-min-w-[200px] tw-shadow-lg tw-rounded-lg tw-mt-[2%] tw-p-4
                                            tw-flex tw-flex-col tw-gap-2`)


    const followUp = `
            <select class="form-select" name="followup-template">
                <option selected value="">Choose Template</option>
                ${
                    templates.map(t => {
                        return (
                            `<option value="${t.id}" >${t.name} #${t.id}</option>`
                        )
                    })
                }
            </select>
            <select class="form-select" name="rule">
                <option selected value="">Select rule</option>
                ${
                    rules.map(r => {
                        return (
                            `<option value="${r[0]}"}>${r[1]}</option>`
                        )
                    })
                }
            </select>
            <div class="input-group mb-3">
                <span class="input-group-text" id="">Schedule</span>
                <input type="datetime-local" class="form-control" name="followup-schedule" id="basic-url" autofocus 
                        value="" 
                        title='followup-schedule'
                        placeholder="default email address column">
            </div>
            <div class="form-check !tw-w-full tw-mt-2 tw-text-lg !tw-place-items-center !tw-flex">
                <button class="btn" onclick="deleteFollowup('${uuid}')">
                    <i class="tw-text-red-600 bi bi-trash"></i>
                </button>
                <input class="form-check-input !tw-ml-auto" onchange="" type="checkbox" 
                    checked value="scheduled" id="followup-scheduled-${uuid}" name="followup-scheduled">
                <label class="form-check-label tw-m-1" for="followup-scheduled-${uuid}">
                    Schedule
                </label>
            </div>
    `;
    followUpcontainer.innerHTML = followUp

    return followUpcontainer
}

const followupsData = [];

function createFollowup(){

    // Create and append the follow-up HTML with data
    const uuid = generateUUID();
    const followUpHTML = followUpTemplate(uuid)
    
    // Append the follow-up HTML to the container
    followUpSection.appendChild(followUpHTML)

    setMinFollowUpDatetime();
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
       
        if (x.name === "file" && (!x.value && !x.title)){
            toastAlert(null, "Please upload your excel file")
            return false
        }


        if (x.name === "template" && !x.value){
            toastAlert(null, "Please select the template")
            return false
        }

        if (x.name === "schedule") {
        
            if(!x.value || new Date(x.value) < new Date()){
                toastAlert(null, "scheduled time must be greater than now!")
                return false
            }
            console.log("value1: ", x.value)
            x.value = new Date(x.value).toLocaleString()
            console.log("value: ", x.value)
        }

    }
    const followUpElements = followUpSection.querySelectorAll("[title='follow-up']");
    
    let followup_data = []

    for (let x=0; x < followUpElements.length; x++){

        const followUpFields = followUpElements[x].querySelectorAll("[name]")

        let data = {}

        for (let y of followUpFields){

            const name = y.name
            const value = y.value

            console.log("followup", name)

            if (name == "followup-template" && !value){
                toastAlert(null, `Select a template for Follow up ${x+1}`)
                return false
            }

            if (name == "rule" && !value){
                toastAlert(null, `Select a rule for follow up ${x+1}`)
                return false
            }

            if (name == "followup-schedule"){
                if (!value || new Date(value) < new Date(campaignSchedule.value)){
                    toastAlert(null, `Follow up ${x+1} date has to be greater than the campaign schedule`)
                    return false
                }
                y.value = new Date(value).toUTCString()
            }
            
            if (name == 'followup-scheduled')
                if (y.checked)
                    data['followup-scheduled'] = value
                else
                    data['followup-scheduled'] = ''

            else
                data[name] = value

        }
        followup_data.push(data)
        console.log("follow up", followup_data, followUpFields, followUpSection)

    }

    hiddenFollowup.value =  JSON.stringify(followup_data)
    return false
}