var curr_telemetry;
var freq = 4;
var choosing = false;
var cursor;
var choose_type;
var choose_id;

function get_telemetry() {
    let request = new XMLHttpRequest();
    request.open('GET', '/get', false);
    request.send();
    if (request.status === 200) {
        return JSON.parse(request.responseText)["drones"];
    } else {
        return null;
    }
}

function update() {
    let data = get_telemetry();
    let list = document.getElementById("drones-list");
    if (data !== null) {
        curr_telemetry = data;
        drawDrones();
        while (list.childElementCount / 2 > data.length) {
            removeLabel((list.childElementCount / 2 - 1).toString());
        }

        while (list.childElementCount / 2 < data.length) {
            addLabel((list.childElementCount / 2).toString());
        }

        for (let i = 0; i < data.length; i++) {
            render_drone(data[i], (i).toString());
        }
    }
}

function render_drone(el, id) {
    if (el.status === "land") {
        document.getElementById(id + "img").src = "/static/svg/drone.svg";
    } else {
        document.getElementById(id + "img").src = "/static/svg/flying_drone.svg";
    }
    document.getElementById(id + "color").style.backgroundColor = el.led;
    document.getElementById(id + "ip").innerHTML = el.ip;
    document.getElementById(id + "x").innerHTML = "x: " + (Math.round(el.pose.x * 100) / 100).toString();
    document.getElementById(id + "y").innerHTML = "y: " + (Math.round(el.pose.y * 100) / 100).toString();
    document.getElementById(id + "z").innerHTML = "z: " + (Math.round(el.pose.z * 100) / 100).toString();
    document.getElementById(id + "nx").innerHTML = "x: " + (Math.round(el.nextp.pose.x * 100) / 100).toString();
    document.getElementById(id + "ny").innerHTML = "y: " + (Math.round(el.nextp.pose.y * 100) / 100).toString();
    document.getElementById(id + "nz").innerHTML = "z: " + (Math.round(el.nextp.pose.z * 100) / 100).toString();
}

function updateCycle() {
    setTimeout(function () {
        try {
            update();
        } catch (e) {

        }
        updateCycle();
    }, 1000 / freq);
}

function addLabel(id) {
    document.getElementById("drones-list").innerHTML += "<div id='" + id + "' class='drone-el'><div><img id='" + id
        + "img' class='drone-img' alt='' src=''/><div class='elbut delet' onclick='delet(" + id + ")'>" +
        "Delete</div></div><div class='elcontento'><div class='full'><strong>Current Pose</strong>" +
        "<div><div id='" + id + "x'></div><div id='" + id + "y'></div><div id='" + id + "z'></div><div class='ip' id='" + id + "ip'></div></div></div>" +
        "<div class='full'><strong>Next Pose</strong>" +
        "<div><div id='" + id + "nx'></div><div id='" + id + "ny'></div><div id='" + id + "nz'></div></div>" +
        "</div><div class='elbutto'>" +
        "<div onclick='land(" + id + ")' class='elbut' style='margin: 8px 8px 4px 8px;'>" +
        "Land</div><div class='elbut' onclick='flyto(" + id + ")' style='margin: 4px 8px 8px 8px;'>" +
        "Fly to</div></div>" +
        "</div>" +
        "<div id='" + id +
        "color' class='colorel'></div></div><hr id='" + id + "hr' />"
}

function land(id) {
    choose_id = parseInt(id);
    choosing = true;
    choose_type = "land";
    canvas.backgroundColor = "#bdbdbd";
    for (let i = 0; i < canvas._objects.length; i++) {
        canvas._objects[i].set('opacity', 0.8);
    }
    canvas.renderAll();
}

function force_land() {
    for (let i = 0; i < curr_telemetry.length; i++) {
        let request = new XMLHttpRequest();
        let send_data = {
            id: i,
            command: 'land',
            x: curr_telemetry[i].pose.x,
            y: curr_telemetry[i].pose.y,
            z: 1.5
        };
        request.open('GET', '/send?' + Object.entries(send_data).map(e => e.join('=')).join('&'), true);
        request.send(null);
    }
}

function flyto(id) {
    choose_id = parseInt(id);
    choosing = true;
    choose_type = "fly";
    canvas.backgroundColor = "#bdbdbd";
    for (let i = 0; i < canvas._objects.length; i++) {
        canvas._objects[i].set('opacity', 0.8);
    }
    canvas.renderAll();
}

function delet(id) {
    Ply.dialog(
        "confirm",
        "Delete Clever from this list?"
    ).done(function (ui) {
        let request = new XMLHttpRequest();
        request.open('GET', '/delete?id=' + id, false);
        request.send();
    })
        .fail(function (ui) {
        });

}

function removeLabel(id) {
    let element = document.getElementById(id);
    element.parentNode.removeChild(element);
    let element2 = document.getElementById(id + "hr");
    element2.parentNode.removeChild(element2);
}