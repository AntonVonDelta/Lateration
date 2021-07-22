import serial
import matplotlib.pyplot as plt
from serial import Serial
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import struct
import pyaudio
import wave
import random
import time
import pickle
import sys
from sklearn.linear_model import LinearRegression

def cycleToDist(c,model):
    try:
        return model.predict(np.array([[c]]))[0]
    except:
        return 0

def printCalibration(model):
    print("Calibration:",str(model.coef_)+" *c + "+str(model.intercept_))


ser = serial.Serial('COM4',115200)
ser.flushInput()

time.sleep(1)
# plt.figure(figsize=(60,3))
plt.xlim(0,60)
plt.ylim(0,2)
plt.hlines(1,0,60)  
# plt.xticks(np.arange(0, 60, 1))
# plt.axis('off')
plt.title("Triangulation")
plt.ion()

# fig, ax = plt.subplots(figsize=(10,3))

print("Started recording....")


start=time.time()
first_hit=1
second_hit=2
sound_speed=34300 # cm/s
cycles_to_seconds=float(1)/16000000  #16MHz arduino
total_length=60
calib1={"x":[],"y":[]}
calib2={"x":[],"y":[]}
model1 = LinearRegression()
model2 = LinearRegression()

start=time.time()

while True:
    try:
        ser_bytes = ser.readline()
        if time.time()-start<4:
            continue

        if "Reset" in ser_bytes:
            continue

        if " " in ser_bytes:
            first=ser_bytes.split(" ")[0]
            sec=ser_bytes.split(" ")[1]

            first_hit=(1 if "1" in first else 2)
            second_hit=3-first_hit
        else:
            print("")

            trigger_cycles=int(ser_bytes)
            trigger_time=trigger_cycles*cycles_to_seconds
            coord_x=0
            dist=0

            
            # Always refer to the distance as relative to the first mic
            if first_hit==1:
                # Linear regression distance
                dist=cycleToDist(trigger_cycles,model2)
                coord_x=(total_length-dist)/2
            else:
                # Linear regression distance
                dist=cycleToDist(trigger_cycles,model1)
                coord_x=dist+(total_length-dist)/2

            # plt.plot(coord_x,1,'|',ms=40)
            plt.eventplot([coord_x], orientation='horizontal', colors='b')
            ax = plt.gca()
            ax.set_xticks([coord_x])
            ax.set_xticklabels([str(coord_x)])
            plt.draw()
            plt.pause(0.01)
            print("Mic",first_hit,"Mic",second_hit)
            print("Trigger cycles:",trigger_cycles)
            print("Aproximate Time:",trigger_time)
            print("Distance:",dist)
            print("Coordinate x:",coord_x)

            #####  CALIBRATION
            input_data=raw_input("Calibration true distance: ")
            start=time.time()
            if  input_data=='\r':
                continue

            true_coord_x=float(input_data)
            true_dist=0
            if first_hit==1:
                true_dist=total_length-true_coord_x*2
            else:
                true_dist=total_length-(total_length-true_coord_x)*2

            if second_hit==1:
                calib1["x"].append([trigger_cycles])
                calib1["y"].append(true_dist)
                model1.fit(calib1["x"],calib1["y"])

                printCalibration(model1)
            else:
                calib2["x"].append([trigger_cycles])
                calib2["y"].append(true_dist)
                model2.fit(calib2["x"],calib2["y"])
                printCalibration(model2)
            
            # point.set_xdata(5)
            # fig.canvas.draw()
            # plt.gcf().show()
            # plt.draw()
        # figure.canvas.flush_events()
        
    except Exception,e:
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print("Keyboard Interrupt",line)
        break




