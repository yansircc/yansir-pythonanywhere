export class ChatUI {
    constructor(userInput='user_input', containerId = 'container', loaderId = 'loader', formId = 'form', isPrintUserInput = false, isHighlightOutput = false) {
        this.userInput = document.querySelector(`#${userInput}`);
        this.container = document.querySelector(`#${containerId}`);
        this.loader = document.querySelector(`#${loaderId}`);
        this.form = document.querySelector(`#${formId}`);
        this.isPrintUserInput = isPrintUserInput;
        this.isHighlightOutput = isHighlightOutput;
        this.init();
    }

    init = () => {
        this.form.addEventListener('submit', this.handleSubmit);
    }

    handleSubmit = (event) => {
        event.preventDefault();
        this.inputValue = this.userInput.value;
        this.container.style.display = 'block';
        this.loader.style.display = 'block';

        if (this.isPrintUserInput) {
            this.container.innerHTML += `<div><span class="user_input">${this.inputValue}</span></div>`;
        }

        const pre = document.createElement('pre');
        const span = document.createElement('span');

        if (this.isHighlightOutput) {
            span.className = 'highlight';
        }

        pre.appendChild(span);
        this.container.appendChild(pre);

        const sessionId = this.getCookie('user_id');
        const source = new EventSource(`/paid_chat?user_input=${encodeURIComponent(this.inputValue)}&session_id=${sessionId}`);

        source.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.response) {
                const golemResponse = data.response;
                span.innerHTML += golemResponse;
            } else if (data.done) {
                source.close();
            }
            this.loader.style.display = 'none';
            this.userInput.value = '';
        };

        source.onerror = (event) => {
            console.error("EventSource failed:", event);
        };
    }

    getCookie = (name) => {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(`${name}=`)) {
                return cookie.substring(name.length + 1);
            }
        }
        return null;
    }
}
