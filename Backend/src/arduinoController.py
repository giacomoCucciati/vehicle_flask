from serial import Serial
import sys
import threading
import time
import requests
from random import randrange

class ArduinoController:
  def __init__(self):
    self.port = ""
    self.ser = None

  def openSerial(self, port):
    self.port = port
    print('Connecting to device', port)
    self.ser = Serial(port, 9600, timeout=None)
    self.ser.flushInput()

  def stopSerial(self):
    print("Empty function")
    #self.ser.close() 
  
  def sendCommand(self, command):
    print('Sending command', command, 'to arduino')
    fullMessage = command + '\n'
    my_str_as_bytes = str.encode(fullMessage)
    self.ser.write(my_str_as_bytes)