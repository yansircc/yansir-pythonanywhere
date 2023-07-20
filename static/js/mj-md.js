document.getElementById('form').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(this);

    fetch('/fio_imgs', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())  // convert the raw response into JSON
    .then(data => console.log(data))  // log the JSON data to the console
    .catch(error => console.error('Error:', error));
});
