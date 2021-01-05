function test() {
    console.log('miau');
}

function check_data(){
    console.log('haciendo get');
    data = JSON.parse(sessionStorage.getItem('data'));
    console.log(data);
    if (data == null){
        //aqui se hace el get al servidor
        // se guarga en session storage
        $.ajax({
        url: "/get_config",
        type: 'GET',
        success: function(res) {
            console.log(res);
            sessionStorage.setItem('data', JSON.stringify(res))
            data = JSON.parse(sessionStorage.getItem('data'));
            show_config();
        }
    });
    }
    else{
        show_config()
    }
}

function show_config(){
    document.getElementById("volume").innerHTML = data['volumen_alarma'];
    document.getElementById("tone").innerHTML = data['tono_alarma'];
    if(data['estado_alarma'] == 1){
        $('#check_alarm').prop('checked',true);
    }
    else if(data['estado_alarma'] == 0){
        console.log('apagada')
        $('#check_alarm').prop('checked',false);
    }
}

function change_state() {
    if (data['estado_alarma'] == 1) {
        data['estado_alarma'] = 0

    } else if (data['estado_alarma'] == 0) {
        data['estado_alarma'] = 1
    }
    post_data();
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


function populate_tones(){
    $( "#song_select" ).empty();
    $.each(data['tonos_alarma'], function (i, p) {
        console.log(i, p)
        $('#song_select').append($('<option></option>').val(p).html(p));

    });
    //$("#song_select[value='"+data['tono_alarma']+"']").attr("selected", true);
    $('[name=options] option').filter(function() {
            return ($(this).text() == data['tono_alarma']); //To select Blue
        }).prop('selected', true);

}


function show_loading(){
    $('#close_song_modal').trigger('click');
    $('#loading_modal').modal('show');
}


function hide_loading(){
    setTimeout(function () {
        $('#loading_modal').modal('hide');
        data['tono_alarma'] = new_audio;
        data['tonos_alarma'].push(new_audio);
        document.getElementById("tone").innerHTML = new_audio;
        $('#file').val('');
        $( "#song_select" ).prop( "disabled", false );
        post_data();
    }, 3000);


}


function upload_file(){
   var form_data = new FormData($('#upload-file')[0]);

   show_loading();
    $.ajax({
        type: 'POST',
        url: '/post_file',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            console.log("success!")
            hide_loading();
        },
    });
}
