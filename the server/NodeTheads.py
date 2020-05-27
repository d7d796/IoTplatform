import urllib.request,json
import socket
import time
import pickle
import threading
from PlotClasses import NBPlot
import queue

READ_API_KEY1='X35HJBVYGRHG3NT6'
CHANNEL1_ID=733218

READ_API_KEY2='K9S6LO2Q5ZODBU0W'
CHANNEL2_ID=739578


class Node(threading.Thread):
    def __init__(self,ip_port):
        threading.Thread.__init__(self)
        #self.xdata = []
        #self.ydata = []
        self.connpar = ip_port
        self.flag = 0
        self.msg = ''
        self.request = ''
        self.alldone = 0
        self.queue = queue.PriorityQueue()


        #self.line = self.setup_plot(self.xdata, self.ydata)

    def run(self):
        #print('in run')
        while True:
            time.sleep(3)
            if (self.flag):
                conn = self.sendRequest(self.msg)
                if 'cloud' in self.request:
                    self.cloud_response(conn)
                elif 'envmon' in self.request:
                    self.envmon_response(conn)
                elif 'actmon' in self.request:
                    self.actmon_response(conn)
                elif 'zigbee' in self.request:
                    self.zigbee_response(conn)
                self.flag = 0

    def envmon_response(self, conn):
        #print("envmon")
        while True:
            msg = self.waitResponse(conn)
            #print(msg)
            result = msg.split(":")
            if 'RPi1' in result[0]:
                print(result[0] + ' temprature = ' + result[2])
                print(result[0] + ' humidity   = ' + result[3])
                self.queue.put(result[2])
            elif 'RPi2' in result[0]:
                print(result[0] + ' dust       = ' + result[2])
                print(result[0] + ' AirQuality = ' + result[3])
            if 'doneall' in result[1]:
                print("All Done")
                self.alldone = 1
                break
            time.sleep(1)
        self.closeConn(conn)


    def actmon_response(self, conn):
        while True:
            msg = self.waitResponse(conn)
            #print(msg)
            result = msg.split(":")
            if 'RPi1' in result[0]:
                print(result[0] + ' light = ' + result[3])
                print(result[0] + ' sound = ' + result[5])
                if '1' in result[3]:
                    print('ALARM : NO LIGHT')
                if '1' in result[5]:
                    print('ALARM : LOUD SOUND')
            elif 'RPi2' in result[0]:
                print(result[0] + ' motion= ' + result[3])
                if '1' in result[3]:
                    print('ALARM : MOTION DETECTED')
            if 'doneall' in result[1]:
                print("All Done")
                self.alldone = 1
                break
            time.sleep(1)
        self.closeConn(conn)

    def zigbee_response(self, conn):
        print("zigbee")
        while True:
            msg = self.waitResponse(conn)
            result = msg.split(":")
            if 'RPi2' in result[0]:
                print(result[2])
            if 'doneall' in result[1]:
                print("All Done")
                self.alldone = 1
                break
            time.sleep(1)
        self.closeConn(conn)

    def cloud_response(self, conn):
        if self.connpar[1] == 9998:
            pl = NBPlot('RPi1')
        elif self.connpar[1] == 9999:
            pl = NBPlot('RPi2')
        while True:
            msg = self.waitResponse(conn)
            command = msg.split(":")
            #print(command)
            if 'RPi1' in command[0]:
                data = self.getCloudData(READ_API_KEY1, CHANNEL1_ID)
            elif 'RPi2' in command[0]:
                data = self.getCloudData(READ_API_KEY2, CHANNEL2_ID)
            #self.xdata.append(datetime.datetime.now())
            #self.ydata.append(int(data['field1']))
            #self.update_plot()
            print('cloud data: '+str(data['field1']))
            pl.plot(int(data['field1']))
            time.sleep(0.5)
            #pl.plot(finished=True)
            if 'doneall' in command[1]:
                print("All Done")
                self.alldone = 1
                break
            time.sleep(1)
        self.closeConn(conn)

    def closeConn(self, s):
        s.send('close'.encode())
        s.close()

    def getCloudData(self, apikey, chid):
        conn = urllib.request.urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                                      % (chid, apikey))
        response = conn.read()
        print('http status code=' + str(conn.getcode()))
        data = json.loads(response)
        #print(data['field1'], data['created_at'])
        #print(type(data['created_at']))
        conn.close()
        return data


    def waitResponse(self, s):
        print('waiting ' + str(self.connpar)+' ....')
        recmsg = s.recv(1024)
        recmsg = pickle.loads(recmsg)
        print('Received: '+ recmsg + ' from '+ str(self.connpar))
        return recmsg


    def sendRequest(self, msg):
        s = socket.socket()
        s.connect(self.connpar)
        print('Sending: '+msg+ ' to '+ str(self.connpar))
        s.send(msg.encode())
        return s











'''
    def setup_plot(self, xdata, ydata):
        print('here')
        plt.show()
        axes = plt.gca()
        plt.setp(axes.get_xticklabels(), rotation=45)
        # axes.set_xlim(0, 100)
        axes.set_ylim(0, 100)
        line, = axes.plot(xdata, ydata, 'r-')
        return line
'''


'''
    def update_plot(self):
        #print('here ' + str(x) + ' ' + str(y))
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        plt.draw()
        plt.scatter(self.xdata, self.ydata)
        plt.pause(1e-17)
        time.sleep(0.5)
'''


'''
for i in nodes_info:
    print(nodes_info[i])
    node = Node(nodes_info[i])
    #node1.daemon = True
    node.start()
'''
