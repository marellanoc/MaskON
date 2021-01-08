var data = {}; // variable que guarda la configuracion de la pagina
var audio = null; // variable que guarda la alarma


function configure(){
    var sonido_alarma = data['tono_alarma']; //nombre de la alarma
    audio = new Audio('/static/alarms/'+sonido_alarma+'.mp3'); // se carga el audio
    audio.volume = data['volumen_alarma']/100; //ajuste de valomen a un valor entre 0 y 1
}

function check_data(){ //funcion que chequea si existe la configuracion en la sessionStorage
    data = JSON.parse(sessionStorage.getItem('data')); // se intenta sacar la configuracion de la sessionStorage
    if (data == null){ //si no esta, se debe obtener
        
        $.ajax({
        url: "/get_config", //se fija la u del servidor donde obtener la configuracion
        type: 'GET',
        success: function(res) { 
            sessionStorage.setItem('data',JSON.stringify(res)) //una vez obtenida se guarda en la sessionStorage
            data=JSON.parse(sessionStorage.getItem('data')); // se saca de la sessionStorage y se guarda en data
            configure(); //se procede a configurar la alarma
        }
    });
    }
    else{ //si la informacion está en la sessionStorage se configura directamente
        configure();
    }
}


function post_data(){ //funcion que manda la configuracion actual al servidor
    sessionStorage.setItem('data',JSON.stringify(data)) // se guarda la configuracion en la sessionStorage
    $.ajax({
        url: "/post_config", //se fija la url de destino para enviar la configuracion
        type: 'POST',
        data: JSON.stringify(data), //se convierte a string el diccionario que guarda la configuracion actual
        dataType: "json",
        contentType: 'application/json',
        success: function(res) {
            console.log(res); //se muestra por consola la respuesta del server

        }
    })
}


function alarm(){ //funcion que activa la alarma 
    if(data['estado_alarma']==1){ //si la alarma no esta silenciada
        audio.loop=true; //activa loop en el audio para que se reproduzca continuamente
        audio.play(); //se hace sonar la alarma
    }
}

function stop_alarm(){ //funcion para detener alarma
    audio.pause(); //se pausa el sonido
    audio.currentTime = 0; //se rebobina hasta el inicio
}

function mute_alarm(){ // funcion para silenciar la alarma 
    if(current_sound==1){ //si la alarma esta sonando, se pone en pausa y se rebobina
        audio.pause();
        audio.currentTime = 0;
    }

    if(data['estado_alarma']==1){ //si la alarma estaba activa
       data['estado_alarma']=0; // se desactiva 
       post_data(); // se envia la configuracion al servidor
       document.getElementById("mute_button").innerHTML = 'Quitar Silencio'; //se cambia el nombre del boton

    }

    else if(data['estado_alarma']==0){ //si la alarma no estaba activa
       data['estado_alarma']=1; //se activa
       post_data(); // se envia la configuracion al servidor
       document.getElementById("mute_button").innerHTML = "Silenciar";//se cambia el nombre del boton
        if(current_sound==1){ //si la alarma deberia estar sonando
            alarm(); //se hace sonar
        }
    }
}