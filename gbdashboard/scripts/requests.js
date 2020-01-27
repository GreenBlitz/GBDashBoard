function createXHR(type, url, callback=null, error=null){
    xhr = new XMLHttpRequest();
    xhr.open(type, url, true);
    xhr.onreadystatechange = function(){
        if(this.readyState === XMLHttpRequest.DONE) {
            if(this.status == 200){
                if(callback != null){
                    callback(this.response);
                }
            }
            else if(error != null){
                error(this.response, this.status)
            }
        }
    }
    return xhr;
}


function post(url, data={}, callback=null, error=null){
    xhr = createXHR('POST', url, callback, error);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xhr.send(JSON.stringify(data));
    return xhr;
}

function get(url, data=null, callback=null, error=null){
    if(data){
        url += '?'
        for(key in data){
            url += encodeURIComponent(key) + '=' + encodeURIComponent(data[key])+'&';
        }
    }
    xhr = createXHR('GET', url, callback, error);
    xhr.send();
    return xhr;
}

function repeat(url, data=null, callback=null, error=null, timeout=2000, method=get){
    function _repeat(){
        let _data;
        if(typeof data == 'function'){
            _data = data();
        }
        else{
            _data = data;
        }
        method(url, _data, callback, error);
    }
    setInterval(_repeat, timeout);
}