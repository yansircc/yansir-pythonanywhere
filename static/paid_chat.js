const container = document.querySelector('#response-container');
const loader = document.getElementById('loader');
const form = document.querySelector('form');

document.addEventListener('DOMContentLoaded', () => {
  form.addEventListener('submit', (event) => {
    const userInput = document.querySelector('input[type="text"]').value;
    event.preventDefault();
    container.style.display = 'block';
    loader.style.display = 'block';
    container.innerHTML += `<div><span>${userInput}</span></div>`;
    fetch('/paid-chat', {
      method: 'POST',
      body: JSON.stringify({ user_input: userInput }),
      headers: { 'Content-Type': 'application/json' }
    })
      .then((response) => response.json())
      .then((data) => {
        loader.style.display = 'none';
        const golemResponse = `<div><span class="highlight">${data.response}</span></div>`;
        container.innerHTML += golemResponse;
      });
  });
});