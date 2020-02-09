
const UPDATE_TIMEOUT = 30;

function getUpdate(dashboardName){

    const url = "/board/" + dashboardName + "/update";
    const http = new XMLHttpRequest();
    http.open("GET",  url, true);
    http.send();

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
                    return;
                }

                var subtable = asJson[key];

                for (let elemKey in subtable){

                    let id = key + "->" + elemKey
                    var element = document.getElementById(id);

                    if (element === null){
                        forceRefresh();
                        return;
                    }

                    element.children[1].firstChild.innerText = subtable[elemKey]

                }

            }

        }
    };

    setTimeout(getUpdate, UPDATE_TIMEOUT, dashboardName);

}

function forceRefresh(){
    location.reload();
}

setTimeout(getUpdate, 500, document.getElementById("tableName").innerText);
