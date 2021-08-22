import json
from flask import Flask, request, jsonify
from datetime import datetime
import ast
import random

app = Flask(__name__)

aligable_users = {"dogukan": "1234",
                  "ESTU": "1234"}


@app.route('/api/sunucusaati', methods=['GET'])
def sunucu_saati():
    if (request.method == 'GET'):
        now = datetime.now()
        server_hour = "{\"saat\": %s,\"dakika\": %s,\"saniye\": %s,\"milisaniye\": %s}" % (
            now.hour, now.minute, now.second, int(now.microsecond / 1000))
        return server_hour
    else:
        return jsonify({"message": "Gecersiz Erisim"})


@app.route('/api/giris', methods=['POST'])
def giris():
    if (request.method == 'POST'):
        data = request.get_json(force=True)
        user = data['kadi']
        password = data['sifre']

        if user in aligable_users.keys():
            if password == aligable_users[user]:
                return jsonify({"message": "Giris Basarili ! "+f"<{user}>"}), 200
        return jsonify({"message": "401 Kimliksiz Erisim Denemesi"}), 400
    else:
        return jsonify({"message": "Gecersiz Erisim"})


@app.route('/api/cikis', methods=['GET'])
def cikis():
    if (request.method == 'GET'):
        return jsonify({"message": "Cikis yapildi !"})
    else:
        return jsonify({"message": "Gecersiz Erisim"})


@app.route('/api/telemetri_gonder', methods=['POST'])
def telemetri_gonder():
    if (request.method == 'POST'):
        data = request.get_json(force=True)
        print("#" * 50)
        print("Takim Bilgisi :", data, f"Zaman : {datetime.now()}", sep="\n")
        print("#" * 50)
        response = telemetry_data_response_generator()
        return response


@app.route('/api/kilitlenme_bilgisi', methods=['POST'])
def kilitlenme_bilgisi():
    if (request.method == 'POST'):
        data = request.get_json(force=True)
        print("#"*50)
        print("Kilitlenme Bilgisi :", data, f"Zaman : {datetime.now()}", sep="\n")
        print("#" * 50)
        return jsonify({"message": "Kilitlenme Bilgisi Alindi"})


def telemetry_data_response_generator():
    now = datetime.now()
    response = {"sistemSaati": {"saat": now.hour, "dakika": now.minute, "saniye": now.second,
                                "milisaniye": int(now.microsecond / 1000)},
                "konumBilgileri": [{
                    "iha_boylam": random.randint(0, 500),
                    "iha_dikilme": random.randint(0, 10),
                    "iha_enlem": random.randint(0, 500),
                    "iha_irtifa": random.randint(0, 500),
                    "iha_yatis": random.randint(-180, 180),
                    "iha_yonelme": random.randint(0, 360),
                    "takim_numarasi": random.randint(2, 10),
                    "zaman_farki": random.randint(0, 100)
                }, {
                    "iha_boylam": random.randint(0, 500),
                    "iha_dikilme": random.randint(0, 10),
                    "iha_enlem": random.randint(0, 500),
                    "iha_irtifa": random.randint(0, 500),
                    "iha_yatis": random.randint(-180, 180),
                    "iha_yonelme": random.randint(0, 360),
                    "takim_numarasi": random.randint(2, 10),
                    "zaman_farki": random.randint(0, 100)
                }, {
                    "iha_boylam": random.randint(0, 500),
                    "iha_dikilme": random.randint(0, 10),
                    "iha_enlem": random.randint(0, 500),
                    "iha_irtifa": random.randint(0, 500),
                    "iha_yatis": random.randint(-180, 180),
                    "iha_yonelme": random.randint(0, 360),
                    "takim_numarasi": random.randint(2, 10),
                    "zaman_farki": random.randint(0, 100)
                }, ]}
    return response



if __name__ == "__main__":
    app.run(debug=True)
