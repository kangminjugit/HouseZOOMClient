function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

window.onload = async function(){
    var data = await eel.get_classList(JSON.parse(localStorage.getItem('accessToken')))();
    if(data['status'] === 'success'){
        data = data['data']['classList'];
        data.map(row => {
            // console.log(row);
            var li = htmlToElement(`<li class="dropdown-item" value=${row['id']}><a  href="#" >${row['year']+'학년 '+row['name']}</a></li>`);
            document.getElementById('class_list').insertAdjacentElement("afterbegin", li);
        })    
    }
}

var itemList = document.getElementsByClassName('.dropdown-item');
for(var i=0; i<itemList.length; i++){
    itemList[i].addEventListener('click', (e) => {
        localStorage.setItem('curClass', JSON.stringify(e.currentTarget.value));
        console.log(e.currentTarget.value);
    })
}