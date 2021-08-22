from communication import Server
import time

"""
    * Server class'ı yarisma sunucusuyla haberlesmek icin kullanılır.
    * Server class'ının testi icin kullanilabilir.
    * Ayri bir terminalde API ' nin baslatildigindan emin olun.
    
"""

if __name__ == "__main__":
    svr = Server("http://127.0.0.1:5000/")
    svr.log_in()
    while True:
        print("----------------------------------")
        server_time = svr.get_server_time()
        print("Sunucu Saati :",server_time)
        print("----------------------------------")
        svr.post_telemetry_data()
        print("----------------------------------")
        svr.post_locking_info()
        print("----------------------------------")
        print(svr.other_teams_info)
        print("----------------------------------")
        time.sleep(0.5)
    svr.log_out()