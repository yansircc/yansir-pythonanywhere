import { ChatUI } from './chat_ui.js';

const _title = document.querySelector('#page-title');
const _form = document.querySelector('#form');

document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI('generate_post', ['#user_input'], 'response-container', 'loader', 'form', true, false, false, () => {
        _title.style.display = 'none';
        _form.style.display = 'none';
        const postArea = document.querySelector('pre > span');
        const postContent = postArea.textContent;
        postArea.innerHTML = postContent;
    }, '&post_type=response_post');
});