import math
from DataAccess.TargetUAV import TargetUAV as TargetUAV


# target_data = 1 target'ın telemetry bilgileri
# Telemetry ile gönderilen her rakip ihanın verisini tutan bir listedir.

class TargetList:
    def __init__(self):
        self.target_dict = {}  # {target_id, target} şeklinde targetları tutar.
        self.targets = []  # Targetların costlarına göre azdan çoğa sıralı targetlar listesi

    def add_target(self, target_data, MyUAV):
        if self.target_dict.keys().__contains__(target_data["takim_numarasi"]):
            print("The target is in the list already!")
            return self.targets

        cost, relative_dist, relative_mov, suit = evaluate_target(target_data, MyUAV)
        new_target = TargetUAV(target_data, suit, relative_mov, relative_dist, cost)

        self.target_dict[target_data["takim_numarasi"]] = new_target
        self.targets.append(new_target)

    def update_list(self, all_targets_data, MyUAV):
        for target_data in all_targets_data:
            if target_data["takim_numarasi"] not in self.target_dict.keys():
                self.add_target(target_data, MyUAV)
                continue

            temp = self.target_dict[target_data["takim_numarasi"]]
            cost, relative_dist, relative_mov, suit = evaluate_target(target_data, MyUAV)
            temp.update(target_data, suit, relative_mov, relative_dist, cost)

        self.sort_targets()

    def sort_targets(self):
        n = len(self.targets)
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if self.targets[j].cost > self.targets[j + 1].cost:
                    self.targets[j], self.targets[j + 1] = self.targets[j + 1], self.targets[j]


def evaluate_target(target_data, MyUAV):
    cost, relative_dist = cost_calculate(target_data, MyUAV)
    relative_mov = relative_movement(target_data, MyUAV)
    suit = suitability(target_data, MyUAV)
    return cost, relative_dist, relative_mov, suit


# cost = MyUAV ve target arasındaki mesafe + dönüş için gerekli yönelme miktarı + irtifa farkı
def cost_calculate(target_data, MyUAV):
    """distance_cost = math.sqrt((target_data["iha_enlem"] - MyUAV.latitude) ** 2
                              + (target_data["iha_enlem"] - MyUAV.longitude) ** 2
                              + (target_data["iha_boylam"] - MyUAV.altitude) ** 2)
    return distance_cost + abs((target_data["iha_yonelme"] - MyUAV.orientation) % 180)
                         + abs(MyUAV.altitude - target_data["iha_irtifa"]), distance_cost
"""
    xy_distance_cost = math.sqrt(
        (target_data["iha_enlem"] - MyUAV.latitude) ** 2 + (target_data["iha_boylam"] - MyUAV.longitude) ** 2)
    total_cost = xy_distance_cost + degree_difference(target_data, MyUAV) + abs(
        MyUAV.altitude - target_data["iha_irtifa"])
    return total_cost, xy_distance_cost


# MyUAV'nin konumuna göre target'ın konum farkı
def relative_movement(target_data, MyUAV):
    rx = target_data["iha_enlem"] - MyUAV.latitude
    ry = target_data["iha_boylam"] - MyUAV.longitude
    rz = target_data["iha_irtifa"] - MyUAV.altitude
    ryonelim = relative_degree_difference(target_data, MyUAV)
    return [rx, ry, rz, ryonelim]


# Eğer target MyUAV'nin (180° derece) önündeyse uygun (True) değilse, arkasındaysa uygun değil (False)
def suitability(target_data, MyUAV):
    if MyUAV.orientation == 0:
        if target_data["iha_enlem"] > MyUAV.latitude:
            return True
        return False

    if MyUAV.orientation == 180:
        if target_data["iha_enlem"] < MyUAV.latitude:
            return True
        return False

    if MyUAV.orientation == 90:
        if target_data["iha_boylam"] > MyUAV.longitude:
            return True
        return False

    if MyUAV.orientation == 270:
        if target_data["iha_boylam"] < MyUAV.longitude:
            return True
        return False

    radiant_siha = math.radians(MyUAV.orientation)
    cos = math.cos(radiant_siha)

    slope = MyUAV.orientation + 90
    radiant_slope = math.radians(slope)
    tan = round(math.tan(radiant_slope), 2)

    t_value = tan * (target_data["iha_enlem"] - MyUAV.latitude) - (target_data["iha_boylam"] - MyUAV.longitude)

    if tan > 0:
        if cos > 0:
            if t_value > 0:
                return True
            return False
        if t_value < 0:
            return True
        return False
    if cos < 0:
        if t_value > 0:
            return True
        return False
    if t_value < 0:
        return True
    return False


def degree_difference(target_data, MyUAV):
    if target_data["iha_yonelme"] > MyUAV.orientation:
        return target_data["iha_yonelme"] - MyUAV.orientation
    return MyUAV.orientation - target_data["iha_yonelme"]


def relative_degree_difference(target_data, MyUAV):
    diff = target_data["iha_yonelme"] - MyUAV.orientation
    if diff > 180:
        return diff - 180
    if diff < -180:
        return diff + 180
    return diff
