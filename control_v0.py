from PIL import Image
from PIL import ImageChops
from PIL import ImageGrab
from PIL import ImageFile
import pymouse
import pyautogui
import pyperclip
import snd
import threading
import time
#import datetime
import zlib
import StringIO


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
    def __init__(self,r_ip, r_port,session_id,INPUT_Q):
        self.r_ip = r_ip
        self.r_port = r_port
        self.session_id = session_id
        self.INPUT_Q = INPUT_Q
    def create_conn(self):
        group_user_id = self.session_id[0:10]
        self.sd = snd.client_run()
        return self.sd.connect_server(self.r_ip, self.r_port, 'PUB'+group_user_id) 
    def capture_image(self):
        # Send starting Image
        try:
            while True:
                time.sleep(3)
                con_stat = self.create_conn()
                self.gd = get_desk()
                new_img_req = True
            while con_stat:
                try:
                        new_img_req = self.INPUT_Q.get_nowait()
                        new_img_req = True
                except:
                    new_img_req = False
                if new_img_req == True:
                    img_1 = self.gd.get_init()
                    i_box = img_1.getbbox()
                    #open('c1.jpg','wb').write(img_1)
                    data = img_1.tostring()
                    padx = ('0000'+str(i_box[2]))[-4:]
                    pady = ('0000'+str(i_box[3]))[-4:]
                    print data[:10],padx,pady
                    #data = 'NNNN'+padx+pady+data
                    message = data
                    #message = zlib.compress(data)
                    con_stat = self.sd.snd_data(message)
                    new_img_req = False
                    #self.output_q.put(message)
                    print "INITIAL IMAGE SENDING..."
                else:
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
                            open('c.jpg','wb').write(contents)
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
                            message = data
                            #message = zlib.compress(data)
                            #print "Sending Image Data",len(message)
                            con_stat = self.sd.snd_data(message)
                            #self.output_q.put(message)
                        except Exception as e:
                            print "Error Image data >>>>>",e
        except Exception as e:
            print "SCREEN SHARE ERROR",e



class soft_input_control():
    # CONTROLING LOCAL MOUSE AND KEYBOARD
    def __init__(self,r_ip,r_port,user_id):
        self.mous = pymouse.PyMouse()
        self.controler = None
        self.r_ip = r_ip
        self.r_port = r_port
        self.user_id = user_id
    def basic_connection_handel(self):
        self.un_run = snd.client_run()
        while True:
            con_stat = self.un_run.connect_server(self.r_ip, self.r_port, 'SUB'+self.user_id)
            if con_stat == True:
                self.un_run.rec_data(self.uni_rec)
            print 'Connection closed Reconnect in 3sec...'
            time.sleep(3)
    def uni_rec(self,data):
        fun = data[16:21]
        from_id = data[0:16]
        self.from_id = from_id
        if fun == 'RCNT':
            if raw_input('Control Request from'+from_id+'Y/N :').find('y') != -1:
                self.controler = from_id
                if self.un_run.snd_data('1'+from_id+self.user_id+'ACNT') != True:
                    print 'Sending data failed'
                    return None
            else:
                print 'Control denied'
        elif from_id == self.controler:
            self.do_it(data[16:])
    def do_it(self,body):
        try:
            if body != None:
                head = body[:4]
                body = body[4:]
                if head == 'MOUS':
                    #MOUSE MOVE EVENT
                    mxy = body.split('|')
                    self.mous.move(int(mxy[0]),int(mxy[1]))
                    #pyautogui.moveTo(int(mxy[0]),int(mxy[1]))
                elif head == 'MCLK':
                    #MOUSE CLICK EVENT
                    mxy = body.split('|')
                    if mxy[2] == 'DCLK':
                        # DOUBLE CLICK
                        if mxy[3] == '1':
                            pyautogui.doubleClick(int(mxy[0]),int(mxy[1]),button='left')
                        elif mxy[3] == '2':
                            pyautogui.doubleClick(int(mxy[0]),int(mxy[1]),button='right')
                    elif mxy[2] == 'SCLK':
                        #SINGLE CLICK
                        if mxy[3] == '1':
                            pyautogui.click(int(mxy[0]),int(mxy[1]),button='left')
                        elif mxy[3] == '2':
                            pyautogui.click(int(mxy[0]),int(mxy[1]),button='right')
                    elif mxy[2] == 'DOWN':
                        #MOUSE PRESS
                        if mxy[3] == '1':
                            pyautogui.mouseDown(int(mxy[0]),int(mxy[1]),button='left')
                        elif mxy[3] == '3':
                            pyautogui.mouseDown(int(mxy[0]),int(mxy[1]),button='right')
                        elif mxy[3] == '4':
                            #SCROLL DOWN
                            pyautogui.scroll(-5,x=int(mxy[0]),y=int(mxy[1]))
                    elif mxy[2] == 'UP':
                        #MOUSE RELEASE
                        if mxy[3] == '1':
                            pyautogui.mouseUp(int(mxy[0]),int(mxy[1]),button='left')
                        elif mxy[3] == '3':
                            pyautogui.mouseUp(int(mxy[0]),int(mxy[1]),button='right')
                        elif mxy[3] == '4':
                            #SCROLL UP
                            pyautogui.scroll(5,x=int(mxy[0]),y=int(mxy[1]))
                elif head == "KCLK":
                    #KEYBOARD EVENT
                    key_ev = body.split('|')
                    if key_ev[0] == 'DOWN':
                        pyautogui.keyDown(key_ev[1])
                    elif key_ev[0] == "UP":
                        pyautogui.keyUp(key_ev[1])
                    elif key_ev[0] == "PRES":
                        pyautogui.press(key_ev[1])
                elif head == 'CLIP':
                    # CLIP BOARD EVENT
                    if body[:4] == 'COPY':
                        #send local clipboard to remote
                        lclip = pyperclip.paste()
                        self.un_run.snd_data('1'+self.from_id+self.user_id+lclip)
                    elif body[:4] == 'PAST':
                        #receive remote clipboad
                        data = body[4:]
                        pyperclip.copy(data)
                
            return True
        except Exception as e:
            print "INPUT CONTROL ERROR",e
            return False
                

s = soft_input_control('127.0.0.1','443','1234567890123456')
s.basic_connection_handel()
#screen = share_screen('127.0.0.1','443','1234567890123456',INPUT_Q)
#screen.capture_image()

# if __name__ == '__main__':
#     try:
#         screen = share_screen('127.0.0.1','443','1234567890123456',INPUT_Q)
#         screen_thread= threading.Thread(target=screen.capture_image)
#         screen_thread.start()
#         soft_in = soft_input_control('127.0.0.1','443','1234567890123456')
#         soft_thread = threading.Thread(target=soft_in.basic_connection_handel)
#         soft_thread.start()
#     except Exception as e:
#         print e
        
        