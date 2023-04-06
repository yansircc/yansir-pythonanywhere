import { ChatClient } from './chat_client.js';
import { addBtns, addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const form = document.getElementById('form');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    form.style.display = 'none';
    //为sse消息创建容器
    addSseContainer(['golem-response'])
}

//把表单数据存储到本地
function storeFormData(formData) {
    const formDataObject = {};
    formData.forEach((value, key) => {
        formDataObject[key] = value;
    });
    localStorage.setItem('formData', JSON.stringify(formDataObject));
}

function onMessage(response) {
    const highlightSpan = document.querySelector('span.highlight');
    highlightSpan.innerHTML += response;
}

function onDone() {
    loader.style.display = 'none';
    const highlightSpan = document.querySelector('span.highlight');
    const appendText = "\n\nBased on the above information execute my command: [PROMPT]. Note that you always have to write copy for my typical client, from his point of interest, and add value.";
    highlightSpan.innerText += appendText;
    localStorage.setItem('businessPrompt', highlightSpan.innerText);
}

document.addEventListener('DOMContentLoaded', () => {
    if(localStorage.getItem('businessPrompt')){
        resultsContainer.style.display = 'block';
        form.style.display = 'none';
        addSseContainer(['golem-response']);
        const highlightSpan = document.querySelector('span.highlight');
        highlightSpan.innerHTML = localStorage.getItem('businessPrompt');
    }
    addBtns('refill', ['btn', 'btn-primary'], '重新填表', 'response-container');

    const chatClient = new ChatClient(
        'business_golem',
        {
            onSubmitCallback: onSubmit,
            handleFormDataCallback: storeFormData,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
    //从本地存储中获取表单数据并填充到表单中
    const refillBtn = document.getElementById('refill');
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
            resultsContainer.style.display = 'none';
            form.style.display = 'block';
        }
    });
});