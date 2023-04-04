import { ChatUI } from './chat_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI('builder_golem', ['#user_input'], 'response-container', 'loader', 'form', true, false, true);
});
