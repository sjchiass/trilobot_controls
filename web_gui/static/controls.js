function httpGetAsync(theUrl) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

var myGamePiece = {
    speedL: 0, speedR: 0
}

var myGameArea = {
    start: function () {
        this.motor_interval = setInterval(updateGameArea, 20);
        this.ultrasonic_interval = setInterval(updateUltrasonic, 2500);
        window.addEventListener('keydown', function (e) {
            myGameArea.keys = (myGameArea.keys || []);
            myGameArea.keys[e.keyCode] = (e.type == "keydown");
        })
        window.addEventListener('keyup', function (e) {
            myGameArea.keys[e.keyCode] = (e.type == "keydown");
        })
    }
}

function updateGameArea() {
    var old_L = myGamePiece.speedL;
    var old_R = myGamePiece.speedR;
    myGamePiece.speedL = 0;
    myGamePiece.speedR = 0;
    var keys_pressed = 0;
    // Arrow keys: left, up, right, down
    if (myGameArea.keys && myGameArea.keys[37]) { myGamePiece.speedL += -0.5; myGamePiece.speedR += 0.5; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[38]) { myGamePiece.speedL += 1; myGamePiece.speedR += 1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[39]) { myGamePiece.speedL += 0.5; myGamePiece.speedR += -0.5; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[40]) { myGamePiece.speedL += -1; myGamePiece.speedR += -1; keys_pressed++; }
    // Numpad (numlock): 1, 2, 3, 4, 5, 6, 7, 8, 9
    if (myGameArea.keys && myGameArea.keys[97]) { myGamePiece.speedL += -0.7; myGamePiece.speedR += 1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[98]) { myGamePiece.speedL += -1; myGamePiece.speedR += -1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[99]) { myGamePiece.speedL += -1; myGamePiece.speedR += -0.7; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[100]) { myGamePiece.speedL += -1; myGamePiece.speedR += 1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[101]) { keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[102]) { myGamePiece.speedL += 1; myGamePiece.speedR += -1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[103]) { myGamePiece.speedL += 0.7; myGamePiece.speedR += 1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[104]) { myGamePiece.speedL += 1; myGamePiece.speedR += 1; keys_pressed++; }
    if (myGameArea.keys && myGameArea.keys[105]) { myGamePiece.speedL += 1; myGamePiece.speedR += 0.7; keys_pressed++; }

    var power = document.getElementById("power").value / 10;
    document.getElementById("power_val").innerHTML = 100 * power;
    var l_balance = Math.min(2 - document.getElementById("balance").value / 50, 1);
    document.getElementById("l_balance").innerHTML = l_balance.toFixed(2);
    var r_balance = Math.min(document.getElementById("balance").value / 50, 1);
    document.getElementById("r_balance").innerHTML = r_balance.toFixed(2);
    if (myGamePiece.speedL != 0) { myGamePiece.speedL *= l_balance * power / keys_pressed; }
    if (myGamePiece.speedR != 0) { myGamePiece.speedR *= r_balance * power / keys_pressed; }
    if (old_L != myGamePiece.speedL && old_R != myGamePiece.speedR) {
        if (myGamePiece.speedL == 0 && myGamePiece.speedR == 0) {
            httpGetAsync("/commands/coast")
        } else {
            httpGetAsync(`/commands/drive?left=${myGamePiece.speedL.toFixed(2)}&right=${myGamePiece.speedR.toFixed(2)}`)
        }
    }
    var old_servo = myGamePiece.servo;
    myGamePiece.servo = document.getElementById("servo").value / 10;
    if (old_servo != myGamePiece.servo) { httpGetAsync(`/commands/servo?angle=${myGamePiece.servo}`); }
}

function updateUltrasonic() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "/commands/ultrasonic", false); // true for asynchronous 
    xmlHttp.send(null);
    document.getElementById("ultrasonic_distance").innerHTML = xmlHttp.responseText;
}

myGameArea.start();