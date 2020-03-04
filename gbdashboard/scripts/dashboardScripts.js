
const UPDATE_TIMEOUT = 100;

function getUpdate(dashboardName){

    const url = "/board/" + dashboardName + "/update";
    const http = new XMLHttpRequest();
    http.open("GET",  url, true);
    http.send();
    var ref = false;

    http.onreadystatechange = (e) => {
        if (http.readyState === 4 && http.status === 200) {
            var asJson = JSON.parse(http.response);

            for (let key in asJson){

                if (key === "__name"){
                    continue;
                }

                var subtableDoc = document.getElementById(key);
                if (subtableDoc === null){
                    forceRefresh();
                    ref = true;
                    return;
                }

                var subtable = asJson[key];

                for (let elemKey in subtable){

                    let id = key + "->" + elemKey
                    var element = document.getElementById(id);

                    if (element === null){
                        forceRefresh();
                        ref = true;
                        return;
                    }

                    textBox = element.children[1].firstChild;
                    if (!textBox.locked){
                        textBox.value = subtable[elemKey]
                    }

                }

            }

        }
    };

    if (!ref){
        setTimeout(getUpdate, UPDATE_TIMEOUT, dashboardName);
    }

}

function forceRefresh(){
    location.reload();
}

function sendData(subtableKeyPair, dashboardName){
    textBox = document.getElementById(subtableKeyPair).children[1].firstChild;
    value = textBox.value;
    textBox.locked = false;
    subtableKeyList = subtableKeyPair.split("->");
    subtable = subtableKeyList[0];
    key = subtableKeyList[1];

    const url = "/board/" + dashboardName + "/senddata?subtable=" + subtable + "&key=" + key + "&value=" + value;
    const http = new XMLHttpRequest();
    http.open("GET",  url, true);
    http.send();
}

setTimeout(getUpdate, 500, document.getElementById("tableName").innerText);
