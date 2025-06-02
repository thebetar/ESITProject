#!/usr/bin/python3

# This scripts generates simulated sensor data in JSON format.
# Example output:
# {"deviceuid":"a0:e6:f8:b6:34:83","devicename":"ST-01","lightmeter":201.83}
# {"deviceuid":"a0:e6:f8:b6:34:83","devicename":"ST-01","IRtemperature":[41.636207,24.099419]}
# {"deviceuid":"a0:e6:f8:b6:34:83","devicename":"ST-01","accelerometer":[0.084894,0.190356,0.101560]}

import time
import signal
import sys
import argparse
import math
from random import normalvariate

addr = "xx"
dev_name = "ST-XX"

lux_mean = 200.00
lux_ampl = 20.0
temp1_mean = 41.01
temp1_ampl = 4.00
temp2_mean = 21.30
temp2_ampl = 3.00
acc_x_mean = 0.1
acc_y_mean = 0.2
acc_z_mean = 0.1


def interruptHandler(signal, frame):
    sys.exit(0)


def setup():
    return st


def readLux(x):
    lux = normalvariate(lux_mean + lux_ampl * math.sin(x), 1.5)
    print(
        '{"deviceuid":"'
        + addr
        + '","devicename":"'
        + dev_name
        + '","lightmeter":'
        + "%.2f" % (lux)
        + "}"
    )


def readIRTemp(x):
    temp1 = normalvariate(temp1_mean + temp1_ampl * math.sin(x), 0.5)
    temp2 = normalvariate(temp2_mean + temp2_ampl * math.sin(x + math.pi / 2.0), 0.4)
    print(
        '{"deviceuid":"'
        + addr
        + '","devicename":"'
        + dev_name
        + '","IRtemperature":['
        + "%f,%f" % (temp1, temp2)
        + "]}"
    )


def readAcceleration():
    acc_x = normalvariate(acc_x_mean, 0.02)
    acc_y = normalvariate(acc_y_mean, 0.02)
    acc_z = normalvariate(acc_z_mean, 0.02)
    print(
        '{"deviceuid":"'
        + addr
        + '","devicename":"'
        + dev_name
        + '","accelerometer":['
        + "%f,%f,%f" % (acc_x, acc_y, acc_z)
        + "]}"
    )


def main():
    signal.signal(signal.SIGINT, interruptHandler)

    phase = 0.0
    phase_step = 5.0

    while True:
        phase = phase + phase_step
        if phase > 360.0:
            phase = phase - 360.0
        phase_rad = phase * math.pi / 180.0
        readLux(phase_rad)
        time.sleep(2)
        readIRTemp(phase_rad)
        time.sleep(2)
        readAcceleration()
        time.sleep(2)


if __name__ == "__main__":
    # specify commandline options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--only",
        action="store_true",
        help="restrict recognized devices to only those specified with -d",
    )
    parser.add_argument(
        "-d",
        "--device",
        nargs="*",
        help="Give device with uid a friendly name, in format: uid=friendlyname e.g. a0:e6:f8:b6:34:83=SHOULDER",
    )

    args = parser.parse_args()

    if not args.device:
        print(
            "No device UID given, example:\n./sensorcollector.py -d a0:e6:f8:b6:34:83=Sensor_name"
        )
        sys.exit(0)

    for dev in args.device:
        (uid, devname) = dev.split("=", 2)
        if not uid or not devname:
            print("could not split device", dev)
            burp
        dev_name = devname
        addr = uid
    try:
        main()
    finally:
        print("Program terminated.")
