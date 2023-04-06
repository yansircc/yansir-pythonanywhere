const eventSource = new EventSource('/paid_chat');
const container = document.querySelector('#container');

eventSource.onmessage = function(event) {
  const data = event.data;
  const newElement = document.createElement('div');
  newElement.innerText = data;
  container.appendChild(newElement); // Append the new element to the container element
};

window.addEventListener('beforeunload', function() {
  eventSource.close(); // Close the SSE connection when the page is about to unload
});
