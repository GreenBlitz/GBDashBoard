
function getUpdate(dashboardName){

    const url = "/board/" + dashboardName + "";
    const http = new XMLHttpRequest();
    http.open("GET",  url, true);
    http.send();

    http.onreadystatechange = (e) => {
        if (http.readyState === 4 && http.status === 200) {
            document.getElementsByName("html")[0].innerHTML = http.response
        }
    }

}

