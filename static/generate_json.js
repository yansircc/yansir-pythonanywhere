window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('query-form');

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const ga4_id = document.getElementById('ga4_id').value;
        const ga4_api_key = document.getElementById('ga4_api_key').value;
        const gads_id = document.getElementById('gads_id').value;
        const gads_label = document.getElementById('gads_label').value;
        const openai_api_key = document.getElementById('openai_api_key').value;
        const sys_prompt = document.getElementById('sys_prompt').value;

        loader.style.display = 'block';
        fetch('/generate_json', {
            method: 'POST',
            body: JSON.stringify({
                'ga4_id': ga4_id,
                'ga4_api_key': ga4_api_key,
                'gads_id': gads_id,
                'gads_label': gads_label,
                'openai_api_key': openai_api_key,
                'sys_prompt': sys_prompt
            }),
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                const jsonData = JSON.stringify(data);
                const blob = new Blob([jsonData], { type: 'application/json' });
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
