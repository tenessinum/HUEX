from django.shortcuts import render
from django.http import JsonResponse


def main(request):
    data = dict()
    return render(request, "main.html", data)


def get_info(request):
    data = dict()

    data["message"] = "OK"
    data["drones"] = \
        [
            {
                "led": "#FF00FF",
                "status": "landed",
                "pose": {
                    "x": 10, "y": 20, "z": 30
                },
                "next": {
                    "x": 20, "y": 15, "z": 20
                }
            }
        ] * 5

    return JsonResponse(data)
