import { ChatClient } from './chat_client.js';
import { addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const form = document.getElementById('form');
const userInput = document.getElementById('user_input');
const title = document.querySelector('.title-container');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    form.style.display = 'none';
    title.style.display = 'none';
    userInput.value = '';
    //为sse消息创建容器
    addSseContainer(['golem-response'], false)
    const golemResponseSpan = document.querySelector('.golem-response span');
    golemResponseSpan.textContent = '';
}

function addCustomFormData(formData) {
    formData.append('post_type', 'response_post')
    return formData;
}

function onMessage(response) {
    const golemResponseSpan = document.querySelector('.golem-response span');
    golemResponseSpan.textContent += response;
}

function onDone() {
    loader.style.display = 'none';
    const golemResponseSpan = document.querySelector('.golem-response span');
    golemResponseSpan.innerHTML = marked.parse(golemResponseSpan.textContent);
}

document.addEventListener('DOMContentLoaded', () => {
    // Load marked.js
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(script);

    const chatClient = new ChatClient(
        'generate_post',
        {
            onSubmitCallback: onSubmit,
            handleFormDataCallback: addCustomFormData,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});