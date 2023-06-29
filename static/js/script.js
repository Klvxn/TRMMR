const flashMessages = document.querySelectorAll('.flash-msg');

flashMessages.forEach((message) => {
  const category = message.getAttribute('data-category');

  switch (category) {
    case 'success':
      message.style.backgroundColor = 'lightgreen';
      break;
    case 'error':
      message.style.backgroundColor = 'lightcoral';
      break;
    default:
      message.style.backgroundColor = 'cadetblue';
  }
  setTimeout(() => {
    message.style.display = "none";
    }, 3000);
});


const formError = document.querySelectorAll(".form-error");
formError.forEach((error) => {
  setTimeout(() => {
    error.style.display = "none";
    error.textContent = ""
  }, 3000);
})


// Paste text from clipboard
function pasteFromClipboard() {
  navigator.clipboard.readText()
    .then(text => {
      const tags = document.querySelectorAll("#URLInput");
      tags.forEach((tag) => {
        tag.value = text;
      })
    })
    .catch(error => {
      console.error("Failed to paste from clipboard: ", error);
    });
}


// Copy text to clipboard
function copyToClipboard(text) {
  const feedbackMessage = document.createElement("p");
  feedbackMessage.id = "feedback";
  document.body.appendChild(feedbackMessage);
  navigator.clipboard.writeText(text)
    .then(() => {
      feedbackMessage.textContent = "Text copied to clipboard";
      feedbackMessage.style.display = "block";

      setTimeout(() => {
        feedbackMessage.textContent = "";
        feedbackMessage.style.display = 'none';
      }, 3000);
    })
    .catch((error) => {
      alert("Error copying text to clipboard:");
    });
}


// Clear input field
function clearInput() {
  const tags = document.querySelectorAll("#URLInput");
  tags.forEach((tag) => {
    tag.value = "";
  })
}


// Add Password Form
function addPasswordForm() {
  const container = document.getElementById("pwd-form");
  const input = document.createElement("input");
  const button = document.createElement("button");

  input.type = "password";
  input.required = true;
  input.placeholder = "Enter Password";
  input.size = 60;
  input.className = "mb-3";
  input.name = "url_password";

  button.innerHTML = "Submit";
  button.type = "submit";

  container.innerHTML = "";
  container.appendChild(input);
  container.appendChild(button);
}
