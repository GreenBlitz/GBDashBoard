function getSelectedCamera(){
    return parseInt(document.getElementById('camera').value);
}
function getSelectedThreshold(){
    let elem = document.getElementById('thresholds');
    return elem.options[elem.selectedIndex].value;
}
function getInputThresholdCode(){
    return document.getElementById('threshold_code').value;
}
function leds(state){
    get('/set_leds', {state:state});
}
function debugMode(state){
    get('/set_debug_mode', {state:state});
}
function exposure(state){
    get('/set_exposure', {raw:(state?11:10), camera: getSelectedCamera()})
}
function autoExposure(state){
    get('/set_auto_exposure', {raw:(state?3:1), camera: getSelectedCamera()})
}
function startVisionMaster(button1, button2){
    button1.disabled = true;
    button2.disabled = false;
    get('/start_vision_master')
}
function stopVisionMaster(button1, button2){
    button1.disabled = true;
    button2.disabled = false;
    get('/stop_vision_master')
}
function startGBVisionStream(button){
    button.disabled = true;
    let callback = function(){button.disabled = false;}
    get('/start_gbvision_stream', {camera: getSelectedCamera()}, callback, callback);
}
function setVisionAlgorithm(algo){
    get('/set_vision_algorithm', {algo: algo})
}
function setThresholdValue(){
    get('/set_threshold_value', {name: getSelectedThreshold(), code: getInputThresholdCode()});
}
get('/get_algorithms_list', null, function(response){
    let lst = JSON.parse(response);
    let elem = document.getElementById("algorithms");
    for(var i in lst){
        elem.innerHTML += '<option value="' + lst[i] + '">' + lst[i] + '</option>';
    }
})
get('/get_all_thresholds', null, function(response){
    let lst = JSON.parse(response);
    let elem = document.getElementById("thresholds");
    for(var i in lst){
        elem.innerHTML += '<option value="' + lst[i] + '">' + lst[i] + '</option>';
    }
})