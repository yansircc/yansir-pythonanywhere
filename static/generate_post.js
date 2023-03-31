window.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('response-container');
  const loader = document.getElementById('loader');
  const form = document.getElementById('query-form');
  const title = document.getElementById('page-title');
  const buttons = document.getElementById('response-buttons');

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    trained_data = localStorage.getItem('dataTrained');
    if(localStorage.getItem('dataTrained')) {
      const userInput = document.querySelector('input[type="text"]').value;
      loader.style.display = 'block';
      fetch('/generate_post', {
          method: 'POST',
          body: JSON.stringify({
            'user_input': userInput,
            'trained_data': localStorage.getItem('dataTrained'),
            'post_type': 'response_post'
          }),
          headers: { 'Content-Type': 'application/json' }
      })
      .then(response => response.json())
      .then(data => {
          container.innerHTML += data.response;
          container.style.display = 'block';
          loader.style.display = 'none';
          title.style.display = 'none';
          form.style.display = 'none';
      })
      .then(() => {
        const publishButton = document.getElementById('publish-button');
        const resetButton = document.getElementById('reset-button');
        resetButton.addEventListener('click', (event) => {
          title.style.display = 'block';
          form.style.display = 'block';
          container.style.display = 'none';
          container.innerHTML = '';
          container.appendChild(buttons);
        });
      })
      .catch(error => console.error(error));
    }
    else {
      alert("没查到本地预训练的cookie, 先完成‘生意’的预训练, 还有, 不要用无痕浏览器")
    }
    return false;
  });
});
