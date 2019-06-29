class WiFi:
    def __init__(self, SSID, password):
        self.SSID = SSID
        self.password = password

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_telemetry(self):
        request = self.post_telemetry()
        return self.exec(request)

    def post_telemetry(self):
        return object()

    def exec(self, request):
        command = request.text
        return command
