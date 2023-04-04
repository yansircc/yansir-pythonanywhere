import { ChatUI } from './chat_ui.js';

const _container = document.getElementById('response-container');
const _form = document.getElementById('form');
const refillBtn = document.getElementById('refill');

_form.addEventListener('submit', (event) => {
    const formData = {};
    const formElements = event.target.elements;
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        if (element.name) {
            formData[element.name] = element.value;
        }
    }
    localStorage.setItem('formData', JSON.stringify(formData));
    _form.style.display = 'none';
});

refillBtn.addEventListener('click', function () {
    const savedData = localStorage.getItem('formData');
    if (savedData) {
        const formData = JSON.parse(savedData);
        const formElements = form.elements;
        for (let i = 0; i < formElements.length; i++) {
            const element = formElements[i];
            if (element.name && formData[element.name]) {
                element.value = formData[element.name];
            }
        }
        _container.style.display = 'none';
        _form.style.display = 'block';
    }
});

const businessChatUI = new ChatUI('business_golem', ['.user_input'], 'response-container', 'loader', 'form', true, false, true, () => {
    const highlightSpan = document.querySelector('.highlight');
    const appendText = "Based on the above information execute my command: [PROMPT]. Note that you always have to write copy for my typical client, from his point of interest, and add value.";
    if (highlightSpan) {
        highlightSpan.innerText += '\n\n' + appendText;
    }
});