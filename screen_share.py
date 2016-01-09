from PIL import Image
from PIL import ImageChops
from PIL import ImageGrab
from PIL import ImageFile
import threading
import Queue
import time
import datetime
import zlib
import pymouse
import pyautogui
import StringIO
import snd

rcv_q = Queue.Queue()
snd_q = Queue.Queue()


class soft_input_control():
    # CONTROLING LOCAL MOUSE AND KEYBOARD
    def __init__(self,INPUT_Q):
        self.mous_press = False
        self.mous = pymouse.PyMouse()
        self.INPUT_Q = INPUT_Q
    def do_it(self):
        while True:
            try:
                try:
                    body = self.INPUT_Q.get_nowait()
                except:
                    body = None
                if body != None:
                    head = body[:4]
                    body = body[4:]
                    if head == 'MOUS' and self.mous_press == False:
                        mxy = body.split('|')
                        self.mous.move(int(mxy[0]),int(mxy[1]))
                        #pyautogui.moveTo(int(mxy[0]),int(mxy[1]))
                    elif head == 'MCLK' or self.mous_press == True:
                        mxy = body.split('|')
                        if mxy[2] == 'DOWN':
                            if mxy[3] == '1':
                                pyautogui.mouseDown(int(mxy[0]),int(mxy[1]),button='left')
                            elif mxy[3] == '3':
                                pyautogui.mouseDown(int(mxy[0]),int(mxy[1]),button='right')
                            else:
                                pyautogui.scroll(5,x=int(mxy[0]),y=int(mxy[1]))
                        else:
                            self.mous_press = False
                            if mxy[3] == '1':
                                pyautogui.mouseUp(int(mxy[0]),int(mxy[1]),button='left')
                            elif mxy[3] == '3':
                                pyautogui.mouseUp(int(mxy[0]),int(mxy[1]),button='right')
                            else:
                                pyautogui.scroll(-5,x=int(mxy[0]),y=int(mxy[1]))
                    elif head == "KCLK":
                        key_ev = body.split('|')
                        if key_ev[0] == 'DOWN':
                            pyautogui.keyDown(key_ev[1])
                        elif key_ev[0] == "UP":
                            pyautogui.keyUp(key_ev[1])
            except Exception as e:
                print "INPUT CONTROL ERROR",e
                

class get_desk():
    def __init__(self):
        pass;
    
    def get_init(self):
        # capture desktop image
        I = ImageGrab.grab()
        return I
    
    def get_cmp(self,img_1):
        # compare previous image with new image
        # crop the changed portion 
        img_2 = self.get_init()
        diffbox = ImageChops.difference(img_1,img_2).getbbox()
        if diffbox == None:
            #Two Images are Same :-)
            return None,None,None
        diffImage = img_2.crop(diffbox)
        return diffImage,img_2,diffbox


class share_screen():
    # PROCESS CAPTURED IMAGE
    def __init__(self,main_ctrl):
        self.output_q = snd_q
        self.rcv_thread_stat = False
        self.snt_thread_stat = False
        self.user_in_control = False
        self.main_ctrl = main_ctrl
        self.s_id = self.main_ctrl.cli_id
        self.u_id = self.main_ctrl.cli_route
    def share(self):
        self.gd = get_desk()
        while True:
            try:
                if self.snt_thread_stat == False:
                    self.snt_thread = threading.Thread(target=self.main_ctrl.snd_data_do_it)
                    self.snt_thread.start()
                    #need to put in GUI.py
                    #main_ctrl.put_http.put({"s_id":s_id,"u_id":u_id,"c_typ":"con","c_msg":"share"})
                    self.snt_thread_stat = self.snt_thread.isAlive()
                    self.capture_image()
            except Exception as e:
                print "Share Screen > ",e
        
    def capture_image(self):
        while self.snt_thread_stat == True:
            # Send starting Image
            img_1 = self.gd.get_init()
            i_box = img_1.getbbox()
            data = img_1.tostring()
            padx = ('0000'+str(i_box[2]))[-4:]
            pady = ('0000'+str(i_box[3]))[-4:]
            data = 'NNNN'+padx+pady+data
            message = zlib.compress(data)
            self.output_q.put(message)
            print "INITIAL IMAGE SENDING..."
            new_img_req = False
            
            while new_img_req == False:
                try:
                    # RECEIVE CONTROLE MESSAGE
                    con_req = self.main_ctrl.get_http_cnt.get_nowait()
                except:
                    con_req = False
                
                if con_req != False:
                    if con_req == 'new_image':
                        # Received new image request
                        new_img_req = True
                    else:
                        #con_req = remote user id ( Received using this id )
                        # Close the Existing control and start new control from user
                        if self.rcv_thread_stat == True:
                            try:
                                self.rcv_thread.close()
                            except:
                                pass;
                            self.user_in_control = False
                        # Receive new control
                        self.rcv_thread = threading.Thread(target=self.main_ctrl.rcv_data_do_it,args=(con_req))
                        self.rcv_thread.start()
                        self.user_in_control = True
                        # Need to send "control_accept" message for accepting the request 
                
                if self.user_in_control == True:
                    if self.rcv_thread.isAlive():
                        pass;
                    else:
                        self.rcv_thread = threading.Thread(target=self.main_ctrl.rcv_data_do_it,args=(con_req))
                        self.rcv_thread.start()
                        self.user_in_control = True
                                        
                diffImage,img_2,box = self.gd.get_cmp(img_1)
                if diffImage != None and diffImage.getbbox()!= None:
                    diff_siz = diffImage.size
                    img_1 = img_2
                    try:
                        output = StringIO.StringIO()
                        #ImageFile.MAXBLOCK = max(diffImage.size) ** 2 # STRUCKING AT 0,0 IMAGE POSITION
                        #ImageFile.MAXBLOCK = 5000000
                        diffImage.save(output,format="JPEG",quality=25, optimize=True)
                        contents = output.getvalue()
                        output.close()
                        diffImage = Image.open(StringIO.StringIO(contents))
                        data = diffImage.tostring()
                        padx = ('0000'+str(diff_siz[0]))[-4:]
                        pady = ('0000'+str(diff_siz[1]))[-4:]
                        pada1 = ('0000'+str(box[0]))[-4:]
                        padb1 = ('0000'+str(box[1]))[-4:]
                        pada2 = ('0000'+str(box[2]))[-4:]
                        padb2 = ('0000'+str(box[3]))[-4:]
                        data = padx+pady+pada1+padb1+pada2+padb2+data
                        message = zlib.compress(data)
                        #print "Sending Image Data",len(message)
                        self.output_q.put(message)
                    except Exception as e:
                        print "Error Image data >>>>>",e
                else:
                    pass;
                
                self.snt_thread_stat = self.snt_thread.isAlive()

class main_start():
    def __init__(self,session_id,usr_id,r_ip,r_port,put_http,get_http_msg):
        self.cli_id = session_id
        self.cli_route = usr_id
        self.r_ip = r_ip
        self.r_port = r_port
        self.put_http = put_http
        self.get_http_cnt = get_http_msg
    def call_me(self,data):
        try:
            rcv_q.put(data)
        except:
            pass;
    def rcv_data_do_it(self,r_uid):
        try:
            c_run = snd.client_run()
            if c_run.connect_server(self.r_ip, self.r_port, self.cli_id, r_uid, 'REC', 'CNTRL') == True:
                c_run.rec_data(self.call_me)
        except Exception as e:
            print "MOUSE_EVENT",e
            return None
    def call_you(self,c_run):
        try:
            snd_q.empty()
        except:
            pass;
        while True:
            try:
                data = snd_q.get_nowait()
                if c_run.snd_data(data) == True:
                    # DATA SEND SUCCESS
                    pass;
                else:
                    # DATA RUN FAILED
                    return None
            except:
                pass;
    def snd_data_do_it(self):
        try:
            c_run = snd.client_run()
            if c_run.connect_server(self.r_ip, self.r_port, self.cli_id, self.cli_route, 'SEN','DISPY') == True:
                self.call_you(c_run)
                #c_run.snd_data(c_run)
        except Exception as e:
            print "REMOTE CONTROLE",e
            return None
    def do_it(self):
        try:
            sv = share_screen(self)
            sv.share()
        except Exception as e:
            print e

#put_http = Queue.Queue()
#get_http_cnt = Queue.Queue()
#m = main_start('1111111111111111','2222233333','192.168.1.123',2077,put_http,get_http_cnt)
#m.do_it()