const form = document.getElementById('business-form');
const loader = document.getElementById('loader');
const container = document.getElementById('response-container');

form.addEventListener('submit', function (event) {
    event.preventDefault();
    localStorage.clear();

    // get all the input elements in the form
    let inputs = document.querySelectorAll('form input');
    // loop through the input elements and add the prefix to the name attribute
    inputs.forEach((input, index) => {
        let prefix = 'a' + (index + 1).toString().padStart(2, '0') + '-';
        input.name = prefix + input.name;
    });

    const data = new FormData(form);
    container.innerHTML = "正在提交...";
    fetch('/submit-business-form', {
        method: 'POST',
        body: data
    }).then(function (response) {
        return response.json();
    }).then(function (data) {
        container.innerHTML = ""; // Clear the container
        container.style.display = "block"; // Make the container visible
        form.style.display = "none"; // Hide the form
        // Loop through the form data and create HTML elements to display each field and its value
        for (let [key, value] of Object.entries(data)) {
            // Skip any keys that start with an underscore
            if (key.startsWith("_")) {
                continue;
            }
            // Store the form data in localStorage
            localStorage.setItem(key, value);

            const field = document.createElement('div');
            const label = document.createElement('span');
            const fieldValue = document.createElement('span');

            label.textContent = key.substring(4) + ": ";
            fieldValue.textContent = value + ";";

            field.appendChild(label);
            field.appendChild(fieldValue);
            container.appendChild(field);
        }
        createButtons();
        copyButton = document.getElementById('copy-button');
        copyButton.style.display = "none";
        let containerHtml = container.innerHTML;
        containerHtml = containerHtml.replace(buttons.outerHTML, '');
        localStorage.setItem("containerHtml", containerHtml);
    });
});

window.addEventListener('load', function () {
    let dataTrained = localStorage.getItem("dataTrained");
    if (dataTrained) {
        container.innerHTML = "<span class='highlight'>" + dataTrained + "</span>";
        createButtons();
        document.getElementById('train-button').style.display = "none";
    } else if (localStorage.length > 0) {
        form.style.display = "none";
        container.style.display = "block";
        container.innerHTML = localStorage.getItem("containerHtml");
        createButtons();
        copyButton = document.getElementById('copy-button');
        copyButton.style.display = "none";
    } else {
        form.style.display = "block";
        container.style.display = "none";
    }
});

const createButtons = function () {
    container.style.display = "block";
    form.style.display = "none";

    const btnContainer = document.createElement('div');
    btnContainer.setAttribute('id', 'buttons');
    container.appendChild(btnContainer);

    // Create a "Resubmit" button and append it to the response container
    const resubmitButton = document.createElement('button');
    resubmitButton.setAttribute('id', 'resubmit-button');
    resubmitButton.classList.add('btn');
    resubmitButton.textContent = '重填';
    btnContainer.appendChild(resubmitButton);
    resubmitButton.addEventListener('click', function () {

        // Loop through the form's input elements and set their values to the corresponding values from local storage
        let formElements = form.elements;
        for (let i = 0; i < formElements.length; i++) {
            let elementName = formElements[i].name;
            for (let j = 0; j < localStorage.length; j++) {
                let key = localStorage.key(j);
                if (key.substring(4) === elementName) {
                    formElements[i].value = localStorage.getItem(key);
                    break;
                }
            }
        }

        localStorage.removeItem('dataTrained');
        container.style.display = 'none'; // Hide the response container
        form.style.display = ''; // Show the form
    });

    const trainButton = document.createElement('button');
    trainButton.setAttribute('id', 'train-button');
    trainButton.classList.add('btn');
    trainButton.textContent = '预训练';
    btnContainer.appendChild(trainButton);
    trainButton.addEventListener('click', function (event) {
        event.preventDefault();
        const prompt = container.textContent.trim(); // Get the text from the response container
        loader.style.display = "block";
        fetch('/chatgpt-training', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `prompt=${encodeURIComponent(prompt)}`
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            loader.style.display = "none";
            container.innerHTML = "<span class='highlight'>" + data.response + "</span>";
            localStorage.setItem("dataTrained", data.response);
            localStorage.setItem("summaried_trained_data", data.summaried_trained_data);
            createButtons();
            document.getElementById('train-button').style.display = "none";
        });
    });

    const copyButton = document.createElement('button');
    copyButton.setAttribute('id', 'copy-button');
    copyButton.classList.add('btn');
    copyButton.textContent = '复制';
    copyButton.addEventListener('click', function (event) {
        const data = document.querySelector('#response-container .highlight').innerText;
        copyToClipboard(data);
        event.preventDefault();
    });
    btnContainer.appendChild(copyButton);

    const closeButton = document.createElement("span");
    closeButton.innerHTML = "&times;";
    closeButton.setAttribute('id', 'close-button');
    closeButton.addEventListener("click", function () {
        localStorage.clear();
    });
    container.appendChild(closeButton);
}

function copyToClipboard(data) {
    const tempElement = document.createElement('textarea');
    tempElement.value = data;
    tempElement.setAttribute('readonly', '');
    tempElement.style.position = 'absolute';
    tempElement.style.left = '-9999px';
    document.body.appendChild(tempElement);
    tempElement.select();
    document.execCommand('copy');
    document.body.removeChild(tempElement);

    // Change copy button text and color
    const copyButton = document.getElementById('copy-button');
    copyButton.innerText = "已复制";
    copyButton.style.backgroundColor = "#3CB371";
    copyButton.style.color = "white";
    copyButton.disabled = true;

    // Reset copy button after 2 seconds
    setTimeout(function () {
        copyButton.innerText = "复制";
        copyButton.style.backgroundColor = "";
        copyButton.style.color = "";
        copyButton.disabled = false;
    }, 2000);
}