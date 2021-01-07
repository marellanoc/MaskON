var data = {};
var audio = null;


function configure(){
    var sonido_alarma = data['tono_alarma']; //EXTRAER DE SESSIONSTORAGE
    audio = new Audio('/static/alarms/'+sonido_alarma+'.mp3'); //PONER NOMBRE EN B
    audio.volume = data['volumen_alarma']/100;
}

function check_data(){
    data = JSON.parse(sessionStorage.getItem('data'));
    if (data == null){
        //aqui se hace el get al servidor
        // se guarga en session storage
        $.ajax({
        url: "/get_config",
        type: 'GET',
        success: function(res) {
            sessionStorage.setItem('data',JSON.stringify(res))
            data=JSON.parse(sessionStorage.getItem('data'));
            configure();
        }
    });
    }
    else{
        configure();
    }
}


function post_data(){
    sessionStorage.setItem('data',JSON.stringify(data))
    $.ajax({
        url: "/post_config",
        type: 'POST',
        data: JSON.stringify(data),
        dataType: "json",
        contentType: 'application/json',
        success: function(res) {
            console.log(res);

        }
    })
}


function alarm(){
    if(data['estado_alarma']==1){
        audio.loop=true;
        audio.play();
    }
}

function stop_alarm(){
    audio.pause();
    audio.currentTime = 0;
}

function mute_alarm(){
    if(current_sound==1){
        audio.pause();
        audio.currentTime = 0;
    }

    if(data['estado_alarma']==1){
       data['estado_alarma']=0;
       post_data();
       document.getElementById("mute_button").innerHTML = 'Quitar Silencio';

    }
    else if(data['estado_alarma']==0){
       data['estado_alarma']=1;
       post_data();
       document.getElementById("mute_button").innerHTML = "Silenciar";
        if(current_sound==1){
            alarm();
        }
    }
}