window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');
    const sysPromptLabel = document.querySelector('label[for="sys_prompt"]');
    const hint = document.createElement('div');
    hint.innerHTML = '不知道怎么写就复制我的命令: If the inquiry has no relationship with B2B procurement, you will give it a rating of 0. If it is relevant, then you will rate it based on the quality of the inquiry.';
    hint.classList.add('hint');
    sysPromptLabel.appendChild(hint);

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(form);

        loader.style.display = 'block';
        fetch('/generate_json', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);

                // Create an anchor element to trigger the download
                const downloadLink = document.createElement('a');
                downloadLink.href = url;
                downloadLink.download = 'my_gtm.json';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(url);
                loader.style.display = 'none';
            })
            .catch(error => console.error(error));
        return false;
    });
});
