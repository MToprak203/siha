class MyUAV:
    def __init__(self):
        self.team_no = 1
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.standing_up = 0
        self.orientation = 0
        self.hospitalization = 0
        self.speed = 0
        self.battery = 0
        self.autonomous = 0
        self.locking = False

    def update(self, values):
        self.latitude = values["latitude"]
        self.longitude = values["longitude"]
        self.altitude = values["altitude"]
        self.standing_up = values["standing_up"]
        self.orientation = values["orientation"]
        self.hospitalization = values["hospitalization"]
        self.speed = values["speed"]
        self.battery = values["battery"]
        self.autonomous = values["autonomous"]
        self.locking = values["locking"]

    def set_team_no(self, team_no):
        self.team_no = team_no

