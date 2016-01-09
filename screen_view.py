# Author : Gowtham Saminathan
# Module : Screen_viewer.py: View remote screen and controle mouse and keyboard 


import pygame
import snd
import zlib
import Image
from pygame.locals import *
import Queue
import threading

rcv_q = Queue.Queue()
snd_q = Queue.Queue()

# Mapping Pygame-key ( Sender Side) to pyAutoGui-key ( Receiver side )

ALLKEYS = {
K_BACKSPACE : "backspace",
K_TAB : "tab",
K_CLEAR : "clear",
K_RETURN : "return",
K_PAUSE : "pause",
K_ESCAPE : "esc",
K_SPACE : "space",
K_EXCLAIM : "!",
K_QUOTEDBL : '"',
K_HASH : "#",
K_DOLLAR : "$",
K_AMPERSAND : "&",
K_QUOTE : "'",
K_LEFTPAREN : "(",
K_RIGHTPAREN : ")",
K_ASTERISK : "*",
K_PLUS : "+",
K_COMMA : ",",
K_MINUS : "-",
K_PERIOD : ".",
K_SLASH : "/",
K_0 : "0",
K_1 : "1",
K_2 : "2",
K_3 : "3",
K_4 : "4",
K_5 : "5",
K_6 : "6",
K_7 : "7",
K_8 : "8",
K_9 : "9",
K_COLON : ":",
K_SEMICOLON : ";",
K_LESS : "<",
K_EQUALS : "=",
K_GREATER : ">",
K_QUESTION : "?",
K_AT : "@",
K_LEFTBRACKET : "[",
K_BACKSLASH : "\\",
K_RIGHTBRACKET :"]",
K_CARET : "^",
K_UNDERSCORE : "_",
K_BACKQUOTE : "`",
K_a : "a",
K_b : "b",
K_c : "c",
K_d : "d",
K_e : "e",
K_f : "f",
K_g : "g",
K_h : "h",
K_i : "i",
K_j : "j",
K_k : "k",
K_l : "l",
K_m : "m",
K_n : "n",
K_o : "o",
K_p : "p",
K_q : "q",
K_r : "r",
K_s : "s",
K_t : "t",
K_u : "u",
K_v : "v",
K_w : "w",
K_x : "x",
K_y : "y",
K_z : "z",
K_DELETE : "delete",
K_KP0 : "num0",
K_KP1 : "num1",
K_KP2 : "num2",
K_KP3 : "num3",
K_KP4 : "num4",
K_KP5 : "num5",
K_KP6 : "num6",
K_KP7 : "num7",
K_KP8 : "num8",
K_KP9 : "num9",
K_KP_PERIOD : ".",
K_KP_DIVIDE : "/",
K_KP_MULTIPLY : "*",
K_KP_MINUS : "-",
K_KP_PLUS : "+",
K_KP_ENTER : "\n",
K_KP_EQUALS : "=",
K_UP : "up",
K_DOWN : "down",
K_RIGHT : "right",
K_LEFT : "left",
K_INSERT : "insert",
K_HOME : "home",
K_END : "end",
K_PAGEUP : "pageup",
K_PAGEDOWN : "pagedown",
K_F1 : "f1",
K_F2 : "f2",
K_F3 : "f3",
K_F4 : "f4",
K_F5 : "f5",
K_F6 : "f6",
K_F7 : "f7",
K_F8 : "f8",
K_F9 : "f9",
K_F10 : "f10",
K_F11 : "f11",
K_F12 : "f12",
K_F13 : "f13",
K_F14 : "f14",
K_F15 : "f15",
K_NUMLOCK : "numlock",
K_CAPSLOCK : "capslock",
K_SCROLLOCK : "scrolllock",
K_RSHIFT : "shiftright",
K_LSHIFT : "shiftleft",
K_RCTRL : "ctrlright",
K_LCTRL : "ctrlleft",
K_RALT : "altright",
K_LALT : "altleft",
K_RMETA : "rightmeta",
K_LMETA : "leftmeta",
K_LSUPER : "winleft",
K_RSUPER : "winright",
K_MODE : "modechange",
K_HELP : "help",
K_PRINT : "printscreen",
K_SYSREQ : "sysrq",
K_BREAK : "break",
K_MENU : "menu",
K_POWER : "power",
K_EURO : "euro"
}


class screen_viewer():
    def __init__(self):
        pass;
    def snd_data(self,data):
        # Send mouse-keyboard control data to Queue
        try:
            snd_q.put(data)
        except Exception as e:
            print "Sending data Q Error",e
    def play_screen(self,main_ctrl):
        # View Remote Screen
        try:
            s_id = main_ctrl.cli_id
            u_id = main_ctrl.cli_route
            play = True
            clock = pygame.time.Clock()
            first_img = False
            rcv_thread_stat = False
            snd_thread_stat = False
            mouse_controle_req = False
            mus_auth = False
            pygame.init()
            while play:
                if rcv_thread_stat == False:                    
                    try:
                        print "SENDIING NEW IMAGES REQUEST"
                        # Start thread to receive image from server
                        print "TRYING TO STATRT THREAD"
                        rcv_thread = threading.Thread(target=main_ctrl.rcv_data_do_it)
                        rcv_thread.start()
                        print "THREAD STARTED"
                        rcv_thread_stat = True
                    except Exception as e:
                        print "THREAD SCREEN PLAY ERROR",e
                        rcv_thread_stat = False
                        
                if rcv_thread_stat == True:
                    rcv_thread_stat = rcv_thread.isAlive()
                
                
                if mouse_controle_req == True:
                    # Send mouse-keyboard control request to server
                    mput_data = {'type':'chat_snt','session_id':s_id,'user_id':u_id , 'to_user':main_ctrl.rusr_route,'msg':'new_control'}
                    #mput_data = {'type':'control_req' , 'session_id' : s_id , 'user_id' : u_id , 'status':'control' }
                    main_ctrl.put_http.put(mput_data)
                    try:
                        # check mouse-keyboard control authorization response
                        mus_auth = main_ctrl.get_http_cnt.get_nowait()
                        mouse_controle_req = False
                    except:
                        mus_auth = False
                    if mus_auth == 'control_accept':
                        # Received authorization response to control mouse-keyboard
                        if snd_thread_stat == False:
                            try:
                                # Start thread to send mouse-keyboard control to server
                                snd_thread = threading.Thread(target=main_ctrl.snd_data_do_it)
                                snd_thread.start()
                                snd_thread_stat = True
                            except Exception as e:
                                snd_thread_stat = False
                if snd_thread_stat == True:
                    snd_thread_stat = snd_thread.isAlive()
                
                
                try:
                    # Decompress received data ( zlib ) 
                    di = zlib.decompress(rcv_q.get_nowait())
                    igot_data = True
                except:
                    igot_data = False
                if igot_data == True:
                    try:
                        control_type = di[:4]
                        if control_type == 'NNNN':
                            # Received initial or full image
                            print "INITIAL IMAGE FOUND>"
                            ix = int(di[4:8])
                            iy = int(di[8:12])
                            img_data = di[12:]
                            # Set pygame display width*height
                            screen = pygame.display.set_mode((ix,iy))
                            # Convert RGB string to Image
                            img = Image.fromstring('RGB',(ix,iy),img_data)
                            img_f = pygame.image.fromstring(img.tostring(),(ix,iy),'RGB')
                            pygame.display.set_caption("Viewing Session :"+str(s_id)+" User: "+str(u_id))
                            # Set pygame key press repeation intravell
                            pygame.key.set_repeat(1000, 10)
                            first_img = True
                        elif first_img == True:
                            try:
                                # updating image using change rectangle image.
                                x = int(di[:4])
                                y = int(di[4:8])
                                img_data = di[24:]
                                a1 = int(di[8:12])
                                b1 = int(di[12:16])
                                a2 = int(di[16:20])
                                b2 = int(di[20:24])
                                img_data = Image.fromstring('RGB',(x,y),img_data)
                                img.paste(img_data,(a1,b1,a2,b2))
                                img_f = pygame.image.fromstring(img.tostring(),(ix,iy),'RGB')
                            except Exception as e:
                                # Something wrong get full image :-(
                                print "IMAGE PASTE ERROR",e
                        else:
                            # FIRST IMAGE NOT RECEIVED , BUT UPDATED IMAGES RECEIVED 
                            # SO PLEASE SEND FIRST IMAGE
                            # Request server to send full image
                            print "ASKING NEW IMAGE"
                            mput_data = {'type':'chat_snt','session_id':s_id,'user_id':u_id ,'to_user':main_ctrl.rusr_route,'msg':'new_image'}
                            main_ctrl.put_http.put(mput_data)
                            
                    except Exception as e:
                        print "RECEIVED DATA PROCESS ERROR>",e
                if first_img == True:
                    try:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.display.quit()
                                play = False
                            
                            # USER CLICK THE SCREEN - > SEND CONTROLE REQUEST    
                            if mouse_controle_req == False:
                                if event.type == pygame.MOUSEBUTTONUP:
                                    mouse_controle_req = True
                            elif event.type == pygame.MOUSEMOTION:
                                # send mouse press
                                self.snd_data('MOUS'+str(event.pos[0])+'|'+str(event.pos[1])+'|'+'DATA')
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                # send mouse press
                                self.snd_data('MCLK'+str(event.pos[0])+'|'+str(event.pos[1])+'|'+'DOWN|'+str(event.button))
                            elif event.type == pygame.MOUSEBUTTONUP:
                                # send mouse press
                                self.snd_data('MCLK'+str(event.pos[0])+'|'+str(event.pos[1])+'|'+'UP|'+str(event.button))
                            elif event.type == pygame.KEYDOWN:
                                # send keyboard press
                                if event.key in ALLKEYS:
                                    prs_key = ALLKEYS[event.key]
                                    self.snd_data('KCLK'+'DOWN'+'|'+prs_key)
                                else:
                                    print "UNKNOWN KEY PRESSED"
                            elif event.type == pygame.KEYUP:
                                # send keyboard press
                                if event.key in ALLKEYS:
                                    prs_key = ALLKEYS[event.key]
                                    self.snd_data('KCLK'+'UP'+'|'+prs_key)
                                else:
                                    print "UNKNOWN KEY RELEASED"
                        
                        # Display the image in screen
                        screen.blit(img_f,(0,0))
                        
                        #if mouse_controle_req == False:
                            # DISPLAY REMOTE CONTROL ICON
                        #    basicfont = pygame.font.SysFont(None, 48)
                        #    text = basicfont.render('ASK ACCESS', True, (255, 0, 0), (255, 255, 255))
                        #   textrect = text.get_rect()
                        #    print screen.get_rect()
                        #    textrect.centerx = screen.get_rect().centerx
                        #    textrect.centery = screen.get_rect().centery
                        #    screen.blit(text, textrect)
                        
                        pygame.display.flip()
                        # update the pygame display 30 fram/sec
                        clock.tick(30)
                    except Exception as e:
                        print "PYGAME DISPLAY ERROR",e
        except Exception as e:
            print "Screen Play Error",e
            return None


# MAIN MODULE STARTING POINT
class main_start():
    def __init__(self,session_id,usr_id,rusr_id,r_ip,r_port,put_http,get_http_cnt):
        self.cli_id = session_id
        self.cli_route = usr_id
        self.r_ip = r_ip
        self.r_port = r_port
        self.put_http = put_http
        self.get_http_cnt = get_http_cnt
        self.rusr_route = rusr_id
    def call_me(self,data):
        # received data from server and save it in Queue
        try:
            rcv_q.put(data)
        except:
            pass;
    def call_you(self,c_run):
        try:
            snd_q.empty()
        except:
            pass;
        while True:
            try:
                # check Queue for new data need to sent, if yes sent the data
                data = snd_q.get_nowait()
                if c_run.snd_data(data) == True:
                    # DATA SENDING SUCCESS
                    pass;
                else:
                    # DATA SENDING FAILED
                    return None
            except:
                pass;
    def rcv_data_do_it(self):
        # Establish connection to server and send session_id,user_id,route and client type ( data receiver client )
        try:
            c_run = snd.client_run()
            if c_run.connect_server(self.r_ip, self.r_port, self.cli_id, self.rusr_route, 'REC','DISPY') == True:
                # once data received call call_me function
                c_run.rec_data(self.call_me)
        except Exception as e:
            print "SCREEN_VIEW",e
            return None
    def snd_data_do_it(self):
        # Establish connection to server and send session_id,user_id,route and client_type ( data sender client )
        try:
            c_run = snd.client_run()
            if c_run.connect_server(self.r_ip, self.r_port, self.cli_id, self.cli_route, 'SEN','CNTRL') == True:
                self.call_you(c_run)
        except Exception as e:
            print "REMOTE CONTROLE",e
            return None
    def do_it(self):
        try:
            sv = screen_viewer()
            sv.play_screen(self)
        except Exception as e:
            print e

#put_http = Queue.Queue()
#get_http_cnt = Queue.Queue()
#m = main_start('1111111111111111','2222233333','192.168.1.123',2077,put_http,get_http_cnt)
#m.do_it()