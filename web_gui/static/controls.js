// The javascript for controlling the bot comes from here:
// https://www.w3schools.com/graphics/game_controllers.asp

function httpGetAsync(theUrl) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

// Use these values to track changes to the JoyStick
// We want to limit the amount of calls to the API
var old_L = 0;
var old_R = 0;
var old_servo = 0.5;

// I don't completely understand how this works but it seems to
// keep arrays of pressed and unpressed keys. These can be checked
// later.
var keyHandler = {
    start: function () {
        window.addEventListener('keydown', function (e) {
            keyHandler.keys = (keyHandler.keys || []);
            keyHandler.keys[e.keyCode] = (e.type == "keydown");
        })
        window.addEventListener('keyup', function (e) {
            keyHandler.keys[e.keyCode] = (e.type == "keydown");
        })
    }
}

// Main loop for robot controls
function updateControls() {
    var keys_pressed = 0;
    var speedL = 0;
    var speedR = 0;

    // Arrow keys: left, up, right, down
    if (keyHandler.keys && keyHandler.keys[37]) { speedL += -0.5; speedR += 0.5; keys_pressed++; }
    if (keyHandler.keys && keyHandler.keys[38]) { speedL += 1; speedR += 1; keys_pressed++; }
    if (keyHandler.keys && keyHandler.keys[39]) { speedL += 0.5; speedR += -0.5; keys_pressed++; }
    if (keyHandler.keys && keyHandler.keys[40]) { speedL += -1; speedR += -1; keys_pressed++; }

    // Power scales boths motors equally
    var power = document.getElementById("power").value / 10;
    document.getElementById("power_val").innerHTML = 100 * power;

    // When balance is 1.00:1.00 nothing happens
    // If balance is changed to 0.70:1.00 by dragging the slider,
    // the left motor will get 70% power while the right motor gets 100%
    // (The overall power level is multiplicative with balance)
    var l_balance = Math.min(2 - document.getElementById("balance").value / 50, 1);
    document.getElementById("l_balance").innerHTML = l_balance.toFixed(2);
    var r_balance = Math.min(document.getElementById("balance").value / 50, 1);
    document.getElementById("r_balance").innerHTML = r_balance.toFixed(2);

    if (speedL != 0) { speedL *= l_balance * power / keys_pressed; }
    if (speedR != 0) { speedR *= r_balance * power / keys_pressed; }

    // Compare against previous values and do nothing if they are unchanged
    if (old_L != speedL || old_R != speedR) {
        if (speedL == 0 && speedR == 0) {
            httpGetAsync("/commands/coast");
        } else {
            httpGetAsync(`/commands/drive?left=${speedL.toFixed(2)}&right=${speedR.toFixed(2)}`);
        }
    }

    // Keep track of current values for next time
    old_L = speedL;
    old_R = speedR;

    // Servo control
    servo = document.getElementById("servo").value / 10;
    if (old_servo != servo) { httpGetAsync(`/commands/servo?angle=${servo}`); }
    old_servo = servo;
}

function updateUltrasonic() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/commands/ultrasonic", false); // true for asynchronous 
    xmlHttp.send(null);
    document.getElementById("ultrasonic_distance").innerHTML = xmlHttp.responseText;
}

window.setInterval(updateControls, 100);
window.setInterval(updateUltrasonic, 2500);

keyHandler.start()
