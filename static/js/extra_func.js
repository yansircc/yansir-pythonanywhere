export const getCookie = (name) => {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(`${name}=`)) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

export const addBtns = (id, classNames, textContent, parentId) => {
    let container = document.querySelector('#'+parentId);
    let btns = document.querySelector('.btns');
    if (!btns) {
      btns = document.createElement('div');
      btns.classList.add('btns');
      if (container) {
        container.appendChild(btns);
      } else {
        document.body.appendChild(btns);
      }
    }
    let btn = document.createElement('button');
    btn.id = id;
    btn.classList.add(...classNames);
    btn.textContent = textContent;
    btns.appendChild(btn);
  }
  
  export const addSseContainer = (classNames, isHighlight=true) => {
    const resultsContainer = document.getElementById('response-container');
    const golemDiv = document.createElement('div');
    golemDiv.classList.add(...classNames);
    resultsContainer.appendChild(golemDiv);
    const span = document.createElement('span');
    if (isHighlight) {
        span.classList.add('highlight');
    }
    golemDiv.appendChild(span);
  }