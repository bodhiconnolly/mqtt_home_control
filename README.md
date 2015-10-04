# mqtt_home_control
An MQTT based multi-Arduino project to control LED lights in multiple rooms

This project has multiple components, aimed to be as modular as possible:

## Light Controllers
 - Arduinos connected to RGB LED strips, which simply receive an mqtt command and activate the relevant lights
 - Each Arduino has a unique individual ID and a room ID. Lights can be controlled for entire rooms or for individual Arduinos (ie fade all kitchen lights, or fade kitchen light 3)
 
 ## Motion Detectors
 - Arduinos attached to PIR motion detectors, each with a room ID
 - These devices simply a signal whenever the state (motion/no motion) of the room changes and with certain time intervals

 ## Motion Processor
 - Python script that captures incoming motion information and decides how to act
 - For example, no motion to motion (during waking hours) will activate full lights
 - Motion to no motion will wait for timeout and then slowly turn lights off (giving a chance for user to wave their hands and turn lights back on)
 
 ## Function Processor
 - Python script that takes a function (ie Motion Processor says "fade lights off") and starts a background thread that will perform that function until it finishes or is stopped
 - Takes a range of functions and parameters, for example "flash lights in kitchen every 3 seconds"
 
 ## iOS App
 - A simple iPhone app that can control individual lights or start functions
 - See [my other github project](https://github.com/bodhiconnolly/iphone_mqtt_controller)
