class TargetUAV:
    def __init__(self, target_data, suitable, r_mov, r_dist, cost):
        self.team_no = target_data["takim_numarasi"]
        self.latitude = target_data["iha_enlem"]
        self.longitude = target_data["iha_boylam"]
        self.altitude = target_data["iha_irtifa"]
        self.standing_up = target_data["iha_dikilme"]
        self.orientation = target_data["iha_yonelme"]
        self.hospitalization = target_data["iha_yatis"]
        self.delay = target_data["zaman_farki"]
        self.suitable = suitable
        self.relative_movement = r_mov
        self.relative_distance = r_dist
        self.cost = cost
        self.locking_available = False

    def update(self, target_data, suitable, r_mov, r_dist, cost):
        self.team_no = target_data["takim_numarasi"]
        self.latitude = target_data["iha_enlem"]
        self.longitude = target_data["iha_boylam"]
        self.altitude = target_data["iha_irtifa"]
        self.standing_up = target_data["iha_dikilme"]
        self.orientation = target_data["iha_yonelme"]
        self.hospitalization = target_data["iha_yatis"]
        self.delay = target_data["zaman_farki"]
        self.suitable = suitable
        self.relative_movement = r_mov
        self.relative_distance = r_dist
        self.cost = cost
