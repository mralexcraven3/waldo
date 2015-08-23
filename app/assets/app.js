Array.prototype.average = function () {
    var sum = 0, j = 0; 
    for (var i = 0; i < this.length, isFinite(this[i]); i++) { 
        sum += parseFloat(this[i]); ++j; 
    } 
    return j ? sum / j : 0; 
};

$(document).ready(function() {
    var history = [];
    var ws = new WebSocket("ws://localhost:1235/websocket");
    var $l100 = $("#load-100");
    var $l50 = $("#load-50");
    var $tr = $("#total-req");
    var $rs = $("#req-sec");

    var refresh = function() {
        var l100 = (100 * history.slice(-500).average()).toFixed(2) + "%";
        $l100.html(l100);
        var l50 = (100 * history.slice(-50).average()).toFixed(2) + "%";
        $l50.html(l50);
        $("title").html("Waldo | " + l100);
        $tr.html(history.length);
    };

    var handle_response = function(code) {
        return parseInt(code, 10) == 200 ? 1 : 0
    };

    ws.onopen = function() {};
    ws.onmessage = function (evt) {
        history.push(handle_response(evt.data));
        refresh();
    };
});
