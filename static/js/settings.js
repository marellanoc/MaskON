function check_data(){ //funcion que chequea si existe la configuracion en la sessionStorage
    data = JSON.parse(sessionStorage.getItem('data')); // se intenta sacar la configuracion de la sessionStorage
    if (data == null){ //si no esta, se debe obtener
        
        $.ajax({
        url: "/get_config", //se fija la u del servidor donde obtener la configuracion
        type: 'GET',
        success: function(res) { 
            sessionStorage.setItem('data',JSON.stringify(res)) //una vez obtenida se guarda en la sessionStorage
            data=JSON.parse(sessionStorage.getItem('data')); // se saca de la sessionStorage y se guarda en data
            show_config() //muestra la configuracion en pantalla
        }
    });
    }
    else{ //si la informacion está en la sessionStorage se configura directamente
        show_config()
    }
}

function show_config(){ //cambia los valores de los componentes html para mostrar la configuracion del servidor 
    document.getElementById("volume").innerHTML = data['volumen_alarma']; //ajuste de volumen
    document.getElementById("tone").innerHTML = data['tono_alarma']; // ajuste del tono de la alarma
    if(data['estado_alarma'] == 1){
        $('#check_alarm').prop('checked',true); //se activa el slide en caso de que la alarma este activa
    }
    else if(data['estado_alarma'] == 0){
        $('#check_alarm').prop('checked',false); //se deja el slide apagado si la alarma esta desactivada
    }
}

function change_state() { //funcion que cambia el estado de la alarma
    if (data['estado_alarma'] == 1) { //si esta activa
        data['estado_alarma'] = 0 //se desactiva

    } else if (data['estado_alarma'] == 0) { //si esta desactivada 
        data['estado_alarma'] = 1 //se activa
    }
    post_data(); //se manda la configuracion al server
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


function populate_tones(){ //funcion que agrega los tonos disponibles al select
    $( "#song_select" ).empty(); //se vacia en caso de que tenga algo
    $.each(data['tonos_alarma'], function (i, p) { //se recorre el array que contiene los nombres
        $('#song_select').append($('<option></option>').val(p).html(p)); //se agregan al select

    });
    
    $('[name=options] option').filter(function() { //se selecciona el tono que esta configurado
            return ($(this).text() == data['tono_alarma']); //se cambia el valor por defecto del select
        }).prop('selected', true);

}


function show_loading(){ //Se muestra un modal que contiene un gif de "cargando"
    $('#close_song_modal').trigger('click');// cierra el modal actual 
    $('#loading_modal').modal('show'); //abre el modal de carga
}


function hide_loading(){  //funcion que esconde el modal de carga una vez que se subio el archivo
    setTimeout(function () { //se esperan 3 segundos para que todo cargue correctamente
        $('#loading_modal').modal('hide'); //se esconde el modal de carga
        data['tono_alarma'] = new_audio; //se selecciona el tono de alarma que se acaba de subir
        data['tonos_alarma'].push(new_audio); //se agrega al array que guarda los nombres de los tonos disponibles
        document.getElementById("tone").innerHTML = new_audio; // se cambia el texto con la cancion seleccionada
        $('#file').val(''); // se limpia el buffer de subida de video del modal de tonos 
        $( "#song_select" ).prop( "disabled", false ); //se activa la casilla de seleccion de tono del modal
        post_data(); //se envia la configuracion al servidor
    }, 3000);


}


function upload_file(){ //funcion que sube los videos al servidor
   var form_data = new FormData($('#upload-file')[0]); //se crea un formulario con el componente que contiene el archivo

   show_loading(); //se muestra el modal de carga
    $.ajax({ //se envia a traves de un POST el archivo ala servidor
        type: 'POST',
        url: '/post_file',  //se define la url donde van los archivos
        data: form_data, //se adjunta el archivo
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) { //una vez enviado el archivo 
            console.log("success!"); //se muestra este mensaje por consola
            hide_loading(); //se llama la funcion que esconde el modal
        },
    });
}
