# Importing Libraries
import serial
import sys
import os
import csv
import datetime
import math
import numpy as np

from collections import deque
import threading
import time
a_x = deque([], maxlen=100)
a_y = deque([], maxlen=100)
a_z = deque([], maxlen=100)


action = deque([], maxlen=3)
for i in range(3):
    action.append(0)
total = np.empty(300, dtype=np.int8)
current_state = 0
previous_state = 0


for i in range(100):
    a_x.append(0)
    a_y.append(0)
    a_z.append(0)
import tensorflow as tf

state_dict = {
    0: 'Idle',
    1: 'Grenade',
    2: "Shield",
    3: "Reload",
    4: "Logout"}

from keras.models import load_model
model = load_model('two_layers.h5')
def export_to_csv(send_dict, data_csv_path):
    """
    This is for saving all the classification data to csv
    """
    # Convert from dict to df to csv row
    for key in send_dict.keys():
        val = send_dict.get(key)
        val_list = [val]
        send_dict.update({key: val_list})
    df = pd.DataFrame.from_dict(send_dict)
    myCsvRow = df.to_numpy().flatten().tolist()

    if (os.path.exists(data_csv_path)):
        # If the file already exists, append the row, if not create a new file and save
        save_df = pd.read_csv(data_csv_path)
        with open(data_csv_path, 'a', newline='', encoding='utf-8') as fd:
            wr = csv.writer(fd, delimiter=',')
            print(myCsvRow)
            wr.writerow(myCsvRow)
    else:
        # Append data to existing file.
        save_df = df
        save_df.to_csv(data_csv_path, index=False)

def log_data(category):
    while True:
        try:
            # num = input("Enter a number: ") # Taki3
            # 3ng input from user
            value = write_read()
            if str(value) == 'b\'\'':
                continue
            list_str = str(value)[2:-7]  # printing the value

            list_int = [int(i) for i in list_str.split(',')]
            # list_int[1:21] = [i / 100 for i in list_int[1:21]]

            # print(list_int[5], list_int[6], list_int[7], list_int[15], list_int[16], list_int[17]) # list_int[15], list_int[16], list_int[17]
            list_int[0] = data + list_int[0]
            out = dict(zip(["batch", "q0_wrist", "q1_wrist", "q2_wrist", "q3_wrist",
                            "ax_wrist", "ay_wrist", "az_wrist", "gx_wrist", "gy_wrist", "gz_wrist",
                            "q0_arm", "q1_arm", "q2_arm", "q3_arm",
                            "ax_arm", "ay_arm", "az_arm", "gx_arm", "gy_arm", "gz_arm"], list_int))
            out["category"] = category
            # euler_from_quaternion(list_int[1], list_int[2], list_int[3],list_int[4])
            export_to_csv(out)
        except KeyboardInterrupt:
            print(data_csv_path)
            print("Terminated")
            key_file.seek(0)
            key_file.write(str(list_int[0]))
            key_file.truncate()
            key_file.close()
            exit(0)
        except:
            pass

def write_read():
    data = arduino.readline()
    return data


def print_data():
    while True:
        try:
            value = write_read()

            if str(value) == 'b\'\'':
                continue
            list_str = str(value)[2:-7]  # printing the value

            list_int = [int(i) for i in list_str.split(',')]
            a_x.pop()
            a_x.appendleft(list_int[0])
            a_y.pop()
            a_y.appendleft(list_int[1])
            a_z.pop()
            a_z.appendleft(list_int[2])

            for i in range(100):
                total[i] = a_x[i]
            for i in range(100):
                total[100 + i] = a_y[i]
            for i in range(100):
                total[200 + i] = a_z[i]

            # q = model.predict(np.array([total]))
            # current_state = int(np.argmax(q))
            # print("check")
            #
            # if current_state != previous_state:
            #     print(state_dict[current_state])
            #     previous_state = current_state

        except KeyboardInterrupt:
            # serial.Serial.close()

            print("Terminated")

            exit(0)
        except:
            pass

def state_predict():
    while True:

        q = model.predict(np.array([total]))

        action.pop()
        action.appendleft(int(np.argmax(q)))

        if action[0] == 1:
            if action[1] == 1 and action[2] == 1:
                print("GRENADE")

        elif action[2] == 2:
            if action[1] == 2 and action[0] == 2:
                print("SHIELD")

        elif action[0] == 4:
            if action[1] == 4:
                print("LOGOUT")

        elif action[0] == 3:
            if action[1] == 3:
                print("RELOAD")
        else:
            print(f"IDLE {a_x[0]}")

        # print(state_dict[int(np.argmax(q))])
        time.sleep(0.1)

if __name__ == "__main__":
    # 0 idle, 1 Grenade   2 Shield    3 Reload     4 Logout
    dir(serial)
    arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1)

    x = threading.Thread(target=print_data)
    y = threading.Thread(target=state_predict)
    x.start()
    y.start()

    x.join()
    y.join()

