from time import sleep
import threading
import datetime
import paho.mqtt.client as mqtt

MQTTServer="home.bodhiconnolly.com"
MQTTPort=1882
waitTime=datetime.timedelta(milliseconds=50)
lastTime=datetime.datetime.now()
fadeSeconds=5

onTopic = "system/room/PIR"
onMessage = "PIR Receiver On"
funcTopic = "room/function/"
incomingTopic = "room/pir/status"

def sendMQTT(topic,message):
    client.publish(topic,message)

class PIRChecker(object):
    def __init__(self):
            super(PIRChecker,self).__init__()
            self.prevState = "inactive"
            self.actedOnPrevious = False
    def timeNeedsLights(self):
        #return 1 or 0
         if datetime.datetime.now().hour<22 and datetime.datetime.now().hour>8:
             return True
         else:
            return False 



    def parseMessage(self,client, userdata, msg):
        payload=msg.payload
        topic=msg.topic
        print topic+': '+payload
        if payload=='active':
            state=True
        elif payload=='inactive':
            state=False
        else:
            print 'Invalid message: '+payload
            return
        lastFunc,awake = self.getStatus()
        if awake:
            if not state:
                if lastFunc == 'none':
                    if state==self.prevState:
                        if not self.actedOnPrevious:
                            self.setFunction('sleep')
                            self.prevState='inactive'
                        else:
                            #lights probably already down
                            pass
                    else:
                        self.setFunction('sleep')
                        self.prevState='inactive'

                        
                else:
                    self.actedOnPrevious=False
                
            elif state:
                if lastFunc == 'none':
                    if self.timeNeedsLights():
                        self.setFunction('fastwake')
                        self.prevState='active'
                    
                    
                

        else:
            self.actedOnPrevious=False
            
    def getStatus(self):
            #get BOOL awake
            #get String lastFunction
            #return tuple
            return 'none',True
            
    def setFunction(self, func):
            self.actedOnPrevious=True
            sendMQTT(funcTopic+func,fadeSeconds)
            
    def on_connect(self, client, userdata, flags, rc):
            client.subscribe(incomingTopic)
            sendMQTT(onTopic,onMessage)
        
        
#### RUNTIME ####
                    
if __name__ == "__main__":
    p=PIRChecker()
    client = mqtt.Client()
    client.on_connect = p.on_connect
    client.on_message = p.parseMessage
    client.connect(MQTTServer, MQTTPort, 60)
    client.loop_forever()