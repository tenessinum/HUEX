var canvas = new fabric.Canvas('c');
canvas.uniScaleKey = "null";

window.addEventListener('resize', resizeCanvas, false);

function resizeCanvas() {
    var style = window.getComputedStyle(document.getElementById("lf"), null);
    canvas.setHeight(parseInt(style.getPropertyValue("height")));
    canvas.setWidth(parseInt(style.getPropertyValue("width")));
    canvas.renderAll();
}

resizeCanvas();


canvas.add(new fabric.Circle({ radius: 30, fill: '#f55', top: 100, left: 100 }));
canvas.backgroundColor = 'rgba(0,0,255,0.3)';
canvas.renderAll();
