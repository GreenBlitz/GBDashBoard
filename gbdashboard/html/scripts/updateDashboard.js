
function getUpdate(dashboardName){

    const url = "/" + dashboardName + "/update";
    const http = new XMLHttpRequest();
    http.open("GET",  url, true);
    http.send();

    http.onreadystatechange = (e) => {

    }

}

