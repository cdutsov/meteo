from Adafruit_BME280 import *
import curses
import paho.mqtt.client as paho
import veml6070


broker="127.0.0.1"
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

def main(stdscr):
    sensor = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
    stdscr.nodelay(1)
    tstart = time.time()
    client1= paho.Client("control1")                           #create client object
    client1.on_publish = on_publish                          #assign function to callback
    client1.connect(broker,port)                                 #establish connection
    veml = veml6070.Veml6070()
    veml.set_integration_time(veml6070.INTEGRATIONTIME_1T)
    
    while (stdscr.getch() == -1) :
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()
        dew_point = sensor.read_dewpoint()
        uv_raw = veml.get_uva_light_intensity_raw()
        uv = veml.get_uva_light_intensity()
        stdscr.addstr(0, 0, 'Timestamp = %0.3f sec' % (time.time() - tstart))
        stdscr.addstr(1, 0, 'Temp      = %0.3f deg C (%0.3f deg F)' % (degrees, ((degrees*9/5)+32)))
        stdscr.addstr(2, 0, 'Pressure  = %0.2f hPa' % hectopascals)
        stdscr.addstr(3, 0, 'Humidity  = %0.2f %%' % humidity)
        stdscr.addstr(4, 0, 'Dew point  = %0.2f deg C'% dew_point)
        stdscr.addstr(5, 0, 'Press any key to exit...')
        stdscr.refresh()
	ret= client1.publish("sensors/temperature", "%0.3f" % (degrees))
	ret= client1.publish("sensors/pressure", "%0.3f" % (hectopascals))
	ret= client1.publish("sensors/humidity", "%0.3f" % (humidity))
	ret= client1.publish("sensors/dewpoint", "%0.3f" % (dew_point))
	ret= client1.publish("sensors/uv", "%0.3f" % (uv))
	ret= client1.publish("sensors/uv_raw", "%0.3f" % (uv_raw))
        time.sleep(1)

        stdscr.erase()


curses.wrapper(main)

