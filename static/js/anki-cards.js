import { ChatClient } from './chat_client.js';
import { addSseContainer, addBtn } from './extra_func.js';

const resultsContainer = document.getElementById('response-container');
const loader = document.getElementById('loader');
const form = document.getElementById('form');

//检查内容是否为合法Json
const isVaildJson = (str) => {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
};

//添加提示信息
const addNotice = (id, noticeText, callback = null) => {
    const noticeElements = document.querySelectorAll('[id*="-notice"]');
    noticeElements.forEach(element => {
        element.remove();
    });
    document.getElementById('cards-list') && document.getElementById('cards-list').remove();
    const span = document.createElement('span');
    span.id = id;
    span.classList.add('highlight')
    span.innerHTML = noticeText;
    resultsContainer.appendChild(span);
    callback && callback();
};

//显示弹窗
const showPopup = (index = null) => {
    const popup = document.getElementById("popup");
    const popupForm = popup.querySelector('form');
    const closeBtn = popup.querySelector('#popup-close');
    const oldCards = localStorage.getItem('ankiCards');
    const oldCardsJson = oldCards ? JSON.parse(oldCards) : [];
    const onSubmit = (e) => {
        e.preventDefault();
        const front = popupForm.querySelector('#front').value.trim();
        const back = popupForm.querySelector('#back').value.trim();
        if (front && back) {
            const newCardsJson = { [front]: back };
            index !== null && index !== undefined ? oldCardsJson.splice(index, 1, newCardsJson) : oldCardsJson.push(newCardsJson);
            localStorage.setItem('ankiCards', JSON.stringify(oldCardsJson));
            popupForm.querySelector('#front').value = '';
            popupForm.querySelector('#back').value = '';
            closeBtn.click();
            addNotice('cards-count-notice', `共制作<b> ${JSON.parse(localStorage.getItem('ankiCards')).length} </b>张卡片，点击可编辑。`, listCards);
        } else {
            addNotice('empty-notice', '正反面都不能为空。');
        }
    };
    const onClose = () => {
        popup.classList.remove("show");
        popupForm.removeEventListener('submit', onSubmit);
    };

    popup.classList.add("show");

    if (index !== null && index !== undefined) {
        popupForm.querySelector('#front').value = Object.keys(oldCardsJson[index])[0];
        popupForm.querySelector('#back').value = Object.values(oldCardsJson[index])[0];
    }
    popupForm.addEventListener('submit', onSubmit);
    closeBtn.addEventListener('click', onClose);
};

//添加功能按钮
const addBtns = () => {
    addBtn('custom-anki-card', ['btn', 'btn-primary'], '自制', 'response-container');
    const customBtn = document.getElementById('custom-anki-card');
    customBtn.addEventListener('click', () => {
        showPopup();
    });
    addBtn('generate-apkg', ['btn', 'btn-primary'], '生成', 'response-container', () => {
        const oldCards = localStorage.getItem('ankiCards');
        if (oldCards) {
            fetchApkg(JSON.parse(oldCards));
            localStorage.removeItem('ankiCards');
            resultsContainer.innerHTML = '';
            addNotice('download-success-notice', '制卡成功，文件已下载到本地。');
        } else {
            addNotice('empty-notice', '当前没卡片，先制卡。');
        }
    });
    addBtn('fetch-chat-history', ['btn', 'btn-primary'], '读取对话', 'response-container', () => {
        const chatHistory = localStorage.getItem('chatHistory');
        if (chatHistory) {
            const userInputContainer = document.querySelector('#user_input');
            userInputContainer.value = '';
            const chatHistoryArray = JSON.parse(chatHistory);
            for (let i = 0; i < chatHistoryArray.length; i++) {
                const key = Object.keys(chatHistoryArray[i])[0];
                const value = chatHistoryArray[i][key];
                userInputContainer.value += `问${i}: ` + key + '\n' + `答${i}: ` + value + '\n\n';
            }
            resultsContainer.innerHTML = '';
            addNotice('chat-history-notice', `成功读取到${chatHistoryArray.length}条问答，检查无误后可提交。`);
        } else {
            addNotice('no-transcript-notice', '没检测到对话记录，先在“对话”页面问几个问题。');
            return;
        }
    });
    addBtn('clear-apkg', ['btn', 'btn-primary'], '清空', 'response-container', () => {
        const result = confirm('确定要清空所有卡片吗？');
        if (result) {
            localStorage.removeItem('ankiCards');
            resultsContainer.innerHTML = '';
            addNotice('clear-succ-notice', '清空成功。');
        }
    });
};

//从服务器获取apkg文件
const fetchApkg = async (data) => {
    const response = await fetch('/generate-apkg', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'anki_cards.apkg';
        document.body.appendChild(a);
        a.click();
        a.remove();
    } else {
        console.error('Error generating Anki package:', response.statusText);
    }
};

//删除特定卡片
const deleteCard = (index) => {
    const oldCards = localStorage.getItem('ankiCards');
    const oldCardsJson = JSON.parse(oldCards);
    oldCardsJson.splice(index, 1);
    localStorage.setItem('ankiCards', JSON.stringify(oldCardsJson));
    addNotice('cards-count-notice', `共制作<b> ${JSON.parse(localStorage.getItem('ankiCards')).length} </b>张卡片，点击可编辑。`, listCards);
};

//列出所有卡片
const listCards = () => {
    const oldCards = localStorage.getItem('ankiCards');
    if (oldCards) {
        const oldCardsJson = JSON.parse(oldCards);
        const ol = document.createElement('ol');
        ol.id = 'cards-list';
        oldCardsJson.forEach((card, index) => {
            const li = document.createElement('li');
            li.setAttribute('data-index', index);
            li.innerHTML = `
                <div class="card-contents">
                    <div class="card-front">${Object.keys(card)[0]}</div>
                    <div class="card-back">${Object.values(card)[0]}</div>
                </div>
                <div class="operation-btns">
                    <span class="edit-card-btn">编辑</span>
                    <span class="delete-card-btn">删除</span>
                </div>`;
            const operationBtns = li.querySelector('.operation-btns');
            const editBtn = li.querySelector('.edit-card-btn');
            const deleteBtn = li.querySelector('.delete-card-btn');
            editBtn.onclick = () => { showPopup(index) };
            deleteBtn.onclick = () => { deleteCard(index) };
            li.onmouseover = () => {
                operationBtns.style.visibility = 'visible';
            };
            li.onmouseout = () => {
                operationBtns.style.visibility = 'hidden';
            };
            ol.appendChild(li);
        });
        resultsContainer.appendChild(ol);
    } else {
        addNotice('no-cards-notice', '暂无卡片，请先制作卡片。');
    }
};

//加载页面时执行
const onLoad = () => {
    resultsContainer.style.display = 'block';
    if (localStorage.getItem('ankiCards')) {
        const oldCards = localStorage.getItem('ankiCards');
        if (isVaildJson(oldCards)) {
            addNotice('cards-count-notice', `共制作<b> ${JSON.parse(localStorage.getItem('ankiCards')).length} </b>张卡片，点击可编辑。`, listCards);
        } else {
            addNotice('local-json-notice', '本地存储的卡片数据有误，已清空。', () => {
                localStorage.removeItem('ankiCards');
            });
        }
    } else {
        addNotice('no-cards-notice', '暂无卡片，请先制作卡片。');
    }
    addBtns();
};

//提交表单时执行
const onSubmit = () => {
    loader.style.display = 'block';
    resultsContainer.innerHTML = '';
    //为sse消息创建容器
    addSseContainer(['golem-response'], false);
    const golemResponseSpan = document.querySelector('.golem-response span');
    golemResponseSpan.textContent = '';
};

//sse消息处理
const onMessage = (response) => {
    const golemResponseSpan = document.querySelector('.golem-response span');
    golemResponseSpan.textContent += response;
};

//sse完成时执行
const onDone = () => {
    loader.style.display = 'none';
    const golemResponseSpan = document.querySelector('.golem-response span');
    const newCards = golemResponseSpan.textContent;
    golemResponseSpan.textContent = '';
    if (isVaildJson(newCards)) {
        if (localStorage.getItem('ankiCards')) {
            const oldCards = localStorage.getItem('ankiCards');
            const mergedCards = JSON.parse(oldCards).concat(JSON.parse(newCards));
            localStorage.setItem('ankiCards', JSON.stringify(mergedCards));
        } else {
            localStorage.setItem('ankiCards', newCards);
        }
        addNotice('cards-count-notice', `共制作<b> ${JSON.parse(localStorage.getItem('ankiCards')).length} </b>张卡片，点击可编辑。`, listCards);
    } else {
        addNotice('response-error-notice', '服务器返回的数据有问题, 请重新制卡。');
        return;
    }
    addBtns();
    document.getElementById('user_input').value = '';
};

document.addEventListener('DOMContentLoaded', () => {
    onLoad();
    const chatClient = new ChatClient(
        'sse/anki_cards',
        {
            onSubmitCallback: onSubmit,
            onMessageCallback: onMessage,
            onDoneCallback: onDone
        }
    );
});
