import { ChatClient } from './chat_client.js';
import { addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    //为sse消息创建容器
    addSseContainer(['golem-response']);
    const highlightSpan = document.querySelector('span.highlight');
    highlightSpan.textContent = '';
}

function onMessage(response) {
    const highlightSpan = document.querySelector('span.highlight');
    highlightSpan.textContent += response;
}

function onDone() {
    loader.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const chatClient = new ChatClient(
        'post_ideas',
        {
            onSubmitCallback: onSubmit,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});