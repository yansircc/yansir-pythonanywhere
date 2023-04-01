import { ChatUI } from './chat_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI('user_input', 'response-container', 'loader', 'form', true, true);
});
