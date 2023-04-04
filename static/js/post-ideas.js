import { ChatUI } from './chat_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI('post_ideas', ['#keyword', '#process'], 'response-container', 'loader', 'form', true, false, true);
});