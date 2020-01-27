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
repeat('/get_led_ring_state', null, function(state){
    document.getElementById('leds').checked = JSON.parse(state);
})
repeat('/get_exposure_state', function(){return {camera: getSelectedCamera()}}, function(state){
    document.getElementById('exposure').checked = JSON.parse(state);
})
repeat('/get_auto_exposure_state', function(){return {camera: getSelectedCamera()}}, function(state){
    document.getElementById('auto_exposure').checked = JSON.parse(state);
})
repeat('/get_vision_master_debug_mode_state', null, function(state){
    document.getElementById('vision_master_debug').checked = JSON.parse(state);
})
repeat('/get_vision_master_process_state', null, function(state){
    document.getElementById('vision_master_start').disabled = JSON.parse(state);
    document.getElementById('vision_master_stop').disabled = !JSON.parse(state);
})
repeat('/get_current_algorithm', null, function(state){
    let elem = document.getElementById('algorithms')
    let index = 0;
    for(var i in elem.children){
        if(elem.children[i].value == state){
            index = i;
            break;
        }
    }
    elem.selectedIndex = parseInt(index);
})
repeat('/get_python_stream_state', null, function(state){
    document.getElementById('python_stream').disabled = JSON.parse(state);
})