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

export const addBtn = (id, classNames, textContent, parentId, onClick=null) => {
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
    btn.onclick = onClick;
    btns.appendChild(btn);
  }
  
  export const addSseContainer = (classNames, isHighlight=true, parentContainerId='response-container') => {
    const parentContainer = document.getElementById(parentContainerId);
    const golemDiv = document.createElement('div');
    const span = document.createElement('span');

    golemDiv.classList.add(...classNames);
    isHighlight && span.classList.add('highlight');

    golemDiv.appendChild(span);
    parentContainer.appendChild(golemDiv);
  }