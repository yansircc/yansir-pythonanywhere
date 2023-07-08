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

export const addBtn = (id, classNames, textContent, parentId, onClick = null) => {
    let container = document.querySelector('#' + parentId);
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

export const addSseContainer = (classNames, isHighlight = true, parentContainerId = 'response-container') => {
    const parentContainer = document.getElementById(parentContainerId);
    const golemDiv = document.createElement('div');
    const span = document.createElement('span');

    golemDiv.classList.add(...classNames);
    isHighlight && span.classList.add('highlight');

    golemDiv.appendChild(span);
    parentContainer.appendChild(golemDiv);
}

export const parseData = (dataStr) => {
    let data = dataStr.split('**Query:** ').slice(1);
    return data.map(item => {
        let [query, ...rest] = item.split('\n');
        let [intent, conf] = rest[0].split(' with ');
        conf = conf.replace(' reliability', '');
        return {
            '关键词': query,
            '搜索意图': intent.replace('Search intent: ', ''),
            '可靠性': conf,
            '内容形式': rest[1].replace('Content format: ', ''),
            '输出类型': rest[2].replace('Content type: ', ''),
            '推荐标题': rest[3].replace('Recommended title: ', ''),
            '描述': rest[4].replace('Description: ', '')
        };
    });
}

export const objectToCsv = (data) => {
    const csvRows = [];
    const headers = Object.keys(data[0]);
    csvRows.push(headers.join(','));

    for (const row of data) {
        const values = headers.map(header => {
            const escaped = ('' + row[header]).replace(/"/g, '""');
            return `"${escaped}"`;
        });
        csvRows.push(values.join(','));
    }
    return csvRows.join('\n');
}

export const downloadCsv = (data) => {
    const blob = new Blob([data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'download.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
