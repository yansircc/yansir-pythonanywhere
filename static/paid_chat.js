const container = document.querySelector('#response-container');
const loader = document.getElementById('loader');
const form = document.querySelector('form');

document.addEventListener('DOMContentLoaded', () => {
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const userInput = document.querySelector('input[type="text"]').value;
        const chatUI = new ChatUI(userInput, 'response-container', 'loader', 'form', true, true);
    });
});
