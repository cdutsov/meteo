from Adafruit_BME280 import *
import paho.mqtt.client as paho
import veml6070
import time

broker = "127.0.0.1"
port = 1883


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


def main():
    sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
    tstart = time.time()
    client1 = paho.Client("control1")  # create client object
    client1.on_publish = on_publish  # assign function to callback
    client1.connect(broker, port)  # establish connection
    veml = veml6070.Veml6070()
    veml.set_integration_time(veml6070.INTEGRATIONTIME_1T)

    file_t = open("temperature.txt", "rw")
    file_p = open("pressure.txt", "rw")
    file_h = open("humidity.txt", "rw")
    file_uv = open("uv.txt", "rw")

    while True:
        vreme = time.strftime("%H:%M:%S")
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
        dew_point = sensor.read_dewpoint()
        uv_raw = veml.get_uva_light_intensity_raw()
        uv = veml.get_uva_light_intensity()
        ret = client1.publish("sensors/temperature", "%0.3f" % (degrees))
        ret = client1.publish("sensors/pressure", "%0.3f" % (hectopascals))
        ret = client1.publish("sensors/humidity", "%0.3f" % (humidity))
        ret = client1.publish("sensors/dewpoint", "%0.3f" % (dew_point))
        ret = client1.publish("sensors/uv", "%0.3f" % (uv))
        ret = client1.publish("sensors/uv_raw", "%0.3f" % (uv_raw))

        file_t.write("%s" % vreme + " %0.3f" % degrees + "\n")
        file_p.write("%s" % vreme + " %0.3f" % hectopascals + "\n")
        file_h.write("%s" % vreme + " %0.3f" % humidity + "\n")
        file_uv.write("%s" % vreme + " %0.3f" % uv + "\n")

        time.sleep(3)


main()
