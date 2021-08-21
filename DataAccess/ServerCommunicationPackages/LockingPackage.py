class LockingPackage:
    def __init__(self, locking_data):
        self.content = {
            "kilitlenmeBaslangicZamani": {
                "saat": locking_data.locking_begin_time.hour,
                "dakika": locking_data.locking_begin_time.min,
                "saniye": locking_data.locking_begin_time.sec,
                "milisaniye": locking_data.locking_begin_time.msec
            },
            "kilitlenmeBitisZamani": {
                "saat": locking_data.locking_end_time.hour,
                "dakika": locking_data.locking_end_time.min,
                "saniye": locking_data.locking_end_time.sec,
                "milisaniye": locking_data.locking_end_time.msec
            },
            "otonom_kilitlenme": locking_data.autonomous
        }