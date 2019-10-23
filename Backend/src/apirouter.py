from flask import Blueprint, jsonify
from flask_socketio import emit, join_room, leave_room
from flask import request
from . import socketio
from .arduinoController import ArduinoController
import time
import logging
import os
import json

apirouter = Blueprint("router", __name__)
arduinoController = ArduinoController()
portList = []

# I don't know where to put the creation of the port list
configFile = open(os.path.join("static", "config.json"), "r")
json_data = json.load(configFile)
print(json_data)
portList = json_data['portlist']

@apirouter.route('/startArduino',methods=['POST'])
def startArduino():
  message = 'Nothing appened'
  params = request.get_json(force=True)
  arduinoController.openSerial(params['selectedPort'])
  message = 'Serial reading started'
  return jsonify({"message": message})

@apirouter.route('/stopArduino',methods=['GET'])
def stopArduino():
  message = 'Nothing appened'
  try:
    arduinoController.stopSerial()
    message = 'Stop message sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred'
  return jsonify({"message": message})

@apirouter.route('/getPageUpdate',methods=['GET'])
def getPageUpdate():
  answer = {
    "selectedPort": arduinoController.port, 
    "portlist": portList, 
  }
  return jsonify(answer)