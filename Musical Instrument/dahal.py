from machine import Pin, SoftI2C, PWM, ADC
import servo, ssd1306, adxl345, network, time, asyncio
from mqtt import MQTTClient




class Dahal:

    def __init__(self):

        self.image = []

        self.mqtt_broker = 'broker.hivemq.com'
        self.port = 1883
        self.topic_sub = 'ME35-24/music'
        self.topic_pub = 'ME35-24/music'

        self.i2c = SoftI2C(scl = Pin(7), sda = Pin(6)) #I2C
        self.wlan = network.WLAN(network.STA_IF)
        self.screen = ssd1306.SSD1306_I2C(128,64,self.i2c) #LCD Display
        self.adx = adxl345.ADXL345(self.i2c)
        self.pot = ADC(Pin(3)) #Potentiometer
        self.pot.atten(ADC.ATTN_11DB)
        self.motor = servo.Servo(Pin(2)) #Servo
        self.sd = Pin(8, Pin.IN) 

        # self.internet_connection()
        # self.mqtt_subscribe()


    def mqtt_subscribe(self):
        # MQTT initialization of client and subscribing to topic 'Mater'

        def callback(topic, msg):
            topic, msg = topic.decode(), msg.decode()
            print(msg)
                


        self.client = MQTTClient('still_dre', self.mqtt_broker, self.port, keepalive=60)
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

    async def potentiometer(self):
        while True:
            self.pot_value = self.pot.read_u16()
            msg = 'Volume {self.pot_value}'
            self.client.publish(self.topic_pub.encode, msg.encode())
            await asyncio.sleep(.01)

    def lcd_display(self):
        self.screen.fill(0)

        # Render the bitmap on the screen from self.image array
        for y in range(64):
            for x in range(128):
                pixel_on = self.image[y][x]  # Get the pixel value (1 or 0)
                self.screen.pixel(x, y, pixel_on)

        self.screen.show()
        

    def populate_image(self):
        try:
            with open("snoop_bitmap.txt", "r") as file:
                # Read each line (representing a row of pixels)
                for line in file:
                    # Strip the newline character and split by commas
                    row = line.strip().split(',')
                    # Convert the '1's and '0's to integers and add to the image array
                    self.image.append([int(pixel) for pixel in row])
            print("Image loaded successfully.")
        except Exception as e:
            print("Error loading image:", e)

    async def main(self):
        task1 = asyncio.create_task(self.check_mqtt())
        task2 = asyncio.create_task(self.potentiometer())
        asyncio.gather(task1,task2)
        asyncio.get_event_loop().run_forever()


board = Dahal()

board.populate_image()
board.lcd_display()

asyncio.run(board.main())






        