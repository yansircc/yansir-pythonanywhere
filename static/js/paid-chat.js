import { ChatUI } from './chat_ui.js';
import { getCookie } from './get_cookie.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI('paid_chat', ['#user_input'], 'response-container', 'loader', 'form', false, true, true);
});

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