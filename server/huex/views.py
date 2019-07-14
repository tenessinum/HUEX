from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from huex.copter import Clever
import random
from json import load, dump
from huex.graphs import build_path, renew, printttt
import logging

allowed_ips = ['127.0.0.1', '192.168.1.206', '192.168.1.123', '192.168.1.168', '192.168.1.165']

logging.disable(logging.CRITICAL)

copters = []


def main(request):
    data = dict()
    if get_client_ip(request) in allowed_ips:
        return render(request, "main.html", data)
    else:
        return redirect('https://github.com/Tennessium/HUEX')


def guest_page(request):
    return render(request, 'chpage.html', dict())


def mobile(request):
    data = dict()
    with open('static/roads.json', 'r') as f:
        file = load(f)
        data['array'] = [i for i in range(0, len(file['points']))]
    return render(request, "mobile.html", data)


def delete(request):
    copters.pop(int(request.GET.dict()["id"]))
    return JsonResponse({})


@csrf_exempt
def post_telemetry(request):
    ip = get_client_ip(request)

    if not get_client_ip(request) in [i.ip for i in copters]:
        copters.append(Clever(ip))

    for i in copters:
        if i.ip == ip:
            i.x = float(request.GET.get("x"))
            i.y = float(request.GET.get("y"))
            i.z = float(request.GET.get("z"))
            # i.yaw = float(request.GET.get("yaw"))
            if str(float(request.GET.get("cell_voltage"))) == 'nan':
                i.voltage = 0
            else:
                i.voltage = float(request.GET.get("cell_voltage"))
            return JsonResponse(i.toNewTelem(copters))


def get_info(request):
    data = dict()

    data["message"] = "OK"
    data["drones"] = []

    for i in range(0, len(copters)):
        data["drones"].append(copters[i].toTelem())

    return JsonResponse(data)


def random_drone():
    r = lambda: random.randint(0, 255)
    return {
        "led": '#%02X%02X%02X' % (r(), r(), r()),
        "status": ["landed", "flight"][random.randint(0, 1)],
        "pose": {
            "x": random.randint(40, 2500), "y": random.randint(40, 2500), "z": random.randint(40, 2500), "yaw": 3.141592
        },
        "next": {
            "x": random.randint(40, 2500), "y": random.randint(40, 2500), "z": random.randint(40, 2500), "yaw": 3.141592
        },
    }


def send_command(request):
    data = request.GET.dict()
    if data['command'] == 'build_path':
        try:
            if not copters[int(data["id"])].path:
                path = build_path(str(data['o']) + '0', str(data['t']) + '0')
                copters[int(data["id"])].path += path
                print('Copter\'s path is now', copters[int(data["id"])].path)
            else:
                print("Error while building path")
                return JsonResponse({'m': 'busy'})
        except:
            print('There is no available path')
            return JsonResponse({"m": "no way"})
    elif data['command'] == 'force_land':
        copters[int(data["id"])].force_landed = True

    # printttt()
    return JsonResponse({"m": "ok"})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_field(request):
    data = request.GET.dict()
    with open('static/roads.json', 'r') as f:
        file_data = load(f)

    if data['m'] == 'add':
        if data['c'] == 'point':
            file_data['points'].append({
                "x": float(data['x']),
                "y": float(data['y'])
            })
        elif data['c'] == 'line':
            if not {'1': int(data['o']), '2': int(data['t'])} in file_data['lines'] and data['o'] != data['t']:
                file_data['lines'].append({
                    '1': int(data['o']),
                    '2': int(data['t'])
                })
    elif data['m'] == 'remove':
        if data['c'] == 'point':
            if int(data['n']) != -1:
                file_data['points'].pop(int(data['n']))
                i = 0
                while i < len(file_data["lines"]):
                    if file_data["lines"][i]["1"] == int(data["n"]) or file_data["lines"][i]["2"] == int(data["n"]):
                        file_data["lines"].pop(i)
                    else:
                        i += 1
                for i in range(0, len(file_data['lines'])):
                    if file_data['lines'][i]['1'] > int(data['n']):
                        file_data['lines'][i]['1'] -= 1
                    if file_data['lines'][i]['2'] > int(data['n']):
                        file_data['lines'][i]['2'] -= 1
        elif data['c'] == 'line':
            for i in range(0, len(file_data['lines'])):
                if file_data['lines'][i] == {'1': int(data['o']), '2': int(data['t'])} or file_data['lines'][i] == {
                    '1': int(data['t']), '2': int(data['o'])}:
                    file_data['lines'].pop(i)
                    break

    with open('static/roads.json', 'w') as f:
        dump(file_data, f)
    renew()
    return JsonResponse({})


def set_color(request):
    data = request.GET.dict()
    copters[int(data['id'])].led = '#' + data['color']
    return JsonResponse({})


def get_dist(request):
    data = request.GET.dict()
    path = build_path(str(data['o']) + '0', str(data['t']) + '0')
    dist = calc_path(path)
    cost = 150 + dist * 30
    return JsonResponse({'dist': dist, 'cost': cost})


def get_distance(x1, y1, z1, x2, y2, z2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


def calc_path(path):
    dist = 0
    with open('static/roads.json', 'r') as f:
        data = load(f)
    for i in range(0, len(path[:-1])):
        p1 = {
            'x': data['points'][int(path[i][:-1])]['x'],
            'y': data['points'][int(path[i][:-1])]['y'],
        }
        if path[i][-1] == 0:
            p1['z'] = 1.5
        else:
            p1['z'] = 2.5
        p2 = {
            'x': data['points'][int(path[i + 1][:-1])]['x'],
            'y': data['points'][int(path[i + 1][:-1])]['y'],
        }
        if path[i + 1][-1] == 0:
            p2['z'] = 1.5
        else:
            p2['z'] = 2.5
        dist += get_distance(p1['x'], p1['y'], p1['z'], p2['x'], p2['y'], p2['z'])
    return dist


def ask_taxi(request):
    data = request.GET.dict()
    busy = 0
    points = []
    for i in copters:
        if i.path != []:
            busy += 1
            points.append(-1)
        else:
            points.append(get_nearest_point(i))

    if busy == len(copters):
        return JsonResponse({'m': 'busy'})

    paths = []
    for i in range(0, len(points)):
        if points[i] != -1:
            paths.append(calc_path(build_path(str(points[i]) + '0', str(data['o']) + '0')))
        else:
            paths.append(9999999)

    print(paths, min(paths))
    nearest_copter = copters[paths.index(min(paths))]
    nearest_copter.path += build_path(str(get_nearest_point(nearest_copter)) + '0', str(data['o']) + '0')
    nearest_copter.path.append('-1')
    nearest_copter.path += build_path(str(data['o']) + '0', str(data['t']) + '0')
    r = lambda: random.randint(0, 255)
    nearest_copter.led = '#%02X%02X%02X' % (r(), r(), r())

    return JsonResponse({'m': 'ok', 'color': nearest_copter.led})


def get_nearest_point(c):
    index = 0
    min_dist = 9999999
    with open('static/roads.json', 'r') as f:
        data = load(f)
    for i in range(0, len(data['points'])):
        dist = get_distance(c.x, c.y, 0, data['points'][i]['x'], data['points'][i]['y'], 0)
        if min_dist > dist:
            index = i
            min_dist = dist
    return index
