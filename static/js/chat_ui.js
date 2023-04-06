import { getCookie } from './extra_func.js'

export class ChatUI {
    constructor(endpoint, userInputSelectors, containerId, loaderId, formId, isClearTranscript, isPrintUserInput, isHighlightOutput, onStreamEnd=()=>{}, appendUrl='') {
        this.endpoint = endpoint;
        this.userInputSelectors = userInputSelectors;
        this.container = document.querySelector(`#${containerId}`);
        this.loader = document.querySelector(`#${loaderId}`);
        this.form = document.querySelector(`#${formId}`);
        this.isClearTranscript = isClearTranscript;
        this.isPrintUserInput = isPrintUserInput;
        this.isHighlightOutput = isHighlightOutput;
        this.onStreamEnd = onStreamEnd;
        this.appendUrl = appendUrl;
        this.init();
    }

    init = () => {
        this.form.addEventListener('submit', this.handleSubmit);
    }

    handleSubmit = (event) => {
        event.preventDefault();
    
        const userInputData = this.userInputSelectors.map((selector) => {
            let userInput;
            if (selector.startsWith('#')) {
                const inputElement = document.querySelector(selector);
                userInput = inputElement.value;
            } else if (selector.startsWith('.')) {
                const inputElements = Array.from(document.querySelectorAll(selector));
    
                const data = {};
                inputElements.forEach(input => {
                    data[input.name] = input.value;
                });
    
                userInput = Object.keys(data)
                    .map((key) => key + '=' + data[key])
                    .join('&');
            }
            return userInput;
        });
    
        this.submitData(userInputData);
    }
    


    submitData(userInputs) {
        this.container.style.display = 'block';
        this.loader.style.display = 'block';

        if (this.isClearTranscript) {
            const userInputElements = document.querySelectorAll('.user_request_strings');
            const preElements = document.querySelectorAll('pre');
            userInputElements.forEach(element => element.remove());
            preElements.forEach(element => element.remove());
        }

        // Join userInputs array into a single string separated by a delimiter (e.g., |||)
        const combinedUserInputs = userInputs.join('|||');

        if (this.isPrintUserInput) {
            userInputs.forEach(userInput => {
                const span = document.createElement('span');
                span.className = 'user_request_strings';
                span.textContent = decodeURIComponent(userInput);
                this.container.appendChild(span);
            });
        }

        const pre = document.createElement('pre');
        const span = document.createElement('span');

        if (this.isHighlightOutput) {
            span.className = 'highlight';
        }

        pre.appendChild(span);
        this.container.appendChild(pre);

        const sessionId = getCookie('user_id');
        const source = new EventSource(`/${this.endpoint}?user_input=${encodeURIComponent(combinedUserInputs)}&session_id=${sessionId}${this.appendUrl}`);

        source.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.response) {
                const golemResponse = data.response;
                span.textContent += golemResponse;
            } else if (data.done) {
                source.close();
                this.loader.style.display = 'none';
                if (this.onStreamEnd) {
                    this.onStreamEnd();
                }
            }

            this.userInputSelectors.forEach(selector => {
                if (selector.startsWith('#')) {
                    const inputElement = document.querySelector(selector);
                    inputElement.value = '';
                } else if (selector.startsWith('.')) {
                    const inputElements = Array.from(document.querySelectorAll(selector));
                    inputElements.forEach(input => {
                        input.value = '';
                    });
                }
            });
        };

        source.onerror = (event) => {
            console.error("EventSource failed:", event);
        };
    }
}

