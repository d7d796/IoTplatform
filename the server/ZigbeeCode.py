import serial
import time
import signal
import glob
from xbee import ZigBee



class myZigbee(object):
    def __init__(self):
        self.properties = {
        "ID":(10,False),
        "CE":(10,False),
        "SH":(0,False),
        "SL":(0,False),
        "MY":(0,False),
        "NI":(0,False)
        }
        self.portOpen = False
        self.commandModeActive = False
        self.available = True
        self.cord = False
        self.port = None
        self.messages = []
        self.port_speed = 9600
        self.long_addr = ''
        self.short_addr = ''
        self.port_assignment()
        self.serial = serial.Serial()
        self.openSerial()
        if self.portOpen == False:
            return False
        self.prop = {}
        self.syncProp()
        if self.prop['MY'] == '0':
            self.cord = True
        self.zb = None

        self.create_Zigbee()
        print("[+] done")


    def create_Zigbee(self):
        print("Creating zb ")
        self.zb = ZigBee(self.serial,escaped=True,callback=self.handle_meesages)

    def port_assignment(self):
        if self.port == None:
            port = None
            ports = glob.glob('/dev/ttyU[A-Za-z]*')
            if not ports:
                print("[-] No serial Ports connected")
                self.port = None
                self.available = False
                return
            else:
                for p in ports:
                    try:
                        s = serial.Serial(p)
                        s.close()
                        port = p
                        print("available port: " + str(port))
                    except (OSError, serial.SerialException):
                        pass

            self.port = port
        else:
            print("[+] port already assigned")
            return

    def printProperties(self):
        for p in self.prop:
            print(p+" : "+str(self.prop[p]))


    def openSerial(self):
        try:
            self.serial.port = self.port
            self.serial.baudrate = self.port_speed
            self.serial.open()
            self.portOpen = True
            print('[+] port has been opened')
        except Exception as msg:
            self.portOpen = False
            self.err = str( msg )
            print("[-] Error Opening the port: "+str(msg))

            # this take the current Settings from the xbee and store in the properties list


     # enter command mode by typing +++
    def commandMode(self):
        self.commandModeActive = True
        self.serial.flushInput()
        time.sleep(1)
        self.write("+++")
        return self.getOK()

            # closing the port
    def close_port(self):
        print("[-] Closing myZigbee")
        if self.portOpen:
            try:
                self.zb.halt()
                self.serial.close()
                print("[+] Port is Closed")
            except Exception as e:
                print("[-] Could not close the serial port")
                print(str(e))
        return


        # if the reply was ok for the set commands, other commands return values
    def getOK(self):
        reply = self.getReply()
        return reply == "OK"

        # this function check the buffer of the xbee and then read the input and return it, reply function
    def getReply(self):
        # get the terminal reply from the xbee
        done = False
        reply = ''
        while ( self.portOpen and not done):
            if self.serial.inWaiting() > 0:
                respone = self.serial.read().decode("utf-8")
                if respone == "\r":
                    done = True
                else:
                    reply += respone
        return reply

    # this go through all the True values in the prop list and that mean they going to change
    def write_settings(self):
        reply = ''
        for p in self.properties:
            if self.properties[p][1]:
                reply += "[+] Writing Setting: "+str(self.properties[p])
                print("[+] Writing Setting: "+str(self.properties[p]))
                reply += self.write_setting(p,self.properties[p][0])

        return reply



    def write_setting(self,prop,value):
            reply = ''
            if self.commandMode():
                cmd = "AT{0} {1}\r".format(prop,value)
                print(cmd)
                reply += "cmd: {0} ".format(cmd)
                try:
                    self.write(cmd)
                    ok = self.getOK()
                    print(ok)
                    reply += "Result : {0} \n".format(ok)
                except Exception as e:
                    print("[-] Error Could not apply the settings "+ str(e))
                    reply += "[-] Error Could not apply the settings "+ str(e) + "\n"
            return reply


    def write(self,msg):
        if self.portOpen:
            self.serial.write(str.encode(msg))

    def writeAndExit(self):
        self.write( "ATWR\r" )
        ok = self.getOK()
        if not ok:
            print("[-] Error Saving settings")
        self.write( "ATCN\r" )
        ok = self.getOK() and ok
        self.commandModeActive = False
        return ok


    def set_property(self,p):
            p = p.replace('set','')
            p = p.replace(' ','')
            print(p)
            v = p[2:]
            print(v)
            p = p[0:2]
            print(p)
            try:
                self.properties[p] = list(self.properties[p])
                self.properties[p][0] = v
                self.properties[p][1] = True
                self.properties[p] = tuple(self.properties[p])
                print("[+] Property Added")
                return "[+] Property Added"
            except Exception as msg:
                print(msg)
                print("[-] Error adding property, check the available properties for configuration")
                return "[-] Error adding property, check the available properties for configuration" + str(msg)

    def syncProp(self):
        if self.commandMode():
            for p in self.properties:
                cmd = "AT{0}\r".format(p)
                try:
                    self.write(cmd)
                    reply = self.getReply()
                    self.properties[p] = list(self.properties[p])
                    self.properties[p][0] = reply
                    self.properties[p] = tuple(self.properties[p])
                except Exception as e:
                    print( "[-] Error Getting Property ~.~ "+str(e))
                    break
            self.writeAndExit()
        self.prop = {
            "ID":self.properties['ID'][0],
            "CE":self.properties['CE'][0],
            "NI":self.properties['NI'][0],
            "SH":self.properties['SH'][0],
            "SL":self.properties['SL'][0],
            "MY":self.properties['MY'][0],
        }



        # this is for handling the CTRL+C and terminal close
    def register_signal_handler(self):
        signal.signal(signal.SIGINT,self.close_port)
        signal.signal(signal.SIGTERM,self.close_port)

    def handle_meesages(self,data):
        print(data)
        self.messages.append(data)

    def print_meesages(self):
        for i in self.messages:
            print(i)

    def zsend(self,message):
        long_addr = bytes(bytearray.fromhex(self.long_addr))
        #short_addr = bytes(bytearray.fromhex(self.short_addr))
        self.zb.send('tx',dest_addr_long=long_addr,dest_addr=self.short_addr,data=message.encode())

    def change_to_cord(self):
        self.zb.halt()
        time.sleep(2)
        self.set_property("CE 1")
        self.write_settings()
        self.cord = True
        self.syncProp()
        time.sleep(10)
        self.create_Zigbee()

    def set_reciever_address(self,long_addr,short_addr):
        self.long_addr = long_addr
        if short_addr == '0':
            self.short_addr = "\x00\x00"
        else:
            self.short_addr = short_addr
            self.short_addr = bytes(bytearray.fromhex(self.short_addr))

    def change_to_route(self):
        self.zb.halt()
        time.sleep(2)
        self.set_property("CE 0")
        self.write_settings()
        self.cord = False
        self.syncProp()
        time.sleep(10)
        self.create_Zigbee()

    def get_one_message(self):
        if len(self.messages) == 0:
            return False
        else:
            return self.messages.pop()



'''
zigbee = myZigbee()
zigbee.printProperties()
SH = "0013A200"
SL = "416307C0"
MY = '0000'
ADDR_LONG = SH + SL
#zigbee.zsend(ADDR_LONG,MY,"hello")
#zigbee.set_property("CE 1")
#zigbee.write_settings()
#zigbee.syncProp()
#zigbee.printProperties()
zigbee.close_port()
'''
