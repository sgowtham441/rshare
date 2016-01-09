import socket   #for sockets
import time
import sys
import websocket

class client_run():
    def __init__(self):
        pass;
    def connect_server(self,r_ip,r_port,cli_id):
        try:
            
            #print r_ip,r_port,cli_id,cli_route,cli_type,cli_function
            print "Connecting ws://"+r_ip+":"+str(r_port)+"/"+str(cli_id)
            self.ws = websocket.WebSocket()
            self.ws.connect("ws://"+r_ip+":"+str(r_port)+"/"+str(cli_id))
            #self.ws.send('00000000')
            return True
        except Exception as e:
            print e
            return False
    def rec_data(self,call_me):
        try:
            while True:
                #print "WAITING FOR DATA RECEICE"
                data = self.ws.recv()
                print "DATA RECEIVED>",len(data)
                call_me(data)
                #print "DATA RECEIVED",len(data)
        except Exception as e:
            print "Receving Error",e
            try:
                self.ws.close()
            except:
                pass
            return False
    def snd_data(self,data):
        try:
            #print "trying to snd",len(data)
            a = time.time()
            self.ws.send_binary(data)
            #s = self.ws.send_binary(data)
            print "DATA SENT>",len(data),">",time.time() - a
            return True
        except Exception as e:
            print 'snd data',e
            try:
                self.ws.close()
            except:
                pass
            return False