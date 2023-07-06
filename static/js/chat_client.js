export class ChatClient {
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
    }

    submit() {
        this.form.dispatchEvent(new Event("submit"));
    }

    onSubmit(event) {
        event.preventDefault();

        const formData = new FormData(this.form);
        this.handleFormDataCallback && this.handleFormDataCallback(formData);
        const headers = new Headers();
        headers.append("Content-Type", "application/x-www-form-urlencoded");

        // Call the onSubmit callback function
        this.onSubmitCallback && this.onSubmitCallback(event);

        fetch("/"+this.routeName, {
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
                // Process the received SSE
                this.eventSource = new EventSource("/"+this.routeName);
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
            // Call the onMessage callback function
            this.onMessageCallback && this.onMessageCallback(eventData.response);
        } else if (eventData.keyword_done) {
            // Process a single keyword's completion
            this.onKeywordDoneCallback && this.onKeywordDoneCallback(event);
        } else if (eventData.done) {
            this.eventSource.close();
            // Call the onDone callback function
            this.onDoneCallback && this.onDoneCallback(event);
        } else if (eventData.exceed) {
            this.eventSource.close();
            // Call the onExceed callback function
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
