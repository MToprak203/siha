from dronekit import connect, VehicleMode
from MyUAVImageProcessor import process_result_package as img_result
import time

movement_result = {
    "msg": "",
    "movement_msg": ""
}

# Kamera hedefin x ekseninde uzaklaşıp yakınlaşmasını ne kadar miktarda alan değişimi olduğuna bakarak hesaplıyor.
# 'img_result' un 'target_movement_x_value' key'i ile bu değere ulaşılabilir.
# Uygun oranın denenip bulunması gerekiyor. Alan hesabı olduğu için küçük oranlar olması daha iyi olur gibi.

speedup_ratio = 1.0 / 1000

# speedup'ta olduğu gibi sağ-sol, yukarı-aşağı dönüşlerde de bir oran belirlenmesi gerekiyor.

yaw_ratio = 1.0 / 100  # sağ-sol dönme oranı
pitch_ratio = 1.0 / 100  # yukarı-aşağı dönme oranı

target_takeoff_altitude = 20


def movement_msg(speedup_value, yaw_value, pitch_value):
    msg = "-- Iha Movement: "
    x_msg = " x: "
    y_msg = " Y: "
    z_msg = " z: "

    if img_result["target_movement_x_msg"] == "no_difference":
        x_msg += "Going same speed"
    elif img_result["target_movement_x_msg"] == "moving_away":
        x_msg += "Speed Up"
    else:
        x_msg += "Slow Down"
    x_msg += f": {speedup_value}"

    if img_result["target_movement_y_msg"] == "0":
        y_msg += "Going Straight"
    elif img_result["target_movement_y_msg"] == "-y":
        y_msg += "Turning Left"
    else:
        y_msg += "Turning Right"
    y_msg += f": {yaw_value}"

    if img_result["target_movement_z_msg"] == "0":
        z_msg += "Going Straight"
    elif img_result["target_movement_z_msg"] == "-z":
        z_msg += "Down"
    else:
        z_msg += "Up"
    z_msg += f": {pitch_value}"

    msg += x_msg + " " + y_msg + " " + z_msg + " --"

    movement_result["movement_msg"] = msg


class MyUAVMovementProcessor:
    def __init__(self, conn_string=None):
        # -- Bağlantı olduğuna 'self.iha' nın kullanılması gerekiyor. --

        #self.iha = connect(conn_string, wait_ready=True)
        pass

    def arm_and_takeoff(self):

        movement_result["msg"] = "Basic pre-arm checks"

        while not self.iha.is_armable:
            movement_result["msg"] = "Waiting for vehicle to initialise..."
            time.sleep(1)

        movement_result["msg"] = "Arming motors"
        self.iha.mode = VehicleMode("AUTO")  # Plane olduğu için AUTO sanırım.
        self.iha.armed = True

        while not self.iha.armed:
            movement_result["msg"] = "Waiting for arming..."
            time.sleep(1)

        movement_result["msg"] = "Taking off!"
        self.iha.simple_takeoff(target_takeoff_altitude)

        while True:
            movement_result["msg"] = f"Altitude: {self.iha.location.global_relative_frame.alt}"

            if self.iha.location.global_relative_frame.alt >= target_takeoff_altitude * 0.95:
                movement_result["msg"] = "Reached target altitude"
                break
            time.sleep(1)

    def track_target_locking(self):
        # 'img_result' tan gelen bilgilerle ihanın kendi xyz eksenlerine göre yapacağı harekete göre hedefi takip etmesini
        # sağlayan fonksiyon.
        if img_result["available_object"] and img_result["target_proper_to_track"]:
            speedup_value = img_result["target_movement_x_value"] * speedup_ratio
            yaw_value = img_result["target_movement_y_value"] * yaw_ratio
            pitch_value = img_result["target_movement_z_value"] * pitch_ratio

            # -- Test amaçlı böyle. 'self.iha' açıldığında buraların da açılması gerekiyor. --
            #self.iha.gimbal.rotate(pitch_value, 0, yaw_value)
            #self.iha.airspeed = speedup_value
            movement_msg(speedup_value, yaw_value, pitch_value)

    def track_target_telemetry(self):
        pass