from datetime import datetime


class MyTime:
    def __init__(self):
        self.hour = "0"
        self.min = "0"
        self.sec = "0"
        self.msec = "0"

    def update_with_package(self, time):
        self.hour = str(time["saat"])
        self.min = str(time["dakika"])
        self.sec = str(time["saniye"])
        self.msec = str(time["milisaniye"])

    def update_without_package(self):
        self.hour = datetime.now().strftime("%H")
        self.min = datetime.now().strftime("%M")
        self.sec = datetime.now().strftime("%S")
        self.msec = str(int(int(datetime.now().strftime("%f")) / 1000))
