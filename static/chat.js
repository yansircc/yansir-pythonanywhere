const chatContainer = document.querySelector('#response-container');
const loader = document.getElementById('loader');
const submitButton = document.querySelector('#query-form input[type="submit"]');
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

function appendMessage(role, content) {
  const messageElement = document.createElement('div');
  messageElement.classList.add(role);
  messageElement.textContent = content;
  chatContainer.appendChild(messageElement);
  chatHistory.push({ role, content });
  saveChatHistory();

  if (role === 'user') {
    sendChatHistory();
  }
}

function assistantResponse(response) {
  appendMessage('assistant', response);
}

function saveChatHistory() {
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

function loadChatHistory() {
  chatHistory.forEach(({ role, content }) => {
    appendMessage(role, content);
  });
}

function sendChatHistory() {
  fetch('/chatgpt', {
    method: 'POST',
    body: JSON.stringify(chatHistory),
    headers: { 'Content-Type': 'application/json' }
  })
  .then(response => response.json())
  .then(data => assistantResponse(data.response))
  .then(() => {
    loader.style.display = 'none';
    let assistantElements = document.querySelectorAll('.assistant');
    assistantElements.forEach(element => {
      let textContent = element.textContent;
      let highlightedText = '<span class="highlight">' + textContent + '</span>';
      element.innerHTML = highlightedText;
    });
  })
  .catch(error => console.error(error));
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const userInput = document.querySelector('input[type="text"]');

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    chatContainer.style.display = 'block';
    loader.style.display = 'block';
    const userMessage = userInput.value;
    appendMessage('user', userMessage);
    userInput.value = '';
  });

  loadChatHistory();
  window.addEventListener('beforeunload', () => {
    localStorage.removeItem('chatHistory');
  });
});
