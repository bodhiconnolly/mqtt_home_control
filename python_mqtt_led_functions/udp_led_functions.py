from time import sleep
import threading
import datetime
import paho.mqtt.client as mqtt


#### CONSTANTS ####

#MQTTServer="home.bodhiconnolly.com"
MQTTServer="192.168.1.100"
MQTTPort=1882
waitTime=datetime.timedelta(milliseconds=50)
ledTopic="room/lights/strips/"
functionTopic="room/function/#"
systemTopic="system/functions/room"
lastTime=datetime.datetime.now()


#### MQTT SENDING ####

def sendMQTT(topic,message):
    client.publish(topic,message)
    
def setRGB(r=None,g=None,b=None):
    if not (r==None):
        sendMQTT(ledTopic+"r",r)
    if not (g==None):
        sendMQTT(ledTopic+"g",g)
    if not (b==None):
        sendMQTT(ledTopic+"b",b)

def setRGBWait(r=None,g=None,b=None):
    global lastTime
    if datetime.datetime.now()-lastTime>waitTime:
        setRGB(r,g,b)
        lastTime=datetime.datetime.now()

def updateStatus(function,wake=None):
    pass

#### THREAD FUNCTIONS ####

class StoppableThread(threading.Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()
        #print "Thread Started"

    def stop(self):
        self._stop.set()

class FadeThread(StoppableThread):
    def __init__(self,fadeSpeed):
        super(FadeThread, self).__init__()
        self.fadeSpeed=fadeSpeed/255
        
    def run(self):
        updateStatus("fade")
        print "Starting fade"
        setRGB(0,0,255)
        while not self._stop.isSet():
             self.fade(self.fadeSpeed)

    def fade(self,fadespeed):
        lastTime=datetime.datetime.now()
        for i in range(0,256,1):
            if not self._stop.isSet():
                setRGBWait(r=i)
                sleep(fadespeed)
            else:
                break
        for i in range(255,-1,-1):
            if not self._stop.isSet():
                setRGBWait(b=i)

                sleep(fadespeed)
            else:
                break
        for i in range(0,256,1):
            if not self._stop.isSet():
                setRGBWait(g=i)
                sleep(fadespeed)
            else:
                break
        for i in range(255,-1,-1):
            if not self._stop.isSet():
                setRGBWait(r=i)
                sleep(fadespeed)
            else:
                break
        for i in range(0,256,1):
            if not self._stop.isSet():
                setRGBWait(b=i)
                sleep(fadespeed)
            else:
                break
        for i in range(255,-1,-1):
            if not self._stop.isSet():
                setRGBWait(g=i)
                sleep(fadespeed)
            else:
                break
            
    def setSpeed(fadeSpeed):
        self.fadeSpeed=fadeSpeed/255

             

class SleepThread(StoppableThread):
    def __init__(self,sleepTime):
        super(SleepThread, self).__init__()
        self.sleepTime=sleepTime
        
    def run(self):
        updateStatus("sleep")
        print "Starting sleep"
        self.ledSleep(self.sleepTime)
             
    def ledSleep(self,sleepTime):
        sleepDelay=(sleepTime)/255
        for i in range(255,100,-1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(sleepDelay*0.2)
            else:
                break
        for i in range(100,50,-1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(sleepDelay*1)
            else:
                break
        for i in range(50,10,-1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(sleepDelay*2)
            else:
                break
        for i in range(10,-1,-1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(sleepDelay*10)
            else:
                break
        updateStatus("none","asleep")


class WakeThread(StoppableThread):
    def __init__(self,wakeTime):
        super(WakeThread, self).__init__()
        self.wakeTime=wakeTime
        
    def run(self):
        print "Starting wake"
        updateStatus("wake")
        self.wake(self.wakeTime)

    def wake(self,sleepTime):
        wakeDelay=(self.wakeTime)/255
        for i in range(1,11,1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(wakeDelay*10)
            else:
                break
        for i in range(11,51,1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(wakeDelay*2)
            else:
                break
        for i in range(51,101,1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(wakeDelay*1)
            else:
                break
        for i in range(101,255,1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(wakeDelay*0.2)
            else:
                break
        setRGB(255,255,255)
        updateStatus("none","awake")

class FastWakeThread(StoppableThread):
    def __init__(self,wakeTime):
        super(FastWakeThread, self).__init__()
        self.wakeTime=wakeTime
        
    def run(self):
        print "Starting fast wake"
        updateStatus("wake")
        self.wake(self.wakeTime)

    def wake(self,sleepTime):
        wakeDelay=(self.wakeTime)/255
        for i in range(1,256,1):
            if not self._stop.isSet():
                setRGBWait(i,i,i)
                sleep(wakeDelay)
            else:
                break
        setRGB(255,255,255)
        updateStatus("none","awake")
            
#### CONTROLLING OBJECT ####
            
class ledController(object):
    def __init__(self):
        self.fadeThread=FadeThread(1)
        self.sleepThread=SleepThread(1)
        self.wakeThread=WakeThread(1)
        self.fastwakeThread=FastWakeThread(1)

    def stopThreads(self):
        self.fadeThread.stop()
        self.sleepThread.stop()
        self.wakeThread.stop()
        self.fastwakeThread.stop()
        
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(functionTopic)
        client.publish(systemTopic,"Function Controller On")

    def parseMessage(self, client, userdata, msg):
        print msg.topic+" "+str(msg.payload)
        topic=msg.topic.split("/")
        payload=msg.payload
        if topic[0]=='room' and topic[1]=='function':
            self.stopThreads()
            updateStatus("none")
            if topic[2]=='sleep':
                self.sleepThread=SleepThread(float(payload))
                self.sleepThread.start()
            elif topic[2]=='wake':
                self.wakeThread=WakeThread(float(payload))
                self.wakeThread.start()
            elif topic[2]=='fastwake':
                self.fastwakeThread=FastWakeThread(float(payload))
                self.fastwakeThread.start()
            elif topic[2]=='fade':
                self.fadeThread=FadeThread(float(payload))
                self.fadeThread.start()
            elif topic[2]=='stop':
                pass
            else:
                print "Not a valid function: " + str(topic)



            
        
            

#### RUNTIME ####
                    
if __name__ == "__main__":
    l=ledController()
    client = mqtt.Client()
    client.on_connect = l.on_connect
    client.on_message = l.parseMessage
    client.connect(MQTTServer, MQTTPort, 60)
    client.loop_forever()




