import { ChatClient } from './chat_client.js';
import { addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    //为sse消息创建容器
    addSseContainer(['golem-response'], false, 'response-container');
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent = '';
}

function sendBusinessPrompt(formData) {
    const businessPrompt = localStorage.getItem('businessPrompt');
    formData.append('businessPrompt', businessPrompt);
}

function onMessage(response) {
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += response;
}

function onDone() {
    loader.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const chatClient = new ChatClient(
        'sse/serp_titles',
        {
            onSubmitCallback: onSubmit,
            handleFormDataCallback: sendBusinessPrompt,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});