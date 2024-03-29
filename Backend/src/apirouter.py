from flask import Blueprint, jsonify
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask import Response
from . import socketio
from .arduinoController import ArduinoController
import time
import logging
import os
import json
import io
from threading import Condition

apirouter = Blueprint("router", __name__)
arduinoController = None
portList = []

# I don't know where to put the creation of the port list
configFile = open(os.path.join("static", "config.json"), "r")
json_data = json.load(configFile)
print(json_data)
portList = json_data['portlist']


@apirouter.route('/startArduino',methods=['POST'])
def startArduino():
  global arduinoController
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    if arduinoController == None:
      arduinoController = ArduinoController()
    arduinoController.openSerial(params['selectedPort'])
    message = 'Serial communication created'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred starting the arduino'
  return jsonify({"message": message})

@apirouter.route('/stopArduino',methods=['GET'])
def stopArduino():
  global arduinoController
  message = 'Nothing happened'
  try:
    arduinoController = None
    message = 'Stop message sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred stopping the arduino'
  return jsonify({"message": message})

@apirouter.route('/sendCommandToArduino', methods=['POST'])
def sendCommandToArduino():
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    print(params['clicktime'])
    arduinoController.sendCommand(params['command'])
    message = 'Command sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred sending command to the arduino'
  return jsonify({"message": message, 'servertime':time.time()})

@apirouter.route('/releaseCommandToArduino', methods=['POST'])
def releaseCommandToArduino():
  message = 'Nothing happened'
  try:
    params = request.get_json(force=True)
    releaseCommand = '-' + params['command']
    arduinoController.sendCommand(releaseCommand)
    message = 'Command sent'
  except Exception as e:
    print('Error: ', e)
    message = 'An error has occurred sending command to the arduino'
  return jsonify({"message": message})


@apirouter.route('/getPageUpdate',methods=['GET'])
def getPageUpdate():
  port = ""
  if arduinoController != None:
    port = arduinoController.port
  answer = {
    "selectedPort": port,
    "portlist": portList
  }
  return jsonify(answer)


try:
    from .camera_pi import Camera
except ImportError:
    print("Python library to contorl PI Camera has not been found! Disabling related functions...")
    def video_feed():
        return jsonify({})

    def gen(camera):
        return jsonify({})
else:
    @apirouter.route('/video_feed') 
    def video_feed(): 
        """Video streaming route. Put this in the src attribute of an img tag.""" 
        return Response(gen(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')
   
    def gen(camera):
        """Video streaming generator function."""
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
