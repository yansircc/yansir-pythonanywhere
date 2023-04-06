import { ChatClient } from './chat_client.js';
import { getCookie, addBtns, addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const userInput = document.getElementById('user_input');

function onFormData(formData) {
    const formElements = Object.keys(formData);
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        if (element.name && formData[element.name]) {
            element.value = formData[element.name];
        }
    }
}

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    const inputDiv = document.createElement('span');
    inputDiv.classList.add('user-input');
    inputDiv.textContent = userInput.value;
    resultsContainer.appendChild(inputDiv);
    userInput.value = '';
    //为sse消息创建容器
    addSseContainer(['golem-response'])
}

function onMessage(response) {
    const elements = document.querySelectorAll('.golem-response');
    const highlightSpan = elements[elements.length - 1].querySelector('span');
    highlightSpan.innerHTML += response;
}

function onDone() {
    loader.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    addBtns('clear-transcript-history', ['btn', 'btn-primary'], '清空历史记录', 'response-container');

    const chatClient = new ChatClient(
        'sse/paid_chat',
        {
            handleFormDataCallback: onFormData,
            onSubmitCallback: onSubmit,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
    const clearTranscriptBtn = document.querySelector('#clear-transcript-history');
    clearTranscriptBtn.addEventListener('click', () => {
        //发起Get请求，清空历史记录
        const sessionId = getCookie('user_id');
        const tableName = 'conversation';
        const columnName = 'transcript_history';
        fetch(`/clear_transcript_history?session_id=${sessionId}&table_name=${tableName}&column_name=${columnName}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.status === 200) {
                    alert('清空成功，刷新页面后生效。')
                    return response.json();
                } else {
                    throw new Error('Something went wrong on api server!');
                }
            })
            .catch(error => {
                console.error(error);
            });
    });
});