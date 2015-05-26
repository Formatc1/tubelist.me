function objToString (obj) {
    var str = '';
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            str += p + '::' + obj[p] + '\n';
        }
    }
    return str;
}


/*  Websocket.  */
var ws = undefined;

function ws_send(msg) {
    (typeof ws !== 'undefined') && ws.send(msg);

}


/* Initialize websockets. */
function ws_initialize(id) {
    var hostname = window.document.location.hostname;
    var port = window.document.location.port;

    if ("WebSocket" in window) {
        /*  Open a websocket to the host.  */
        var wsproto = "ws";

        if (hostname == "localhost" || hostname == "127.0.0.1") {
            ws = new WebSocket(wsproto + "://" + hostname + ":8080/ws/" + id);
        }
        else {
            ws = new WebSocket(wsproto + "://" + hostname + ":8000/ws/" + id);
        }
        /*  Handle open, message and close events.  */
        ws.onopen = function () {
            // var at = Date(Date.now());
            // ztextarea.value = at + ": WebSocket opened - \n";
        };
        ws.onmessage = function (msg) {
            // ztextarea.value = msg.data + "\n" + ztextarea.value;
            data = $.parseJSON(msg.data);
            switch (data.task) {
                case "change_order":
                    var video = $('#videos-list [data-id="'+data.id+'"]');
                    if (data.position < 0) {
                        video.insertBefore('#videos-list ul li:eq('+data.index+')');
                    }
                    else {
                        video.insertAfter('#videos-list ul li:eq('+data.index+')');
                    }
                break;
                case "add":
                    $('#videos-list ul').append('<li data-id="'+data.id+'" data-order="'+data.order+'">'+data.name+' <a href="/'+data.identifier+'/delete/'+data.id+'/">Delete</a></li>')
                break;
                case "delete":
                    $('#videos-list [data-id="'+data.id+'"]').remove();
                break;

            }
            if (data.task == "change_order") {
                

                // $('#videos-list [data-id="'+data.id+'"]').attr('data-order'));
            };
            // alert(data.id);
        };
        ws.onclose = function () {
            // var at = Date(Date.now());
            // ztextarea.value = at + ": WebSocket closed!\n" + ztextarea.value;
            alert("closed");
        };

    }
    else {
        alert("No WebSocket support in your browser.");
    }

}

jQuery(document).ready(function($) {
    var id = $("#videos-list").attr('data-id');
    ws_initialize(id);
    var oldIndex = 0;
    $('#videos-list .videos').disableSelection();
    $('#videos-list .videos').sortable({
        start: function(event, ui) {
            oldIndex = ui.item.index();
        },
        update: function(event, ui) {
            var order = ui.item.attr("data-order");
            var position = ui.item.index() - oldIndex;
            var data = {"task": "change_order", "id": id, "video_id": ui.item.attr("data-id"), "position": position, "index": ui.item.index()};
            // alert(JSON.stringify(data));
            ws_send(JSON.stringify(data));
        }
    });
});