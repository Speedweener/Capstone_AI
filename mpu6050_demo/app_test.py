# Importing Libraries
import serial
import time
import pandas as pd
import sys
import os
import signal
import csv
import datetime
import math

dir(serial)
arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1)
data_csv_path = 'io/' + 'Reload_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'

key_file = open("key_value", 'r+')
data = int(key_file.read())

def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    roll_x = math.degrees(roll_x)
    # pitch_y = math.degrees(pitch_y)
    yaw_z = math.degrees(yaw_z)
    print(x,y, z,w)
    print(roll_x, pitch_y, yaw_z)

    # return roll_x, pitch_y, yaw_z  # in radians

def export_to_csv(send_dict):
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


def write_read():
    # data = arduino.read(arduino.inWaiting())
    data = arduino.readline()
    return data


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
            master_list = [0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0]

            list_int[0] = data + list_int[0]
            master_list[0] = list_int[0]
            master_list[5] = list_int[1]
            master_list[6] = list_int[2]
            master_list[7] = list_int[3]
            out = dict(zip(["batch", "q0_wrist", "q1_wrist", "q2_wrist", "q3_wrist",
                            "ax_wrist", "ay_wrist", "az_wrist", "gx_wrist", "gy_wrist", "gz_wrist",
                            "q0_arm", "q1_arm", "q2_arm", "q3_arm",
                            "ax_arm", "ay_arm", "az_arm", "gx_arm", "gy_arm", "gz_arm"], master_list))
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



if __name__ == "__main__":
    # 0 idle, 1 Grenade   2 Shield    3 Reload     4 Logout
    argv = int(sys.argv[1])
    log_data(argv)
