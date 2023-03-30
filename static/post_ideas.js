const form = document.getElementById('query-form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const container = document.getElementById('response-container');
    const loader = document.getElementById('loader');
    const keywordInput = document.getElementById('keyword');
    const processInput = document.getElementById('process');

    // 将文本框中的每一行字符串转换为数组
    const keywordArray = keywordInput.value.split('\n').map(str => str.trim());
    const processArray = processInput.value.split('\n').map(str => str.trim());

    // 获取 local storage 中的 dataTrained
    const trainedData = localStorage.getItem('dataTrained');

    // 创建包含两个数组的 JSON 对象
    const data = {
        keywords: keywordArray,
        processes: processArray,
        trained_data: trainedData
    };

    loader.style.display = 'block';

    fetch('/post-ideas', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            container.innerHTML += '<pre>' + data.response + '</pre>';
            container.style.display = 'block';
            loader.style.display = 'none';
        })
        .catch(error => console.error(error));
});