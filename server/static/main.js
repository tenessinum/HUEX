var curr_telemetry;
var freq = 0.5;
var choosing = false;
var cursor;

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
    if (el.status === "landed") {
        document.getElementById(id + "img").src = "/static/svg/drone.svg";
    } else {
        document.getElementById(id + "img").src = "/static/svg/flying_drone.svg";
    }
    document.getElementById(id + "color").style.backgroundColor = el.led;
    document.getElementById(id + "pos").innerHTML = JSON.stringify(el.pose);
}

function updateCycle() {
    setTimeout(function () {
        update();
        updateCycle();
    }, 1000 / freq);
}

function addLabel(id) {
    document.getElementById("drones-list").innerHTML += "<div id='" + id + "' class='drone-el'><img id='" + id
        + "img' class='drone-img' alt='' src=''/><div class='elcontento'><div class='full' id='" + id + "pos'></div><div class='elbutto'>" +
        "<div onclick='land(" + id + ")' class='elbut' style='margin: 8px 8px 4px 8px;'>" +
        "Land</div><div class='elbut' onclick='flyto(" + id + ")' style='margin: 4px 8px 8px 8px;'>" +
        "Fly to</div></div>" +
        "</div>" +
        "<div id='" + id +
        "color' class='colorel'></div></div><hr id='" + id + "hr' />"
}

function land(id) {
    choosing = true;
    canvas.on('mouse:down', function (opt) {
        var land_point = opt.absolutePointer;
        console.log(land_point);
        canvas.on('mouse:down', function (opt) {
            var evt = opt.e;
            if (evt.altKey === true) {
                this.isDragging = true;
                this.selection = false;
                this.lastPosX = evt.clientX;
                this.lastPosY = evt.clientY;
            }
        });
        choosing = false;
    });
}

function flyto(id) {
    choosing = true;
    canvas.set('fill', "#444444");
    canvas.on('mouse:down', function (opt) {
        var flying_point = opt.absolutePointer;
        console.log(flying_point);
        setTimeout(function () {
            canvas.on('mouse:down', function (opt) {
                var evt = opt.e;
                if (evt.altKey === true) {
                    this.isDragging = true;
                    this.selection = false;
                    this.lastPosX = evt.clientX;
                    this.lastPosY = evt.clientY;
                }
            });
        }, 500);
        canvas.set('fill', "#FFFFFF");
        choosing = false;
    });
}

function reset_canvas() {
    canvas.on('mouse:down', function (opt) {
        var evt = opt.e;
        if (evt.altKey === true) {
            this.isDragging = true;
            this.selection = false;
            this.lastPosX = evt.clientX;
            this.lastPosY = evt.clientY;
        }
    });
    canvas.on('mouse:move', function (opt) {
        if (this.isDragging) {
            var e = opt.e;
            this.viewportTransform[4] += e.clientX - this.lastPosX;
            this.viewportTransform[5] += e.clientY - this.lastPosY;
            this.requestRenderAll();
            this.lastPosX = e.clientX;
            this.lastPosY = e.clientY;
        }
    });
    canvas.on('mouse:up', function (opt) {
        this.isDragging = false;
        this.selection = true;
    });
}

function removeLabel(id) {
    let element = document.getElementById(id);
    element.parentNode.removeChild(element);
    let element2 = document.getElementById(id + "hr");
    element2.parentNode.removeChild(element2);
}