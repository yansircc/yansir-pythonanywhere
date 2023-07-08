import { addSseContainer, parseData, objectToCsv, downloadCsv } from './extra_func.js';

class ChatClient {
    constructor(
        routeName='',
        {
            onSubmitCallback = null,
            handleFormDataCallback = null,
            onMessageCallback = null,
            onDoneCallback = null
        }
    ) {
        this.form = document.getElementById('form');
        this.routeName = routeName;
        this.onSubmitCallback = onSubmitCallback;
        this.handleFormDataCallback = handleFormDataCallback;
        this.onMessageCallback = onMessageCallback;
        this.onDoneCallback = onDoneCallback;

        this.form.addEventListener("submit", this.onSubmit.bind(this));
        this.current_query = "";
        this.allQueriesSubmitted = false;
    }

    onSubmit(event) {
        event.preventDefault();
        const textarea = document.getElementById('query');
        this.queries = textarea.value.split('\n');
        // delete all empty lines
        this.queries = this.queries.filter(query => query.trim() !== '');
        this.submitNextquery();
        this.allQueriesSubmitted = this.queries.length === 0;
    }

    submitNextquery() {
        if (!this.queries.length) {
            this.allQueriesSubmitted = true;
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
            .then(response => response.json())  // Parse response as JSON
            .then(data => {
                // Handle the data received from the server
                this.onMessageCallback && this.onMessageCallback(data);
                this.onDoneCallback && this.onDoneCallback();
                this.submitNextquery();
                this.checkAllDone();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        
    }

    checkAllDone() {
        if (this.allQueriesSubmitted) {
            const resultSpan = document.querySelector('.golem-response span');
            const content = resultSpan.textContent;
            resultSpan.innerHTML = marked.parse(resultSpan.textContent);
            loader.style.display = 'none';
            console.log(content);
            const data = parseData(content);
            console.log(data);
            const csvData = objectToCsv(data);
            downloadCsv(csvData);
        }
    }
}



const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');

function onSubmit() {
    loader.style.display = 'block';
    resultsContainer.style.display = 'block';
    // Create output container for messages
    addSseContainer(['golem-response'], false, 'response-container');
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += "**Query:** " + this.current_query + "\n";
}

function onMessage(response) {
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += response;
}

function onDone() {
    loader.style.display = 'none';
    const resultSpan = document.querySelector('.golem-response span');
    resultSpan.textContent += "\n\n";
}

document.addEventListener('DOMContentLoaded', () => {
    // Load marked.js
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    document.head.appendChild(script);

    const chatClient = new ChatClient(
        'no_sse/serp_titles',
        {
            onSubmitCallback: onSubmit,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});
