# Linux import pyscreenshot as ImageGrab
from PIL import Image
from PIL import ImageChops
from PIL import ImageGrab
from PIL import ImageFile
import base64
import pymouse
import pyautogui
import pyperclip
import threading
import time
import datetime
import zlib
#import chardet
import StringIO
from Tkinter import *
import ttk
import Queue
import urllib2
import websocket
import json


################################################################################################
# from Tkinter import *
# from ScrolledText import *
# import tkFont
# import ttk
# from ScrolledText import *


INPUT_Q = Queue.Queue()
screen_q = Queue.Queue()
screen_output_q = Queue.Queue()
uni_rcv_q = Queue.Queue()
uni_snd_q = Queue.Queue()
screen_control_q = Queue.Queue()
gui_q = Queue.Queue()
uni_rcv_gui_q = Queue.Queue()
global usrinfo
usrinfo = {}


qui_inputq = Queue.Queue()
qui_outputq = Queue.Queue()


def proxy_check():
    
    try:
        proxy = urllib2.getproxies()
        http_proxy = proxy.get('http')
        https_proxy = proxy.get('https')
        if http_proxy != None and https_proxy != None:
            return [http_proxy,https_proxy]
        if http_proxy != None:
            return [http_proxy]
        elif https_proxy != None:
            return [https_proxy]
        else:
            return False
    except Exception as e:
        print "UNABLE TO GET PROXY INFO: "+str(e)
        return None



class mini_gui():
    def __init__(self):
        pass;
    def task(self,a):
        if a == 'B' :
            data = self.B['text']
            screen_q.queue.clear()
            print 'Action',data
            screen_q.put(data)
            if data == 'PLAY':
                self.B['text'] = 'PAUSE'
            elif data == 'PAUSE':
                self.B['text'] = 'PLAY'
        elif a == 'B1':
            pass;
    def task_b(self,e):
        usr = self.cb3.get()
        print 'Control Pass to',usr
        self.soft_con.default_auth(usr)
       
    def send_helo(self):
        ustat = json.dumps({'name':self.uname})
        screen_output_q.put(self.grp_id+'BEATHAII|'+ustat)
        self.master.after(5000, self.send_helo)

    def task_c(self):
        try:
            d = qui_inputq.get_nowait()
            if d['type'] == 'MSG':
                self.l1['value'] = d['data']
            elif d['type'] == 'ADD':
                current_control = self.cb3.get()
                all_users = list(self.cb3['values'])
                all_users.append(d['data'])
                self.cb3['values'] = list(set(all_users))
                self.cb3.set(current_control)
                if d['data'] != current_control:
                    #POP UP FOR ALLOW ACCESS
                    self.l1['values'] = str(d['data'])+' asking controle'
            elif d['type'] == 'REMOVE':
                current_control = self.cb3.get()
                all_users = list(self.cb3['values'])
                try:
                    all_users.remove(d['data'])
                except:
                    pass;
                self.cb3['values'] = list(set(all_users))
                self.cb3.set(current_control)
        except Exception as e:
            pass
        self.master.after(1000, self.task_c)
    
    def gui_exit(self):
        exit()
    def gui_help(self):
        pass;
    def start(self,id,soft_con,grp_id,uname):
        print id
        self.grp_id = grp_id
        self.uname = uname
        self.soft_con = soft_con
        self.master = Tk()
        self.master.overrideredirect(1)
        #self.top_lev = self.master.Toplevel()
        #self.top_lev.overrideredirect(1)
        self.master.geometry('310x30')
        #self.master.resizable(width=FALSE, height=FALSE)

        #self.cities = ('Toronto', 'Ottawa')
        self.cb3 = ttk.Combobox(self.master, state='readonly')
        self.cb3.pack(pady=0, padx=0)
        self.cb3.place(height=25, width=200,x=50, y=10)
        self.cb3.bind('<<ComboboxSelected>>',self.task_b)
        self.cb3['values'] = ['CONTROL_DENIED']
        self.cb3.set('CONTROL_DENIED')

        self.B = Button(self.master,relief=GROOVE,fg='white', bg='orange', text ="PAUSE", command = lambda: self.task('B'))
        self.B.pack()
        self.B.place(height=25, width=50,x=0, y=10)
        
        
        
        self.B1 = Button(self.master,relief=GROOVE,fg='white', bg='red', text ="EXIT", command = lambda: self.gui_exit())
        self.B1.pack()
        self.B1.place(height=25, width=50,x=250, y=10)
        
        yy = self.master.winfo_screenwidth()/2
        
        self.master.geometry('310x35+'+str(yy-150)+'+0')
        self.master.attributes("-alpha", 0.7)
        self.master.wm_attributes("-topmost", 1)
        self.master.configure(background='green')
        

        self.l1 = Label(self.master, text="Connecting to Server ..", font=("Helvetica", 8),fg="white",bg='orange',anchor=W, justify=LEFT)
        self.l1.place(height=10, width=310,x=1, y=0)


        self.B2 = Button(self.master,relief=FLAT,fg='white', bg='orange', text ="...", command = lambda: self.gui_help())
        self.B2.pack()
        self.B2.place(height=25, width=10,x=300, y=10)
        
        self.master.after(100, self.task_c)
        self.master.after(1000, self.send_helo)
        mainloop()



# class basic(Frame):
#     def __init__(self,top):
#         Frame.__init__(self, top)
#         self.top = top
#         self.top.live_usr.insert(END,'JOINED USERS:\n','a')
#         print ">>>"
#         self.start()
#     def start(self):
#         print "Hai"
# 
# class gui(Frame):
#     def __init__(self,root):
#         Frame.__init__(self, root)
#         self.root = root
#         self.test()
#     def func(self):
#         s = soft_input_control('192.168.1.2','443','1234567890123456')
#         main_con_thread = threading.Thread(target=s.basic_connection_handel)
#         main_con_thread.start()
#     def test(self):
#         
#         
#         self.root.configure(background='skyblue')
#         self.root.geometry("250x450-50+50")
#         self.root.resizable(width=False, height=False)
#         b_font = tkFont.Font(size=9,weight="bold")
# 
#         self.live_usr = ScrolledText(root)
#         self.live_usr.vbar.config(troughcolor = 'red', bg = 'blue')
#         self.live_usr.pack()
#         self.live_usr.place(x=0,y=250,width=200, height=100)    
#         self.live_usr.tag_config("a",foreground='blue',font=('', 10, 'bold'))
#         self.live_usr.tag_config("b",foreground='black',font=('', 8, 'bold'))
#         #live_usr.insert(END,'JOINED USERS:\n','a')
#         #live_usr.insert(END,'GOWTHAM','b')
#         #live_usr.config(state=DISABLED)
#         #live_usr.config(state=NORMAL)
#         #live_usr.config(state=DISABLED)
# 
#         self.live_usr2 = ScrolledText(root)
#         self.live_usr2.vbar.config(troughcolor = 'red', bg = 'blue')
#         self.live_usr2.pack()
#         self.live_usr2.place(x=0,y=0,width=200, height=100)    
#         self.live_usr2.tag_config("a",foreground='blue',font=('', 10, 'bold'))
#         self.live_usr2.tag_config("b",foreground='black',font=('', 8, 'bold'))
#         #live_usr2.insert(END,'JOINED USERS:\n','a')
#         #live_usr2.insert(END,'GOWTHAM','b')
# 
# 
#         chat_box_buttion = Button(self.root, text =">>", command = '', font = b_font,relief=GROOVE)
#         chat_box_buttion.pack()
#         chat_box_buttion.place(x=201,y=250, height=30, width=30)
#         self.func()
################################################################################################
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
    def __init__(self):
        pass;
    def capture_image(self,to_addr,ws_snd):
        # Send starting Image
        try:
            while True:
                con_stat = True
                self.gd = get_desk()
                img_1 = self.gd.get_init()
                new_img_req = True
                i = True
                while con_stat:
                    try:
                        new_img_req = screen_q.get_nowait()
                        if new_img_req == 'PAUSE':
                            print 'PAUSE CONTROLE RECEIVED'
                            i = False
                            new_img_req = False
                            time.sleep(0.200)
                        else:
                            print 'PLAY CONTROLE RECEIVED'
                            i = True
                            new_img_req = True
                    except:
                        new_img_req = False
                    try:
                        ws_snd.sock.send_binary(screen_output_q.get_nowait())
                    except:
                        pass
                    if new_img_req == True:
                        new_img_req = False
                        img_1 = self.gd.get_init()
                        i_box = img_1.getbbox()
                        #open('c1.jpg','wb').write(img_1)
                        #data = img_1.tobytes()
                        padx = str(i_box[2])
                        pady = str(i_box[3])
                        #data = 'NNNN'+padx+pady+data
                        output = StringIO.StringIO()
                        
                        img_1.save(output,format="JPEG",quality=50, optimize=True)
                        ig = output.read()
                        contents = output.getvalue()
                        
                        #open('test.jpg','wb').write(contents)
                        #open('c.jpg','wb').write(contents)
                        output.close()
                        #data = Image.open(StringIO.StringIO(contents))
                        #data = data.tobytes()
                        data = contents
                        #open('ssss.jpg','wb').write(data)
                        data = base64.b64encode(data)
                        data = to_addr+'DESK0|0|'+data
                        message = data
                        #message = zlib.compress(data)
                        ws_snd.sock.send_binary(message)
                        new_img_req = False
                        #self.output_q.put(message)
                        #return None
                    elif i == True:
                        diffImage,img_2,box = self.gd.get_cmp(img_1)
                        if diffImage != None and diffImage.getbbox()!= None:
                            diff_siz = diffImage.size
                            img_1 = img_2
                            try:
                                output = StringIO.StringIO()
                                #ImageFile.MAXBLOCK = max(diffImage.size) ** 2 # STRUCKING AT 0,0 IMAGE POSITION
                                #ImageFile.MAXBLOCK = 5000000
                                diffImage.save(output,format="JPEG",quality=50, optimize=True)
                                contents = output.getvalue()
                                output.close()
                                data = to_addr+'DESK'+str(box[0])+'|'+str(box[1])+'|'+base64.b64encode(contents)
                                message = data
                                #zlib.compress(data)
                                #print "Sending Image Data",len(message)
                                #con_stat = self.sd.snd_data(message)
                                ws_snd.sock.send_binary(message)
                                time.sleep(0.5)
                            except Exception as e:
                                print "Error Image data >>>>>",e
        except Exception as e:
            print "SCREEN SHARE ERROR",e



class soft_input_control():
    # CONTROLING LOCAL MOUSE AND KEYBOARD
    def __init__(self):
        self.mous = pymouse.PyMouse()
        self.controler = None
     
    def default_auth(self,auth):
        
        self.controler = usrinfo.get(auth)
        if self.controler != None:
                screen_output_q.put(self.controler+'ACNT')
                self.controler = usrinfo.get(auth)
    def uni_rec(self,data):
        try:
            fun = data[16:20]
            from_id = data[0:16]
            self.from_id = from_id
            
            if fun == 'RCNT':
                usn = usrinfo.get(self.from_id)
                if usn != None:
                    qui_inputq.put({'type':'ADD','data':usn})
                if self.controler == from_id:
                    screen_output_q.put(self.controler+'ACNT')
            elif from_id == self.controler:
                self.do_it(data[16:])
        except Exception as e:
            print e
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
                        screen_output_q.put_nowait(self.controler+lclip)
                    elif body[:4] == 'PAST':
                        #receive remote clipboad
                        data = body[4:]
                        pyperclip.copy(data)
                 
            return True
        except Exception as e:
            print "INPUT CONTROL ERROR",e
            return False
                 

#s = soft_input_control('192.168.1.2','443','1234567890123456')
#s.basic_connection_handel()


#screen = share_screen('192.168.1.2','443','B234567890123456',INPUT_Q)
#screen.capture_image()

# if __name__ == '__main__':
#     try:
#         screen = share_screen('192.168.1.2','443','1234567890123456',INPUT_Q)
#         screen_thread= threading.Thread(target=screen.capture_image)
#         screen_thread.start()
#         soft_in = soft_input_control('192.168.1.2','443','1234567890123456')
#         soft_thread = threading.Thread(target=soft_in.basic_connection_handel)
#         soft_thread.start()
#     except Exception as e:
#         print e
        
# root = Tk()
# app = gui(root)
# root.mainloop()       




class root_main():
    
    def __init__(self,r_ip,r_port,con_id,grp_id,uname):
        self.r_ip = r_ip
        self.r_port = r_port
        self.con_id = con_id
        self.t2_stat = False
        self.grp_id = grp_id
        self.uname = uname
        self.soft_con = soft_input_control()
    
    def on_open(self,ws):
        print 'Websocket Connection opened'
    
    def on_message(self,ws,data):
        snd_typ = data [16:20]
        
        if snd_typ == 'NIMG':
            print 'New Image Request Received'
            try:
                self.t2_stat = self.t2.isAlive()
            except:
                pass;
            if self.t2_stat != True:
                scr = share_screen()
                self.t2 = threading.Thread(target=scr.capture_image,args=(self.grp_id,self.ws,))
                self.t2.start()
            screen_q.put(snd_typ)
        elif snd_typ == 'BEAT':
            if data[20:24] == 'HAII':
                # THIS WILL EXECUTE ONLY IF RECEIVED UNICAST HAII
                ustat = json.dumps({'name':self.uname,'bchatid':0,'uchatid':0})
                screen_output_q.put(data[0:16]+'BEATHELO|'+ustat)
            elif data[20:24] == 'HELO':
                print data[25:]
                usrn = json.loads(data[25:])
                if usrn.get('name') != None:
                    qui_inputq.put({'type':'ADD','data':usrn.get('name')})
                    # FOR NAME TO ID AND ID TO NAME SEARCH
                    usrinfo.update({usrn.get('name'):data[0:16]})
                    usrinfo.update({data[0:16]:usrn.get('name')})
        else :
            print 'Received',snd_typ
            self.soft_con.uni_rec(data)
    
    def on_error(self,ws,e):
        print 'Websocket Error',e
    
    def on_close(self,ws):
        try:
            print 'Websocket Connection closed'
            self.t2.close()
        except Exception as e:
            print 'Websocket close error',e
    
    def gui(self):
        try:
            mgui = mini_gui()
            gui_thread = threading.Thread(target=mgui.start,args=('USER_ID',self.soft_con,self.grp_id,self.uname))
            gui_thread.start()
            self.start()
        except:
            pass;   
        
    def start(self):
        ws_url = 'ws://'+str(self.r_ip)+':'+str(self.r_port)+'/'+self.con_id
        prxy_info = proxy_check()
        if prxy_info == False or None:
            print 'No Proxy detected'
            self.ws = websocket.WebSocketApp(ws_url,on_message = self.on_message,on_error = self.on_error,on_close = self.on_close,on_open = self.on_open)
            self.ws.run_forever()
        else:
            for prx in prxy_info:
                http_proxy_auth = ['username','password']
                http_add = prx.split('//')
                http_add_all = http_add[1].split(':')
                http_add = http_add_all[0]
                http_port = http_add_all[1]
                self.ws = websocket.WebSocketApp(ws_url,on_message = self.on_message,on_error = self.on_error,on_close = self.on_close,on_open = self.on_open)
                self.ws.run_forever(ws_url,http_proxy_host=http_add,http_proxy_port=http_port)
        

        
         
r = root_main('192.168.1.123','8080','SUB1000000000000005-1000000000000005','1000000000000000','Terror')
r.gui()