var map;
var fr = -1;
var to = -1;

function addPoints() {
    var availCollection = new ymaps.GeoObjectCollection(null, {
        preset: 'islands#greenIcon'
    });
    var naCollection = new ymaps.GeoObjectCollection(null, {
        preset: 'islands#redIcon'
    });
    for (var i = 0, l = coords.length; i < l; i++) {
        if (i !== fr && i !== to) {
            availCollection.add(new ymaps.Placemark(coords[i], {iconContent: i}));
        } else {
            naCollection.add(new ymaps.Placemark(coords[i], {iconContent: i}));
        }
    }
    availCollection.events.add('click', function (e) {
        mapSel(e.get('target').properties.get('iconContent'))
    });

    map.geoObjects.add(availCollection);
    map.geoObjects.add(naCollection);
}

function finalPanel() {
    document.getElementById("finalFrom").value = fr.toString();
    M.updateTextFields();

    document.getElementById("finalTo").value = to.toString();
    M.updateTextFields();

    document.getElementById("progress").style.display = '';
    document.getElementById("flightInfo").style.display = 'none';

    var instance = M.Modal.getInstance(document.getElementById('final'));
    instance.open();


    fetch('/get_dist?o=' + fr.toString() + '&t=' + to.toString())
        .then(
            function (response) {
                if (response.status === 200) {
                    response.json().then(function (resp) {
                        console.log(resp);
                        document.getElementById('dist').innerHTML = (Math.round(resp.dist * 100) / 100).toString() + ' м';
                        document.getElementById('cost').innerHTML = (Math.round(resp.cost * 100) / 100).toString() + ' ₽';
                        document.getElementById("progress").style.display = 'none';
                        document.getElementById("flightInfo").style.display = '';
                    });
                }
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function mapSel(point) {
    if (fr !== -1) toSel(false, point);
    else fromSel(false, point)
}

function fromSel(button, point) {

    fr = point;

    if (to === -1) {
        document.getElementById("askTo").style.display = '';
        document.getElementById("askFrom").style.display = 'none';
        document.getElementById("to" + point.toString()).style.display = 'none';
    } else {
        document.getElementById("askTo").style.display = 'none';
        document.getElementById("askFrom").style.display = 'none';
        finalPanel()
    }

    map.geoObjects.removeAll();
    addPoints();

    return false;
}

function toSel(button, point) {
    document.getElementById("askTo").style.display = 'none';
    to = point;
    console.log(fr, to);

    map.geoObjects.removeAll();
    addPoints();

    finalPanel();

    return false
}


function fromChange() {
    fr = -1;
    map.geoObjects.removeAll();
    addPoints();

    var instance = M.Modal.getInstance(document.getElementById('final'));
    instance.close();

    document.getElementById("askTo").style.display = 'none';
    document.getElementById("askFrom").style.display = '';

    for (var i = 0, l = coords.length; i < l; i++) {
        document.getElementById("from" + i.toString()).style.display = '';
    }
    document.getElementById("from" + to.toString()).style.display = 'none';
}

function toChange() {
    to = -1;
    map.geoObjects.removeAll();
    addPoints();

    var instance = M.Modal.getInstance(document.getElementById('final'));
    instance.close();

    document.getElementById("askTo").style.display = '';
    document.getElementById("askFrom").style.display = 'none';

    for (var i = 0, l = coords.length; i < l; i++) {
        document.getElementById("to" + i.toString()).style.display = '';
    }
    document.getElementById("to" + fr.toString()).style.display = 'none';
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function order() {
    document.getElementById('end').style.display = '';
    fetch('/ask_taxi?o=' + fr.toString() + '&t=' + to.toString())
        .then(
            function (response) {
                if (response.status === 200) {
                    response.json().then(function (resp) {
                        console.log(resp);
                        if (resp.m === 'busy') {
                            var color = hexToRgb('#ff0000');
                            var gray = (color.r + color.g + color.b + 1) / 3;
                            if (gray > 127) document.getElementById('loaderText').style.color = '#000000';
                            else document.getElementById('loaderText').style.color = '#FFFFFF';

                            document.getElementById('end').style.backgroundColor = '#ff0000';
                            document.getElementById('loader').style.display = 'none';
                            document.getElementById('loaderText').innerHTML = 'Всё занято, попробуйте позже :(';
                            document.getElementById('loaderText').style.display = '';

                            setTimeout(function () {
                                window.location.reload(false)
                            }, 1000)
                        } else if (resp.m === 'wrong') {
                            var color = hexToRgb('#ff0000');
                            var gray = (color.r + color.g + color.b + 1) / 3;
                            if (gray > 127) document.getElementById('loaderText').style.color = '#000000';
                            else document.getElementById('loaderText').style.color = '#FFFFFF';

                            document.getElementById('end').style.backgroundColor = '#ff0000';
                            document.getElementById('loader').style.display = 'none';
                            document.getElementById('loaderText').innerHTML = 'Полеты в данную точку временно ограничены';
                            document.getElementById('loaderText').style.display = '';

                            setTimeout(function () {
                                window.location.reload(false)
                            }, 1000)
                        } else {
                            var color = hexToRgb(resp.color);
                            var gray = (color.r + color.g + color.b + 1) / 3;
                            if (gray > 127) document.getElementById('loaderText').style.color = '#000000';
                            else document.getElementById('loaderText').style.color = '#FFFFFF';

                            document.getElementById('end').style.backgroundColor = resp.color;
                            document.getElementById('loader').style.display = 'none';
                            document.getElementById('loaderText').innerHTML = 'Летим!';
                            document.getElementById('loaderText').style.display = '';

                            setTimeout(check, 1000, resp.ip)
                        }
                    });
                }
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}

function check(ip) {
    fetch('/ip_status?ip=' + ip.toString())
        .then(
            function (response) {
                if (response.status === 200) {
                    response.json().then(function (resp) {
                        console.log(resp);
                        if (resp.status === 'wrong') {
                            alert('Хрен тебе )')
                        } else {
                            if (resp.status === 'flight_to_dest')
                                document.getElementById('loaderText').innerHTML = "Летим к месту прибытия";
                            else if (resp.status === 'landed') {
                                document.getElementById('loaderText').innerHTML = "Полет завершен. Спасибо за заказ!";
                                setTimeout(function () {
                                    window.location.reload(false)
                                }, 1000);
                                return;
                            } else if (resp.status === 'flight_to_human')
                                document.getElementById('loaderText').innerHTML = "Летим к месту отправления";
                            else if (resp.status === 'human_wait')
                                document.getElementById('loaderText').innerHTML = "Ожидаем человека в месте отправления";
                            setTimeout(check, 500, ip)
                        }
                    });
                }
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });

}


ymaps.ready(function () {

    var LAYER_NAME = 'user#layer',
        MAP_TYPE_NAME = 'user#customMap',
        // Директория с тайлами.
        TILES_PATH = 'https://sandbox.api.maps.yandex.net/examples/ru/2.1/custom_map/images/tiles',
        /* Для того чтобы вычислить координаты левого нижнего и правого верхнего углов прямоугольной координатной
         * области, нам необходимо знать максимальный зум, ширину и высоту изображения в пикселях на максимальном зуме.
         */
        MAX_ZOOM = 5,
        PIC_WIDTH = 10,
        PIC_HEIGHT = 10;

    /**
     * Конструктор, создающий собственный слой.
     */
    var Layer = function () {
        var layer = new ymaps.Layer('', {
            // Если есть необходимость показать собственное изображение в местах неподгрузившихся тайлов,
            // раскомментируйте эту строчку и укажите ссылку на изображение.
            notFoundTile: '/static/map.jpg'
        });
        // Указываем доступный диапазон масштабов для данного слоя.
        layer.getZoomRange = function () {
            return ymaps.vow.resolve([0, 20]);
        };
        // Добавляем свои копирайты.
        layer.getCopyrights = function () {
            return ymaps.vow.resolve('© Human Express');
        };
        return layer;
    };
    // Добавляем в хранилище слоев свой конструктор.
    ymaps.layer.storage.add(LAYER_NAME, Layer);

    /**
     * Создадим новый тип карты.
     * MAP_TYPE_NAME - имя нового типа.
     * LAYER_NAME - ключ в хранилище слоев или функция конструктор.
     */
    var mapType = new ymaps.MapType(MAP_TYPE_NAME, [LAYER_NAME]);
    // Сохраняем тип в хранилище типов.
    ymaps.mapType.storage.add(MAP_TYPE_NAME, mapType);

    // Вычисляем размер всех тайлов на максимальном зуме.
    var worldSize = Math.pow(2, MAX_ZOOM) * 256;
    /**
     * Создаем карту, указав свой новый тип карты.
     */
    map = new ymaps.Map('map', {
        center: [2.5, 1.5],
        zoom: 11,
        controls: [/*'zoomControl'*/],
        type: MAP_TYPE_NAME
    }, {

        // Задаем в качестве проекции Декартову. При данном расчёте центр изображения будет лежать в координатах [0, 0].
        projection: new ymaps.projection.Cartesian([[PIC_HEIGHT / 2 - worldSize, -PIC_WIDTH / 2], [PIC_HEIGHT / 2, worldSize - PIC_WIDTH / 2]], [false, false]),
        // Устанавливаем область просмотра карты так, чтобы пользователь не смог выйти за пределы изображения.
        //restrictMapArea: [[-PIC_HEIGHT / 2, -PIC_WIDTH / 2], [PIC_HEIGHT / 2, PIC_WIDTH / 2]]

        // При данном расчёте, в координатах [0, 0] будет находиться левый нижний угол изображения,
        // правый верхний будет находиться в координатах [PIC_HEIGHT, PIC_WIDTH].
        // projection: new ymaps.projection.Cartesian([[PIC_HEIGHT - worldSize, 0], [PIC_HEIGHT, worldSize]], [false, false]),
        // restrictMapArea: [[0, 0], [PIC_HEIGHT, PIC_WIDTH]]
    });


    addPoints()
});
