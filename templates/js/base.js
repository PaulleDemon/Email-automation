// initialization

const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
return new bootstrap.Tooltip(tooltipTriggerEl)
})

const passwordInputs = document.querySelectorAll('input[type="password"]');

passwordInputs.forEach((passwordInput) => {
    // Create a container div 
    const container = passwordInput.parentElement
    // Create a toggle button
    const toggleButton = document.createElement('button');

    toggleButton.classList.add("btn", "btn-outline-secondary", "toggle-password");
    toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    
    // Append the elements to the container
    container.appendChild(toggleButton);
  
    toggleButton.addEventListener('click', (e) => {
        e.preventDefault()
        togglePasswordVisibility(toggleButton, passwordInput);
    });
  })

function togglePasswordVisibility(toggleButton, inputElement) {
    if (inputElement.type === "password") {
      inputElement.type = "text";
      toggleButton.innerHTML = '<i class="bi bi-eye"></i>';
    } else {
      inputElement.type = "password";
      toggleButton.innerHTML = '<i class="bi bi-eye-slash"></i>';
    }
}