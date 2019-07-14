var choses = [];

function next(i) {
    if (choses.length < 2) {
        document.getElementById(i.toString() + 'el').style.backgroundColor = '#cbcbcb';
        document.getElementById(i.toString() + 'el').onclick = function () {
        };
        document.getElementById('name').innerHTML = "Выберите точку прибытия";
        choses.push(i);
    }
    if (choses.length === 2) {
        document.getElementById('butt').onclick = work;
    }
}

function work() {
    let req = new XMLHttpRequest();
    req.open('GET', '/get_dist?o=' + choses[0].toString() + '&t=' + choses[1].toString(), false);
    req.send(null);
    if (req.status === 200) {
        let resp = JSON.parse(req.responseText);
        console.log(resp);
        document.getElementById('butt').style.backgroundColor = '#aba72d';
        document.getElementById('text').innerHTML = 'Поехали? ' + (Math.round(resp.dist * 100) / 100).toString() + ' м, ' + (Math.round(resp.cost * 100) / 100).toString() + ' ₽';
    }
    document.getElementById('butt').onclick = function () {
        let req = new XMLHttpRequest();
        req.open('GET', '/ask_taxi?o=' + choses[0].toString() + '&t=' + choses[1].toString(), false);
        req.send(null);
        if (req.status === 200) {
            let resp = JSON.parse(req.responseText);
            if (resp.m === 'busy') {
                document.getElementById('butt').style.backgroundColor = '#94322e';
                document.getElementById('butt').onclick = function () {

                };
                document.getElementById('text').innerHTML = 'Всё занято, попробуйте позже(';
            } else {
                document.getElementById('butt').onclick = function () {

                };
                document.getElementById('text').innerHTML = 'Летим!';
                document.getElementById('butt').style.backgroundColor = resp.color;
            }
        }
    }
}
