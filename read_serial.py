import serial


def get_dust_particles():
    with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
        sentence = ser.readline()
        return sentence
        dat = 0.
        # try:
        #     dat = float(ser.readline().rsplit(',')[1])
        # except:
        #     dat = False
        # return dat


# while True:
#     with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
#         line = ser.readline()
#         print line
