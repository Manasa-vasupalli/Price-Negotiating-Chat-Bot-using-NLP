
const chatLog = document.querySelector('.chatlog');
const inputBox = document.querySelector('#messageInput');
const sendButton = document.querySelector('#sendButton');

function addMessage(message, isReceived) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', isReceived ? 'received' : 'sent');
  messageElement.innerHTML = `<p>${message}</p>`;
  chatLog.appendChild(messageElement);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function sendMessage(price) {
  const message = inputBox.value;
  addMessage(message, false);
  inputBox.value = '';

  fetch('/get_bot_response', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      price: price
    })
  })
  .then(response => {
    console.log(response);
    return response.json();
  })
  .then(data => {
    const botResponse = data.bot_response;
    addMessage(botResponse, true);
  })
  .catch(error => {
    console.error(error);
  });
}
sendButton.addEventListener('click', function(event) {
  event.preventDefault(); 
  const price = document.querySelector('input[name="price"]').value; 
  sendMessage(price);
});

