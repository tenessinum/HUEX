from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from huex.copter import Clever
import random
from json import load, dump

'''
copters = [Clever('0.0.0.0'), Clever('0.0.0.1'), Clever('0.0.0.2')]
for i in copters:
    i.random()
'''

copters = [Clever('0.0.0.0')]


def main(request):
    data = dict()
    return render(request, "main.html", data)


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
            i.yaw = float(request.GET.get("yaw"))
            i.voltage = float(request.GET.gat("cell_voltage"))
            return JsonResponse(i.toNewTelem())


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

    copters[int(data["id"])].addCommand(data)

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
                file_data["points"].pop(int(data['n']))
                i = 0
                while i < len(file_data["lines"]):
                    if file_data["lines"][i]["1"] == int(data["n"]) or file_data["lines"][i]["2"] == int(data["n"]):
                        print(file_data["lines"].pop(i))
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

    return JsonResponse({})
