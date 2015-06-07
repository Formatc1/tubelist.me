function objToString (obj) {
    var str = '';
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            str += p + '::' + obj[p] + '\n';
        }
    }
    return str;
}

var player;
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

        };
        ws.onmessage = function (msg) {
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
                    reload_order();
                break;
                case "add":
                    $('#videos-list ul').append('<li data-id="'+data.id+'" data-order="'+data.order+'" data-identifier="'+data.identifier+'">'+data.name+' <a href="/'+data.playlist+'/delete/'+data.id+'/" class="delete-video">Delete</a></li>');
                    add_video(data.identifier);
                break;
                case "delete":
                    var identifier = $('#videos-list [data-id="'+data.id+'"]').attr('data-identifier');
                    $('#videos-list [data-id="'+data.id+'"]').remove();
                    delete_video(identifier);
                break;
                case "change_name":
                    $('#playlist-title').text(data.name);
                break;

            }
        };
        ws.onclose = function () {

        };

    }
    else {
        // alert("No WebSocket support in your browser. Cooperative edit unavailable.");
    }

}

var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
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
            ws_send(JSON.stringify(data));
            reload_order();
        }
    });

    $('#playlist-title').on("blur", function(){
        var url = $(this).attr('data-url');
        $.ajax({
            url: '/'+ url +'/change-name/',
            data: {name: $(this).text()}
        });
    });

    $('#videos-list').on('click', 'a.delete-video', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        var id = $(this).parent('li').attr('data-identifier');
        $.ajax({
            url: url
        });
        return false;
    });

    $('#search').on('submit', function(event) {

        event.preventDefault();
        var url = $(this).attr('action');
        var query = $(this).children('input.query').val();
        $.ajax({
            url: url+'ajax/',
            data: {q: query}
        })
        .done(function(html) {
            if(html != ""){
                $('#videos-list').hide();
            }
            $('.search-placeholder').html(html).show();
        })        
    });

    $('.search-placeholder').on('click', 'a.add', function(event) {
        event.preventDefault();
        $('.search-placeholder').hide();
        var url = $(this).attr('href');
        $.ajax({
            url: url
        })
        .done(function() {
            $('#videos-list').show();
        })
    });

    $('.search-placeholder').on('click', 'a.navigation', function(event) {
        event.preventDefault();
        $('.search-placeholder').hide();
        var url = $(this).attr('href');
        $.ajax({
            url: url
        })
        .done(function(html) {
            $('.search-placeholder').html(html).show();
        })
    });

    $('.search-placeholder').on('click', 'a.back', function(event) {
        event.preventDefault();
        $('#videos-list').show();
        $('.search-placeholder').hide();
    });
});


function onYouTubeIframeAPIReady() {
    player = new YT.Player('ytplayer', {});

}

function delete_video(id) {
    if (player) {
        var state = player.getPlayerState();
        var actualIds = player.getPlaylist();
        var actualIndex = 0;
        var removedIndex = actualIds.indexOf(id);
        actualIds.splice(removedIndex, 1);
        var actualTime = 0;
        if(state == 1 || state == 2 || state == 3) {
            actualIndex = player.getPlaylistIndex();
            actualTime = player.getCurrentTime();
            if(removedIndex < actualIndex) {
                actualIndex -= 1;
            }
            else if(removedIndex == actualIndex) {
                actualTime = 0;
            }
            player.loadPlaylist(actualIds, actualIndex, actualTime);
            if(state == 2) {
                player.pauseVideo();
            }
        }
        else {
            player.cuePlaylist(actualIds, actualIndex, actualTime);
        }
    }
}

function add_video(id) {
    if (player) {
        var state = player.getPlayerState();
        var actualIds = player.getPlaylist();
        var actualIndex = 0;
        actualIds.push(id);
        var actualTime = 0;
        if(state == 1 || state == 2 || state == 3) {
            actualIndex = player.getPlaylistIndex();
            actualTime = player.getCurrentTime();
            player.loadPlaylist(actualIds, actualIndex, actualTime);
            if(state == 2) {
                player.pauseVideo();
            }
        }
        else {
            player.cuePlaylist(actualIds, actualIndex, actualTime);
        }
    }
}

function reload_order() {
    if (player) {
        var state = player.getPlayerState();
        var actualIds = player.getPlaylist();
        var actualIndex = 0;
        var actualTime = 0;
        var ids = [];
        $('#videos-list .videos li').each(function(index) {
            ids.push($(this).attr('data-identifier'));
        });
        if(state == 1 || state == 2 || state == 3) {
            actualIndex = player.getPlaylistIndex();
            actualIndex = ids.indexOf(actualIds[actualIndex]);
            actualTime = player.getCurrentTime();
            player.loadPlaylist(ids, actualIndex, actualTime);
            if(state == 2) {
                player.pauseVideo();
            }
        }
        else {
            player.cuePlaylist(ids, actualIndex, actualTime);
        }
    }
}