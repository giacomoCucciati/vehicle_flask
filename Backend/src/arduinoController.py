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
    self.ser = Serial(port, 9600, timeout=None)
    self.ser.flushInput()

  def stopSerial(self):
    print("Empty function")
    #self.ser.close() 