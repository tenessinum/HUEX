from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import random


def main(request):
    data = dict()
    return render(request, "main.html", data)


@csrf_exempt
def post_telemetry(request):
    r = lambda: random.randint(0, 255)
    print(request.POST)

    new_telem = {
        "command": "land",  # "navigate", "land", "take_off"
        "led": '#%02X%02X%02X' % (r(), r(), r()),
        "x": 0,
        "y": 0,
        "z": 2,
        "yaw": 0
    }
    return JsonResponse(new_telem)


def get_info(request):
    data = dict()

    data["message"] = "OK"
    data["drones"] = []

    data["drones"].append(random_drone())
    data["drones"].append(random_drone())
    data["drones"].append(random_drone())
    data["drones"].append(random_drone())
    data["drones"].append(random_drone())

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
    return JsonResponse({"m": "ok"})
