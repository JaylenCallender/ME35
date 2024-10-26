import time, asyncio, network
from BLE_CEEO import Yell
from mqtt import MQTTClient
from machine import ADC

class Still_Dre:
    def __init__(self):

        #Broker Init
        self.mqtt_broker = 'broker.hivemq.com'
        self.port = 1883
        self.topic_sub = 'ME35-24/music'

        #Network Init
        self.wlan = network.WLAN(network.STA_IF)

        NoteOn = 0x90
        NoteOff = 0x80
        StopNotes = 123
        SetInstroment = 0xC0
        Reset = 0xFF

        velocity = {'off':0, 'pppp':8,'ppp':20,'pp':31,'p':42,'mp':53,
            'mf':64,'f':80,'ff':96,'fff':112,'ffff':127}
            
        self.p = Yell('Jaylen', verbose = True, type = 'midi')

        self.volume = velocity['f']
        self.newVolume = 0 
        self.photoValue = 0
        self.photoResistor = ADC(27)
        self.paused = False

        self.current_step = 0
        self.current_step2 = 0
        self.step = []
        self.step2 = []
        channel = 0
        
        self.c5 = 72
        self.e5 = 76
        self.a5 = 81
        self.g5 = 79
        self.b4 = 71
        self.a1 = 33
        self.b1 = 35
        self.e1 = 28


        cmd = NoteOn
        off = NoteOff
        channel = 0x0F & channel
        timestamp_ms = time.ticks_ms()
        tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
        tsL =  0x80 | (timestamp_ms & 0b1111111)

        c =  cmd | channel
        o = off | channel  

        #on  
        self.c5_payload = bytes([tsM,tsL,c,self.c5,velocity['f']])
        self.e5_payload = bytes([tsM,tsL,c,self.e5,velocity['f']])
        self.a5_payload = bytes([tsM,tsL,c,self.a5,velocity['f']])
        self.g5_payload = bytes([tsM,tsL,c,self.g5,velocity['f']])
        self.b4_payload = bytes([tsM,tsL,c,self.b4,velocity['f']])
        self.a1_payload = bytes([tsM,tsL,c,self.a1,velocity['f']])
        self.b1_payload = bytes([tsM,tsL,c,self.b1,velocity['f']])
        self.e1_payload = bytes([tsM,tsL,c,self.e1,velocity['f']])

        #off
        self.c5_payload_off = bytes([tsM,tsL,o,self.c5,velocity['f']])
        self.e5_payload_off = bytes([tsM,tsL,o,self.e5,velocity['f']])
        self.a5_payload_off = bytes([tsM,tsL,o,self.a5,velocity['f']])
        self.g5_payload_off = bytes([tsM,tsL,o,self.g5,velocity['f']])
        self.b4_payload_off = bytes([tsM,tsL,o,self.b4,velocity['f']])
        self.a1_payload_off = bytes([tsM,tsL,o,self.a1,velocity['f']])
        self.b1_payload_off = bytes([tsM,tsL,o,self.b1,velocity['f']])
        self.e1_payload_off = bytes([tsM,tsL,o,self.e1,velocity['f']])


        
        #self.internet_connection()
        #self.mqtt_subscribe()
        self.ble_connect()
        

    def new_pitch(self):
        print("Values have been changed")
        self.c5 = 84
        self.e5 = 88
        self.a5 = 93
        self.g5 = 91
        self.b4 = 83
        self.a1 = 45
        self.b1 = 47
        self.e1 = 40
    
    def old_pitch(self):
        print("Values reverted")
        self.c5 = 72
        self.e5 = 76
        self.a5 = 81
        self.g5 = 79
        self.b4 = 71
        self.a1 = 33
        self.b1 = 35
        self.e1 = 28

    def mqtt_subscribe(self):
        # MQTT initialization of client and subscribing to topic 'Mater'

        def callback(topic, msg):
            topic, msg = topic.decode(), msg.decode()
            print(msg)
            if msg == "play":
                self.paused = False
                self.play()
            elif msg == "pause":
                self.paused = True
                self.pause()
            elif msg == "1.00, 0.00":
                self.new_pitch()
                self.play()
            elif msg == "0.00, 1.00":
                self.old_pitch()
                self.play()
            elif msg == "Volume {}":
                self.newVolume = {}
                self.changeVelocity()



        self.client = MQTTClient('music', self.mqtt_broker, self.port, keepalive=60)
        self.client.connect()
        print('Connected to %s MQTT broker' % self.mqtt_broker)
        self.client.set_callback(callback)  # Set the callback for incoming messages
        self.client.subscribe(self.topic_sub.encode())  # Subscribe to a topic
        print(f'Subscribed to topic {self.topic_sub}')  # Debug print

    def internet_connection(self):
        try:
            self.wlan.active(True)
            self.wlan.connect('Tufts_Robot', '')

            while self.wlan.ifconfig()[0] == '0.0.0.0':
                print('.', end=' ')
                time.sleep(1)

            # We should have a valid IP now via DHCP
            print(self.wlan.ifconfig())
        except Exception as e:
            print("Failed Connection: ", e)
            quit()

    async def check_mqtt(self):
        while True:
            self.client.check_msg()
            await asyncio.sleep(.01)

    def changeVelocity(self):
        self.volume = self.newVolume

    def ble_connect(self):
        self.p.connect_up()
        time.sleep(3.5)   

    def vStep1(self):
        self.step = [(self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0), 
                     (self.b4_payload, .35),
                     (self.b4_payload_off, 0), 
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0), 
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.b4_payload, .35),
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .35), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .35),
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .35), 
                     (self.b4_payload_off, 0), 
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0), 
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .35),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0), 
                     (self.b4_payload, .35),
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .35),
                     (self.a5_payload_off, 0),
                     (self.b4_payload, .35),
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .35),
                     (self.g5_payload_off, 0),
                     (self.e5_payload, .35),
                     (self.e5_payload_off, 0),
                     (self.c5_payload, .2), #begin cea quick
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0), #endcea
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0), #endbeg_quick and cea quick
                     (self.b4_payload, .2),
                     (self.b4_payload_off, 0),
                     (self.c5_payload, .2), #begin cea quick
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0),
                     (self.c5_payload, .2),
                     (self.c5_payload_off, 0),
                     (self.e5_payload, .2),
                     (self.e5_payload_off, 0),
                     (self.a5_payload, .2),
                     (self.a5_payload_off, 0), #endcea
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0),
                     (self.b4_payload, .2), #beginbeg_quick
                     (self.b4_payload_off, 0),
                     (self.e5_payload, .2), 
                     (self.e5_payload_off, 0),
                     (self.g5_payload, .2), 
                     (self.g5_payload_off, 0), #endbeg_quick and cea quick
                     (self.b4_payload, .2)
                     
        ]

    def vStep2(self):
        self.step2 = [(self.c5_payload, self.e5_payload, self.a5_payload, .5), #start cea same
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end cea same
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), #start of bea same
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end of bea same
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5), #start cea same
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end cea same
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), #start of bea same
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end of bea same
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5), #start cea same
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end cea same
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), #start of bea same
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end of bea same
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5), #start cea same
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.c5_payload, self.e5_payload, self.a5_payload, .5),
                      (self.c5_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end cea same
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), #start of bea same
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.a5_payload, .5), 
                      (self.b4_payload_off, self.e5_payload_off, self.a5_payload_off, 0), #end of bea same
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),
                      (self.b4_payload, self.e5_payload, self.g5_payload, .5), #start of beg same
                      (self.b4_payload_off, self.e5_payload_off, self.g5_payload_off, 0),


                      
        
        
        ]

    def pause(self):
        if self.paused:
            print("Paused")


    #Check the photoresistor value to see if it exceeds the limit 
    def check_photo(self):
        
        self.photoValue = self.photoResistor.read_u16()
        print(self.photoValue)
        if self.photoValue > 800:
            self.paused = True
        else:
            self.paused = False
            
    #Continously check the photoresistor value
    async def photo(self):
        while True:
            self.photoValue = self.photoResistor.read_u16()
            print(self.photoValue)
            if self.photoValue < 800:
                self.paused = False
                self.play()
                await asyncio.sleep(.1)
            else:
                self.paused = True
                # self.play()
            await asyncio.sleep(.1)

    #Play Still Dre by Dr.Dre ft Snoop Dogg 
    def play(self):
        self.vStep1()
        while self.current_step < len(self.step) and not self.paused:
                self.client.check_msg()
                self.check_photo()
                payload, delay = self.step[self.current_step]
                self.action(payload)
                if delay > 0:
                    time.sleep(delay)
                self.current_step += 1

                
        if(self.current_step == len(self.step)):
            del self.step
            
        
        self.vStep2()
        

        while self.current_step2 < len(self.step2) and not self.paused:
            self.client.check_msg()
            self.check_photo()
            payload1, payload2, payload3, delay = self.step2[self.current_step2]
            self.action2(payload1, payload2, payload3)
            if delay > 0:
                time.sleep(delay)
            self.current_step2 += 1

        if(self.current_step2 == len(self.step2)):
            del self.step2
            self.p.disconnect()
        
    #Send bytes over ble
    def action(self, payload):
        self.p.send(payload)

    #Send bytes over ble 
    def action2(self, payload1, payload2, payload3):
        self.p.send(payload1)
        self.p.send(payload2)
        self.p.send(payload3)

    async def main(self):

        self.task1 = asyncio.create_task(self.photo())
        self.task2 = asyncio.create_task(self.check_mqtt())

        asyncio.gather(self.task1, self.task2)
        asyncio.get_event_loop().run_forever()


play = Still_Dre()

asyncio.run(play.main())