import socketserver
import pickle
import http.client, urllib
from time import localtime, strftime
import psutil
import time
import random
from ZigbeeCode import myZigbee


key = 'VDRJODBINSG4TUQW'

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

def read_humidity():
    print('reading humidity.....')
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
    if math.isnan(humidity) == False:
        print("humidity =%.02f%%" % (humidity))
    return humidity'''

def sense_light():
    print('sensing light.....')
    return random.randint(1, 100)
    '''light_sensor = 0 # Connect the Grove Light Sensor to analog port A0
    led = 4 # Connect the LED to digital port D4
    grovepi.pinMode(light_sensor,"INPUT")
    grovepi.pinMode(led,"OUTPUT")
    sensor_value = grovepi.analogRead(light_sensor)
    resistance = (float)(1023 - sensor_value) * 10 / sensor_value # Calculate resistance of sensor in K
    threshold = 10
    if resistance > threshold:
        grovepi.digitalWrite(led, 1)
    else:
        grovepi.digitalWrite(led, 0)
    print("sensor_value = %d resistance = %.2f" % (sensor_value, resistance))
    return resistance'''

def sense_sound():
    print('sensing sound.....')
    return random.randint(1, 100)
    '''sound_sensor = 0 # Connect the Grove sound Sensor to analog port A0
    led = 5 # Connect the Grove LED to digital port D5
    grovepi.pinMode(sound_sensor, "INPUT")
    grovepi.pinMode(led, "OUTPUT")
    sensor_value = grovepi.analogRead(sound_sensor)
    # The threshold to turn the led on 400.00 * 5 / 1024 = 1.95v
    threshold_value = 400
    if sensor_value > threshold_value:
        grovepi.digitalWrite(led, 1)
    else:
        grovepi.digitalWrite(led, 0)
    print("sensor_value = %d" % sensor_value)
    return sensor_value'''

def read_pressure():
    print('reading pressure.....')
    return random.randint(1, 100)

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
                lightdata = sense_light()
                print('light = ' + str(lightdata))
                sounddata = sense_sound()
                print('sound = '+ str(sounddata))
                threshold_light = 50
                threshold_sound = 50
                alarm_light = 0
                alarm_sound = 0
                if lightdata < threshold_light:
                    alarm_light = 1
                if sounddata > threshold_sound:
                    alarm_sound = 1
                if counter == (i + 1):
                    state = "RPi1:doneall"
                else:
                    state = "RPi1:done"
                message = str(state) + ':light:' + str(alarm_light)+ ':sound:' + str(alarm_sound)
                print(message)
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)

        if 'envmon' in command[0]:
            print(command[0])
            for i in range(counter):

                print('the ' + str(i + 1) + ' reading')
                tempdata = read_temperature()
                output_temp = "temp = " + str(tempdata)
                humdata = read_humidity()
                output_hum = "humidity = " + str(humdata)
                if counter == (i+1):
                    state = "RPi1:doneall"
                else:
                    state = "RPi1:done"
                message = str(state)+':'+str(tempdata)+':'+str(humdata)
                print(message)
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)

        if 'cloud' in command[0]:
            for i in range(counter):
                print('the ' + str(i+1) + ' reading')
                tempdata = read_temperature()
                output = "temp = " + str(tempdata)
                print("Reading " + output)
                if SendToCloud(tempdata):
                    print('data has been sent to the cloud successfully')
                else:
                    print("The cloud connection failed")
                if counter == (i+1):
                    message = "RPi1:doneall"
                else:
                    message = "RPi1:done"
                message = pickle.dumps(message)
                self.request.send(message)

        if 'zigbee' in command[0]:
            zigbee = myZigbee()
            zigbee.printProperties()
            #zigbee.set_reciever_address()
            for i in range(counter):
                print('the ' + str(i+1) + ' reading')
                tempdata = read_temperature()
                output = "temp = " + str(tempdata)
                print("Reading " + output)
                zigbee.zsend(tempdata)
                if counter == (i+1):
                    message = "RPi1:doneall"
                else:
                    message = "RPi1:done"
                message = pickle.dumps(message)
                self.request.send(message)
                time.sleep(interval)








    def finish(self):
        print("[+] Request Finishes")




HOST, PORT = '127.0.0.1', 9998

server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
server.allow_reuse_address = True
print("[+] Start listening")
server.serve_forever()
