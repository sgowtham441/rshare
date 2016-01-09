import logging
#from guppy import hpy
#import zlib
#hp=hpy()
###HAI
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('serverlog_new.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s > %(levelname)s > %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False # DISABLE LOG STDOUT

logger.info('\n'+'='*20)

try:    
    import tornado.httpserver
    import tornado.websocket
    import tornado.ioloop
    import tornado.web
    import pika
    import random
    from pika import TornadoConnection
    #from pika.adapters.tornado_connection import TornadoConnection
except Exception as e:
    logger.error('MODULES IMPORTING ERROR:'+str(e))
    exit

username = 'gowtham'
password = 'gowtham'
amq_ip = '127.0.0.1'
amq_port = 5672
amq_Vhost = '/'
web_port = 443
connection = None
channel = None

class rmq_conn():
    
    def __init__(self):
        global connection
        self.websocket = None
        self.connecting = False
        self.properties = pika.BasicProperties(content_type="text/plain",delivery_mode=1)
        self.credentials = pika.PlainCredentials(username, password)
    
    def rmq_connect(self):
        global connection
        try:
            if connection != None:
                if connection.is_open:
                    self.rmq_chennal(connection)
                    return
            param = pika.ConnectionParameters(host=amq_ip,port=amq_port,virtual_host=amq_Vhost,credentials=self.credentials)
            connection = TornadoConnection(param,on_open_callback=self.rmq_chennal,stop_ioloop_on_close=False)
            #connection.add_on_close_callback(self.on_closed)
            logger.info('RMQ_CONN CONNECTED')
            #print 'RMQ_CONN CONNECTED'
        except Exception as e:
            print 'RMQ_CONN :'+str(e)
            logger.error('RMQ_CONN :'+str(e))
    
    def rmq_chennal(self,up_connection):
        global connection
        global channel
        try:
            try:
                # CHECK CHANNEL IS ALREAD OPEN
                if channel.is_open == True:
                    self.rmq_exchange(None)
                    return
            except :
                pass
            connection = up_connection
            connection.channel(self.rmq_exchange)
            print 'RMQ_CHANNEL CREATED'
            logger.info('RMQ_CHANNEL CREATED')
        except Exception as e:
            print 'RMQ_CHANNEL :'+str(e)
            logger.error('RMQ_CHANNEL :'+str(e))
    
    def rmq_exchange(self, up_channel):
        global channel
        try:
            if up_channel != None:
                channel = up_channel
            channel.exchange_declare(exchange='SCREENSHARE',type="direct",
                                          auto_delete=True,durable=False,callback=self.rmq_queue)
            print 'RMQ_EXCHANGE_DECLEARED'
            logger.info('RMQ_EXCHANGE_DECLEARED')
        except Exception as e:
            print 'RMQ_EXCHANGE :'+str(e)
            logger.error('RMQ_EXCHANGE :'+str(e))
    
    def rmq_queue(self, frame):
        global channel
        try:
            #result = channel.queue_declare(exclusive=True)
            #self.queue_name = result.method.queue
            print channel.queue_declare(auto_delete=True,queue = self.queue_name,
                                       durable=False,exclusive=False,callback=self.rmq_queue_bind)
            print 'RMQ_QUEUE_DECLARE'
            logger.info('RMQ_QUEUE_DECLARE')
        except Exception as e:
            print 'RMQ_QUEUE_DECLARE :'+str(e)
            logger.error('RMQ_QUEUE_DECLARE :'+str(e))
    
    def rmq_queue_bind(self, frame):
        global channel
        try:
            print channel.queue_bind(exchange='SCREENSHARE',
                                    queue=self.queue_name,
                                    routing_key=self.rmq_route,
                                    callback=self.rmq_queue_bound)
            print 'RMQ_QUEUE_BINDED'
            logger.info('RMQ_QUEUE_BINDED')
        except Exception as e:
            print 'RMQ_QUEUE_BIND :'+str(e)
            logger.error('RMQ_QUEUE_BIND :'+str(e))
    
    def rmq_queue_bound(self, frame):
        global channel
        try:
            if self.client_type != 'PUB':
                # CLIENT IS SUB
                channel.basic_consume(consumer_callback=self.data_to_ws,
                                           queue=self.queue_name,
                                           no_ack=True)
                print 'SUB CLIENT'
                logger.info('SUB CLIENT')
            else:
                # CLIENT IS PUB
                print 'PUB CLIENT'
                logger.info('PUB CLIENT')
        except Exception as e:
            print 'RMQ_QUEUE_BOND :'+str(e)
            logger.error('RMQ_QUEUE_BOND :'+str(e))   
    
    def data_to_ws(self, channel, method, header, body):
        #Send the Cosumed message via Websocket to browser.
        try:
            # STOP BROADCAST TO WHO SEND IT
            if body[0:16] == self.rmq_client_id:
                self.websocket.write_message(body,binary=True)
            else:
                return
            #body = '' #Windows Fix
        except Exception as e:
            print 'DATA_TO_WS :'+str(e)
                    
    def data_to_rmq(self, ws_msg):
        #UNICAST AND BROADCAST
        global channel
        try:
            cnt = ws_msg[0]
            if cnt == '0':
                #IF FIRST CHAR IS 0 IT IS BROADCAST MESSAGE TO SAME ROUTE
                route = self.rmq_route
                ws_msg = ws_msg[1:]
            elif cnt == '1':
                # IF FIRST CHAR NOT 0 THEN USE 2-17 as unicast route key ( 16 chare route_key) 
                route = ws_msg[1:17]
                ws_msg =  ws_msg[17:] 
            else:
                return None
            #Publish the message from Websocket to RabbitMQ
            channel.basic_publish(exchange='SCREENSHARE',
                                       routing_key=route,
                                       body = ws_msg,properties=self.properties)
        except Exception as e:
            print 'DATA_TO_RMQ :'+str(e)
            logger.error('DATA_TO_RMQ :'+str(e))
    
    def cleanup(self):
        global channel
        try:
            channel.queue_delete(queue=self.queue_name)
        except Exception as e:
            print e
            pass
       
    #def on_closed(self,connection,close_code,close_type):
        # CLOSE TORANDO SERVER
        #tornado.ioloop.IOLoop.instance().stop()
class torando_websoc(tornado.websocket.WebSocketHandler):
    def open(self,ws_url):
        try:
            #tornado.websocket.WebSocketHandler.set_nodelay(True)
            print 'CONNECTED WS: '+str(self.open_args)
            logger.info('CONNECTED WS: '+str(self.open_args))
            self.rmq_conn = rmq_conn()
            self.rmq_conn.websocket = self
            rmq_client_id = ws_url.split('-')
            if len(rmq_client_id) == 2:
                self.rmq_conn.rmq_client_id = rmq_client_id[1]
                rmq_route = rmq_client_id[0]
                self.rmq_conn.rmq_route = rmq_route[3:]
                self.rmq_conn.client_type = rmq_route[0:3]
                self.rmq_conn.queue_name = self.rmq_conn.rmq_route+str(random.randint(1,66666677))+'Q'
                self.id2 = ioloop.add_timeout(0, self.rmq_conn.rmq_connect)
                #self.set_nodelay(True)
            else:
                print 'INVALID URL ( CLOSING CONNECTION ):'+ws_url
                logger.error('INVALID URL ( CLOSING CONNECTION ):'+ws_url)
                return
        except Exception as e:
            print 'WS_ON_CONNECT :'+str(e)
            logger.error('WS_ON_CONNECT :'+str(e))
    
    def on_message(self,msg):
        try:
            self.rmq_conn.data_to_rmq(msg)
            #print hp.heap().byrcs[0].byid
        except Exception as e:
            print 'WS_ON_MESSAGE :'+str(e)
            logger.error('WS_ON_MESSAGE :'+str(e))
    
    def on_error(self, error):
        print 'WS_ON_ERROR :'+str(error)
        logger.error('WS_ON_ERROR :'+str(error))
    
    def check_origin(self, origin):
        return True
    
    def on_close(self):
        try:
            
            print 'WS_ON_CLOSE: '+str(self.open_args)
            logger.info('WS_ON_CLOSE: '+str(self.open_args))
            self.rmq_conn.cleanup()
            del self
            #print ioloop.remove_timeout(self.id2)
            #self.rmq_conn.channel.close()
            #del self.rmq_conn
        except Exception as e:
            print e
            logger.error('WS_ON_CLOSE :'+str(e))
            
if __name__ == '__main__':
    try:
        app = [(r'/(.*)',torando_websoc ),]
        application = tornado.web.Application(app)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(web_port)
        logger.info("WEBSERVER START LISTERNING ON: "+str(web_port))
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.start()
    except Exception as e:
        print e
        logger.error('HTTP SERVER :'+str(e))
