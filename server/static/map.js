var canvas = new fabric.Canvas('c');
canvas.uniScaleKey = "null";

window.addEventListener('resize', resizeCanvas, false);

function resizeCanvas() {
    var style = window.getComputedStyle(document.getElementById("lf"), null);
    canvas.setHeight(parseInt(style.getPropertyValue("height")));
    canvas.setWidth(parseInt(style.getPropertyValue("width")));
    //imgInstance.scaleToWidth(canvas.width);
    canvas.renderAll();
}


canvas.setZoom(canvas.getZoom() / 10);

canvas.viewportTransform[4] += canvas.width * 2;
canvas.viewportTransform[5] += canvas.height * 3;

canvas.renderAll();

var chosen = 0;
var choses = [];

function loadField() {
    let request = new XMLHttpRequest();
    request.open('GET', '/static/map.txt', false);
    request.send();
    var markers = [];

    if (request.status === 200) {
        let arr = request.responseText.split("\n");

        for (let i = 0; i < arr.length; i++) {
            let str = arr[i].split(" ");
            let id = parseInt(str[0]);
            let size = parseFloat(str[1]) * 1000 / 6;
            let shiftX = parseFloat(str[2]) * 1000;
            let shiftY = parseFloat(str[3]) * 1000;
            let angle = parseFloat(str[5]) / Math.PI * 180;

            try {
                var marker = generateArucoMarker(4, 4, "4x4_1000", id);

                marker.set({
                    angle: angle,
                    id: id,
                    scaleX: size,
                    scaleY: size,
                    left: shiftX,
                    top: -shiftY,
                    marker: true
                });

                let a = marker.aCoords;
                let center = {x: (a.bl.x + a.tr.x) / 2, y: (a.bl.y + a.tr.y) / 2};

                marker.set('top', marker.top - (a.tl.y + center.y) * 1000 / 18);
                marker.set('left', marker.left + (a.tl.x - center.x) * 1000 / 18);

                markers.push(marker);
            } catch (e) {

            }
        }

    }
    let req = new XMLHttpRequest();
    req.open('GET', '/static/roads.json', false);
    req.send();
    if (req.status === 200) {
        var canvas_data = JSON.parse(req.responseText);
        roads = canvas_data;
        for (let i = 0; i < canvas_data.lines.length; i++) {
            let coords = [canvas_data.points[canvas_data.lines[i]["1"]].x * 1000, -canvas_data.points[canvas_data.lines[i]["1"]].y * 1000, canvas_data.points[canvas_data.lines[i]["2"]].x * 1000, -canvas_data.points[canvas_data.lines[i]["2"]].y * 1000];
            let line = new fabric.Line(coords, {
                fill: 'red',
                stroke: 'red',
                strokeWidth: 15,
            });
            markers.push(line);
        }
        for (let i = 0; i < canvas_data.points.length; i++) {
            let line = new fabric.Circle({
                radius: 100,
                fill: 'red',
                left: canvas_data.points[i].x * 1000 - 100,
                top: -canvas_data.points[i].y * 1000 - 100,
                selectable: false
            });
            markers.push(line);
        }
    }

    try {
        var group = new fabric.Group(markers, {
            selectable: false
        });
        canvas._objects.unshift(group);
        canvas.renderAll();
    } catch (e) {

    }
}

function generateMarkerObject(width, height, bits) {
    var marker = [];

    // Background rect
    var backRect = new fabric.Rect({
        left: 0,
        top: 0,
        originX: 'left',
        originY: 'top',
        width: width + 2,
        height: height + 2,
        fill: 'black'
    });
    marker.push(backRect);

    // "Pixels"
    for (var i = 0; i < height; i++) {
        for (var j = 0; j < width; j++) {
            var color = bits[i * height + j] ? 'white' : 'black';
            var pixel = new fabric.Rect({
                left: j + 1,
                top: i + 1,
                originX: 'left',
                originY: 'top',
                width: 1,
                height: 1,
                fill: color,
                hasBorders: false
            });
            marker.push(pixel);
        }
    }
    // generate group object
    var group = new fabric.Group(marker, {
        width: width + 2,
        height: height + 2,
        originX: 'left',
        originY: 'top',
        transparentCorners: false,
        lockScalingFlip: true
    }).setCoords().setControlsVisibility({
        'ml': false,
        'mt': false,
        'mr': false,
        'mb': false
    });

    return group;
}

function generateArucoMarker(width, height, dictName, id) {
    var bytes = dict[dictName][id];
    var bits = [];
    var bitsCount = width * height;

    // Parse marker's bytes
    for (var byte of bytes) {
        var start = bitsCount - bits.length;
        for (var i = Math.min(7, start - 1); i >= 0; i--) {
            bits.push((byte >> i) & 1);
        }
    }

    return generateMarkerObject(width, height, bits);
}


resizeCanvas();
loadField();
canvas.renderAll();

canvas.on('mouse:down', function (opt) {
    var evt = opt.e;
    if (evt.altKey === true) {
        this.isDragging = true;
        this.selection = false;
        this.lastPosX = evt.clientX;
        this.lastPosY = evt.clientY;
    } else if (choosing === true) {
        var land_point = opt.absolutePointer;
        var point1 = get_point(land_point.x, -land_point.y);
        if (point1 === -1 && choses.length === 0) {
            let request = new XMLHttpRequest();
            let send_data = {
                id: choose_id,
                command: choose_type,
                x: land_point.x / 1000,
                y: -land_point.y / 1000,
                z: 1.5
            };
            request.open('GET', '/send?' + Object.entries(send_data).map(e => e.join('=')).join('&'), true);
            request.send(null);
            choosing = false;
        } else {
            if (chosen === 0) {
                var point1 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
                if (point1 !== -1) {
                    choses.push(point1);
                    chosen += 1;
                    return
                }
            } else if (chosen === 1) {
                var point2 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
                if (point2 !== -1) {
                    choses.push(point2);
                    let request = new XMLHttpRequest();
                    let send_data = {
                        id: choose_id,
                        command: 'buiild_path',
                        o: choses[0],
                        t: choses[1]
                    };
                    request.open('GET', '/send?' + Object.entries(send_data).map(e => e.join('=')).join('&'), true);
                    request.send(null);
                }
                choses = [];
                chosen = 0
            }
        }
    } else if (adding_point === true) {
        let request = new XMLHttpRequest();
        request.open('GET', '/set?m=add&c=point&x=' + (opt.absolutePointer.x / 1000).toString() + '&y=' + (-opt.absolutePointer.y / 1000).toString(), true);
        request.send(null);
        adding_point = false;
        canvas._objects.shift();
        loadField();
    } else if (adding_line === true) {
        if (chosen === 0) {
            var point1 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
            if (point1 !== -1) {
                choses.push(point1);
                chosen += 1;
                return
            }
        } else if (chosen === 1) {
            var point2 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
            if (point2 !== -1) {
                choses.push(point2);
                let request = new XMLHttpRequest();
                request.open('GET', '/set?m=add&c=line&o=' + choses[0].toString() + '&t=' + choses[1].toString(), true);
                request.send(null);
                adding_line = false;
                canvas._objects.shift();
                loadField();
            }
            choses = [];
            chosen = 0
        }
    } else if (remove_point === true) {
        let request = new XMLHttpRequest();
        request.open('GET', '/set?m=remove&c=point&n=' + get_point(opt.absolutePointer.x, -opt.absolutePointer.y).toString(), true);
        request.send(null);
        remove_point = false;
        canvas._objects.shift();
        loadField();
    } else if (remove_line === true) {
        if (chosen === 0) {
            var point1 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
            if (point1 !== -1) {
                choses.push(point1);
                chosen += 1;
                return
            }
        } else if (chosen === 1) {
            var point2 = get_point(opt.absolutePointer.x, -opt.absolutePointer.y);
            if (point2 !== -1) {
                choses.push(point2);
                let request = new XMLHttpRequest();
                request.open('GET', '/set?m=remove&c=line&o=' + choses[0].toString() + '&t=' + choses[1].toString(), true);
                request.send(null);
                remove_line = false;
                canvas._objects.shift();
                loadField();
            }
            choses = [];
            chosen = 0
        }
    }
    canvas.backgroundColor = "#f9f9f9";
    for (let i = 0; i < canvas._objects.length; i++) {
        canvas._objects[i].set('opacity', 1);
    }
    canvas.renderAll();
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

canvas.on('mouse:wheel', function (opt) {
    var delta = opt.e.deltaY;
    var zoom = canvas.getZoom();
    zoom = zoom + delta / 200;
    if (zoom > 20) zoom = 20;
    if (zoom < 0.01) zoom = 0.01;
    canvas.zoomToPoint({x: opt.e.offsetX, y: opt.e.offsetY}, zoom);
    opt.e.preventDefault();
    opt.e.stopPropagation();
    canvas.renderAll();
});


function drawDrones() {
    var thr = 1;
    if (choosing) {
        thr = 1;
    }

    while (canvas._objects.length - thr < curr_telemetry.length) {
        let circ = new fabric.Circle({
            radius: 100, fill: 'green', left: 100, top: 100, selectable: false
        });
        canvas.add(circ);
    }
    while (canvas._objects.length - thr > curr_telemetry.length) {
        canvas._objects.pop();
    }
    for (let i = 0; i < curr_telemetry.length; i++) {
        canvas._objects[i + 1].set('fill', curr_telemetry[i].led);
        canvas._objects[i + 1].animate('left', curr_telemetry[i].pose.x * 1000 - 100, {
            duration: 1000 / freq,
            easing: fabric.util.ease.easeInSine
        });
        canvas._objects[i + 1].animate('top', -curr_telemetry[i].pose.y * 1000 - 100, {
            onChange: canvas.renderAll.bind(canvas),
            duration: 1000 / freq,
            easing: fabric.util.ease.easeInSine
        });
        /*canvas._objects[i + 1].left = curr_telemetry[i].pose.x;
        canvas._objects[i + 1].top = -curr_telemetry[i].pose.y - 100;*/
    }
    canvas.renderAll();
}

function get_point(x, y) {
    for (var i = 0; i < roads.points.length; i++) {
        //console.log([x, roads.points[i].x, y, roads.points[i].y]);
        let lena = Math.sqrt(Math.pow(x - roads.points[i].x * 1000, 2) + Math.pow(y - roads.points[i].y * 1000, 2));
        //console.log(lena);
        if (lena <= 100) {
            return i
        }
    }

    return -1
}