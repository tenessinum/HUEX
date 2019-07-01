from django.shortcuts import render
from django.http import JsonResponse
import random


def main(request):
    data = dict()
    return render(request, "main.html", data)


def post_telemetry(request):
    return JsonResponse({"m": "ok"})


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
            "x": random.randint(40, 400), "y": random.randint(40, 400), "z": random.randint(40, 400)
        },
        "next": {
            "x": random.randint(40, 400), "y": random.randint(40, 400), "z": random.randint(40, 400)
        },
    }
