/*  Websocket.  */
var ws = undefined;

function ws_send(msg) {
    (typeof ws !== 'undefined') && ws.send(msg);

}
/*  End of function  ws_send.  */


/* Initialize websockets. */
function ws_initialize(ztextarea) {
    var hostname = window.document.location.hostname;
    var port = window.document.location.port;

    if ("WebSocket" in window) {
        /*  Open a websocket to the host.  */
        var wsproto = "ws";

        if (hostname == "localhost" || hostname == "127.0.0.1") {
            ws = new WebSocket(wsproto + "://" + hostname + ":8080/ws/1");
        }
        else {
            ws = new WebSocket(wsproto + "://" + hostname + ":8000/ws/1");
        }
        /*  Handle open, message and close events.  */
        ws.onopen = function () {
            // var at = Date(Date.now());
            // ztextarea.value = at + ": WebSocket opened - \n";
        };
        ws.onmessage = function (msg) {
            // ztextarea.value = msg.data + "\n" + ztextarea.value;
            alert(msg);
        };
        ws.onclose = function () {
            // var at = Date(Date.now());
            // ztextarea.value = at + ": WebSocket closed!\n" + ztextarea.value;
        };

    }
    else {
        alert("No WebSocket support in your browser.");
    }

}
