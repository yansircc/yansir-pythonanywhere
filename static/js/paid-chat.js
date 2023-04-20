import { ChatClient } from './chat_client.js';
import { addBtn, addSseContainer } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const userInput = document.getElementById('user_input');

const chatRoundsContainer = document.createElement('div');
chatRoundsContainer.id = 'chat-rounds';
resultsContainer.appendChild(chatRoundsContainer);

//把对话保存到localStorage
const saveTranscript = (input, response) => {
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
    const chatRound = {};
    chatRound[input] = response;
    chatHistory.push(chatRound);
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
};

//把对话添加到页面
const appendTranscript = (input, response, index, highlightCallback) => {
    const countChatRoundDiv = document.createElement('div');
    countChatRoundDiv.id = `chat-round-${index}`;
    countChatRoundDiv.classList.add('chat-round');

    const inputDiv = document.createElement('div');
    inputDiv.classList.add('user-input');
    inputDiv.innerHTML = `${input}`;
    countChatRoundDiv.appendChild(inputDiv);

    const responseDiv = document.createElement('div');
    responseDiv.classList.add('golem-response');
    responseDiv.innerHTML = `${marked.parse(response)}`;
    responseDiv.style.whiteSpace = 'normal';
    highlightCallback && highlightCallback(responseDiv);

    countChatRoundDiv.appendChild(responseDiv);
    chatRoundsContainer.appendChild(countChatRoundDiv);
};

//创建临时div，用于显示新的SSE对话
const createTempDiv = () => {
    const tempDiv = document.createElement('div');
    tempDiv.id = 'temp-div';
    const inputDiv = document.createElement('div');
    inputDiv.classList.add('user-input');
    const userInput = document.getElementById('user_input').value;
    inputDiv.innerHTML = `<span>${userInput}</span>`;
    tempDiv.appendChild(inputDiv);
    chatRoundsContainer.appendChild(tempDiv);
    addSseContainer(['golem-response'], false, 'temp-div');
};

//添加功能按钮
const addBtns = () => {
    addBtn('clear-transcript-history', ['btn', 'btn-primary'], '清空对话', 'response-container', () => {
        localStorage.removeItem('chatHistory');
        const allChatRoundDiv = document.querySelectorAll('[id*="chat-round-"]');
        for (let i = 0; i < allChatRoundDiv.length; i++) {
            allChatRoundDiv[i].remove();
        }
        resultsContainer.style.display = 'none';
        alert('历史记录已清空');
    });
    //addBtn('convert-to-anki', ['btn', 'btn-primary'], '转为Anki', 'response-container', () => {});
};

//展示历史对话
const showChatHistory = () => {
    const chatHistory = localStorage.getItem('chatHistory');
    if (!chatHistory) {
        return;
    }
    try {
        JSON.parse(chatHistory);
    }
    catch (e) {
        localStorage.removeItem('chatHistory');
        alert('历史记录已损坏，已清空');
        resultsContainer.style.display = 'none';
        return;
    }
    const chatHistoryArray = JSON.parse(chatHistory);
    for (let i = 0; i < chatHistoryArray.length; i++) {
        const key = Object.keys(chatHistoryArray[i])[0];
        const value = chatHistoryArray[i][key];
        appendTranscript(key, value, i);
    }
};

//检查页面上是否有对话记录
const checkTranscript = () => {
    const allChatRoundDiv = document.querySelectorAll('[id*="chat-round-"]');
    if (allChatRoundDiv.length === 0) {
        return false;
    }
    return true;
};

const onSubmit = () => {
    createTempDiv();
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    userInput.value = '';
    userInput.focus();
}

const onHandleFormData = (formData) => {
    const chatHistory = localStorage.getItem('chatHistory');
    chatHistory && formData.append('chat_history', chatHistory);
    return formData;
}

const onMessage = (response) => {
    const tempDiv = document.getElementById('temp-div');
    const golemResponseSpan = tempDiv.querySelector('.golem-response');
    golemResponseSpan.innerHTML += response;
}

const onDone = () => {
    loader.style.display = 'none';
    //移除临时div，并把对话记录添加到页面
    const tempDiv = document.getElementById('temp-div');
    const userInput = tempDiv.querySelector('.user-input').textContent;
    const golemResponse = tempDiv.querySelector('.golem-response').textContent;
    tempDiv.remove();
    saveTranscript(userInput, golemResponse);
    appendTranscript(userInput, golemResponse, chatRoundsContainer.childElementCount);
}

const onExceed = () => {
    const tempDiv = document.getElementById('temp-div');
    tempDiv.remove();
    alert('文本量超过限制，请重新输入。');
    loader.style.display = 'none';
    resultsContainer.style.display = checkTranscript() ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const chatClient = new ChatClient(
        'sse/paid_chat',
        {
            onSubmitCallback: onSubmit,
            handleFormDataCallback: onHandleFormData,
            onMessageCallback: onMessage,
            onDoneCallback: onDone,
            onExceedCallback: onExceed,
        }
    );

    // Load marked.js
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(script);

    script.onload = () => {
        showChatHistory();
        addBtns();
        resultsContainer.style.display = checkTranscript() ? 'block' : 'none';
        userInput.focus();
    };
});
