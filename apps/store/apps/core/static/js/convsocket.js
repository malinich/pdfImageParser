$(document).ready(function() {
    updater.start();
});


var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/convsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
        if (message.error){
            $('#message').html('<div> <h4>error:' + message.error +'</h4></div>');
        }
        else {
            $('#message').html('<div> <h4>Created:' + message.count +' pdf image</h4></div>');
        }

    }
};
