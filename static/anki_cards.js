window.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('response-container');
    const loader = document.getElementById('loader');
    const form = document.getElementById('query-form');
    const ankiCards = document.getElementById('anki-cards');

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const userInput = ankiCards.value;
        loader.style.display = 'block';
        fetch('/generate_anki_cards', {
            method: 'POST',
            body: JSON.stringify({ 'user_input': userInput }),
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                container.innerHTML += data.response;
                container.style.display = 'block';
                loader.style.display = 'none';
                //循环获取Json中的键值对，把键作为标题，把值作为内容，制作预览版的速记卡片，并循环添加到container中，并生成一个确认按钮，监听用户是否点击，如果点击，则把当前Json的内容转为anki格式的文件，冰球浏览器自动下载该文件
                //每个卡片的右上角都创建一个“edit”小图标
                //监听用户是否点击edit图标，如果点击了，则该图标对应的卡片的标题和正文变为可输入状态，用户点击卡片外，则变回普通状态，并同步修改Json中对应的Key的内容或value的内容
            })
            .catch(error => console.error(error));

        return false;
    });
});
