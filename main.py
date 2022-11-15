import socket
from joblib import load
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import pandas as pd
from geopy.geocoders import Nominatim
from geopy import distance
import serial
from geographiclib.geodesic import Geodesic

subs = 'RESET'
arduReset = '#'
host = '192.168.18.229'
port = 9999
s = socket.socket()

print('Waiting for connection..')
try:
    s.connect((host, port))
except socket.error as e:
    print(str(e))

print('Connected!')

arduino = serial.Serial("COM3", 9600)

while True:
    msg = s.recv(1024).decode()
    while len(msg) > 10:
        msg2 =s.recv(1024).decode()
        if msg2 != msg:
            print("message1= ", msg)
            print("message2= ",msg2)
            data = msg2.split()
            print(data)
            lat = data[0]
            lng = data[1]

            lat = float(lat)
            lng = float(lng)
            geocoder = Nominatim(user_agent="i know python")
            place1 = (-6.934232845510125, 107.62352571325448)
            place2 = (lat, lng)
            jarak = distance.distance(place1, place2).m * 170
            isian = 5

            brng = Geodesic.WGS84.Inverse(-6.934232845510125, 107.62352571325448, lat, lng)['azi1']
            print(brng)
            brng = brng + 90
            brng = round(brng)
            if brng < 40:
                brng = 40
            elif brng > 140:
                brng = 140
            
            # fitting scaler using pandas
            filepath = "tabel_tembak.csv"
            data_tembak = pd.read_csv(filepath)
            data_tembak_sudut = data_tembak.drop(['tipe', 'waktu_lintas_det', 'sudut_elevasi_der', 'sudut_elevasi_rad'], axis=1)
            data_tembak_sudut["jarak_km"] = data_tembak_sudut["jarak_m"] / 1000
            data_tembak_sudut["jarak_cm"] = data_tembak_sudut["jarak_m"] * 100
            scaler = StandardScaler()
            scaler.fit(data_tembak_sudut)

            # constant
            pi = 22 / 7
            t=np.arange(0,60,0.1)

            # load models
            model = load('model.pkl')

            # getting data from post
            isian = isian

            jarak_m = jarak
            jarak_km = 0
            jarak_cm = 0

            input_query = (isian, jarak_m, jarak_km, jarak_cm)

            # convert meter to km and cm
            input_list = list(input_query)
            converted_km = input_list[1] / 1000
            converted_cm = input_list[1] * 100
            input_list[2] = converted_km
            input_list[3] = converted_cm
            input_query = tuple(input_list)

            # convert to array and reshape
            input_data_as_numpy = np.asarray(input_query)
            input_data_reshaped = input_data_as_numpy.reshape(1, -1)

            # standardize data
            std_data = scaler.transform(input_data_reshaped)

            # predict
            result = model.predict(std_data)
            result = float(result)
            result = round(result)
            print(result, "derajat")
            print(brng, "azimuth")
            result = 90 - result

            # convert result(derajat) to radian
            radian = result * (pi / 180)
            radian_not_converted = radian
            radian = round(radian * 1000)

            result = "X{0:d}Y{1:d}".format((brng), (result))
            arduino.write(result.encode())
            print(jarak, "meter")
            # print(result, "derajat")
            break
        
        else:
            print('')