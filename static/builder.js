document.getElementById('query-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const query = document.getElementById('query-input').value;
    const loader = document.getElementById('loader');
    const container = document.getElementById('response-container');
    loader.style.display = "block";
    container.style.display = "none";
    container.innerHTML = "";
    fetch('/builder-submit', {
        method: 'POST',
        body: new FormData(event.target)
    }).then(function (response) {
        return response.json();
    }).then(function (data) {
        loader.style.display = "none";
        if (/```([^`]+)```/g.test(data.response)) {
            container.innerHTML = data.response.replace(/```([^`]+)```/g, "<span class='highlight'>$1</span>");
        } else {
            container.innerHTML = data.response;
        }
        container.style.display = "block";

        // Add "Copy this code" button
        const copyButton = document.createElement('button');
        copyButton.innerText = "复制";
        copyButton.classList.add('copy-button');
        copyButton.addEventListener('click', function (event) {
            const code = document.querySelector('#response-container .highlight').innerText;
            copyToClipboard(code);
            event.preventDefault();
        });
        container.appendChild(copyButton);
    });
});

function copyToClipboard(code) {
    const tempElement = document.createElement('textarea');
    tempElement.value = code;
    tempElement.setAttribute('readonly', '');
    tempElement.style.position = 'absolute';
    tempElement.style.left = '-9999px';
    document.body.appendChild(tempElement);
    tempElement.select();
    document.execCommand('copy');
    document.body.removeChild(tempElement);

    // Change copy button text and color
    const copyButton = document.querySelector('.copy-button');
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