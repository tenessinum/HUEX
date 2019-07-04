from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from huex.copter import Clever
import random

'''
copters = [Clever('0.0.0.0'), Clever('0.0.0.1'), Clever('0.0.0.2')]
for i in copters:
    i.random()
'''

copters = [Clever('0.0.0.0'), Clever('0.0.0.1'), Clever('0.0.0.2')]


def main(request):
    data = dict()
    return render(request, "main.html", data)


def delete(request):
    copters.pop(int(request.GET.dict()["id"]))
    return JsonResponse({})


@csrf_exempt
def post_telemetry(request):
    r = lambda: random.randint(0, 255)

    if not get_client_ip(request) in [i.ip for i in copters]:
        copters.append(Clever(get_client_ip(request)))

    '''new_telem = {
        "command": "land", # "navigate", "land", "take_off"
        "led": '#%02X%02X%02X' % (r(), r(), r()),
        "x": 0,
        "y": 0,
        "z": 2,
        "yaw": 0
    }'''

    for i in copters:
        if i.ip == get_client_ip(request):
            i.x = float(request.POST.get("x"))
            i.y = float(request.POST.get("y"))
            i.z = float(request.POST.get("z"))
            i.yaw = float(request.POST.get("yaw"))
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
