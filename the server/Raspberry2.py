import socketserver
import pickle
import http.client, urllib
from time import localtime, strftime
import psutil
import time
import random
from ZigbeeCode import myZigbee
import atexit

key = 'T9L3S0VMLJE5DYSN'

def sense_motion():
    print('sensing motion.....')
    return random.randint(1, 100)
    '''pir_sensor = 8 # Connect the Grove PIR Motion Sensor to digital port D8
    grovepi.pinMode(pir_sensor, "INPUT")
    sense_value = grovepi.digitalRead(pir_sensor)
    if motion_sense():
        print('Motion Detected')
    else:
        print('-')

    return sense_value'''

def read_dust():
    print('reading dust.....')
    return random.randint(1, 100)
    '''atexit.register(grovepi.dust_sensor_dis)
    print("Reading from the dust sensor")
    grovepi.dust_sensor_en()
    [new_val, lowpulseoccupancy] = grovepi.dustSensorRead()
    return lowpulseoccupancy'''

def read_airQ():
    print('reading air quality.....')
    return random.randint(1, 100)
    '''# Connect the Grove Air Quality Sensor to analog port A0
    air_sensor = 0
    grovepi.pinMode(air_sensor, "INPUT")
    sensor_value = grovepi.analogRead(air_sensor)
    if sensor_value > 700:
        print("High pollution")
    elif sensor_value > 300:
        print("Low pollution")
    else:
        print("Air fresh")
    return sensor_value'''

def read_temperature():
    print('reading temp.....')
    return random.randint(1, 100)
    '''# Connect the Grove Temperature & Humidity Sensor Pro to digital port D4
    sensor = 4  # The Sensor goes on digital port 4.
    # temp_humidity_sensor_type
    # Grove Base Kit comes with the blue sensor.
    blue = 0  # The Blue colored sensor.
    white = 1  # The White colored sensor.
    #  This example uses the blue colored sensor.
    #  The first parameter is the port, the second parameter is the type of sensor.
    [temp, humidity] = grovepi.dht(sensor, blue)
    if math.isnan(temp) == False:
        print("temp = %.02f C " % (temp))
    return temp'''


def SendToCloud(data):
    params = urllib.parse.urlencode({'field1': data, 'key': key})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    time.sleep(16)
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print(data)
        print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
        print(response.status, response.reason)
        data = response.read()
        conn.close()
        return True
    except:
        return False

class MyTCPHandler(socketserver.BaseRequestHandler):

    # this method for converting binary to string, packets come from network, also check if there is error
    def controller_recv(self):
        try:
            msg = str(self.request.recv(1024),'utf-8')
            if msg == b'':
                print("[-] Connection Broken")
                self.request.close()
            return msg
        except Exception as e:
            print("[-] Could not receive: " + str(e))
            return False

    def handle(self):
        # self.request is the TCP socket connected to the client
        #while True:
        msg = self.controller_recv()
        print("msg: " + msg)
        command = msg.split(":")
        duration = int(command[1])
        print(duration)
        interval = int(command[2])
        print(interval)
        counter = int(duration / interval)
        print(counter)

        if 'actmon' in command[0]:
            print(command[0])
            for i in range(counter):
                print('the ' + str(i + 1) + ' reading')
                motiondata = sense_motion()
                print('motion = ' + str(motiondata))
                threshold = 50
                alarm = 0
                if motiondata > threshold:
                    alarm = 1
                if counter == (i+1):
                    state = "RPi2:doneall"
                else:
                    state = "RPi2:done"
                message = str(state)+':motion:'+str(alarm)
                print(message)
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)

        if 'envmon' in command[0]:
            print(command[0])
            for i in range(counter):
                print('the ' + str(i + 1) + ' reading')
                dustdata = read_dust()
                print('dust = ' + str(dustdata))
                aqdata = read_airQ()
                print('air quality = ' + str(aqdata))
                if counter == (i+1):
                    state = "RPi2:doneall"
                else:
                    state = "RPi2:done"
                message = str(state)+':'+str(dustdata)+':'+str(aqdata)
                print(message)
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)

        if 'cloud' in command[0]:
            for i in range(counter):
                print('the ' + str(i+1) + ' reading')
                tempdata = read_temperature()
                print("temp = " + str(tempdata))
                if SendToCloud(tempdata):
                    print('data has been sent to the cloud successfully')
                else:
                    print("The cloud connection failed")
                if counter == (i+1):
                    message = "RPi2:doneall"
                else:
                    message = "RPi2:done"
                message = pickle.dumps(message)
                self.request.send(message)

        if 'zigbee' in command[0]:
            zigbee = myZigbee()
            zigbee.printProperties()
            time.sleep(duration)
            time.sleep(interval)
            #zigbee.set_reciever_address()
            length = len(zigbee.messages)
            if length == 0:
                msg = "no msgs\n"
            else:
                msg = str(length) + "\n"

            for i in range(length):
                print('the ' + str(i+1) + ' reading')
                s = zigbee.get_one_message()
                if length == (i+1):
                    message = "RPi2:doneall:" + s
                else:
                    message = "RPi2:done:" + s
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)

    def finish(self):
        print("[+] Request Finishes")




HOST, PORT = '127.0.0.1', 9999

server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
server.allow_reuse_address = True
print("[+] Start listening")
server.serve_forever()
