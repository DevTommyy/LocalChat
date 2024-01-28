function checkAlreadyLogged() {
    const urlParam = new URLSearchParams(window.location.search);

    checkExpire('auth');

    if((checkExpire('id') !== null && !checkExpire('id')) && localStorage.getItem('id')){
        id = JSON.parse(localStorage.getItem('id')).value;

        if((urlParam.get('id') !== null || urlParam.get('id') !== '') && urlParam.get('id') !== id){
            window.location.replace(`/chatroom?id=${id}`);
        }  
        return true;
    }
    return false;
}

function checkAuth() {
    if(!checkAlreadyLogged()){
        if(!checkId()){
            window.location.replace('/');
        }
    }
}

function checkId() {
    const urlString = window.location.search;
    const urlParam = new URLSearchParams(urlString);

    fetch('/get_unique_id')
        .then(response => response.json())
        .then(data => {
            if (urlParam.get('id') !== data.unique_id) {
               return false;
            }
            else {
                setWithExpire('id', data.unique_id);
                setWithExpire('auth', 'true')
            }
        });
    return true;
}

function setWithExpire(key, value) {
    const now = new Date();
    const week = 604800000;
    //NOTA PER TESTING TOGLIERE WEEK RIGA 38 (1 MINUTO IN MS = 60000)
    const item = {
		value: value,
		expiry: now.getTime() + week,
	}
    localStorage.setItem(key, JSON.stringify(item));
}

function checkExpire(key) {
    const itemStr = localStorage.getItem(key);

	if (!itemStr) {
		return null;
	}
	const item = JSON.parse(itemStr);
	const now = new Date();

	if (now.getTime() > item.expiry) {
		localStorage.removeItem(key);
		return true;
	}
	return false;
}

// function otherAuth() {
//     if(sessionStorage.getItem('auth') != 'true'){
//         window.location.replace("/");
//     }
// }
