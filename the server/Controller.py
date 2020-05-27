from NodeTheads import Node
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import time

nodes_info = [('127.0.0.1',9998),('127.0.0.1',9999)]


class SimpleEcho(WebSocket):
    def handleMessage(self):
        msg = self.data
        print(msg)
        command = msg.split(":")
        node1.msg = msg
        node2.msg = msg
        node1.request = command[0]
        node2.request = command[0]
        node1.flag = 1
        node2.flag = 1

        results = "Hello 1"
        self.sendMessage(results)

        #while True:
            #print("inside loop")
            #results = node1.queue.get()
            #print("the results = " + results)


        #duration = duration+5
        #time.sleep(duration)

        #results = "hhhhhhhhhh 1"




        #self.sendMessage(self.data)

    def handleClose(self):
        print(self.address, 'closed')


#print(nodes_info[0])
node1 = Node(nodes_info[0])
#node2.daemon = True
node1.start()

#print(nodes_info[1])
node2 = Node(nodes_info[1])
#node2.daemon = True
node2.start()

server = SimpleWebSocketServer('', 9997, SimpleEcho)
server.allow_reuse_address = True
print("[+] Start listening")
server.serveforever()
