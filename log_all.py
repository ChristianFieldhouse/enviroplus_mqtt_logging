#!/usr/bin/env python3
import time
import datetime
from collections import deque
import sys
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging
import paho.mqtt.client as mqtt

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""
log_all.py
publishes all the sensor data to mqtt broker
""")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set("scales", "scales_password")

client.connect("christianfieldhouse.duckdns.org", 1883, 60)

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp


cpu_temps = [get_cpu_temperature()] * 5

delay = 0.5  # Debounce the proximity tap
mode = 0     # The starting mode
log_length = 50

values = {
    k : deque(maxlen=log_length)
    for k in [
        "proximity_",
        "temperature_C",
        "pressure_hPa",
        "humidity_%",
        "light_Lux",
        "oxidised_k0",
        "reduced_k0",
        "nh3_k0",
        "pm1_ug/m3",
        "pm2.5_ug/m3",
        "pm10_ug/m3",
        "time_s",
    ]
}
secs_between_readings = 0

while True:
    for repeat in range(log_length):
        values["proximity_"].append(ltr559.get_proximity())
        values["temperature_C"].append(bme280.get_temperature())
        values["pressure_hPa"].append(bme280.get_pressure())
        values["humidity_%"].append(bme280.get_humidity())
        values["light_Lux"].append(ltr559.get_lux())
        gas_data = gas.read_all()
        values["oxidised_k0"].append(gas_data.oxidising / 1000)
        values["reduced_k0"].append(gas_data.reducing / 1000)
        values["nh3_k0"].append(gas_data.nh3 / 1000)
        particulates = pms5003.read()
        values["pm1_ug/m3"].append(particulates.pm_ug_per_m3(1.0))
        values["pm2.5_ug/m3"].append(particulates.pm_ug_per_m3(2.5))
        values["pm10_ug/m3"].append(particulates.pm_ug_per_m3(10))
        values["time_s"].append(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
        print(
            "all readings: ",
            {
                k: sum(v) / len(v)
                for k, v in values.items()
                if k != "time_s"
            },
            end=" "*100 + "\r",
        )
        time.sleep(secs_between_readings)
    print("\npublishing to mqtt broker ...")
    for k, v in values.items():
        if k != "time_s":
            client.publish(
                topic=f"enviroplus/{k}",
                payload=str(sum(v)/len(v)),
                retain=True,
            )



