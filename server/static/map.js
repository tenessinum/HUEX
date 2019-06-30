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

fabric.Image.fromURL('/static/sample_aruco.png', function (oImg) {
    canvas.add(oImg);
    oImg.moveTo(0);
}, {
    selectable: false
});

resizeCanvas();
canvas.renderAll();

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

canvas.on('mouse:wheel', function (opt) {
    var delta = opt.e.deltaY;
    var pointer = canvas.getPointer(opt.e);
    var zoom = canvas.getZoom();
    zoom = zoom + delta / 200;
    if (zoom > 20) zoom = 20;
    if (zoom < 0.01) zoom = 0.01;
    canvas.zoomToPoint({x: opt.e.offsetX, y: opt.e.offsetY}, zoom);
    opt.e.preventDefault();
    opt.e.stopPropagation();
});


function drawDrones() {
    while (canvas._objects.length - 1 < curr_telemetry.length) {
        let circ = new fabric.Circle({
            radius: 20, fill: 'green', left: 100, top: 100
        });
        canvas.add(circ);
    }
    while (canvas._objects.length - 1 > curr_telemetry.length) {
        canvas._objects.pop();
    }
    for (let i = 0; i < curr_telemetry.length; i++) {
        canvas._objects[i + 1].fill = curr_telemetry[i].led;
        canvas._objects[i + 1].left = curr_telemetry[i].pose.x;
        canvas._objects[i + 1].top = curr_telemetry[i].pose.y;
    }
    canvas.renderAll();
}