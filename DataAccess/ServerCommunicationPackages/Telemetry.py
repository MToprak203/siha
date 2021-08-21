class Telemetry:
    def __init__(self, my_uav, target, gps_time):
        self.content = {
            "takim_numarasi": my_uav.team_no,
            "IHA_enlem": my_uav.latitude,
            "IHA_boylam": my_uav.longitude,
            "IHA_irtifa": my_uav.altitude,
            "IHA_dikilme": my_uav.standing_up,
            "IHA_yonelme": my_uav.orientation,
            "IHA_yatis": my_uav.hospitalization,
            "IHA_hiz": my_uav.speed,
            "IHA_batarya": my_uav.battery,
            "IHA_otonom": my_uav.autonomous,
            "IHA_kilitlenme": my_uav.locking,
            "Hedef_merkez_X": (target[0] + target[2]) / 2,
            "Hedef_merkez_Y": (target[1] + target[3]) / 2,
            "Hedef_genislik": target[2],
            "Hedef_yukseklik": target[3],
            "GPSSaati": {
                "saat": gps_time.hour,
                "dakika": gps_time.min,
                "saniye": gps_time.sec,
                "milisaniye": gps_time.msec
            }
        }