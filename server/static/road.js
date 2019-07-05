function add_object(type) {
    canvas.backgroundColor = "#bdbdbd";
    for (let i = 0; i < canvas._objects.length; i++) {
        canvas._objects[i].set('opacity', 0.8);
    }
    canvas.renderAll();
    if (type === 'point') {
        adding_point = true;
        adding_line = false;
        remove_point = false;
        remove_line = false;
        choosing = false;
    } else {
        adding_point = false;
        adding_line = true;
        remove_point = false;
        remove_line = false;
        choosing = false;
    }
}

function remove_object(type) {
    canvas.backgroundColor = "#bdbdbd";
    for (let i = 0; i < canvas._objects.length; i++) {
        canvas._objects[i].set('opacity', 0.8);
    }
    canvas.renderAll();
    if (type === 'point') {
        adding_point = false;
        adding_line = false;
        remove_point = true;
        remove_line = false;
        choosing = false;
    } else {
        adding_point = false;
        adding_line = false;
        remove_point = false;
        remove_line = true;
        choosing = false;
    }
}
