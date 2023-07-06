import { addSseContainer } from './extra_func.js';
class ChatClient {
    constructor(
        routeName='',
        {
            onSubmitCallback = null,
            handleFormDataCallback = null,
            onMessageCallback = null,
            onErrorCallback = null,
            onDoneCallback = null,
            onExceedCallback = null
        }
    ) {
        this.form = document.getElementById('form');
        this.routeName = routeName;
        this.eventSource = null;

        // Add callback functions
        this.onSubmitCallback = onSubmitCallback;
        this.handleFormDataCallback = handleFormDataCallback;
        this.onMessageCallback = onMessageCallback;
        this.onErrorCallback = onErrorCallback;
        this.onDoneCallback = onDoneCallback;
        this.onExceedCallback = onExceedCallback;

        this.form.addEventListener("submit", this.onSubmit.bind(this));
        this.current_query = "";
    }

    onSubmit(event) {
        event.preventDefault();
        const textarea = document.getElementById('query');
        this.queries = textarea.value.split('\n');
        // delete all empty lines
        this.queries = this.queries.filter(query => query.trim() !== '');
        this.submitNextquery();
    }

    submitNextquery() {
        if (!this.queries.length) {
            return;
        }

        const query = this.queries.shift();
        this.current_query = query;
        const formData = new FormData();
        formData.append('query', query);

        this.handleFormDataCallback && this.handleFormDataCallback(formData);
        const headers = new Headers();
        headers.append("Content-Type", "application/x-www-form-urlencoded");

        this.onSubmitCallback && this.onSubmitCallback();

        fetch("/" + this.routeName, {
            method: "POST",
            headers: headers,
            body: new URLSearchParams(formData),
        })
            .then((response) => {
                if (response.ok) {
                    return response;
                } else {
                    throw new Error("Error sending the POST request");
                }
            })
            .then((response) => {
                this.eventSource = new EventSource("/" + this.routeName);
                this.eventSource.onmessage = this.onMessage.bind(this);
                this.eventSource.onerror = this.onError.bind(this);
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }

    onMessage(event) {
        const eventData = JSON.parse(event.data);

        if (eventData.response) {
            this.onMessageCallback && this.onMessageCallback(eventData.response);
        } else if (eventData.query_done) {
            this.onqueryDoneCallback && this.onqueryDoneCallback(event);
        } else if (eventData.done) {
            this.eventSource.close();
            this.onDoneCallback && this.onDoneCallback(event);
            // Submit the next query after receiving a response
            this.submitNextquery();
        } else if (eventData.exceed) {
            this.eventSource.close();
            this.onExceedCallback && this.onExceedCallback(event);
        }
    }

    onError(error) {
        console.error("Error receiving SSE:", error);
        console.error("Status:", error.target.status);
        this.eventSource.close();
        // Call the onError callback function
        this.onErrorCallback && this.onErrorCallback(error);
    }
}


const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    //为sse消息创建容器
    addSseContainer(['golem-response'], false, 'response-container');
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += "**Query:** " + this.current_query + "\n";
}

function sendBusinessPrompt(formData) {
    const businessPrompt = localStorage.getItem('businessPrompt');
    formData.append('businessPrompt', businessPrompt);
}

function onMessage(response) {
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += response;
}

function onDone() {
    loader.style.display = 'none';
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += "\n\n";
    //resultSpan.innerHTML = marked.parse(resultSpan.textContent);
    //resultSpan.style.whiteSpace = 'normal';
}

document.addEventListener('DOMContentLoaded', () => {
    // Load marked.js
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(script);

    const chatClient = new ChatClient(
        'sse/serp_titles',
        {
            onSubmitCallback: onSubmit,
            handleFormDataCallback: sendBusinessPrompt,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});